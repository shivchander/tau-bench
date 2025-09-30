# GEPA Synthetic Data Training Plan for Tau-Bench

## Project Overview

This document contains a complete plan for using synthetic tau-bench data to train better airline agents using the GEPA (Genetic-Pareto) optimization framework.

## Current Analysis Summary

### Synthetic Data Available
- **456 total validated synthetic tasks** (100 easy + 356 medium difficulty)
- **Data location**:
  - `tau_bench/sdg/validated_tasks_easy_with_instructions.json` (100 tasks)
  - `tau_bench/sdg/validated_tasks_medium_with_instructions.json` (356 tasks)
- **Data quality**: High-quality instruction-action pairs with realistic airline scenarios
- **Integration**: Already supported via `task_split="synthetic"` in tau-bench

### Current Performance Baseline
- **GPT-4o on airline tasks**: 42% success rate (84/200 successful from historical data)
- **Action distribution in synthetic data**:
  - `update_reservation_baggages`: 304 occurrences
  - `book_reservation`: 279 occurrences
  - `update_reservation_flights`: 269 occurrences
  - `cancel_reservation`: 219 occurrences
  - Plus 9 other action types

### Data Structure
Each synthetic task contains:
```json
{
  "user_id": "anya_lee_9572",
  "actions": [
    {
      "name": "cancel_reservation",
      "kwargs": {"reservation_id": "7KYHMW"}
    },
    // ... more actions
  ],
  "instruction": "Your user id is anya_lee_9572. You want to cancel...",
  "difficulty": "medium",
  "method": "few_shot_learning"
}
```

## Implementation Plan

### Phase 1: Setup and Baseline (Day 1)

#### 1.1 Install Dependencies
```bash
# On cluster
cd tau-bench
uv pip install gepa
```

#### 1.2 Run Baseline Evaluation
```bash
# Test current performance on synthetic data
python run.py --env airline --task-split synthetic --agent-strategy tool-calling \
  --model gpt-4o --model-provider openai --max-concurrency 10 \
  --num-trials 1 --start-index 0 --end-index 50
```

#### 1.3 Analyze Results
- Measure current success rate on synthetic tasks
- Identify common failure patterns
- Save baseline results for comparison

### Phase 2: GEPA Adapter Implementation (Days 1-2)

#### 2.1 Create TauBenchGEPAAdapter

Create file: `tau_bench/optimization/gepa_adapter.py`

