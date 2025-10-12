#!/usr/bin/env python3
"""
Simple Few-Shot Instruction Generator for Tau-Bench

Uses direct action→instruction mapping examples to teach the model
how to generate natural customer service instructions.
"""

import json
import os
import asyncio
from typing import Dict, List, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_users(
    users_file: str = "tau_bench/envs/airline/data/users.json",
) -> Dict[str, Any]:
    """Load user data from JSON file."""
    with open(users_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_reservations(
    reservations_file: str = "tau_bench/envs/airline/data/reservations.json",
) -> Dict[str, Any]:
    """Load reservations data from JSON file."""
    with open(reservations_file, "r", encoding="utf-8") as f:
        return json.load(f)


# Few-shot examples from original tau-bench data
FEW_SHOT_EXAMPLES = [
    {
        "actions": [
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
            }
        ],
        "instruction": (
            "Your user id is mia_li_3668. You want to fly from New York to Seattle "
            "on May 20 (one way). You do not want to fly before 11am est. "
            "You want to fly in economy. You prefer direct flights but one stopover "
            "also fine. If there are multiple options, you prefer the one with the "
            "lowest price. You have 3 baggages. You do not want insurance. "
            "You want to use your two certificates to pay. If only one certificate "
            "can be used, you prefer using the larger one, and pay the rest with "
            "your 7447 card. You are reactive to the agent and will not say anything "
            "that is not asked. Your birthday is in your user profile so you do not "
            "prefer to provide it."
        ),
    },
    {
        "actions": [
            {
                "name": "update_reservation_flights",
                "kwargs": {
                    "reservation_id": "OBUT9V",
                    "cabin": "economy",
                    "flights": [
                        {"flight_number": "HAT078", "date": "2024-05-27"},
                        {"flight_number": "HAT118", "date": "2024-05-27"},
                        {"flight_number": "HAT290", "date": "2024-05-27"},
                        {"flight_number": "HAT175", "date": "2024-05-27"},
                    ],
                    "payment_id": "gift_card_6276644",
                },
            },
            {
                "name": "update_reservation_baggages",
                "kwargs": {
                    "reservation_id": "OBUT9V",
                    "total_baggages": 2,
                    "nonfree_baggages": 0,
                    "payment_id": "gift_card_6276644",
                },
            },
        ],
        "instruction": (
            "Your user id is sofia_kim_7287, and you want to change for your Houston "
            "to Denver trip (reservation id not remembered), the fastest return trip "
            "(including stopover time) possible on the same day as the departure trip "
            "(May 27). You don't care about money but want to stay in economy. "
            "You also want to add one checked bag. You want to use your gift card "
            "with the smallest balance to pay. You are reactive to the agent and will "
            "not say anything that is not asked. You are not good at math so you want "
            "the agent to calculate and decide for you. Try to paraphrase instead of "
            "repeating this instruction. It is urgent."
        ),
    },
    {
        "actions": [
            {
                "name": "update_reservation_flights",
                "kwargs": {
                    "reservation_id": "FQ8APE",
                    "cabin": "economy",
                    "flights": [
                        {"flight_number": "HAT056", "date": "2024-05-25"},
                        {"flight_number": "HAT138", "date": "2024-05-25"},
                    ],
                    "payment_id": "gift_card_8190333",
                },
            },
            {
                "name": "update_reservation_passengers",
                "kwargs": {
                    "reservation_id": "FQ8APE",
                    "passengers": [
                        {
                            "first_name": "Omar",
                            "last_name": "Rossi",
                            "dob": "1970-06-06",
                        }
                    ],
                },
            },
            {
                "name": "update_reservation_baggages",
                "kwargs": {
                    "reservation_id": "FQ8APE",
                    "total_baggages": 3,
                    "nonfree_baggages": 0,
                    "payment_id": "gift_card_8190333",
                },
            },
        ],
        "instruction": (
            "Your user id is omar_rossi_1241. For your upcoming trip from New York "
            "to Chicago, you want to change the passenger to yourself, upgrade it "
            "to economy class, and have 3 checked bags. You prefer gift card payment. "
            "Your birthday is in your user profile so you do not prefer to provide it. "
            "You are reactive to the agent and will not say anything that is not asked."
        ),
    },
]


