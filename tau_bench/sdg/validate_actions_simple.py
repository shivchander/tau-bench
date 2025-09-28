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
import re


def create_tools_map():
    """Create tools mapping directly from ALL_TOOLS."""
    return {tool.get_info()["function"]["name"]: tool for tool in ALL_TOOLS}


def calculate_correct_booking_total(data, action_kwargs) -> int:
    """Calculate the correct total cost for a book_reservation action."""
    flights = action_kwargs.get("flights", [])
    passengers = action_kwargs.get("passengers", [])
    insurance = action_kwargs.get("insurance", "no")
    nonfree_baggages = action_kwargs.get("nonfree_baggages", 0)
    cabin = action_kwargs.get("cabin", "economy")

    num_passengers = len(passengers)
    num_flights = len(flights)

    # Calculate flight costs - get pricing from first flight as reference
    flight_cost_per_passenger = 0
    if flights:
        first_flight = flights[0]
        flight_number = first_flight["flight_number"]
        date = first_flight["date"]

        if flight_number in data["flights"]:
            flight_data = data["flights"][flight_number]
            if date in flight_data["dates"]:
                date_data = flight_data["dates"][date]
                prices = date_data.get("prices", {})
                flight_cost_per_passenger = prices.get(cabin, 150)  # Default fallback

    # Calculate total costs
    flight_cost = flight_cost_per_passenger * num_passengers * num_flights
    insurance_cost = 30 * num_passengers if insurance == "yes" else 0
    baggage_cost = 50 * nonfree_baggages

    total_cost = flight_cost + insurance_cost + baggage_cost
    return total_cost


def redistribute_payment_amounts(payment_methods, total_cost, data, user_id) -> List[Dict[str, Any]]:
    """Redistribute payment amounts to match the correct total while respecting balances."""
    user_data = data["users"].get(user_id, {})
    user_payment_methods = user_data.get("payment_methods", {})

    corrected_payments = []
    remaining_cost = total_cost

    # Sort payment methods: certificates first, then gift cards, then credit cards
    sorted_payments = []
    for pm in payment_methods:
        payment_id = pm["payment_id"]
        if payment_id in user_payment_methods:
            pm_info = user_payment_methods[payment_id]
            source = pm_info.get("source", "")

            if source == "certificate":
                sorted_payments.insert(0, (pm, pm_info))  # Certificates first
            elif source == "gift_card":
                sorted_payments.append((pm, pm_info))  # Gift cards middle
            elif source == "credit_card":
                sorted_payments.append((pm, pm_info))  # Credit cards last

    # Distribute amounts
    for i, (pm, pm_info) in enumerate(sorted_payments):
        payment_id = pm["payment_id"]
        source = pm_info.get("source", "")

        if remaining_cost <= 0:
            break

        if source in ["certificate", "gift_card"]:
            # Use available balance, up to remaining cost
            available_balance = pm_info.get("amount", 0)
            amount_to_use = min(available_balance, remaining_cost)
        else:  # credit_card
            # Credit cards can cover the full remaining amount
            amount_to_use = remaining_cost

        if amount_to_use > 0:
            corrected_payments.append({
                "payment_id": payment_id,
                "amount": amount_to_use
            })
            remaining_cost -= amount_to_use

    return corrected_payments


def fix_payment_calculation_error(data, action_dict, error_msg) -> Dict[str, Any]:
    """Fix payment calculation errors by redistributing amounts correctly."""
    # Parse expected total from error message
    match = re.search(r"total price is (\d+)", error_msg)
    if not match:
        return action_dict  # Can't parse expected total

    expected_total = int(match.group(1))

    # Get user_id from action
    user_id = action_dict["kwargs"].get("user_id")
    if not user_id:
        return action_dict  # No user_id to work with

    # Get existing payment methods (keep the same IDs)
    payment_methods = action_dict["kwargs"].get("payment_methods", [])
    if not payment_methods:
        return action_dict  # No payment methods to fix

    # Redistribute amounts correctly
    corrected_payments = redistribute_payment_amounts(payment_methods, expected_total, data, user_id)

    # Update the action with corrected payment amounts
    fixed_action = action_dict.copy()
    fixed_action["kwargs"] = action_dict["kwargs"].copy()
    fixed_action["kwargs"]["payment_methods"] = corrected_payments

    return fixed_action