```python
import json
import os
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

from gepa import GEPAAdapter, EvaluationBatch
from tau_bench.envs import get_env
from tau_bench.agents.tool_calling_agent import ToolCallingAgent
from tau_bench.types import Task, Action


@dataclass
class TauBenchDataInst:
    """Single tau-bench task instance"""
    task: Task
    task_index: int


@dataclass
class TauBenchTrajectory:
    """Execution trajectory for a tau-bench task"""
    task_index: int
    messages: List[Dict[str, Any]]
    actions_taken: List[Action]
    final_reward: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class TauBenchOutput:
    """Raw output from tau-bench execution"""
    reward: float
    success: bool
    messages: List[Dict[str, Any]]


class TauBenchGEPAAdapter(GEPAAdapter[TauBenchDataInst, TauBenchTrajectory, TauBenchOutput]):
    """GEPA adapter for optimizing tau-bench airline agents"""

    def __init__(
        self,
        model: str = "gpt-4o",
        model_provider: str = "openai",
        temperature: float = 0.0,
        max_steps: int = 30
    ):
        self.model = model
        self.model_provider = model_provider
        self.temperature = temperature
        self.max_steps = max_steps

    def evaluate(
        self,
        batch: List[TauBenchDataInst],
        candidate: Dict[str, str],
        capture_traces: bool = False
    ) -> EvaluationBatch[TauBenchTrajectory, TauBenchOutput]:
        """
        Evaluate agent with candidate system prompt on batch of tasks

        candidate should contain:
        - "system_prompt": The wiki content to use as system prompt
        """
        outputs = []
        scores = []
        trajectories = [] if capture_traces else None

        # Get environment with synthetic tasks
        env = get_env(
            env_name="airline",
            user_strategy="llm",
            user_model="gpt-4o",
            task_split="synthetic",
            user_provider="openai"
        )

        # Create agent with candidate system prompt
        wiki_content = candidate.get("system_prompt", env.wiki)
        agent = ToolCallingAgent(
            tools_info=env.tools_info,
            wiki=wiki_content,  # Use evolved system prompt
            model=self.model,
            provider=self.model_provider,
            temperature=self.temperature
        )

        for data_inst in batch:
            try:
                # Run agent on this task
                result = agent.solve(env, task_index=data_inst.task_index, max_num_steps=self.max_steps)

                success = result.reward > 0.5  # Binary success

                output = TauBenchOutput(
                    reward=result.reward,
                    success=success,
                    messages=result.messages
                )
                outputs.append(output)
                scores.append(float(success))  # Binary scoring: 1.0 if success, 0.0 if failure

                if capture_traces:
                    trajectory = TauBenchTrajectory(
                        task_index=data_inst.task_index,
                        messages=result.messages,
                        actions_taken=self._extract_actions_from_messages(result.messages),
                        final_reward=result.reward,
                        success=success,
                        error_message=None
                    )
                    trajectories.append(trajectory)

            except Exception as e:
                # Handle failures gracefully
                output = TauBenchOutput(
                    reward=0.0,
                    success=False,
                    messages=[]
                )
                outputs.append(output)
                scores.append(0.0)

                if capture_traces:
                    trajectory = TauBenchTrajectory(
                        task_index=data_inst.task_index,
                        messages=[],
                        actions_taken=[],
                        final_reward=0.0,
                        success=False,
                        error_message=str(e)
                    )
                    trajectories.append(trajectory)

        return EvaluationBatch(
            outputs=outputs,
            scores=scores,
            trajectories=trajectories
        )

    def make_reflective_dataset(
        self,
        candidate: Dict[str, str],
        eval_batch: EvaluationBatch[TauBenchTrajectory, TauBenchOutput],
        components_to_update: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Build reflective dataset from failed executions"""

        reflective_data = {}

        if "system_prompt" in components_to_update:
            system_prompt_data = []

            for i, (trajectory, output) in enumerate(zip(eval_batch.trajectories, eval_batch.outputs)):
                if not output.success:  # Focus on failures
                    # Extract task instruction and expected actions
                    task = self._get_task_by_index(trajectory.task_index)

                    feedback_parts = []
                    if trajectory.error_message:
                        feedback_parts.append(f"Error: {trajectory.error_message}")

                    # Analyze what went wrong
                    expected_actions = [a.name for a in task.actions]
                    actual_actions = [a.name for a in trajectory.actions_taken]

                    if len(actual_actions) == 0:
                        feedback_parts.append("Agent failed to take any actions")
                    elif set(actual_actions) != set(expected_actions):
                        feedback_parts.append(f"Expected actions: {expected_actions}, but agent took: {actual_actions}")

                    record = {
                        "Inputs": {
                            "user_instruction": task.instruction,
                            "user_id": task.user_id,
                            "expected_actions": [a.name for a in task.actions]
                        },
                        "Generated Outputs": {
                            "actions_taken": actual_actions,
                            "final_reward": output.reward,
                            "message_count": len(trajectory.messages)
                        },
                        "Feedback": " | ".join(feedback_parts) if feedback_parts else "Task failed without clear error"
                    }
                    system_prompt_data.append(record)

            reflective_data["system_prompt"] = system_prompt_data

        return reflective_data

    def _extract_actions_from_messages(self, messages: List[Dict[str, Any]]) -> List[Action]:
        """Extract Action objects from message history"""
        actions = []
        for msg in messages:
            if msg.get("tool_calls"):
                for tool_call in msg["tool_calls"]:
                    if tool_call.get("function"):
                        action = Action(
                            name=tool_call["function"]["name"],
                            kwargs=json.loads(tool_call["function"]["arguments"])
                        )
                        actions.append(action)
        return actions

    def _get_task_by_index(self, task_index: int) -> Task:
        """Get task by index from synthetic dataset"""
        # Load synthetic tasks
        env = get_env(
            env_name="airline",
            user_strategy="llm",
            user_model="gpt-4o",
            task_split="synthetic",
            user_provider="openai"
        )
        return env.tasks[task_index]
```

