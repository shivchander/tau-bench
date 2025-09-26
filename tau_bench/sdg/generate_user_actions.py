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


def load_users(
    users_file: str = "tau_bench/envs/airline/data/users.json",
) -> Dict[str, Any]:
    """Load user data from JSON file."""
    with open(users_file, "r") as f:
        return json.load(f)


def load_reservations(
    reservations_file: str = "tau_bench/envs/airline/data/reservations.json",
) -> Dict[str, Any]:
    """Load reservations data from JSON file."""
    with open(reservations_file, "r") as f:
        return json.load(f)


def load_flights(
    flights_file: str = "tau_bench/envs/airline/data/flights.json",
) -> Dict[str, Any]:
    """Load flights data from JSON file."""
    with open(flights_file, "r") as f:
        return json.load(f)


def get_detailed_flight_info(
    flight_number: str, flights_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Get complete details for a specific flight with per-date seat availability."""
    if flight_number not in flights_data:
        return None

    flight_info = flights_data[flight_number]
    origin = flight_info["origin"]
    destination = flight_info["destination"]

    # Get available dates with detailed seat info per date
    available_dates_with_seats = []
    pricing = {}

    for date, date_info in flight_info["dates"].items():
        if date_info["status"] == "available":
            date_seats = date_info.get("available_seats", {})
            available_dates_with_seats.append({"date": date, "seats": date_seats})
            # Get pricing from first available date (consistent across dates)
            if not pricing:
                pricing = date_info.get("prices", {})

    # Limit to first 5 dates for prompt brevity
    available_dates_with_seats = available_dates_with_seats[:5]

    return {
        "flight_number": flight_number,
        "route": f"{origin} → {destination}",
        "origin": origin,
        "destination": destination,
        "available_dates_with_seats": available_dates_with_seats,
        "pricing": pricing,
    }


def get_user_relevant_flight_constraints(
    user_id: str,
    users_data: Dict[str, Any],
    reservations_data: Dict[str, Any],
    flights_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Get flight constraints relevant to a specific user - their existing flights + additional options."""
    import random

    # 1. Extract flights from user's existing reservations
    user = users_data.get(user_id, {})
    user_flight_numbers = set()

    for res_id in user.get("reservations", []):
        if res_id in reservations_data:
            reservation = reservations_data[res_id]
            for flight in reservation.get("flights", []):
                user_flight_numbers.add(flight["flight_number"])

    # 2. Add 5 random flights for variety (avoid duplicates)
    all_flights = list(flights_data.keys())
    available_random = [f for f in all_flights if f not in user_flight_numbers]
    num_random = min(5, len(available_random))
    random_flights = (
        random.sample(available_random, num_random) if available_random else []
    )

    # 3. Combine flight numbers (will get detailed info below)

    # 4. Get detailed information for each flight
    user_flights = []
    additional_flights = []
    all_dates = set()

    for flight_num in user_flight_numbers:
        flight_details = get_detailed_flight_info(flight_num, flights_data)
        if flight_details:
            user_flights.append(flight_details)
            all_dates.update(
                [d["date"] for d in flight_details["available_dates_with_seats"]]
            )

    for flight_num in random_flights:
        flight_details = get_detailed_flight_info(flight_num, flights_data)
        if flight_details:
            additional_flights.append(flight_details)
            all_dates.update(
                [d["date"] for d in flight_details["available_dates_with_seats"]]
            )

    return {
        "user_flights": user_flights,
        "additional_flights": additional_flights,
        "all_relevant_flights": user_flights + additional_flights,
        "date_range": f"{min(all_dates)} to {max(all_dates)}"
        if all_dates
        else "2024-05-01 to 2024-05-30",
    }


def get_tool_info() -> List[Dict[str, Any]]:
    """Get the full information of all available tools including function signatures."""
    return [tool.get_info() for tool in ALL_TOOLS]


def format_tools_for_prompt(tools_info: List[Dict[str, Any]]) -> str:
    """Format tool information for the LLM prompt with full signatures."""
    formatted_tools = []

    for tool_info in tools_info:
        func_info = tool_info["function"]
        tool_name = func_info["name"]
        description = func_info["description"]

        # Format parameters
        params = func_info["parameters"]["properties"]
        required_params = func_info["parameters"].get("required", [])

        param_lines = []
        for param_name, param_details in params.items():
            param_type = param_details.get("type", "unknown")
            is_required = (
                "(REQUIRED)" if param_name in required_params else "(optional)"
            )
            param_desc = param_details.get("description", "")

            param_line = f"    - {param_name}: {param_type} {is_required}"
            if param_desc:
                param_line += f" - {param_desc}"
            param_lines.append(param_line)

        tool_format = f"""
{tool_name}:
  Description: {description}
  Parameters:
{chr(10).join(param_lines)}"""

        formatted_tools.append(tool_format)

    return "\n".join(formatted_tools)


def get_user_context(
    user_id: str, users_data: Dict[str, Any], reservations_data: Dict[str, Any]
) -> str:
    """Extract relevant context about a user for the teacher model."""
    user = users_data[user_id]

    context = f"User ID: {user_id}\n"
    context += f"Membership Level: {user.get('membership', 'None')}\n"

    # Payment methods - extract from payment_methods structure
    payment_methods = []
    if "payment_methods" in user:
        context += "Payment Methods:\n"
        for payment_id, payment_info in user["payment_methods"].items():
            if payment_info["source"] == "certificate":
                payment_methods.append(
                    f"  - ID: {payment_id} (Certificate, ${payment_info['amount']} available)"
                )
            elif payment_info["source"] == "gift_card":
                payment_methods.append(
                    f"  - ID: {payment_id} (Gift Card, ${payment_info['amount']} available)"
                )
            elif payment_info["source"] == "credit_card":
                last_four = payment_info.get("last_four", "XXXX")
                brand = payment_info.get("brand", "unknown")
                payment_methods.append(
                    f"  - ID: {payment_id} (Credit Card, {brand} ending in {last_four}, unlimited)"
                )

        context += "\n".join(payment_methods) + "\n"

    # Saved passengers
    if "saved_passengers" in user:
        passengers = []
        for passenger in user["saved_passengers"]:
            passengers.append(
                f"{passenger['first_name']} {passenger['last_name']} (DOB: {passenger['dob']})"
            )
        context += f"Saved Passengers: {', '.join(passengers)}\n"

    # Existing reservations with full details
    reservation_ids = user.get("reservations", [])
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
                for i, flight in enumerate(res["flights"], 1):
                    context += f"    {i}. {flight['flight_number']} on {flight['date']} ({flight['origin']} → {flight['destination']})\n"
                context += f"  Baggage: {res['total_baggages']} total, {res['nonfree_baggages']} paid\n"
                context += f"  Insurance: {res['insurance']}\n"
                context += f"  Created: {res['created_at']}\n\n"
    else:
        context += "\nNo existing reservations.\n"

    return context


def build_generation_prompt(
    selected_user_id: str,
    user_context: str,
    flight_constraints: Dict[str, Any],
    tools_info: List[Dict[str, Any]],
    difficulty: str,
    config: Dict[str, int],
) -> str:
    """Build the complete prompt for user action generation."""

    # Provide concrete examples of complete Action structures
    action_examples = """
COMPLETE ACTION EXAMPLES (COPY THESE STRUCTURES EXACTLY):

book_reservation example (WITH CALCULATED PAYMENT):
{
    "name": "book_reservation",
    "kwargs": {
        "user_id": "mia_li_3668",
        "origin": "JFK",
        "destination": "SEA",
        "flight_type": "one_way",
        "cabin": "economy",
        "flights": [
            {"flight_number": "HAT136", "date": "2024-05-20"},
            {"flight_number": "HAT039", "date": "2024-05-20"}
        ],
        "passengers": [
            {"first_name": "Mia", "last_name": "Li", "dob": "1990-04-05"}
        ],
        "payment_methods": [
            {"payment_id": "certificate_7504069", "amount": 250},
            {"payment_id": "credit_card_4421486", "amount": 24}
        ],
        "total_baggages": 3,
        "nonfree_baggages": 0,
        "insurance": "yes"
    }
}

update_reservation_flights example:
{
    "name": "update_reservation_flights",
    "kwargs": {
        "reservation_id": "ABC123",
        "cabin": "business",
        "flights": [
            {"flight_number": "HAT201", "date": "2024-05-18"}
        ],
        "payment_id": "credit_card_1234567"
    }
}

update_reservation_baggages example:
{
    "name": "update_reservation_baggages",
    "kwargs": {
        "reservation_id": "ABC123",
        "total_baggages": 2,
        "nonfree_baggages": 1,
        "payment_id": "gift_card_9876543"
    }
}"""

    # Create difficulty-specific prompts
    if difficulty == "easy":
        task_description = f"""Generate a simple, single-action customer service scenario ({config["target_action_count"]} action).
Focus on straightforward tasks like:
- Getting reservation or user details
- Simple flight searches
- Basic certificate sending
- Simple calculations

The scenario should be something a customer could resolve quickly with minimal complexity."""

    elif difficulty == "medium":
        task_description = f"""Generate a moderate complexity customer service scenario ({config["target_action_count"]} actions).
Focus on multi-step scenarios like:
- Booking flights with specific requirements (payment methods, baggage, insurance)
- Updating existing reservations (flights, passengers, baggage)
- Cancel and rebook scenarios
- Scenarios requiring multiple lookups and one update

The scenario should involve some decision-making and multiple related actions."""

    else:  # hard
        task_description = f"""Generate a complex, multi-faceted customer service scenario ({config["target_action_count"]} actions).
Focus on complex scenarios like:
- Managing multiple reservations simultaneously
- Complex booking scenarios with multiple passengers and payment methods
- Multi-step reservation modifications with calculations
- Scenarios involving multiple cancellations and rebookings
- Complex baggage and payment management across multiple flights

The scenario should be realistic but require significant customer service intervention."""

    # Build user-specific flight constraints section
    def format_flight_info(flight):
        pricing_text = (
            ", ".join(
                [f"{cabin} ${price}" for cabin, price in flight["pricing"].items()]
            )
            if flight["pricing"]
            else "pricing unavailable"
        )

        # Format detailed seat availability per date
        date_seat_details = []
        for date_info in flight["available_dates_with_seats"]:
            date = date_info["date"]
            seats = date_info["seats"]
            seat_breakdown = ", ".join(
                [f"{cabin}:{count}" for cabin, count in seats.items()]
            )
            date_seat_details.append(f"{date}({seat_breakdown})")

        dates_seats_text = (
            " | ".join(date_seat_details) if date_seat_details else "no available dates"
        )
        return f"  {flight['flight_number']}: {flight['route']} | Pricing: {pricing_text}\n    Seat Availability: {dates_seats_text}"

    user_flights_text = ""
    if flight_constraints["user_flights"]:
        user_flights_text = f"""
FROM USER'S EXISTING RESERVATIONS (can be updated/cancelled):
{chr(10).join([format_flight_info(flight) for flight in flight_constraints["user_flights"]])}
"""

    additional_flights_text = ""
    if flight_constraints["additional_flights"]:
        additional_flights_text = f"""
ADDITIONAL AVAILABLE FLIGHTS (for new bookings):
{chr(10).join([format_flight_info(flight) for flight in flight_constraints["additional_flights"]])}
"""

    flight_constraints_text = f"""
AVAILABLE FLIGHTS FOR {selected_user_id}:
{user_flights_text}{additional_flights_text}
CRITICAL FLIGHT+DATE PAIRING REQUIREMENTS:
- You MUST ONLY use flight numbers listed above
- You MUST ONLY use dates shown as available for each specific flight
- CRITICAL: Each flight has its own specific list of available dates - you CANNOT mix flight numbers with dates from other flights
- BEFORE selecting any flight, find the flight number in the list above and ONLY use dates listed for THAT SPECIFIC flight
- You MUST use exact pricing shown (economy/business) for payment calculations
- DO NOT make up flight numbers, dates, or prices

SEAT AVAILABILITY CONSTRAINTS (CRITICAL - MUST CHECK BEFORE EVERY BOOKING):
- Each flight+date combination has LIMITED seats per cabin class shown as: date(basic_economy:X, economy:Y, business:Z)
- X,Y,Z are the EXACT number of available seats for that cabin class on that specific date
- BEFORE selecting any flight+date+cabin combination, you MUST verify seats are available
- RULE: If ANY cabin class shows 0 seats, you CANNOT book that cabin class on that date
- RULE: If booking multiple passengers, seat count MUST be >= number of passengers

CRITICAL SEAT CHECKING EXAMPLES:
- If HAT164 shows "2024-05-17(basic_economy:9, economy:19, business:0)"
  → You CAN book basic_economy (9 available) or economy (19 available)
  → You CANNOT book business class (0 available) on 2024-05-17
- If HAT260 shows "2024-05-21(basic_economy:0, economy:6, business:1)"
  → You CANNOT book basic_economy (0 available) on 2024-05-21
  → You CAN book economy (6 available) or business (1 available)
- For multiple passengers: If booking 2 passengers and see "economy:1", you CANNOT book economy (need 2 seats, only 1 available)

FLIGHT+DATE+SEAT VALIDATION PROCESS (FOLLOW THIS EXACTLY):
1. Choose your desired flight number (e.g., HAT074)
2. Find that EXACT flight number in the list above
3. Look at the available dates listed for THAT SPECIFIC flight only
4. Choose ONLY a date that appears in that flight's date list
5. For your chosen flight+date combination, check the seat availability
6. Verify your desired cabin class has >0 seats available
7. If seats available >= passengers needed, you can proceed
8. If date not available for that flight OR seats = 0, choose different flight/date/cabin

EXAMPLE VALIDATION:
- You want HAT074: Look up HAT074 in the list → available dates are 2024-05-16, 2024-05-17, 2024-05-18, 2024-05-19, 2024-05-20
- You CANNOT use HAT074 on 2024-05-12 (not in HAT074's available dates)
- You CAN use HAT074 on 2024-05-17 (appears in HAT074's available dates)
- Then check seat availability for HAT074 on 2024-05-17 specifically

PAYMENT CALCULATION RULES (CRITICAL - CALCULATE EXACT AMOUNTS):
- Total cost = (flight_price × number_of_passengers × number_of_flights) + insurance + baggage_fees
- Insurance: $30 per passenger if "insurance": "yes"
- Baggage: $50 per non-free baggage
- Payment methods amounts must add up EXACTLY to the total cost
- BEFORE generating any book_reservation action, you MUST manually calculate the exact total

PAYMENT METHOD REQUIREMENTS:
- You MUST use EXACT payment IDs from the user's Payment Methods section above
- Copy payment IDs exactly - DO NOT modify numbers or make typos
- Gift Cards/Certificates: Check available balance, must have sufficient funds
- Credit Cards: Unlimited balance, always usable
- Examples: Use "gift_card_3112961" exactly as shown, not "gift_card_5112961" """

    prompt = f"""You are designing a {difficulty} difficulty customer service task for an airline system.

User Context:
{user_context}

AVAILABLE TOOLS WITH FULL SIGNATURES:
{format_tools_for_prompt(tools_info)}

CRITICAL REQUIREMENTS:
- You MUST use ONLY the exact action names listed above (case-sensitive snake_case format)
- You MUST use ONLY the exact parameter names shown for each tool
- You MUST provide ALL REQUIRED parameters for each action
- DO NOT use CamelCase like "GetReservationDetails" - use snake_case like "get_reservation_details"
- DO NOT make up parameter names - use only those specified in the tool signatures above

{flight_constraints_text}

REQUIRED PARAMETER VALIDATION:
- EVERY action MUST include ALL parameters marked as (REQUIRED) in the tool signatures above
- For instance, book_reservation MUST ALWAYS include: payment_methods, total_baggages, nonfree_baggages, insurance
- NEVER omit required parameters - this will cause validation failure

{action_examples}

Task Requirements:
{task_description}

You must respond with valid JSON only. Use this exact JSON format:
{{
    "user_id": "{selected_user_id}",
    "difficulty": "{difficulty}",
    "target_action_count": {config["target_action_count"]},
    "actions": [
        {{
            "name": "exact_action_name_from_list_above",
            "kwargs": {{
                "param1": "value1",
                "param2": "value2"
            }}
        }}
    ],
}}

Critical Requirements:
- Generate exactly {config["target_action_count"]} actions for {difficulty} difficulty
- Each action must have proper structure with name and kwargs
- MANDATORY: Use ONLY the exact action names from the list above (snake_case format)
- CRITICAL: Action names must be exact matches from the tools list (e.g., "get_reservation_details", NOT "GetReservationDetails")
- CRITICAL PARAMETER COMPLETENESS: Every action MUST include ALL required parameters
  * book_reservation: MUST include payment_methods, total_baggages, nonfree_baggages, insurance
  * update_reservation_flights: MUST include payment_id
  * update_reservation_baggages: MUST include payment_id
  * Check the tool signatures above and include EVERY parameter marked (REQUIRED)
- Use actual reservation IDs from user context (e.g., "reservation_id": "ABC123")
- Use actual payment IDs from user profile (e.g., "certificate_1234567", "gift_card_9876543")
- MANDATORY: Use only valid flight numbers from the system (shown above, HAT001-HAT300+ format)
- MANDATORY: Use only valid dates within range {flight_constraints["date_range"]}
- CRITICAL FLIGHT+DATE VALIDATION: For ANY flight booking action, you MUST follow the validation process
  * Step 1: Find your chosen flight number in the flight list above
  * Step 2: Verify your chosen date appears in THAT SPECIFIC flight's available dates
  * Step 3: Check seat availability for that exact flight+date combination
  * Never use a flight with a date that's not listed for that specific flight
  * Never book a cabin class that shows 0 seats on your chosen date
- Actions must be logically connected and realistic for this user's specific context
- Ensure the scenario complexity matches the {difficulty} difficulty level"""

    return prompt


def debug_save_prompt(
    selected_user_id: str,
    user_context: str,
    flight_constraints: Dict[str, Any],
    tools_info: List[Dict[str, Any]],
    difficulty: str,
    config: Dict[str, int],
    output_file: str = "/tmp/debug_prompt.txt",
) -> None:
    """Save the generated prompt to a file for debugging purposes."""
    prompt = build_generation_prompt(
        selected_user_id,
        user_context,
        flight_constraints,
        tools_info,
        difficulty,
        config,
    )
    with open(output_file, "w") as f:
        f.write(prompt)
    print(f"Debug prompt saved to {output_file}")


async def generate_user_actions(
    users_data: Dict[str, Any],
    reservations_data: Dict[str, Any],
    flights_data: Dict[str, Any],
    tools_info: List[Dict[str, Any]],
    api_key: str,
    difficulty: str,
) -> Dict[str, Any]:
    """Generate user selection, difficulty, and actions using OpenAI API."""

    # Randomly select a user
    user_ids = list(users_data.keys())
    selected_user_id = random.choice(user_ids)
    user_context = get_user_context(selected_user_id, users_data, reservations_data)

    # Get user-specific flight constraints
    flight_constraints = get_user_relevant_flight_constraints(
        selected_user_id, users_data, reservations_data, flights_data
    )

    # Define difficulty levels
    difficulty_config = {
        "easy": {"min_actions": 1, "max_actions": 1},
        "medium": {"min_actions": 2, "max_actions": 5},
        "hard": {"min_actions": 5, "max_actions": 8},
    }

    config = difficulty_config[difficulty]

    # Randomly select target action count within range
    target_action_count = random.randint(config["min_actions"], config["max_actions"])
    config["target_action_count"] = target_action_count

    client = AsyncOpenAI(api_key=api_key)

    # Build the complete prompt using the separated function
    prompt = build_generation_prompt(
        selected_user_id,
        user_context,
        flight_constraints,
        tools_info,
        difficulty,
        config,
    )

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at designing realistic customer service scenarios for airline systems. Always provide complete action structures with proper kwargs.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)

        # Validate the result
        result_difficulty = result["difficulty"]
        action_count = len(result["actions"])

        # Verify the difficulty matches what we requested
        if result_difficulty != difficulty:
            raise ValueError(
                f"Expected difficulty '{difficulty}', but got '{result_difficulty}'"
            )

        # Verify action count is within expected range
        min_actions, max_actions = config["min_actions"], config["max_actions"]
        if not (min_actions <= action_count <= max_actions):
            raise ValueError(
                f"Action count {action_count} doesn't match {difficulty} difficulty range ({min_actions}-{max_actions})"
            )

        return result

    except Exception as e:
        print(f"Error generating actions: {e}")
        return None


