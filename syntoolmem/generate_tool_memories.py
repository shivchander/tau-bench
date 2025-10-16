"""
Generate tool memory database from tau-bench airline tools and policies.

For each tool and each of its arguments, create synthetic scenarios where:
- Happy path: Valid user query that satisfies policy → tool call
- Adversarial path: Plausible query that violates policy → refusal

Uses async processing for parallel LLM calls with configurable concurrency.
"""

import asyncio
import json
import os
import argparse
import random
import importlib
from pathlib import Path
from openai import AsyncOpenAI
import chromadb
from tqdm import tqdm
from dotenv import load_dotenv
from jinja2 import Template

from syntoolmem.tool_policy_mapping import TOOL_POLICY_MAPPING

# Load environment variables
load_dotenv()

# Initialize async OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_tools():
    """
    Dynamically load all tool classes from tau_bench/envs/airline/tools.

    Returns:
        dict: {tool_name: tool_schema}
    """
    tools = {}
    tools_dir = Path("tau_bench/envs/airline/tools")

    # List all Python files except __init__.py
    tool_files = [f for f in tools_dir.glob("*.py") if f.name != "__init__.py"]

    for tool_file in tool_files:
        module_name = f"tau_bench.envs.airline.tools.{tool_file.stem}"
        try:
            module = importlib.import_module(module_name)
            # Find the Tool class in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and hasattr(attr, "get_info")
                    and attr_name != "Tool"
                ):
                    tool_info = attr.get_info()
                    tool_name = tool_info["function"]["name"]
                    tools[tool_name] = tool_info
                    break
        except Exception as e:
            print(f"Warning: Could not load tool from {tool_file}: {e}")

    return tools


def extract_tool_arguments(tool_schema):
    """
    Extract all argument names from a tool schema.

    Args:
        tool_schema: Tool schema dictionary from get_info()

    Returns:
        list: List of argument names (required + optional)
    """
    parameters = tool_schema["function"]["parameters"]
    properties = parameters.get("properties", {})
    return list(properties.keys())


def build_tool_arg_pairs(tools, max_tools=None):
    """
    Build list of (tool_name, argument_name) pairs.

    Args:
        tools: Dictionary of tool schemas
        max_tools: Optional limit on number of tools to process

    Returns:
        list: [(tool_name, arg_name), ...]
    """
    pairs = []
    tool_names = list(tools.keys())

    if max_tools:
        tool_names = tool_names[:max_tools]

    for tool_name in tool_names:
        tool_schema = tools[tool_name]
        arguments = extract_tool_arguments(tool_schema)
        for arg_name in arguments:
            pairs.append((tool_name, arg_name))

    return pairs


def load_user_data():
    """Load users and reservations from JSON files."""
    data_dir = Path("tau_bench/envs/airline/data")

    with open(data_dir / "users.json", "r") as f:
        users = json.load(f)

    with open(data_dir / "reservations.json", "r") as f:
        reservations = json.load(f)

    return users, reservations


def sample_user_and_reservations(users, reservations):
    """
    Randomly sample a user and their reservations.

    Args:
        users: Dictionary of all users
        reservations: Dictionary of all reservations

    Returns:
        tuple: (user_profile_dict, user_reservations_list)
    """
    # Sample random user
    user_id = random.choice(list(users.keys()))
    user_profile = users[user_id]

    # Get user's reservations
    user_reservation_ids = user_profile.get("reservations", [])
    user_reservations = [
        reservations[res_id]
        for res_id in user_reservation_ids
        if res_id in reservations
    ]

    return user_profile, user_reservations


async def generate_scenario(
    tool_name,
    tool_schema,
    focused_arg,
    policy_text,
    template,
    users,
    reservations,
    semaphore,
):
    """
    Generate one happy+adversarial scenario using GPT-4o.

    Args:
        tool_name: Name of the tool
        tool_schema: Full tool schema from get_info()
        focused_arg: The specific argument to focus scenarios on
        policy_text: Relevant policy section
        template: Jinja2 template for prompt
        users: All users data
        reservations: All reservations data
        semaphore: Asyncio semaphore for concurrency control

    Returns:
        dict: {happy_path: {...}, adversarial_path: {...}, metadata: {...}}
    """
    # Sample user and reservations
    user_profile, user_reservations = sample_user_and_reservations(users, reservations)

    # Render template
    prompt = template.render(
        user_profile=json.dumps(user_profile, indent=2),
        reservations=json.dumps(user_reservations, indent=2),
        tool=json.dumps(tool_schema, indent=2),
        policy=policy_text,
        focused_argument=focused_arg,
    )

    async with semaphore:
        try:
            response = await openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)

            # Add metadata
            result["metadata"] = {
                "tool_name": tool_name,
                "focused_argument": focused_arg,
                "user_id": user_profile.get("user_id", "unknown"),
            }

            return result

        except Exception as e:
            print(f"\nError generating scenario for {tool_name}.{focused_arg}: {e}")
            # Return empty scenario on error
            return {
                "happy_path": None,
                "adversarial_path": None,
                "metadata": {
                    "tool_name": tool_name,
                    "focused_argument": focused_arg,
                    "error": str(e),
                },
            }


