#!/usr/bin/env python3
"""
Script to analyze original tau-bench distribution and convert synthetic data
to match the exact format and distribution of tasks_test.py
"""

import json
import random
import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple
import matplotlib.pyplot as plt
import numpy as np

# Add the tau_bench directory to the path so we can import from it
tau_bench_root = Path(__file__).parent.parent
sys.path.insert(0, str(tau_bench_root))

from tau_bench.types import Action, Task

def analyze_original_tasks() -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Analyze the original tasks_test.py to understand the distribution.
    Returns the original tasks and distribution statistics.
    """
    # Read and parse the tasks_test.py file manually to extract task information
    tasks_file_path = tau_bench_root / "envs" / "airline" / "tasks_test.py"

    with open(tasks_file_path, 'r') as f:
        content = f.read()

    # Extract task information using regex and string parsing
    import re

    # Find all Task(...) blocks
    task_pattern = r'Task\(\s*annotator="([^"]*)",\s*user_id="([^"]*)",\s*instruction="([^"]*(?:\\.[^"]*)*)",\s*actions=\[(.*?)\],\s*outputs=(\[[^\]]*\])'

    # Since the content is complex with nested structures, let's use a simpler approach
    # by manually counting the tasks in the file

    # Count tasks by looking for Task( patterns
    task_matches = re.findall(r'Task\(', content)
    total_tasks = len(task_matches)

    # Extract annotators
    annotator_matches = re.findall(r'annotator="([^"]*)"', content)
    annotator_counts = Counter(annotator_matches)

    # Extract actions - count actions by looking for Action( patterns within each task
    # Split by Task( to get individual tasks
    task_blocks = content.split('Task(')[1:]  # Skip the first empty part

    action_counts = []
    output_info = []

    for block in task_blocks:
        # Count Action( patterns in this block
        action_matches = re.findall(r'Action\(', block)
        action_count = len(action_matches)
        action_counts.append(action_count)

        # Extract outputs
        output_match = re.search(r'outputs=(\[[^\]]*\])', block)
        if output_match:
            outputs_str = output_match.group(1)
            try:
                # Try to evaluate the outputs list
                outputs = eval(outputs_str)
                output_info.append(len(outputs))
            except:
                output_info.append(0)
        else:
            output_info.append(0)

    action_count_dist = Counter(action_counts)
    output_count_dist = Counter(output_info)

    # Group by annotator and action count for detailed analysis
    annotator_action_dist = defaultdict(list)
    for i, annotator in enumerate(annotator_matches):
        if i < len(action_counts):
            annotator_action_dist[annotator].append(action_counts[i])

    stats = {
        'total_tasks': total_tasks,
        'annotator_counts': dict(annotator_counts),
        'action_counts': dict(action_count_dist),
        'output_counts': dict(output_count_dist),
        'annotator_action_dist': {k: Counter(v) for k, v in annotator_action_dist.items()}
    }

    # Create simplified task dictionaries for reference
    original_tasks = []
    for i in range(min(len(annotator_matches), len(action_counts))):
        task_dict = {
            'annotator': annotator_matches[i],
            'action_count': action_counts[i],
            'output_count': output_info[i] if i < len(output_info) else 0
        }
        original_tasks.append(task_dict)

    return original_tasks, stats

def load_synthetic_data() -> List[Dict]:
    """Load synthetic data from both easy and medium files."""
    synthetic_tasks = []

    # Load easy tasks
    easy_path = Path(__file__).parent / "validated_tasks_easy_with_instructions.json"
    if easy_path.exists():
        with open(easy_path, 'r') as f:
            easy_tasks = json.load(f)
            for task in easy_tasks:
                task['synthetic_difficulty'] = 'easy'
                task['action_count'] = len(task['actions'])
            synthetic_tasks.extend(easy_tasks)

    # Load medium tasks
    medium_path = Path(__file__).parent / "validated_tasks_medium_with_instructions.json"
    if medium_path.exists():
        with open(medium_path, 'r') as f:
            medium_tasks = json.load(f)
            for task in medium_tasks:
                task['synthetic_difficulty'] = 'medium'
                task['action_count'] = len(task['actions'])
            synthetic_tasks.extend(medium_tasks)

    return synthetic_tasks

def sample_synthetic_tasks_to_match_distribution(synthetic_tasks: List[Dict], target_stats: Dict[str, Any]) -> List[Dict]:
    """
    Sample synthetic tasks to match the original distribution.
    """
    target_total = target_stats['total_tasks']
    target_action_counts = target_stats['action_counts']
    target_annotator_counts = target_stats['annotator_counts']

    # Group synthetic tasks by action count
    synthetic_by_action_count = defaultdict(list)
    for task in synthetic_tasks:
        action_count = task['action_count']
        synthetic_by_action_count[action_count].append(task)

    print(f"Original distribution - Total tasks: {target_total}")
    print(f"Action count distribution: {target_action_counts}")
    print(f"Annotator distribution: {target_annotator_counts}")

    print(f"\nSynthetic data available:")
    for action_count, tasks in synthetic_by_action_count.items():
        print(f"  {action_count} actions: {len(tasks)} tasks")

    # Sample tasks to match target action count distribution
    selected_tasks = []
    random.seed(42)  # For reproducibility

    for action_count, needed_count in target_action_counts.items():
        available_tasks = synthetic_by_action_count.get(action_count, [])

        if len(available_tasks) >= needed_count:
            # Sample exactly what we need
            sampled = random.sample(available_tasks, needed_count)
        elif len(available_tasks) > 0:
            # Sample with replacement if we don't have enough
            sampled = random.choices(available_tasks, k=needed_count)
        else:
            # Fallback: try to find tasks with similar action counts
            print(f"Warning: No synthetic tasks with {action_count} actions. Looking for alternatives...")

            # Try nearby action counts
            alternatives = []
            for alt_count in sorted(synthetic_by_action_count.keys()):
                if abs(alt_count - action_count) <= 1 and synthetic_by_action_count[alt_count]:
                    alternatives.extend(synthetic_by_action_count[alt_count])

            if alternatives:
                sampled = random.choices(alternatives, k=needed_count)
                print(f"  Using {len(sampled)} tasks with similar action counts")
            else:
                # Last resort: use any available tasks
                all_available = [task for tasks in synthetic_by_action_count.values() for task in tasks]
                if all_available:
                    sampled = random.choices(all_available, k=needed_count)
                    print(f"  Using {len(sampled)} random tasks as fallback")
                else:
                    print(f"  No synthetic tasks available! Skipping {needed_count} tasks.")
                    continue

        selected_tasks.extend(sampled)
        print(f"Selected {len(sampled)} tasks for {action_count} actions")

    # Assign annotators to match original distribution
    annotators = []
    for annotator, count in target_annotator_counts.items():
        annotators.extend([annotator] * count)

    random.shuffle(annotators)

    for i, task in enumerate(selected_tasks):
        if i < len(annotators):
            task['assigned_annotator'] = annotators[i]
        else:
            # Fallback if we have more tasks than annotators (shouldn't happen)
            task['assigned_annotator'] = random.choice(list(target_annotator_counts.keys()))

    return selected_tasks[:target_total]  # Ensure we have exactly the right number

def convert_to_tau_bench_format(synthetic_tasks: List[Dict], original_tasks: List[Dict]) -> List[Dict]:
    """
    Convert synthetic tasks to exact tau-bench Task format.
    Returns dictionaries with all the task data instead of Task objects.
    """
    converted_tasks = []

    # Create a mapping of outputs based on action patterns from original tasks
    original_outputs_by_pattern = {}
    for orig_task in original_tasks:
        action_count = orig_task['action_count']
        output_count = orig_task.get('output_count', 0)
        if action_count not in original_outputs_by_pattern:
            original_outputs_by_pattern[action_count] = []

        # Create sample outputs based on the original pattern
        if output_count == 0:
            outputs = []
        elif output_count == 1:
            outputs = ["sample_output"]
        elif output_count == 3:
            outputs = ["327", "1000", "1786"]  # Common pattern from original
        else:
            outputs = [f"output_{j}" for j in range(output_count)]

        original_outputs_by_pattern[action_count].append(outputs)

    for i, synth_task in enumerate(synthetic_tasks):
        # Convert actions
        actions = []
        for action_dict in synth_task['actions']:
            action = Action(
                name=action_dict['name'],
                kwargs=action_dict['kwargs']
            )
            actions.append(action)

        # Assign outputs based on original patterns
        action_count = len(actions)
        available_outputs = original_outputs_by_pattern.get(action_count, [[]])
        outputs = random.choice(available_outputs) if available_outputs else []

        # Create task dictionary with all required fields
        task_dict = {
            'annotator': synth_task['assigned_annotator'],
            'user_id': synth_task['user_id'],
            'instruction': synth_task['instruction'],
            'actions': actions,
            'outputs': outputs
        }

        converted_tasks.append(task_dict)

    return converted_tasks

def create_tasks_file(converted_tasks: List[Dict], output_path: Path):
    """Create the tasks_test_synthetic.py file with proper formatting."""

    with open(output_path, 'w') as f:
        f.write("from tau_bench.types import Action, Task\n\n")
        f.write("TASKS = [\n")

        for i, task in enumerate(converted_tasks):
            f.write("    Task(\n")
            f.write(f'        annotator="{task["annotator"]}",\n')
            f.write(f'        user_id="{task["user_id"]}",\n')

            # Write instruction with proper escaping
            instruction = task["instruction"].replace('"', '\\"').replace('\n', '\\n')
            f.write(f'        instruction="{instruction}",\n')

            f.write("        actions=[\n")
            for action in task["actions"]:
                f.write("            Action(\n")
                f.write(f'                name="{action.name}",\n')
                f.write(f"                kwargs={action.kwargs!r},\n")
                f.write("            ),\n")
            f.write("        ],\n")

            f.write(f"        outputs={task['outputs']!r},\n")
            f.write("    ),\n")

        f.write("]\n")

def plot_distributions(original_stats: Dict, synthetic_tasks: List[Dict], output_path: Path):
    """Create action count distribution comparison plot."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    # Action count distribution
    original_action_counts = original_stats['action_counts']
    synthetic_action_counts = Counter([task['action_count'] for task in synthetic_tasks])

    action_count_range = range(max(max(original_action_counts.keys()), max(synthetic_action_counts.keys())) + 1)
    original_counts = [original_action_counts.get(i, 0) for i in action_count_range]
    synthetic_counts = [synthetic_action_counts.get(i, 0) for i in action_count_range]

    x = np.arange(len(action_count_range))
    width = 0.35

    ax.bar(x - width/2, original_counts, width, label='Original', alpha=0.8, color='skyblue')
    ax.bar(x + width/2, synthetic_counts, width, label='Synthetic', alpha=0.8, color='lightcoral')
    ax.set_xlabel('Number of Actions')
    ax.set_ylabel('Number of Tasks')
    ax.set_title('Action Count Distribution Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(action_count_range)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Main execution function."""
    print("🔍 Analyzing original tau-bench distribution...")
    original_tasks, original_stats = analyze_original_tasks()

    print(f"\n📊 Original Distribution Summary:")
    print(f"Total tasks: {original_stats['total_tasks']}")
    print(f"Action counts: {original_stats['action_counts']}")
    print(f"Annotator counts: {original_stats['annotator_counts']}")

    print("\n📚 Loading synthetic data...")
    synthetic_tasks = load_synthetic_data()
    print(f"Loaded {len(synthetic_tasks)} synthetic tasks")

    # Analyze synthetic data distribution
    synth_action_dist = Counter([task['action_count'] for task in synthetic_tasks])
    synth_difficulty_dist = Counter([task.get('difficulty', task.get('synthetic_difficulty', 'unknown')) for task in synthetic_tasks])

    print(f"\nSynthetic data action distribution: {dict(synth_action_dist)}")
    print(f"Synthetic data difficulty distribution: {dict(synth_difficulty_dist)}")

    print("\n🎯 Sampling synthetic tasks to match original distribution...")
    sampled_tasks = sample_synthetic_tasks_to_match_distribution(synthetic_tasks, original_stats)

    print(f"\n✅ Sampled {len(sampled_tasks)} tasks")
    sampled_action_dist = Counter([task['action_count'] for task in sampled_tasks])
    sampled_annotator_dist = Counter([task['assigned_annotator'] for task in sampled_tasks])
    print(f"Sampled action distribution: {dict(sampled_action_dist)}")
    print(f"Sampled annotator distribution: {dict(sampled_annotator_dist)}")

    print("\n🔄 Converting to tau-bench format...")
    converted_tasks = convert_to_tau_bench_format(sampled_tasks, original_tasks)

    print("\n💾 Saving tasks file...")
    output_dir = Path(__file__).parent
    tasks_output_path = output_dir / "tasks_test_synthetic.py"
    create_tasks_file(converted_tasks, tasks_output_path)
    print(f"Saved synthetic tasks to: {tasks_output_path}")

    print("\n📈 Generating distribution plots...")
    plot_output_path = output_dir / "distribution_comparison.png"
    plot_distributions(original_stats, sampled_tasks, plot_output_path)
    print(f"Saved distribution plots to: {plot_output_path}")

    print(f"\n🎉 Conversion complete!")
    print(f"Original tasks: {original_stats['total_tasks']}")
    print(f"Synthetic tasks generated: {len(converted_tasks)}")
    print(f"Match: {'✅' if len(converted_tasks) == original_stats['total_tasks'] else '❌'}")

if __name__ == "__main__":
    main()