#### 2.2 Create Training Script

Create file: `tau_bench/optimization/train_with_gepa.py`

```python
#!/usr/bin/env python3
"""
Train tau-bench airline agents using GEPA optimization on synthetic data
"""
import json
import os
from typing import List

import gepa
from tau_bench.envs import get_env
from tau_bench.optimization.gepa_adapter import TauBenchGEPAAdapter, TauBenchDataInst


def load_synthetic_tasks(max_tasks: int = 50) -> List[TauBenchDataInst]:
    """Load synthetic tau-bench tasks for training"""
    env = get_env(
        env_name="airline",
        user_strategy="llm",
        user_model="gpt-4o",
        task_split="synthetic",
        user_provider="openai"
    )

    # Use medium difficulty tasks for training
    data_instances = []
    for i, task in enumerate(env.tasks[:max_tasks]):
        if hasattr(task, 'difficulty') and task.difficulty == "medium":
            data_instances.append(TauBenchDataInst(task=task, task_index=i))

    return data_instances


def main():
    # Load training data (subset for faster iteration)
    print("Loading synthetic training tasks...")
    train_tasks = load_synthetic_tasks(max_tasks=50)  # Start with smaller set
    print(f"Loaded {len(train_tasks)} training tasks")

    # Get baseline system prompt
    env = get_env(
        env_name="airline",
        user_strategy="llm",
        user_model="gpt-4o",
        task_split="synthetic",
        user_provider="openai"
    )

    seed_candidate = {
        "system_prompt": env.wiki  # Start with current wiki content
    }

    # Create adapter
    adapter = TauBenchGEPAAdapter(
        model="gpt-4o",
        model_provider="openai",
        temperature=0.0
    )

    # Run GEPA optimization
    print("Starting GEPA optimization...")
    result = gepa.optimize(
        adapter=adapter,
        seed_candidate=seed_candidate,
        trainset=train_tasks,
        valset=train_tasks[:10],  # Use subset for validation
        max_iterations=5,  # Start with fewer iterations
        batch_size=5,     # Small batches for faster feedback
    )

    # Save results
    os.makedirs("results/gepa_optimization", exist_ok=True)

    with open("results/gepa_optimization/optimized_candidate.json", "w") as f:
        json.dump(result.best_candidate, f, indent=2)

    with open("results/gepa_optimization/optimization_log.json", "w") as f:
        json.dump({
            "final_score": result.best_score,
            "iterations": result.num_iterations,
            "original_wiki_length": len(seed_candidate["system_prompt"]),
            "optimized_wiki_length": len(result.best_candidate["system_prompt"])
        }, f, indent=2)

    print(f"Optimization complete!")
    print(f"Best score: {result.best_score}")
    print(f"Results saved to results/gepa_optimization/")

    # Show diff in system prompts
    print("\n=== SYSTEM PROMPT CHANGES ===")
    original = seed_candidate["system_prompt"]
    optimized = result.best_candidate["system_prompt"]

    print(f"Original length: {len(original)} characters")
    print(f"Optimized length: {len(optimized)} characters")

    if original != optimized:
        print("System prompt was modified by GEPA!")
        # Could add diff visualization here
    else:
        print("System prompt unchanged")


if __name__ == "__main__":
    main()
```

### Phase 3: Execution and Validation (Days 2-3)

#### 3.1 Run Training
```bash
# Create optimization directory
mkdir -p tau_bench/optimization

# Run GEPA training
cd tau-bench
python tau_bench/optimization/train_with_gepa.py
```

#### 3.2 Evaluate Results
```bash
# Test optimized agent performance
python run.py --env airline --task-split synthetic --agent-strategy tool-calling \
  --model gpt-4o --model-provider openai --max-concurrency 10 \
  --num-trials 1 --start-index 0 --end-index 50 \
  --custom-wiki results/gepa_optimization/optimized_candidate.json
```

Note: You'll need to modify `run.py` to support `--custom-wiki` flag, or manually replace the wiki content in the agent.

#### 3.3 Analysis Script

Create file: `tau_bench/optimization/analyze_results.py`