async def process_all_scenarios(
    tool_arg_pairs,
    tools,
    users,
    reservations,
    scenarios_per_arg=3,
    max_concurrency=10,
):
    """
    Process all (tool, arg) pairs with multiple scenarios each.

    Args:
        tool_arg_pairs: List of (tool_name, arg_name) tuples
        tools: Dictionary of tool schemas
        users: All users data
        reservations: All reservations data
        scenarios_per_arg: Number of scenarios to generate per argument
        max_concurrency: Maximum concurrent LLM calls

    Returns:
        list: List of scenario dictionaries
    """
    # Load Jinja2 template
    template_path = Path("syntoolmem/prompts/memory_generator.j2")
    with open(template_path, "r") as f:
        template = Template(f.read())

    semaphore = asyncio.Semaphore(max_concurrency)
    tasks = []

    # Create tasks for all scenarios
    for tool_name, arg_name in tool_arg_pairs:
        tool_schema = tools[tool_name]
        policy_text = TOOL_POLICY_MAPPING.get(
            tool_name, "No specific policy found for this tool."
        )

        for scenario_idx in range(scenarios_per_arg):
            tasks.append(
                generate_scenario(
                    tool_name,
                    tool_schema,
                    arg_name,
                    policy_text,
                    template,
                    users,
                    reservations,
                    semaphore,
                )
            )

    # Execute all tasks with progress bar
    print(
        f"\nGenerating {len(tasks)} scenarios with max_concurrency={max_concurrency}..."
    )

    with tqdm(total=len(tasks), desc="Generating scenarios") as pbar:
        async def task_with_progress(task):
            result = await task
            pbar.update(1)
            return result

        scenarios = await asyncio.gather(*[task_with_progress(t) for t in tasks])

    return scenarios


