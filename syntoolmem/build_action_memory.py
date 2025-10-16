"""
Build action memory database from tau-bench trajectories.

For each action in each trajectory, create a ChromaDB entry where:
- Document: Natural language description of what the action does (LLM-generated)
- Metadata: The actual action tool call

Uses async processing for parallel LLM calls with configurable concurrency.
"""

import asyncio
import json
import os
import argparse
from pathlib import Path
from openai import AsyncOpenAI
import chromadb
from tqdm import tqdm
from dotenv import load_dotenv
from syntoolmem.tasks_airline_medium import TASKS as AIRLINE_TASKS
from syntoolmem.tasks_retail_train import TASKS_TRAIN as RETAIL_TASKS

# Load environment variables
load_dotenv()

# Initialize async OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Environment-specific prompts
AIRLINE_PROMPT_TEMPLATE = """Given this flight reservation system action, generate a clear, natural language description (1-2 sentences) of what it does.

Action:
{action_json}

Focus on:
- What the action accomplishes
- Key parameters (cabin class, payment method, etc.)
- Any distinguishing features

Examples:
- "Cancel a flight reservation using reservation ID"
- "Add additional baggage to reservation including non-free checked bags paid with credit card"
- "Book a round-trip economy class flight with multiple payment methods (gift card and credit card)"
- "Update reservation flights to business class using gift card payment"

Return ONLY the description text, no JSON or extra formatting."""

RETAIL_PROMPT_TEMPLATE = """Given this e-commerce customer service action, generate a clear, natural language description (1-2 sentences) of what it does.

Action:
{action_json}

Focus on:
- What the action accomplishes
- Key parameters (item details, payment methods, etc.)
- Any distinguishing features

Examples:
- "Cancel a pending order using order ID"
- "Modify shipping address for pending order to new city and zip code"
- "Change item in pending order from leather boots to synthetic boots paid with PayPal"
- "Apply discount coupon to order and update total price"

Return ONLY the description text, no JSON or extra formatting."""


def get_prompt_for_env(env_name: str, action: dict) -> str:
    """
    Get the appropriate prompt template for the environment.

    Args:
        env_name: Environment name ('airline' or 'retail')
        action: Action dictionary

    Returns:
        Formatted prompt string
    """
    action_json = json.dumps(action, indent=2)

    if env_name == "airline":
        return AIRLINE_PROMPT_TEMPLATE.format(action_json=action_json)
    elif env_name == "retail":
        return RETAIL_PROMPT_TEMPLATE.format(action_json=action_json)
    else:
        raise ValueError(
            f"Unknown environment: {env_name}. Choose 'airline' or 'retail'."
        )


async def generate_action_description(action, semaphore, env_name="airline"):
    """
    Use LLM to generate a natural language description of what an action does.

    Args:
        action: Dictionary with 'name' and 'kwargs' keys
        semaphore: Asyncio semaphore for concurrency control
        env_name: Environment name ('airline' or 'retail')

    Returns:
        String description of the action
    """
    prompt = get_prompt_for_env(env_name, action)

    async with semaphore:
        try:
            response = await openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )

            description = response.choices[0].message.content.strip()
            # Remove quotes if LLM added them
            if description.startswith('"') and description.endswith('"'):
                description = description[1:-1]
            return description
        except Exception as e:
            print(f"Error generating description: {e}")
            # Fallback to simple description
            return f"Perform {action['name']} action"


async def process_all_actions(trajectories, max_concurrency, env_name="airline"):
    """
    Process all actions from trajectories in parallel.

    Args:
        trajectories: List of trajectory dictionaries
        max_concurrency: Maximum number of concurrent LLM calls
        env_name: Environment name ('airline' or 'retail')

    Returns:
        Tuple of (documents, metadatas, ids)
    """
    semaphore = asyncio.Semaphore(max_concurrency)

    # Collect all actions with their metadata
    tasks = []
    action_info = []

    for traj_idx, trajectory in enumerate(trajectories):
        for action_idx, action in enumerate(trajectory["actions"]):
            tasks.append(generate_action_description(action, semaphore, env_name))
            action_info.append(
                {"action": action, "traj_idx": traj_idx, "action_idx": action_idx}
            )

    # Process all actions concurrently with progress bar
    print(
        f"\nGenerating descriptions for {len(tasks)} actions with max_concurrency={max_concurrency}..."
    )

    # Track progress using as_completed for UI feedback, but gather results in order
    with tqdm(total=len(tasks), desc="Generating descriptions") as pbar:
        # Create a wrapper to update progress
        async def task_with_progress(task):
            result = await task
            pbar.update(1)
            return result

        # Execute all tasks with progress tracking
        descriptions = await asyncio.gather(*[task_with_progress(t) for t in tasks])

    # Build the final lists
    documents = []
    metadatas = []
    ids = []

    for info, description in zip(action_info, descriptions):
        documents.append(description)
        metadatas.append(
            {
                "action": json.dumps(info["action"]),
                "action_name": info["action"]["name"],
                "trajectory_id": info["traj_idx"],
                "action_index": info["action_idx"],
            }
        )
        ids.append(f"traj_{info['traj_idx']}_action_{info['action_idx']}")

    return documents, metadatas, ids


