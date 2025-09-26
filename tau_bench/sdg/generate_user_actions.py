#!/usr/bin/env python3
"""
Script 1: Combined User Sampling and Action Generation
Randomly selects a user and difficulty level, then generates appropriate actions using OpenAI API.
"""

import json
import random
import os
import asyncio
from typing import Dict, List, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import tools directly from the airline tools module
from tau_bench.envs.airline.tools import ALL_TOOLS

def load_users(users_file: str = "tau_bench/envs/airline/data/users.json") -> Dict[str, Any]:
    """Load user data from JSON file."""
    with open(users_file, 'r') as f:
        return json.load(f)

def load_reservations(reservations_file: str = "tau_bench/envs/airline/data/reservations.json") -> Dict[str, Any]:
    """Load reservations data from JSON file."""
    with open(reservations_file, 'r') as f:
        return json.load(f)

def load_flights(flights_file: str = "tau_bench/envs/airline/data/flights.json") -> Dict[str, Any]:
    """Load flights data from JSON file."""
    with open(flights_file, 'r') as f:
        return json.load(f)

def get_flight_constraints(flights_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract valid flight numbers, routes, and available dates from flights data."""
    valid_flights = []
    valid_dates = set()
    routes = {}

    for flight_number, flight_info in flights_data.items():
        # Collect flight numbers and routes
        origin = flight_info['origin']
        destination = flight_info['destination']
        routes[flight_number] = f"{origin} → {destination}"

        # Collect available dates for this flight
        flight_dates = []
        for date, date_info in flight_info['dates'].items():
            valid_dates.add(date)
            if date_info['status'] == 'available':
                flight_dates.append(date)

        if flight_dates:
            valid_flights.append({
                "flight_number": flight_number,
                "route": routes[flight_number],
                "available_dates": flight_dates[:5]  # Limit to first 5 for prompt brevity
            })

    return {
        "valid_flight_numbers": list(flights_data.keys()),
        "valid_dates": sorted(list(valid_dates)),
        "sample_valid_flights": valid_flights[:10],  # First 10 for prompt
        "date_range": f"{min(valid_dates)} to {max(valid_dates)}"
    }

def get_tool_names() -> List[str]:
    """Get the names of all available tools."""
    return [tool.__name__ for tool in ALL_TOOLS]

def get_user_context(user_id: str, users_data: Dict[str, Any], reservations_data: Dict[str, Any]) -> str:
    """Extract relevant context about a user for the teacher model."""
    user = users_data[user_id]

    context = f"User ID: {user_id}\n"
    context += f"Membership Level: {user.get('membership', 'None')}\n"

    # Payment methods - extract from payment_methods structure
    payment_methods = []
    if 'payment_methods' in user:
        for payment_id, payment_info in user['payment_methods'].items():
            if payment_info['source'] == 'certificate':
                payment_methods.append(f"Certificate {payment_id}: ${payment_info['amount']}")
            elif payment_info['source'] == 'gift_card':
                payment_methods.append(f"Gift Card {payment_id}: ${payment_info['amount']}")
            elif payment_info['source'] == 'credit_card':
                last_four = payment_info.get('last_four', 'XXXX')
                brand = payment_info.get('brand', 'unknown')
                payment_methods.append(f"Credit Card {payment_id} ({brand} ending in {last_four})")

    context += f"Payment Methods: {', '.join(payment_methods)}\n"

    # Saved passengers
    if 'saved_passengers' in user:
        passengers = []
        for passenger in user['saved_passengers']:
            passengers.append(f"{passenger['first_name']} {passenger['last_name']} (DOB: {passenger['dob']})")
        context += f"Saved Passengers: {', '.join(passengers)}\n"

    # Existing reservations with full details
    reservation_ids = user.get('reservations', [])
    if reservation_ids:
        context += f"\nExisting Reservations ({len(reservation_ids)} total):\n"
        for res_id in reservation_ids:
            if res_id in reservations_data:
                res = reservations_data[res_id]
                context += f"- Reservation {res_id}:\n"
                context += f"  Route: {res['origin']} → {res['destination']}\n"
                context += f"  Type: {res['flight_type']}, Class: {res['cabin']}\n"
                context += f"  Passengers: {len(res['passengers'])}\n"
                context += f"  Total Cost: ${sum(payment['amount'] for payment in res['payment_history'])}\n"
                context += f"  Flights: {len(res['flights'])} flight(s)\n"
                for i, flight in enumerate(res['flights'], 1):
                    context += f"    {i}. {flight['flight_number']} on {flight['date']} ({flight['origin']} → {flight['destination']})\n"
                context += f"  Baggage: {res['total_baggages']} total, {res['nonfree_baggages']} paid\n"
                context += f"  Insurance: {res['insurance']}\n"
                context += f"  Created: {res['created_at']}\n\n"
    else:
        context += "\nNo existing reservations.\n"

    return context

async def generate_user_actions(users_data: Dict[str, Any], reservations_data: Dict[str, Any], tools: List[str], api_key: str, difficulty: str, flight_constraints: Dict[str, Any]) -> Dict[str, Any]:
    """Generate user selection, difficulty, and actions using OpenAI API."""

    # Randomly select a user
    user_ids = list(users_data.keys())
    selected_user_id = random.choice(user_ids)
    user_context = get_user_context(selected_user_id, users_data, reservations_data)

    # Define difficulty levels
    difficulty_config = {
        "easy": {"min_actions": 1, "max_actions": 1},
        "medium": {"min_actions": 2, "max_actions": 5},
        "hard": {"min_actions": 6, "max_actions": 10}
    }

    config = difficulty_config[difficulty]

    client = AsyncOpenAI(api_key=api_key)

    # Provide concrete example of Action structure
    action_example = '''Action(
    name="book_reservation",
    kwargs={
        "user_id": "mia_li_3668",
        "origin": "JFK",
        "destination": "SEA",
        "flight_type": "one_way",
        "cabin": "economy",
        "flights": [
            {"flight_number": "HAT136", "date": "2024-05-20"},
            {"flight_number": "HAT039", "date": "2024-05-20"},
        ],
        "passengers": [
            {"first_name": "Mia", "last_name": "Li", "dob": "1990-04-05"}
        ],
        "payment_methods": [
            {"payment_id": "certificate_7504069", "amount": 250},
            {"payment_id": "credit_card_4421486", "amount": 5},
        ],
        "total_baggages": 3,
        "nonfree_baggages": 0,
        "insurance": "no",
    },
)'''

    # Create difficulty-specific prompts
    if difficulty == "easy":
        task_description = f"""Generate a simple, single-action customer service scenario ({config['min_actions']} action).
Focus on straightforward tasks like:
- Getting reservation or user details
- Simple flight searches
- Basic certificate sending
- Simple calculations

The scenario should be something a customer could resolve quickly with minimal complexity."""

    elif difficulty == "medium":
        task_description = f"""Generate a moderate complexity customer service scenario ({config['min_actions']}-{config['max_actions']} actions).
Focus on multi-step scenarios like:
- Booking flights with specific requirements (payment methods, baggage, insurance)
- Updating existing reservations (flights, passengers, baggage)
- Cancel and rebook scenarios
- Scenarios requiring multiple lookups and one update

The scenario should involve some decision-making and multiple related actions."""

    else:  # hard
        task_description = f"""Generate a complex, multi-faceted customer service scenario ({config['min_actions']}-{config['max_actions']} actions).
Focus on complex scenarios like:
- Managing multiple reservations simultaneously
- Complex booking scenarios with multiple passengers and payment methods
- Multi-step reservation modifications with calculations
- Scenarios involving multiple cancellations and rebookings
- Complex baggage and payment management across multiple flights

The scenario should be realistic but require significant customer service intervention."""

    # Build flight constraints section
    flight_constraints_text = f"""
Valid Flight System Data:
- Date Range: {flight_constraints['date_range']}
- Sample Valid Flights with Routes:
{chr(10).join([f"  {flight['flight_number']}: {flight['route']} (available: {', '.join(flight['available_dates'][:3])}...)" for flight in flight_constraints['sample_valid_flights'][:8]])}

CRITICAL: Only use flight numbers that exist in the system (HAT001-HAT300+ range) and dates within {flight_constraints['date_range']} range."""

    prompt = f"""You are designing a {difficulty} difficulty customer service task for an airline system.

User Context:
{user_context}

Available Tools/Actions:
{', '.join(tools)}

{flight_constraints_text}

Example Action Structure:
{action_example}

Task Requirements:
{task_description}

You must respond with valid JSON only. Use this exact JSON format:
{{
    "user_id": "{selected_user_id}",
    "difficulty": "{difficulty}",
    "target_action_count": <number between {config['min_actions']} and {config['max_actions']}>,
    "actions": [
        {{
            "name": "ActionName",
            "kwargs": {{
                "param1": "value1",
                "param2": "value2"
            }}
        }}
    ],
}}

Critical Requirements:
- Generate exactly {config['min_actions']}-{config['max_actions']} actions for {difficulty} difficulty
- Each action must have proper structure with name and kwargs
- Use actual reservation IDs from user context (e.g., "reservation_id": "ABC123")
- Use actual payment IDs from user profile (e.g., "certificate_1234567", "gift_card_9876543")
- MANDATORY: Use only valid flight numbers from the system (shown above, HAT001-HAT300+ format)
- MANDATORY: Use only valid dates within range {flight_constraints['date_range']}
- Actions must be logically connected and realistic for this user's specific context
- Ensure the scenario complexity matches the {difficulty} difficulty level"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert at designing realistic customer service scenarios for airline systems. Always provide complete action structures with proper kwargs."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Validate the result
        result_difficulty = result["difficulty"]
        action_count = len(result["actions"])

        # Verify the difficulty matches what we requested
        if result_difficulty != difficulty:
            raise ValueError(f"Expected difficulty '{difficulty}', but got '{result_difficulty}'")

        # Verify action count is within expected range
        min_actions, max_actions = config["min_actions"], config["max_actions"]
        if not (min_actions <= action_count <= max_actions):
            raise ValueError(f"Action count {action_count} doesn't match {difficulty} difficulty range ({min_actions}-{max_actions})")

        return result

    except Exception as e:
        print(f"Error generating actions: {e}")
        return None

async def main():
    """Main function to run the user and action generation."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate synthetic tau-bench tasks')
    parser.add_argument('--num-samples', type=int, default=1,
                       help='Number of user action sequences to generate (default: 1)')
    parser.add_argument('--output-file', type=str, default='tau_bench/sdg/generated_user_actions',
                       help='Output file for generated files (default: tau_bench/sdg/generated_user_actions)')
    parser.add_argument('--max-concurrency', type=int, default=8,
                       help='Maximum concurrent API requests (default: 5)')
    parser.add_argument('--difficulty', type=str, choices=['easy', 'medium', 'hard'], default='medium',
                       help='Difficulty level for generated tasks (default: medium)')
    args = parser.parse_args()

    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    # Load data
    print("Loading users, reservations, flights, and tools...")
    users_data = load_users()
    reservations_data = load_reservations()
    flights_data = load_flights()
    tools = get_tool_names()
    flight_constraints = get_flight_constraints(flights_data)

    print(f"Loaded {len(users_data)} users, {len(reservations_data)} reservations, {len(flights_data)} flights, and {len(tools)} tools")
    print(f"Flight date range: {flight_constraints['date_range']}")
    print(f"Available tools: {', '.join(tools)}")

    # Generate multiple samples concurrently
    results = []
    failed_count = 0

    print(f"Generating {args.num_samples} {args.difficulty} user action sequences with max {args.max_concurrency} concurrent requests...")

    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(args.max_concurrency)

    async def generate_with_semaphore(sample_id: int):
        async with semaphore:
            try:
                result = await generate_user_actions(users_data, reservations_data, tools, api_key, args.difficulty, flight_constraints)
                if result:
                    print(f"  ✓ Generated {result['difficulty']} scenario for user {result['user_id']} with {len(result['actions'])} actions (sample {sample_id+1})")
                    return result
                else:
                    print(f"  ✗ Failed to generate sample {sample_id+1}")
                    return None
            except Exception as e:
                print(f"  ✗ Failed to generate sample {sample_id+1}: {e}")
                return None

    # Create tasks for concurrent execution
    tasks = [generate_with_semaphore(i) for i in range(args.num_samples)]

    # Execute all tasks concurrently
    completed_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    for result in completed_results:
        if isinstance(result, Exception):
            failed_count += 1
        elif result is not None:
            results.append(result)
        else:
            failed_count += 1

    # Save results
    if results:
        print(f"\nSuccessfully generated {len(results)} samples ({failed_count} failed)")

        output_file = args.output_file + ".json"
        # Always save as array to single file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Load existing data if file exists
        existing_data = []
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r') as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]  # Convert single item to list
            except (json.JSONDecodeError, FileNotFoundError):
                existing_data = []

        # Append new results
        all_data = existing_data + results

        with open(output_file, 'w') as f:
            json.dump(all_data, f, indent=2)

        print(f"Added {len(results)} samples to {output_file} (total: {len(all_data)} samples)")
    else:
        print("Failed to generate any user actions")

if __name__ == "__main__":
    asyncio.run(main())