def build_few_shot_prompt(
    new_actions: List[Dict],
    user_id: str,
    users_data: Dict[str, Any],
    reservations_data: Dict[str, Any],
) -> str:
    """Build a comprehensive few-shot prompt with system guidance and task framing."""

    # 1. TASK DESCRIPTION
    task_description = (
        "### TASK: \n"
        "Generate a natural language instruction from a user's action sequence.\n\n"
        "Given a user profile and a sequence of airline booking system actions, write a fluent, "
        "natural instruction that a real traveler would give to a customer service agent. "
        "The instruction should lead the agent to perform exactly those actions.\n\n"
        "### CRITICAL REQUIREMENTS:\n"
        f"- ALWAYS start with 'Your user id is {user_id}.'\n"
        "- Use second-person voice only ('You want...', 'You prefer...') never first-person\n"
        "- Capture ALL constraints from the actions (specific payment methods, flight numbers, dates, etc.)\n"
        "- When specifying payment methods, use human-readable descriptions:\n"
        "  * If user has multiple credit cards, specify by brand and last 4 digits (e.g., 'your Visa ending in 7447')\n"
        "  * If user has multiple certificates/gift cards, specify by amount (e.g., 'your $250 certificate')\n"
        "  * If only one payment method of a type exists, simpler form is OK (e.g., 'your gift card')\n"
        "- Include specific flight numbers, dates, and reservation IDs from the actions\n"
        "- Include conditional logic and fallback preferences where appropriate\n"
        "- Add behavioral constraints: 'You are reactive to the agent and will not say anything that is not asked'\n"
        "- Never mention internal IDs (like payment_id values), function names, or technical details\n\n"
    )

    # 2. FEW-SHOT EXAMPLES
    examples_section = "### EXAMPLES OF GOOD INSTRUCTIONS:\n\n"
    for i, example in enumerate(FEW_SHOT_EXAMPLES, 1):
        example_user_id = example["actions"][0]["kwargs"].get("user_id", "unknown")
        examples_section += f"Example {i}:\n"
        examples_section += f"User ID: {example_user_id}\n"
        examples_section += f"Actions:\n{json.dumps(example['actions'], indent=2)}\n\n"
        examples_section += f'Generated Instruction:\n"{example["instruction"]}"\n\n'
        examples_section += "-" * 80 + "\n\n"

    # 3. USER PROFILE
    user_profile_section = f"### USER PROFILE FOR {user_id}:\n\n"
    if user_id in users_data:
        user_profile_section += json.dumps(users_data[user_id], indent=2)
        user_profile_section += "\n\n"

        # 4. USER'S RESERVATIONS
        user_reservations = users_data[user_id].get("reservations", [])
        if user_reservations:
            user_profile_section += f"### EXISTING RESERVATIONS FOR {user_id}:\n\n"
            for res_id in user_reservations:
                if res_id in reservations_data:
                    user_profile_section += f"Reservation {res_id}:\n"
                    user_profile_section += json.dumps(reservations_data[res_id], indent=2)
                    user_profile_section += "\n\n"
    else:
        raise ValueError(f"User {user_id} not found in database")

    user_profile_section += "=" * 80 + "\n\n"

    # 5. ACTIONS TO GENERATE INSTRUCTION FOR
    actions_section = "### NOW GENERATE AN INSTRUCTION FOR THESE ACTIONS:\n\n"
    actions_section += json.dumps(new_actions, indent=2)
    actions_section += "\n\n"
    actions_section += "=" * 80 + "\n\n"

    # 6. FINAL GENERATION PROMPT
    final_prompt = (
        f"Generate a natural language instruction for the actions above.\n\n"
        f"Remember:\n"
        f"- Start with 'Your user id is {user_id}.'\n"
        f"- Look at the user profile to see what payment methods are available\n"
        f"- If multiple payment methods of the same type exist, disambiguate in the instruction\n"
        f"- Capture all specific constraints (flight numbers, dates, reservation IDs, payment methods)\n"
        f"- Write as the customer explaining what they want to the agent\n"
        f"- Use natural, conversational language\n\n"
        f"Instruction:"
    )

    # Combine all sections
    return (
        task_description
        + examples_section
        + user_profile_section
        + actions_section
        + final_prompt
    )


async def generate_instruction(
    actions: List[Dict],
    user_id: str,
    users_data: Dict[str, Any],
    reservations_data: Dict[str, Any],
    api_key: str,
) -> str:
    """Generate instruction using few-shot learning."""
    client = AsyncOpenAI(api_key=api_key)

    prompt = build_few_shot_prompt(actions, user_id, users_data, reservations_data)

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert at writing one natural-language task instruction "
                        "for a travel agent benchmark."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        instruction = response.choices[0].message.content
        if instruction:
            instruction = instruction.strip()
            # Remove quotes if present
            if instruction.startswith('"') and instruction.endswith('"'):
                instruction = instruction[1:-1]

            # Ensure it starts with the user ID
            user_prefix = f"Your user id is {user_id}."
            if not instruction.lower().startswith(user_prefix.lower()):
                instruction = f"{user_prefix} {instruction}"

            return instruction
        return ""

    except Exception as e:
        print(f"Error generating instruction: {e}")
        return ""


