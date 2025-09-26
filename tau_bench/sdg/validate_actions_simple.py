#!/usr/bin/env python3
"""
Simple Action Validation for Synthetic Tau-Bench Tasks
Based on the approach from retail_action_hash.py - much simpler and faster!
"""

import json
import os
import sys
from typing import Dict, List, Any, Tuple
import argparse

from tau_bench.envs.airline.data import load_data
from tau_bench.envs.airline.tools import ALL_TOOLS
from tau_bench.envs.base import RESPOND_ACTION_NAME


def create_tools_map():
    """Create tools mapping directly from ALL_TOOLS."""
    return {tool.get_info()["function"]["name"]: tool for tool in ALL_TOOLS}


def validate_action_sequence_simple(data_load_func, tools_map, actions: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Validate a sequence of actions by executing them directly on fresh data.
    Much simpler than creating full environment!

    Returns:
        (is_valid, error_message)
    """
    try:
        # Load fresh data
        data = data_load_func()

        # Execute each action in sequence
        for i, action_dict in enumerate(actions):
            action_name = action_dict["name"]
            action_kwargs = action_dict["kwargs"]

            # Skip respond actions (not relevant for our validation)
            if action_name == RESPOND_ACTION_NAME:
                continue

            # Check if action exists
            if action_name not in tools_map:
                return False, f"Action {i+1}: Unknown action '{action_name}'"

            # Try to execute the action
            try:
                result = tools_map[action_name].invoke(data=data, **action_kwargs)

                # Check if result indicates an error
                if isinstance(result, str) and result.startswith("Error:"):
                    return False, f"Action {i+1} ({action_name}) failed: {result}"

            except Exception as e:
                return False, f"Action {i+1} ({action_name}) exception: {str(e)}"

        # If we get here, all actions executed successfully
        return True, ""

    except Exception as e:
        return False, f"Validation error: {str(e)}"


def load_synthetic_data(file_path: str) -> List[Dict[str, Any]]:
    """Load synthetic action sequences from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def validate_batch_simple(synthetic_data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Validate a batch of synthetic action sequences using simple approach.
    Returns:
        (all_sequences_with_validation, valid_sequences_only)
    """
    all_sequences_with_validation = []
    valid_sequences = []

    print(f"Validating {len(synthetic_data)} action sequences...")

    # Create tools map once
    tools_map = create_tools_map()

    for i, sequence in enumerate(synthetic_data):
        user_id = sequence["user_id"]
        difficulty = sequence["difficulty"]
        actions = sequence["actions"]

        # Validate the sequence
        is_valid, error_msg = validate_action_sequence_simple(load_data, tools_map, actions)

        # Create sequence with validation metadata
        sequence_with_validation = sequence.copy()
        sequence_with_validation["validation"] = {
            "is_valid": is_valid,
            "error_message": error_msg if not is_valid else None,
            "validation_sequence_number": i + 1
        }

        all_sequences_with_validation.append(sequence_with_validation)

        if is_valid:
            print(f"  ✓ Sequence {i+1}: {difficulty} difficulty, user {user_id}, {len(actions)} actions - VALID")
            valid_sequences.append(sequence)
        else:
            print(f"  ✗ Sequence {i+1}: {difficulty} difficulty, user {user_id}, {len(actions)} actions - INVALID ({error_msg})")

    success_rate = len(valid_sequences) / len(synthetic_data) * 100
    print(f"\nValidation complete: {len(valid_sequences)}/{len(synthetic_data)} sequences valid ({success_rate:.1f}% success rate)")

    return all_sequences_with_validation, valid_sequences


def main():
    """Main function to run action sequence validation."""
    parser = argparse.ArgumentParser(description='Validate synthetic tau-bench action sequences (simple approach)')
    parser.add_argument('--input-file', type=str, required=True,
                       help='Input file containing synthetic action sequences')
    parser.add_argument('--output-file', type=str, required=True,
                       help='Output file for validated action sequences')
    parser.add_argument('--in-place', action='store_true',
                       help='Update the input file in-place with validation metadata (default: create new output file)')

    args = parser.parse_args()

    # Load synthetic data
    if not os.path.exists(args.input_file):
        print(f"Error: Input file {args.input_file} does not exist")
        sys.exit(1)

    print(f"Loading synthetic data from {args.input_file}...")
    synthetic_data = load_synthetic_data(args.input_file)

    if not synthetic_data:
        print("No synthetic data found in input file")
        sys.exit(1)

    # Validate sequences
    all_sequences_with_validation, valid_sequences = validate_batch_simple(synthetic_data)

    # Determine output file
    if args.in_place:
        output_file = args.input_file
        description = f"updated {args.input_file} in-place with validation metadata for all {len(all_sequences_with_validation)} sequences"
    else:
        output_file = args.output_file
        description = f"saved all {len(all_sequences_with_validation)} sequences with validation metadata to {args.output_file}"

    # Always save all sequences with validation metadata
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(all_sequences_with_validation, f, indent=2)

    print(f"\n{description}")
    print(f"Validation results: {len(valid_sequences)}/{len(synthetic_data)} sequences valid ({len(valid_sequences)/len(synthetic_data)*100:.1f}% success rate)")


if __name__ == "__main__":
    main()