```python
#!/usr/bin/env python3
"""
Analyze GEPA optimization results
"""
import json
from pathlib import Path


def compare_performance(baseline_file: str, optimized_file: str):
    """Compare baseline vs optimized performance"""

    with open(baseline_file) as f:
        baseline_results = json.load(f)

    with open(optimized_file) as f:
        optimized_results = json.load(f)

    baseline_success = sum(1 for r in baseline_results if r["reward"] > 0.5)
    optimized_success = sum(1 for r in optimized_results if r["reward"] > 0.5)

    baseline_rate = baseline_success / len(baseline_results)
    optimized_rate = optimized_success / len(optimized_results)

    improvement = optimized_rate - baseline_rate

    print(f"=== PERFORMANCE COMPARISON ===")
    print(f"Baseline success rate: {baseline_rate:.2%} ({baseline_success}/{len(baseline_results)})")
    print(f"Optimized success rate: {optimized_rate:.2%} ({optimized_success}/{len(optimized_results)})")
    print(f"Improvement: {improvement:+.2%}")

    if improvement > 0.1:  # 10% improvement
        print("✅ Significant improvement achieved!")
    elif improvement > 0:
        print("✅ Modest improvement achieved")
    else:
        print("❌ No improvement or performance degraded")


if __name__ == "__main__":
    baseline_file = "results/baseline_synthetic_results.json"
    optimized_file = "results/optimized_synthetic_results.json"

    if Path(baseline_file).exists() and Path(optimized_file).exists():
        compare_performance(baseline_file, optimized_file)
    else:
        print("Result files not found. Run baseline and optimized evaluations first.")
```

## Key Implementation Notes

### Dependencies Required
- `gepa>=0.0.17` (already installed)
- Existing tau-bench dependencies
- OpenAI API access

### Environment Variables
```bash
export OPENAI_API_KEY="your_api_key_here"
```

### Directory Structure
```
tau-bench/
├── tau_bench/
│   ├── optimization/           # New directory
│   │   ├── gepa_adapter.py    # GEPA adapter implementation
│   │   ├── train_with_gepa.py # Training script
│   │   └── analyze_results.py # Analysis tools
│   └── sdg/
│       ├── validated_tasks_easy_with_instructions.json
│       └── validated_tasks_medium_with_instructions.json
└── results/
    └── gepa_optimization/      # Training outputs
```

## Success Metrics

### Primary Metrics
- **Task completion rate**: % of synthetic tasks completed successfully
- **Target**: >10% improvement over baseline

### Secondary Metrics
- **Action efficiency**: Average steps to completion
- **Policy compliance**: Adherence to airline rules in wiki.md

### Evaluation Protocol
1. Run baseline on 50 synthetic tasks
2. Train GEPA with 50 synthetic tasks (5 iterations)
3. Evaluate optimized agent on same 50 tasks
4. Compare success rates

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure all tau-bench dependencies are installed
2. **API rate limits**: Reduce batch_size and add delays if needed
3. **Memory issues**: Reduce max_tasks in training script
4. **Convergence issues**: Increase max_iterations or adjust learning parameters

### Debug Steps
1. Test adapter.evaluate() on single task first
2. Verify synthetic task loading works correctly
3. Check that messages are properly extracted
4. Validate scoring logic (binary 0/1 for success/failure)

## Next Steps After Initial Success

1. **Scale up training**: Use all 356 medium tasks
2. **Hyperparameter tuning**: Adjust batch sizes, iterations
3. **Multi-component optimization**: Optimize both system prompt and few-shot examples
4. **Transfer evaluation**: Test on original 50 airline test tasks
5. **Error analysis**: Deep dive into remaining failure cases

## Research Extensions

1. **Difficulty progression**: Train on easy tasks first, then medium
2. **Curriculum learning**: Order training tasks by complexity
3. **Multi-modal optimization**: Combine system prompt + few-shot examples
4. **Cross-validation**: Split synthetic data into train/val/test sets
5. **Real-world validation**: Test optimized agents on human-generated tasks

---

**Status**: Ready for implementation on cluster
**Estimated time**: 2-3 days for full pipeline
**Dependencies**: GEPA installed, OpenAI API access, tau-bench working environment