def validate_action_sequence_simple(data_load_func, tools_map, actions: List[Dict[str, Any]]) -> Tuple[bool, str, List[Dict[str, Any]]]:
    """
    Validate a sequence of actions by executing them directly on fresh data.
    Attempts to fix payment calculation errors automatically.

    Returns:
        (is_valid, error_message, corrected_actions)
    """
    try:
        # Load fresh data
        data = data_load_func()
        corrected_actions = actions.copy()
        payment_corrections_made = False

        # Execute each action in sequence
        for i, action_dict in enumerate(corrected_actions):
            action_name = action_dict["name"]
            action_kwargs = action_dict["kwargs"]

            # Skip respond actions (not relevant for our validation)
            if action_name == RESPOND_ACTION_NAME:
                continue

            # Check if action exists
            if action_name not in tools_map:
                return False, f"Action {i+1}: Unknown action '{action_name}'", corrected_actions

            # Try to execute the action
            try:
                result = tools_map[action_name].invoke(data=data, **action_kwargs)

                # Check if result indicates an error
                if isinstance(result, str) and result.startswith("Error:"):
                    # Try to fix payment calculation errors for book_reservation
                    if action_name == "book_reservation" and "payment amount does not add up" in result:
                        print(f"    🔧 Attempting to fix payment calculation error in action {i+1}")
                        fixed_action = fix_payment_calculation_error(data, action_dict, result)

                        # Try the fixed action
                        try:
                            fixed_result = tools_map[action_name].invoke(data=data, **fixed_action["kwargs"])
                            if isinstance(fixed_result, str) and fixed_result.startswith("Error:"):
                                return False, f"Action {i+1} ({action_name}) failed even after correction: {fixed_result}", corrected_actions
                            else:
                                # Success! Update the corrected actions
                                corrected_actions[i] = fixed_action
                                payment_corrections_made = True
                                print(f"    ✅ Payment calculation fixed for action {i+1}")
                        except Exception as e:
                            return False, f"Action {i+1} ({action_name}) exception after correction: {str(e)}", corrected_actions
                    else:
                        return False, f"Action {i+1} ({action_name}) failed: {result}", corrected_actions

            except Exception as e:
                return False, f"Action {i+1} ({action_name}) exception: {str(e)}", corrected_actions

        # If we get here, all actions executed successfully
        if payment_corrections_made:
            print(f"    💳 Payment corrections applied successfully")
        return True, "", corrected_actions

    except Exception as e:
        return False, f"Validation error: {str(e)}", actions


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
        is_valid, error_msg, corrected_actions = validate_action_sequence_simple(load_data, tools_map, actions)

        # Use corrected actions if available
        final_sequence = sequence.copy()
        if corrected_actions != actions:
            final_sequence["actions"] = corrected_actions
            final_sequence["payment_corrections_applied"] = True

        # Create sequence with validation metadata
        sequence_with_validation = final_sequence.copy()
        sequence_with_validation["validation"] = {
            "is_valid": is_valid,
            "error_message": error_msg if not is_valid else None,
            "validation_sequence_number": i + 1,
            "payment_corrections_applied": corrected_actions != actions
        }

        all_sequences_with_validation.append(sequence_with_validation)

        if is_valid:
            correction_note = " (with payment corrections)" if corrected_actions != actions else ""
            print(f"  ✓ Sequence {i+1}: {difficulty} difficulty, user {user_id}, {len(actions)} actions - VALID{correction_note}")
            valid_sequences.append(final_sequence)
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