async def main():
    """Main function to run the user and action generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic tau-bench tasks")
    parser.add_argument(
        "--num-samples",
        type=int,
        default=1,
        help="Number of user action sequences to generate (default: 1)",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="tau_bench/sdg/generated_user_actions",
        help="Output file for generated files (default: tau_bench/sdg/generated_user_actions)",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=8,
        help="Maximum concurrent API requests (default: 5)",
    )
    parser.add_argument(
        "--difficulty",
        type=str,
        choices=["easy", "medium", "hard"],
        default="medium",
        help="Difficulty level for generated tasks (default: medium)",
    )
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
    tools_info = get_tool_info()

    # Extract tool names for display
    tool_names = [tool["function"]["name"] for tool in tools_info]

    print(
        f"Loaded {len(users_data)} users, {len(reservations_data)} reservations, {len(flights_data)} flights, and {len(tools_info)} tools"
    )
    print(f"Available tools: {', '.join(tool_names)}")
    print(
        "Note: Flight constraints will be generated per-user to include their existing reservations"
    )

    # Generate multiple samples concurrently
    results = []
    failed_count = 0

    print(
        f"Generating {args.num_samples} {args.difficulty} user action sequences with max {args.max_concurrency} concurrent requests..."
    )

    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(args.max_concurrency)

    async def generate_with_semaphore(sample_id: int):
        async with semaphore:
            try:
                result = await generate_user_actions(
                    users_data,
                    reservations_data,
                    flights_data,
                    tools_info,
                    api_key,
                    args.difficulty,
                )
                if result:
                    print(
                        f"  ✓ Generated {result['difficulty']} scenario for user {result['user_id']} with {len(result['actions'])} actions (sample {sample_id + 1})"
                    )
                    return result
                else:
                    print(f"  ✗ Failed to generate sample {sample_id + 1}")
                    return None
            except Exception as e:
                print(f"  ✗ Failed to generate sample {sample_id + 1}: {e}")
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
        print(
            f"\nSuccessfully generated {len(results)} samples ({failed_count} failed)"
        )

        output_file = args.output_file + ".json"
        # Always save as array to single file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Load existing data if file exists
        existing_data = []
        if os.path.exists(output_file):
            try:
                with open(output_file, "r") as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]  # Convert single item to list
            except (json.JSONDecodeError, FileNotFoundError):
                existing_data = []

        # Append new results
        all_data = existing_data + results

        with open(output_file, "w") as f:
            json.dump(all_data, f, indent=2)

        print(
            f"Added {len(results)} samples to {output_file} (total: {len(all_data)} samples)"
        )
    else:
        print("Failed to generate any user actions")


if __name__ == "__main__":
    asyncio.run(main())
