#!/usr/bin/env python3
"""
Task Instruction Generation for Synthetic Tau-Bench Tasks
Backtranslation: Action Sequences → Natural Language Instructions

This script takes validated action sequences and generates natural language
task instructions that would realistically lead to those actions.
"""

import json
import random
import os
import asyncio
import argparse
from typing import Dict, List, Any, Tuple
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_validated_trajectories(file_path: str) -> List[Dict[str, Any]]:
    """Load validated action trajectories from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def load_user_data(file_path: str = "tau_bench/envs/airline/data/users.json") -> Dict[str, Any]:
    """Load user database from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def load_domain_policy(file_path: str = "tau_bench/envs/airline/wiki.md") -> str:
    """Load airline domain policy from markdown file."""
    with open(file_path, 'r') as f:
        return f.read()



def get_user_context(user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract relevant user information for instruction generation."""
    user = user_data.get(user_id, {})

    context = {
        "user_id": user_id,
        "name": user.get("name", {}),
        "membership": user.get("membership", "regular"),
        "payment_methods": [],
        "existing_reservations": user.get("reservations", []),
        "saved_passengers": user.get("saved_passengers", [])
    }

    # Format payment methods for natural reference
    payment_methods = user.get("payment_methods", {})
    for payment_id, payment_info in payment_methods.items():
        source = payment_info.get("source", "")

        if source == "credit_card":
            brand = payment_info.get("brand", "").title()
            last_four = payment_info.get("last_four", "XXXX")
            context["payment_methods"].append({
                "id": payment_id,
                "type": "credit_card",
                "description": f"{brand} credit card ending in {last_four}",
                "reference": f"credit card ending in {last_four}"
            })
        elif source == "gift_card":
            amount = payment_info.get("amount", 0)
            context["payment_methods"].append({
                "id": payment_id,
                "type": "gift_card",
                "description": f"gift card with ${amount}",
                "reference": f"gift card"
            })
        elif source == "certificate":
            amount = payment_info.get("amount", 0)
            context["payment_methods"].append({
                "id": payment_id,
                "type": "certificate",
                "description": f"travel certificate worth ${amount}",
                "reference": f"travel certificate"
            })

    return context


def build_instruction_prompt(
    user_context: Dict[str, Any],
    actions: List[Dict[str, Any]],
    domain_policy: str
) -> str:
    """Create a prompt for generating natural language instructions."""
    import json

    # Analyze action complexity
    action_count = len(actions)
    action_types = [action["name"] for action in actions]

    # Determine if this is a simple or complex action sequence
    simple_actions = {"get_reservation_details", "get_user_details", "list_all_airports", "search_direct_flight", "search_onestop_flight"}
    is_simple = action_count == 1 and action_types[0] in simple_actions

    if is_simple:
        # Simple action - generate focused, concise instruction
        action = actions[0]
        action_name = action["name"]

        if action_name == "get_reservation_details":
            reservation_id = action["kwargs"]["reservation_id"]
            prompt = f"""Generate a concise, focused airline customer instruction for checking a reservation.

USER: {user_context["user_id"]} | {user_context["membership"]} member

ACTION: Check reservation {reservation_id}

SIMPLE INSTRUCTION EXAMPLES:
"Your user id is aarav_garcia_1177. You want to check your reservation M05KNL details."
"Your user id is emma_thompson_8432. You need to verify the departure time for your reservation ABC123 because you're coordinating a ride to the airport."
"Your user id is john_doe_456. You want to confirm your flight details for reservation XYZ789."

Generate a simple, focused instruction (1-2 sentences) starting with "Your user id is {user_context["user_id"]}." that explains why they need to check reservation {reservation_id}:"""

        elif action_name in {"search_direct_flight", "search_onestop_flight"}:
            kwargs = action["kwargs"]
            origin = kwargs["origin"]
            destination = kwargs["destination"]
            date = kwargs["date"]
            prompt = f"""Generate a concise airline customer instruction for searching flights.

USER: {user_context["user_id"]} | {user_context["membership"]} member

ACTION: Search flights from {origin} to {destination} on {date}

SIMPLE SEARCH EXAMPLES:
"Your user id is harper_ahmed_8302. You are searching for a direct flight from JFK to SEA on 2024-05-16."
"Your user id is jane_smith_456. You want to find a direct flight from JFK to SEA on May 16th. You prefer morning departures but afternoon is acceptable."

Generate a simple instruction (1-2 sentences) starting with "Your user id is {user_context["user_id"]}." for searching flights from {origin} to {destination} on {date}:"""

        elif action_name == "get_user_details":
            prompt = f"""Generate a concise instruction for checking user account details.

USER: {user_context["user_id"]} | {user_context["membership"]} member

SIMPLE USER DETAIL EXAMPLES:
"Your user id is raj_khan_9352. You want to check your account details."
"Your user id is olivia_anderson_8651. You need to verify your payment methods and travel certificates."

Generate a simple instruction (1-2 sentences) starting with "Your user id is {user_context["user_id"]}." for checking account details:"""

        elif action_name == "list_all_airports":
            prompt = f"""Generate a concise instruction for listing airports.

USER: {user_context["user_id"]} | {user_context["membership"]} member

SIMPLE AIRPORT LISTING EXAMPLES:
"Your user id is aarav_sanchez_7773. You want to see all available airports."
"Your user id is sophia_garcia_4224. You need to view all airports for planning your trip."

Generate a simple instruction (1-2 sentences) starting with "Your user id is {user_context["user_id"]}." for listing airports:"""

        else:
            # Fallback for other simple actions
            prompt = f"""Generate a simple, focused instruction for this action.

USER: {user_context["user_id"]} | {user_context["membership"]} member

ACTION: {json.dumps(actions[0], indent=2)}

Generate a simple instruction (1-2 sentences) starting with "Your user id is {user_context["user_id"]}." that explains this action:"""

    else:
        # Complex action sequence - generate detailed, rich instruction
        prompt = f"""Generate a detailed, realistic airline customer instruction that creates the exact action sequence below.

USER CONTEXT:
- User ID: {user_context["user_id"]}
- Membership: {user_context["membership"]}
- Payment Methods: {', '.join([pm['description'] for pm in user_context["payment_methods"]])}
- Existing Reservations: {', '.join(user_context["existing_reservations"])}

ACTIONS TO ACCOMPLISH:
{json.dumps(actions, indent=2)}

COMPLEX TAU-BENCH INSTRUCTION EXAMPLES:

EXAMPLE 1 - Complex booking with constraints:
"Your user id is mia_li_3668. You want to fly from New York to Seattle on May 20 (one way). You do not want to fly before 11am est. You want to fly in economy. You prefer direct flights but one stopover also fine. If there are multiple options, you prefer the one with the lowest price. You have 3 baggages. You do not want insurance. You want to use your two certificates to pay. If only one certificate can be used, you prefer using the larger one, and pay the rest with your 7447 card. You are reactive to the agent and will not say anything that is not asked. Your birthday is in your user profile so you do not prefer to provide it."

EXAMPLE 2 - Complex modification with geographic preferences:
"Your user id is aarav_garcia_1177. For your upcoming trip from ATL to PHL, you want to change for the cheapest economy flight and for the day after the original reservation. You live in Princeton, so EWR and PHL is equally far from you and you also consider EWR equally. You are happy with original payment for refund."

EXAMPLE 3 - Complex scenario with conditional logic:
"Your user id is sofia_kim_7287, and you want to change for your Houston to Denver trip (reservation id not remembered), the fastest return trip (including stopover time) possible on the same day as the departure trip (May 27). You don't care about money but want to stay in economy. You also want to add one checked bag. You want to use your gift card with the smallest balance to pay. You are reactive to the agent and will not say anything that is not asked. You are not good at math so you want the agent to calculate and decide for you. Try to paraphrase instead of repeating this instruction. It is urgent."

GENERATE COMPLEX INSTRUCTION REQUIREMENTS:
1. **Start with**: "Your user id is {user_context["user_id"]}."
2. **Create realistic scenario** that naturally leads to the actions shown
3. **Include rich constraints**:
   - Time preferences (no flights before/after X, morning/evening preferences)
   - Price sensitivity and decision criteria (cheapest, second cheapest, budget limits)
   - Geographic preferences (airport choices, location-based decisions)
   - Payment strategy (preference order, fallback logic, budget considerations)
   - Flight type preferences (direct vs stopover, specific cabin classes)
4. **Add conditional decision logic**: "If X, then Y. If that's not possible, then Z."
5. **Include behavioral instructions**: "You are reactive/proactive", "You do not prefer to provide X", "You want the agent to calculate for you"
6. **Add realistic motivations**: Why they need this, urgency, personal circumstances
7. **Complex payment logic**: Use certificates first, then gift cards, specific card preferences, budget limits

Generate a detailed, realistic tau-bench style instruction:"""

    return prompt


async def generate_instruction(prompt: str, api_key: str) -> str:
    """Use OpenAI API to generate a natural language instruction."""
    client = AsyncOpenAI(api_key=api_key)

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at creating realistic customer service instructions. Generate natural, human-like instructions that would lead to specific action sequences."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.8  # Add some creativity for behavioral variety
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error generating instruction: {e}")
        return ""


def create_task_object(
    instruction: str,
    actions: List[Dict[str, Any]],
    user_id: str,
    difficulty: str,
    trajectory_metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create a tau-bench compatible Task object."""
    task = {
        "instruction": instruction,
        "actions": actions,
        "user_id": user_id,
        "difficulty": difficulty,
        "synthetic_generation": {
            "method": "backtranslation",
            "source": "validated_action_sequence",
            "generated_timestamp": None  # Will be set during processing
        }
    }

    if trajectory_metadata:
        task["trajectory_metadata"] = trajectory_metadata

    return task


async def process_single_trajectory(
    trajectory: Dict[str, Any],
    user_data: Dict[str, Any],
    domain_policy: str,
    api_key: str
) -> Dict[str, Any]:
    """Process a single validated trajectory to generate instruction."""
    user_id = trajectory["user_id"]
    actions = trajectory["actions"]
    difficulty = trajectory.get("difficulty", "medium")

    print(f"Processing trajectory for user {user_id} with {len(actions)} actions...")

    # Get user context
    user_context = get_user_context(user_id, user_data)

    # Build prompt with raw actions
    prompt = build_instruction_prompt(user_context, actions, domain_policy)

    # Generate instruction
    instruction = await generate_instruction(prompt, api_key)

    if not instruction:
        print(f"  ❌ Failed to generate instruction for user {user_id}")
        return None

    print(f"  ✅ Generated instruction for user {user_id}")

    # Create task object
    task = create_task_object(
        instruction=instruction,
        actions=actions,
        user_id=user_id,
        difficulty=difficulty,
        trajectory_metadata=trajectory.get("validation", {})
    )

    return task


async def process_trajectories(
    trajectories: List[Dict[str, Any]],
    user_data: Dict[str, Any],
    domain_policy: str,
    api_key: str,
    max_concurrency: int = 5
) -> List[Dict[str, Any]]:
    """Process all trajectories with concurrency control."""
    tasks = []
    completed_tasks = []

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrency)

    async def process_with_semaphore(trajectory):
        async with semaphore:
            return await process_single_trajectory(trajectory, user_data, domain_policy, api_key)

    # Process only valid trajectories
    valid_trajectories = [t for t in trajectories if t.get("validation", {}).get("is_valid", False)]
    print(f"Processing {len(valid_trajectories)} valid trajectories out of {len(trajectories)} total...")

    # Create all tasks
    for trajectory in valid_trajectories:
        task = process_with_semaphore(trajectory)
        tasks.append(task)

    # Execute with progress tracking
    for i, task in enumerate(asyncio.as_completed(tasks), 1):
        result = await task
        if result:
            completed_tasks.append(result)
        print(f"Progress: {i}/{len(tasks)} trajectories processed")

    print(f"\nCompleted: {len(completed_tasks)} task instructions generated")
    return completed_tasks