async def build_tool_memory_async(
    collection_name="tool_memory_airline",
    max_tools=None,
    scenarios_per_arg=3,
    max_concurrency=10,
):
    """
    Build ChromaDB collection from tool schemas and policies.

    Args:
        collection_name: Name for the ChromaDB collection
        max_tools: Maximum number of tools to process (None = all)
        scenarios_per_arg: Number of scenarios per argument
        max_concurrency: Maximum concurrent LLM calls

    Returns:
        ChromaDB collection
    """
    # Load tools and data
    print("Loading tools...")
    tools = load_tools()
    print(f"Loaded {len(tools)} tools")

    print("Loading user and reservation data...")
    users, reservations = load_user_data()
    print(f"Loaded {len(users)} users and {len(reservations)} reservations")

    # Build tool-argument pairs
    tool_arg_pairs = build_tool_arg_pairs(tools, max_tools)
    print(f"Processing {len(tool_arg_pairs)} (tool, argument) pairs")

    # Generate all scenarios
    scenarios = await process_all_scenarios(
        tool_arg_pairs,
        tools,
        users,
        reservations,
        scenarios_per_arg,
        max_concurrency,
    )

    # Prepare ChromaDB entries
    documents = []
    metadatas = []
    ids = []

    for scenario_idx, scenario in enumerate(scenarios):
        if scenario.get("happy_path") and scenario["happy_path"]:
            # Happy path entry
            happy = scenario["happy_path"]
            documents.append(happy["user_utterance"])
            metadatas.append({
                "tool_call": json.dumps(happy["output"]),
                "policy_reasoning": happy["policy_checklist"],
                "path_type": "happy",
                "tool_name": scenario["metadata"]["tool_name"],
                "focused_argument": scenario["metadata"]["focused_argument"],
            })
            ids.append(f"{scenario['metadata']['tool_name']}_{scenario['metadata']['focused_argument']}_{scenario_idx}_happy")

        if scenario.get("adversarial_path") and scenario["adversarial_path"]:
            # Adversarial path entry
            adv = scenario["adversarial_path"]
            documents.append(adv["user_utterance"])
            metadatas.append({
                "tool_call": "null",  # No tool call in adversarial path
                "policy_reasoning": adv["policy_checklist"],
                "path_type": "adversarial",
                "tool_name": scenario["metadata"]["tool_name"],
                "focused_argument": scenario["metadata"]["focused_argument"],
                "refusal_message": adv["output"]["content"],
            })
            ids.append(f"{scenario['metadata']['tool_name']}_{scenario['metadata']['focused_argument']}_{scenario_idx}_adversarial")

    # Create ChromaDB collection
    print("\nCreating ChromaDB collection...")
    script_dir = Path(__file__).parent
    db_path = script_dir / "chroma_db_tool_memories"
    client = chromadb.PersistentClient(path=str(db_path))

    # Delete existing collection if it exists
    try:
        client.delete_collection(collection_name)
        print(f"Deleted existing collection '{collection_name}'")
    except Exception:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={
            "description": "Tool memory - synthetic scenarios for tool calls and policy compliance"
        },
    )

    # Add all entries to ChromaDB
    print(f"\nAdding {len(documents)} entries to ChromaDB...")
    collection.add(documents=documents, metadatas=metadatas, ids=ids)

    print(f"\n✓ Successfully created collection '{collection_name}'")
    print(f"✓ Total entries stored: {len(documents)}")
    print(f"✓ Collection contains {collection.count()} items")

    # Show statistics
    tool_counts = {}
    path_type_counts = {"happy": 0, "adversarial": 0}

    for metadata in metadatas:
        tool_name = metadata["tool_name"]
        path_type = metadata["path_type"]
        tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
        path_type_counts[path_type] += 1

    print("\nTool distribution:")
    for tool_name in sorted(tool_counts.keys()):
        print(f"  {tool_name}: {tool_counts[tool_name]} scenarios")

    print(f"\nPath type distribution:")
    print(f"  Happy paths: {path_type_counts['happy']}")
    print(f"  Adversarial paths: {path_type_counts['adversarial']}")

    return collection


def build_tool_memory(
    collection_name="tool_memory_airline",
    max_tools=None,
    scenarios_per_arg=3,
    max_concurrency=10,
):
    """Synchronous wrapper for build_tool_memory_async."""
    return asyncio.run(
        build_tool_memory_async(
            collection_name, max_tools, scenarios_per_arg, max_concurrency
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
        print(f"User utterance: {doc}")
        print(f"Tool: {metadata['tool_name']}")
        print(f"Focused argument: {metadata['focused_argument']}")
        print(f"Path type: {metadata['path_type']}")
        print(f"\nPolicy reasoning:\n{metadata['policy_reasoning']}")

        if metadata['path_type'] == 'happy':
            print(f"\nTool call:")
            print(json.dumps(json.loads(metadata['tool_call']), indent=2))
        else:
            print(f"\nRefusal message: {metadata.get('refusal_message', 'N/A')}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate tool memory database from airline tools and policies"
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="tool_memory_airline",
        help="Name for the ChromaDB collection (default: tool_memory_airline)",
    )
    parser.add_argument(
        "--max-tools",
        type=int,
        default=None,
        help="Maximum number of tools to process (default: all)",
    )
    parser.add_argument(
        "--scenarios-per-arg",
        type=int,
        default=3,
        help="Number of scenarios to generate per argument (default: 3)",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=10,
        help="Maximum number of concurrent LLM calls (default: 10)",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running test queries after building the database",
    )

    args = parser.parse_args()

    # Build the tool memory
    collection = build_tool_memory(
        collection_name=args.collection_name,
        max_tools=args.max_tools,
        scenarios_per_arg=args.scenarios_per_arg,
        max_concurrency=args.max_concurrency,
    )

    # Test with some example queries
    if not args.skip_tests:
        print("\n" + "=" * 80)
        print("TESTING RETRIEVAL")
        print("=" * 80)

        test_retrieval(collection, "I need to cancel my flight reservation", n_results=2)
        test_retrieval(collection, "Can I add more baggage to my booking?", n_results=2)
        test_retrieval(collection, "I want to change my flight to a different date", n_results=2)
