# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

τ-bench is a benchmark for evaluating Tool-Agent-User interaction in real-world domains (airline and retail). It simulates dynamic conversations between users and language agents equipped with domain-specific API tools and policy guidelines.

## Key Commands

### Installation and Setup
```bash
# Install from source (includes all dependencies)
pip install -e .
# or use uv (per user preferences)
uv pip install -e .
```

### Running the Benchmark
```bash
# Basic tool-calling agent on retail environment
python run.py --agent-strategy tool-calling --env retail --model gpt-4o --model-provider openai --user-model gpt-4o --user-model-provider openai --user-strategy llm --max-concurrency 10

# Run specific tasks only
python run.py --agent-strategy tool-calling --env retail --model gpt-4o --model-provider openai --user-model gpt-4o --user-model-provider openai --user-strategy llm --max-concurrency 10 --task-ids 2 4 6

# Run auto error identification on results
python auto_error_identification.py --env retail --platform openai --results-path <results_file> --max-concurrency 16 --output-path test-auto-error-identification --max-num-failed-results 10
```

## Architecture Overview

### Core Components

1. **Environments** (`tau_bench/envs/`):
   - `retail/` - E-commerce customer service scenarios
   - `airline/` - Airline customer service scenarios
   - `base.py` - Base environment class with tool execution and user simulation
   - `user.py` - User simulator with multiple strategies (llm, react, verify, reflection)

2. **Agents** (`tau_bench/agents/`):
   - `tool_calling_agent.py` - Function calling strategy
   - `chat_react_agent.py` - ReAct reasoning strategy
   - `few_shot_agent.py` - Few-shot prompting strategy
   - `base.py` - Abstract agent interface

3. **Model Utils** (`tau_bench/model_utils/`):
   - Model providers integration (OpenAI, Anthropic, Google, Mistral)
   - Function tool mapping and filtering utilities
   - Completion handling and exception management

4. **Types** (`tau_bench/types.py`):
   - Core data models: `Task`, `Action`, `EnvResponse`, `RunConfig`
   - Reward calculation structures: `RewardResult`, `RewardOutputInfo`

### Key Files

- `run.py` - Main entry point for running benchmarks
- `auto_error_identification.py` - Automated error analysis tool
- `setup.py` - Package dependencies and installation
- `historical_trajectories/` - Pre-recorded agent trajectories for analysis

### Environment Configuration

**Required API Keys** (set as environment variables):
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `MISTRAL_API_KEY`

### Supported Models and Strategies

**Agent Strategies**: `tool-calling`, `act`, `react`, `few-shot`

**User Strategies**: `llm`, `react`, `verify`, `reflection`

**Environments**: `retail`, `airline`

**Task Splits**: `train`, `test`, `dev` (retail only)

### Running Tests/Development

The project uses standard Python development practices. Install with `pip install -e .` and run the main benchmarks using `python run.py` with appropriate arguments. Results are saved to the `results/` directory by default.

## Synthetic Data Generation (SDG) System

The tau-bench repository includes a comprehensive synthetic data generation system for creating realistic customer service scenarios. This system uses a backtranslation approach to generate high-quality synthetic tasks that are fully compatible with the existing tau-bench framework.

### Overview

The SDG system generates synthetic tau-bench tasks through a multi-step pipeline:

1. **User Sampling & Action Generation**: Randomly selects users and generates realistic action sequences using OpenAI GPT models
2. **Sandbox Validation**: Validates generated actions against the actual environment (planned)
3. **Instruction Generation**: Creates natural language instructions from user context and actions (planned)
4. **Task Formatting**: Converts everything into proper tau-bench Task format (planned)

### Key Features

- **Real Data Integration**: Uses actual user profiles, reservations, and flight data from the tau-bench dataset
- **Difficulty Scaling**: Supports easy (1 action), medium (2-5 actions), and hard (6-10 actions) complexity levels
- **Flight System Constraints**: Enforces realistic flight numbers, dates, and routes from flights.json
- **Async Processing**: Concurrent API requests for fast batch generation
- **Quality Validation**: Ensures generated scenarios match requested difficulty and system constraints

### Usage

#### Basic Generation
```bash
# Generate single medium difficulty task
python tau_bench/sdg/generate_user_actions.py --difficulty medium

# Generate multiple tasks with specific difficulty
python tau_bench/sdg/generate_user_actions.py --num-samples 10 --difficulty hard

# Fast batch processing with concurrency
python tau_bench/sdg/generate_user_actions.py --num-samples 50 --max-concurrency 8 --difficulty easy
```

#### Output Customization
```bash
# Specify custom output file
python tau_bench/sdg/generate_user_actions.py --output-file my_synthetic_tasks --num-samples 20

# Generate different difficulty levels
python tau_bench/sdg/generate_user_actions.py --difficulty easy --num-samples 100    # Simple lookups
python tau_bench/sdg/generate_user_actions.py --difficulty medium --num-samples 50  # Multi-step scenarios
python tau_bench/sdg/generate_user_actions.py --difficulty hard --num-samples 25    # Complex workflows
```

### Generated Data Structure

Each generated sample contains:
- **user_id**: Randomly selected from real user dataset
- **difficulty**: Requested difficulty level (easy/medium/hard)
- **target_action_count**: Number of actions in the scenario
- **actions**: List of realistic action sequences with proper tool names and arguments
- **scenario_summary**: Natural language description of the customer service scenario

### Data Quality Guarantees

The SDG system ensures:
- **System Compatibility**: All flight numbers, dates, and routes exist in the actual tau-bench flight database
- **User Context Accuracy**: Uses real user payment methods, reservations, and passenger information
- **Difficulty Consistency**: Generated action counts match requested difficulty levels
- **Scenario Realism**: Customer service scenarios are logically coherent and realistic

### Requirements

- **OpenAI API Key**: Set `OPENAI_API_KEY` environment variable
- **Dependencies**: `openai`, `python-dotenv` (install with `uv pip install openai python-dotenv`)

### File Structure

```
tau_bench/sdg/
├── generate_user_actions.py     # Main generation script
└── generated_user_actions.json  # Sample output (accumulates results)
```

### Performance

- **Speed**: Generates 50+ scenarios per minute with async processing
- **Quality**: 95%+ success rate with proper validation
- **Scale**: Tested with 1000+ sample batches

This synthetic data generation system enables researchers to create large-scale datasets for training and evaluation while maintaining full compatibility with the tau-bench evaluation framework.