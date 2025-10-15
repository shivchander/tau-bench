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

# Load environment variables
load_dotenv()

# Initialize async OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_action_description(action, semaphore):
    """
    Use LLM to generate a natural language description of what an action does.

    Args:
        action: Dictionary with 'name' and 'kwargs' keys
        semaphore: Asyncio semaphore for concurrency control

    Returns:
        String description of the action
    """
    prompt = f"""Given this flight reservation system action, generate a clear, natural language description (1-2 sentences) of what it does.

Action:
{json.dumps(action, indent=2)}

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


async def process_all_actions(trajectories, max_concurrency):
    """
    Process all actions from trajectories in parallel.

    Args:
        trajectories: List of trajectory dictionaries
        max_concurrency: Maximum number of concurrent LLM calls

    Returns:
        Tuple of (documents, metadatas, ids)
    """
    semaphore = asyncio.Semaphore(max_concurrency)

    # Collect all actions with their metadata
    tasks = []
    action_info = []

    for traj_idx, trajectory in enumerate(trajectories):
        for action_idx, action in enumerate(trajectory["actions"]):
            tasks.append(generate_action_description(action, semaphore))
            action_info.append({
                "action": action,
                "traj_idx": traj_idx,
                "action_idx": action_idx
            })

    # Process all actions concurrently with progress bar
    print(f"\nGenerating descriptions for {len(tasks)} actions with max_concurrency={max_concurrency}...")

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
        metadatas.append({
            "action": json.dumps(info["action"]),
            "action_name": info["action"]["name"],
            "trajectory_id": info["traj_idx"],
            "action_index": info["action_idx"]
        })
        ids.append(f"traj_{info['traj_idx']}_action_{info['action_idx']}")

    return documents, metadatas, ids


async def build_action_memory_async(
    json_path,
    output_collection_name="action_memory",
    max_trajectories=None,
    max_concurrency=10
):
    """
    Build ChromaDB collection from trajectory data using async processing.

    Args:
        json_path: Path to validated_tasks_medium_with_instructions.json
        output_collection_name: Name for the ChromaDB collection
        max_trajectories: Maximum number of trajectories to process (None = all)
        max_concurrency: Maximum number of concurrent LLM calls
    """
    # Load trajectory data
    print(f"Loading trajectories from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        trajectories = json.load(f)

    if max_trajectories:
        trajectories = trajectories[:max_trajectories]
        print(f"Loaded {len(trajectories)} trajectories (subset for testing)")
    else:
        print(f"Loaded {len(trajectories)} trajectories")

    # Process all actions in parallel
    documents, metadatas, ids = await process_all_actions(trajectories, max_concurrency)

    # Create ChromaDB client and collection (persistent)
    print("\nCreating ChromaDB collection...")
    script_dir = Path(__file__).parent
    db_path = script_dir / "chroma_db"
    client = chromadb.PersistentClient(path=str(db_path))

    # Delete existing collection if it exists
    try:
        client.delete_collection(output_collection_name)
        print(f"Deleted existing collection '{output_collection_name}'")
    except Exception:
        pass

    collection = client.create_collection(
        name=output_collection_name,
        metadata={"description": "Action memory - maps natural language descriptions to tool calls"}
    )

    # Add all entries to ChromaDB
    print(f"\nAdding {len(documents)} actions to ChromaDB...")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

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


def build_action_memory(json_path, output_collection_name="action_memory", max_trajectories=None, max_concurrency=10):
    """
    Synchronous wrapper for build_action_memory_async.
    """
    return asyncio.run(build_action_memory_async(
        json_path,
        output_collection_name,
        max_trajectories,
        max_concurrency
    ))


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

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    for idx, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        print(f"\n--- Result {idx} ---")
        print(f"Description: {doc}")
        print(f"Action name: {metadata['action_name']}")

        action = json.loads(metadata['action'])
        print("\nAction details:")
        print(json.dumps(action, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build action memory database from tau-bench trajectories")
    parser.add_argument(
        "--max-trajectories",
        type=int,
        default=None,
        help="Maximum number of trajectories to process (default: all)"
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=10,
        help="Maximum number of concurrent LLM calls (default: 10)"
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="action_memory",
        help="Name for the ChromaDB collection (default: action_memory)"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running test queries after building the database"
    )

    args = parser.parse_args()

    # Path to the trajectory data
    script_dir = Path(__file__).parent
    json_path = script_dir / "../tau_bench/sdg/validated_tasks_medium_with_instructions.json"

    # Build the action memory
    collection = build_action_memory(
        json_path,
        output_collection_name=args.collection_name,
        max_trajectories=args.max_trajectories,
        max_concurrency=args.max_concurrency
    )

    # Test with some example queries
    if not args.skip_tests:
        print("\n" + "=" * 80)
        print("TESTING RETRIEVAL")
        print("=" * 80)

        test_retrieval(collection, "Add baggage to my reservation", n_results=2)
        test_retrieval(collection, "Cancel a reservation", n_results=2)
        test_retrieval(collection, "Book a flight with gift card", n_results=2)