def load_action_sequences(file_path: str) -> List[Dict]:
    """Load action sequences from JSON file and filter for valid ones only."""
    with open(file_path, "r", encoding="utf-8") as f:
        all_sequences = json.load(f)

    # Filter for valid sequences only
    valid_sequences = []
    invalid_count = 0

    for sequence in all_sequences:
        validation = sequence.get("validation", {})
        is_valid = validation.get(
            "is_valid", True
        )  # Default to True if no validation info

        if is_valid:
            valid_sequences.append(sequence)
        else:
            invalid_count += 1
            error_msg = validation.get("error_message", "Unknown validation error")
            print(
                f"⚠️  Skipping invalid sequence for user {sequence.get('user_id', 'unknown')}: {error_msg}"
            )

    print(f"📊 Loaded {len(all_sequences)} total sequences")
    print(f"✅ {len(valid_sequences)} valid sequences to process")
    if invalid_count > 0:
        print(f"❌ {invalid_count} invalid sequences filtered out")

    return valid_sequences


async def process_action_sequences(
    sequences: List[Dict], api_key: str, max_concurrency: int = 10
) -> List[Dict]:
    """Process action sequences and generate instructions with concurrency control."""
    # Load user and reservation data once
    print("Loading user and reservation data...")
    users_data = load_users()
    reservations_data = load_reservations()
    print(f"Loaded {len(users_data)} users and {len(reservations_data)} reservations")

    semaphore = asyncio.Semaphore(max_concurrency)

    async def process_single_sequence(sequence: Dict, index: int) -> Dict:
        async with semaphore:
            user_id = sequence["user_id"]
            print(
                f"Processing sequence {index + 1}/{len(sequences)} for user {user_id}..."
            )

            instruction = await generate_instruction(
                actions=sequence["actions"],
                user_id=sequence["user_id"],
                users_data=users_data,
                reservations_data=reservations_data,
                api_key=api_key,
            )

            if instruction:
                result = {
                    "user_id": sequence["user_id"],
                    "actions": sequence["actions"],
                    "instruction": instruction,
                    "difficulty": sequence.get("difficulty", "medium"),
                    "method": "few_shot_learning",
                }
                print(f"  ✅ Generated: {instruction[:100]}...")
                return result

            print("  ❌ Failed to generate instruction")
            return None

    # Create tasks for all sequences
    tasks = [
        process_single_sequence(sequence, i) for i, sequence in enumerate(sequences)
    ]

    # Execute with concurrency control
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out None results and exceptions
    valid_results = []
    failed_count = 0
    error_count = 0

    for result in results:
        if isinstance(result, dict) and result is not None:
            valid_results.append(result)
        elif result is None:
            failed_count += 1
        elif isinstance(result, Exception):
            error_count += 1
            print(f"Error processing sequence: {result}")

    if failed_count > 0:
        print(f"⚠️  {failed_count} sequences failed to generate instructions")
    if error_count > 0:
        print(f"❌ {error_count} sequences had errors")

    return valid_results


def save_results(results: List[Dict], output_file: str):
    """Save generated instructions to JSON file."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} instructions to {output_file}")


async def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate instructions using few-shot learning"
    )
    parser.add_argument(
        "--input-file", required=True, help="Input JSON file with action sequences"
    )
    parser.add_argument(
        "--output-file", required=True, help="Output JSON file for instructions"
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=10,
        help="Maximum number of concurrent API requests (default: 10)",
    )

    args = parser.parse_args()

    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return

    # Load input data
    print(f"Loading action sequences from {args.input_file}...")
    sequences = load_action_sequences(args.input_file)

    # Generate instructions
    print(
        f"Generating instructions using few-shot learning "
        f"(concurrency: {args.max_concurrency})..."
    )
    results = await process_action_sequences(sequences, api_key, args.max_concurrency)

    # Save results
    save_results(results, args.output_file)

    # Summary
    print(f"\n✅ Successfully generated {len(results)} instructions")
    if results:
        lengths = [len(r["instruction"]) for r in results]
        words = [len(r["instruction"].split()) for r in results]
        avg_length = sum(lengths) / len(lengths)
        avg_words = sum(words) / len(words)
        print(
            f"Length stats: {min(lengths)}-{max(lengths)} chars (avg: {avg_length:.0f})"
        )
        print(f"Word stats: {min(words)}-{max(words)} words (avg: {avg_words:.0f})")


if __name__ == "__main__":
    asyncio.run(main())
