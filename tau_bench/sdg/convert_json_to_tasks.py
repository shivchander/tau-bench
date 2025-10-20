#!/usr/bin/env python3
"""
Script to convert JSON synthetic data to tau-bench tasks_*.py format.
Takes a JSON file and outputs a Python file with Task objects.
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict
import sys

# Add the tau_bench directory to the path so we can import from it
tau_bench_root = Path(__file__).parent.parent
sys.path.insert(0, str(tau_bench_root))

from tau_bench.types import Action, Task


def load_json_data(json_path: Path) -> List[Dict]:
    """Load synthetic data from JSON file."""
    with open(json_path, 'r') as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON file must contain a list of tasks")

    print(f"Loaded {len(data)} tasks from {json_path}")
    return data


def convert_to_tau_bench_format(json_tasks: List[Dict]) -> List[Dict]:
    """
    Convert JSON tasks to tau-bench Task format.
    Returns dictionaries with all the task data instead of Task objects.
    """
    converted_tasks = []

    for i, task_data in enumerate(json_tasks):
        # Validate required fields
        required_fields = ['user_id', 'actions', 'instruction']
        missing_fields = [field for field in required_fields if field not in task_data]
        if missing_fields:
            print(f"Warning: Task {i} missing required fields: {missing_fields}. Skipping.")
            continue

        # Convert actions
        actions = []
        for action_dict in task_data['actions']:
            if 'name' not in action_dict or 'kwargs' not in action_dict:
                print(f"Warning: Task {i} has malformed action: {action_dict}. Skipping task.")
                break

            action = Action(
                name=action_dict['name'],
                kwargs=action_dict['kwargs']
            )
            actions.append(action)
        else:  # Only add task if all actions were valid
            # Get annotator (use default if not provided)
            annotator = task_data.get('annotator', 'synthetic')

            # Get outputs (empty list if not provided)
            outputs = task_data.get('outputs', [])

            # Create task dictionary
            task_dict = {
                'annotator': annotator,
                'user_id': task_data['user_id'],
                'instruction': task_data['instruction'],
                'actions': actions,
                'outputs': outputs
            }

            converted_tasks.append(task_dict)

    print(f"Successfully converted {len(converted_tasks)} tasks")
    return converted_tasks


def create_tasks_file(converted_tasks: List[Dict], output_path: Path):
    """Create the tasks_*.py file with proper formatting."""

    with open(output_path, 'w') as f:
        f.write("from tau_bench.types import Action, Task\n\n")
        f.write("TASKS = [\n")

        for i, task in enumerate(converted_tasks):
            f.write("    Task(\n")
            f.write(f'        annotator="{task["annotator"]}",\n')
            f.write(f'        user_id="{task["user_id"]}",\n')

            # Write instruction with proper escaping
            instruction = task["instruction"].replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
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


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Convert JSON synthetic data to tau-bench tasks_*.py format"
    )
    parser.add_argument(
        '--input-file',
        type=str,
        required=True,
        help='Path to input JSON file'
    )
    parser.add_argument(
        '--output-file',
        type=str,
        help='Path to output Python file (default: tasks_<input_name>.py)'
    )

    args = parser.parse_args()

    # Resolve input path
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist")
        sys.exit(1)

    # Determine output path
    if args.output_file:
        output_path = Path(args.output_file)
    else:
        # Create output filename based on input filename
        input_stem = input_path.stem  # filename without extension
        output_path = Path(__file__).parent / f"tasks_{input_stem}.py"

    print(f"🔄 Converting {input_path} to {output_path}")
    print()

    # Load JSON data
    print("📚 Loading JSON data...")
    json_tasks = load_json_data(input_path)

    # Convert to tau-bench format
    print("\n🔄 Converting to tau-bench format...")
    converted_tasks = convert_to_tau_bench_format(json_tasks)

    # Create tasks file
    print("\n💾 Creating tasks file...")
    create_tasks_file(converted_tasks, output_path)

    print(f"\n✅ Successfully created {output_path}")
    print(f"   Total tasks: {len(converted_tasks)}")
    print(f"   Skipped: {len(json_tasks) - len(converted_tasks)}")


if __name__ == "__main__":
    main()