async def build_action_memory_async(
    output_collection_name="action_memory",
    max_trajectories=None,
    max_concurrency=10,
    env_name="airline",
):
    """
    Build ChromaDB collection from trajectory data using async processing.

    Args:
        output_collection_name: Name for the ChromaDB collection
        max_trajectories: Maximum number of trajectories to process (None = all)
        max_concurrency: Maximum number of concurrent LLM calls
        env_name: Environment name ('airline' or 'retail')
    """
    # Load trajectory data from imported tasks
    print(f"Loading trajectories for {env_name} environment...")

    # Select tasks based on environment
    if env_name == "airline":
        tasks = AIRLINE_TASKS
    elif env_name == "retail":
        tasks = RETAIL_TASKS
    else:
        raise ValueError(f"Unknown environment: {env_name}")

    # Convert Task objects to trajectory format
    trajectories = []
    for task in tasks:
        trajectories.append(
            {
                "user_id": task.user_id,
                "actions": [{"name": a.name, "kwargs": a.kwargs} for a in task.actions],
                "instruction": task.instruction,
                "outputs": task.outputs if hasattr(task, "outputs") else [],
            }
        )

    if max_trajectories:
        trajectories = trajectories[:max_trajectories]
        print(f"Loaded {len(trajectories)} trajectories (subset for testing)")
    else:
        print(f"Loaded {len(trajectories)} trajectories")

    # Process all actions in parallel
    documents, metadatas, ids = await process_all_actions(
        trajectories, max_concurrency, env_name
    )

    # Create ChromaDB client and collection (persistent)
    print("\nCreating ChromaDB collection...")
    script_dir = Path(__file__).parent
    db_path = script_dir / f"chroma_db_{env_name}"
    client = chromadb.PersistentClient(path=str(db_path))

    # Delete existing collection if it exists
    try:
        client.delete_collection(output_collection_name)
        print(f"Deleted existing collection '{output_collection_name}'")
    except Exception:
        pass

    collection = client.create_collection(
        name=output_collection_name,
        metadata={
            "description": "Action memory - maps natural language descriptions to tool calls"
        },
    )

    # Add all entries to ChromaDB
    print(f"\nAdding {len(documents)} actions to ChromaDB...")
    collection.add(documents=documents, metadatas=metadatas, ids=ids)

    print(f"\n✓ Successfully created collection '{output_collection_name}'")
    print(f"✓ Total actions stored: {len(documents)}")
    print(f"✓ Collection contains {collection.count()} items")

    # Show some statistics
    action_types = {}
    for metadata in metadatas:
        action_name = metadata["action_name"]
        action_types[action_name] = action_types.get(action_name, 0) + 1

    print("\nAction type distribution:")
    for action_name in sorted(action_types.keys()):
        print(f"  {action_name}: {action_types[action_name]} instances")

    return collection


def build_action_memory(
    output_collection_name="action_memory",
    max_trajectories=None,
    max_concurrency=10,
    env_name="airline",
):
    """
    Synchronous wrapper for build_action_memory_async.
    """
    return asyncio.run(
        build_action_memory_async(
            output_collection_name, max_trajectories, max_concurrency, env_name
        )
    )


def test_retrieval(collection, query, n_results=3):
    """
    Test retrieval from the collection.

    Args:
        collection: ChromaDB collection
        query: Natural language query
        n_results: Number of results to return
    """
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    results = collection.query(query_texts=[query], n_results=n_results)

    for idx, (doc, metadata) in enumerate(
        zip(results["documents"][0], results["metadatas"][0]), 1
    ):
        print(f"\n--- Result {idx} ---")
        print(f"Description: {doc}")
        print(f"Action name: {metadata['action_name']}")

        action = json.loads(metadata["action"])
        print("\nAction details:")
        print(json.dumps(action, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build action memory database from tau-bench trajectories"
    )
    parser.add_argument(
        "--env",
        type=str,
        choices=["airline", "retail"],
        default="airline",
        help="Environment to build memory for (default: airline)",
    )
    parser.add_argument(
        "--max-trajectories",
        type=int,
        default=None,
        help="Maximum number of trajectories to process (default: all)",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=10,
        help="Maximum number of concurrent LLM calls (default: 10)",
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default=None,
        help="Name for the ChromaDB collection (default: action_memory_{env})",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running test queries after building the database",
    )

    args = parser.parse_args()

    # Determine collection name
    collection_name = args.collection_name or f"action_memory_{args.env}"

    # Build the action memory
    collection = build_action_memory(
        output_collection_name=collection_name,
        max_trajectories=args.max_trajectories,
        max_concurrency=args.max_concurrency,
        env_name=args.env,
    )

    # Test with some example queries
    if not args.skip_tests:
        print("\n" + "=" * 80)
        print("TESTING RETRIEVAL")
        print("=" * 80)

        if args.env == "airline":
            test_retrieval(collection, "Add baggage to my reservation", n_results=2)
            test_retrieval(collection, "Cancel a reservation", n_results=2)
            test_retrieval(collection, "Book a flight with gift card", n_results=2)
        elif args.env == "retail":
            test_retrieval(collection, "Modify my order address", n_results=2)
            test_retrieval(collection, "Cancel my pending order", n_results=2)
            test_retrieval(collection, "Change item in my order", n_results=2)