def save_tasks(tasks: List[Dict[str, Any]], output_file: str):
    """Save generated tasks to JSON file."""
    # Add generation timestamp
    import datetime
    timestamp = datetime.datetime.now().isoformat()

    for task in tasks:
        task["synthetic_generation"]["generated_timestamp"] = timestamp

    with open(output_file, 'w') as f:
        json.dump(tasks, f, indent=2)

    print(f"Saved {len(tasks)} task instructions to {output_file}")


async def main():
    """Main function to run instruction generation."""
    parser = argparse.ArgumentParser(description='Generate task instructions from validated trajectories')
    parser.add_argument('--input-file', type=str, required=True,
                       help='Input file with validated trajectories')
    parser.add_argument('--output-file', type=str, required=True,
                       help='Output file for generated task instructions')
    parser.add_argument('--max-concurrency', type=int, default=10,
                       help='Maximum concurrent API requests')
    parser.add_argument('--users-file', type=str, default="tau_bench/envs/airline/data/users.json",
                       help='Path to users database file')
    parser.add_argument('--policy-file', type=str, default="tau_bench/envs/airline/wiki.md",
                       help='Path to domain policy file')

    args = parser.parse_args()

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return

    # Load input data
    print("Loading input data...")
    trajectories = load_validated_trajectories(args.input_file)
    user_data = load_user_data(args.users_file)
    domain_policy = load_domain_policy(args.policy_file)

    print(f"Loaded {len(trajectories)} trajectories and {len(user_data)} users")

    # Process trajectories
    tasks = await process_trajectories(
        trajectories=trajectories,
        user_data=user_data,
        domain_policy=domain_policy,
        api_key=api_key,
        max_concurrency=args.max_concurrency
    )

    # Save results
    if tasks:
        save_tasks(tasks, args.output_file)
    else:
        print("No tasks generated")


if __name__ == "__main__":
    asyncio.run(main())