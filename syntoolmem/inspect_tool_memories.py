"""
Inspect the tool memory database created by generate_tool_memories.py
"""

import chromadb
import json
import argparse
from pathlib import Path
from collections import defaultdict

# Parse command line arguments
parser = argparse.ArgumentParser(description="Inspect tool memory database")
parser.add_argument(
    "--collection-name",
    type=str,
    default="tool_memory_airline",
    help="Collection name to inspect (default: tool_memory_airline)"
)
parser.add_argument(
    "--group-by",
    type=str,
    choices=["tool", "argument", "path"],
    default="tool",
    help="How to group results: by tool, argument, or path type (default: tool)"
)
parser.add_argument(
    "--show-details",
    action="store_true",
    help="Show full details for each entry (can be verbose)"
)
args = parser.parse_args()

# Connect to ChromaDB (persistent)
script_dir = Path(__file__).parent
db_path = script_dir / "chroma_db_tool_memories"
client = chromadb.PersistentClient(path=str(db_path))

# Get the collection
try:
    collection = client.get_collection(args.collection_name)
except:
    print(f"Collection '{args.collection_name}' not found in {db_path}.")
    print(f"Run: uv run python -m syntoolmem.generate_tool_memories")
    exit(1)

print("=" * 80)
print(f"TOOL MEMORY INSPECTION")
print(f"Collection: {args.collection_name}")
print("=" * 80)

# Get collection stats
count = collection.count()
print(f"\nTotal entries: {count}")

# Get all items
result = collection.get()

# Count stats
tool_counts = defaultdict(int)
path_type_counts = defaultdict(int)
arg_counts = defaultdict(int)

for metadata in result['metadatas']:
    tool_counts[metadata['tool_name']] += 1
    path_type_counts[metadata['path_type']] += 1
    arg_counts[metadata['focused_argument']] += 1

print(f"\n{'='*80}")
print("STATISTICS")
print(f"{'='*80}")

print(f"\nPath Type Distribution:")
print(f"  Happy paths: {path_type_counts['happy']}")
print(f"  Adversarial paths: {path_type_counts['adversarial']}")

print(f"\nTool Distribution:")
for tool in sorted(tool_counts.keys()):
    print(f"  {tool}: {tool_counts[tool]} scenarios")

print(f"\nTop 10 Most Common Arguments:")
for arg, count in sorted(arg_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {arg}: {count} scenarios")

# Group entries based on user preference
print(f"\n{'='*80}")
print(f"ENTRIES GROUPED BY {args.group_by.upper()}")
print(f"{'='*80}")

if args.group_by == "tool":
    groups = defaultdict(list)
    for doc_id, document, metadata in zip(result['ids'], result['documents'], result['metadatas']):
        groups[metadata['tool_name']].append({
            'id': doc_id,
            'utterance': document,
            'metadata': metadata
        })

    for tool_name in sorted(groups.keys()):
        entries = groups[tool_name]
        print(f"\n{'='*80}")
        print(f"TOOL: {tool_name} ({len(entries)} scenarios)")
        print(f"{'='*80}")

        # Show happy vs adversarial breakdown
        happy = sum(1 for e in entries if e['metadata']['path_type'] == 'happy')
        adv = sum(1 for e in entries if e['metadata']['path_type'] == 'adversarial')
        print(f"  Happy: {happy} | Adversarial: {adv}")

        if args.show_details:
            for idx, entry in enumerate(entries[:5], 1):  # Show first 5
                print(f"\n  [{idx}] {entry['metadata']['path_type'].upper()}")
                print(f"      Argument: {entry['metadata']['focused_argument']}")
                print(f"      Utterance: {entry['utterance'][:100]}...")

elif args.group_by == "argument":
    groups = defaultdict(list)
    for doc_id, document, metadata in zip(result['ids'], result['documents'], result['metadatas']):
        groups[metadata['focused_argument']].append({
            'id': doc_id,
            'utterance': document,
            'metadata': metadata
        })

    for arg_name in sorted(groups.keys()):
        entries = groups[arg_name]
        print(f"\n{'='*80}")
        print(f"ARGUMENT: {arg_name} ({len(entries)} scenarios)")
        print(f"{'='*80}")

        # Show tool breakdown
        tools = defaultdict(int)
        for e in entries:
            tools[e['metadata']['tool_name']] += 1
        print(f"  Tools: {', '.join(f'{t}({c})' for t, c in tools.items())}")

elif args.group_by == "path":
    for path_type in ['happy', 'adversarial']:
        entries = [
            {
                'id': doc_id,
                'utterance': document,
                'metadata': metadata
            }
            for doc_id, document, metadata in zip(result['ids'], result['documents'], result['metadatas'])
            if metadata['path_type'] == path_type
        ]

        print(f"\n{'='*80}")
        print(f"PATH TYPE: {path_type.upper()} ({len(entries)} scenarios)")
        print(f"{'='*80}")

        if args.show_details:
            for idx, entry in enumerate(entries[:5], 1):  # Show first 5
                print(f"\n  [{idx}] Tool: {entry['metadata']['tool_name']}")
                print(f"      Argument: {entry['metadata']['focused_argument']}")
                print(f"      Utterance: {entry['utterance'][:100]}...")
                print(f"      Policy reasoning: {entry['metadata']['policy_reasoning'][:150]}...")

# Test queries
print(f"\n{'='*80}")
print("TESTING QUERIES")
print(f"{'='*80}")

queries = [
    "I need to cancel my flight reservation",
    "Can I add more baggage to my booking?",
    "I want to change my flight to a different date",
    "How do I get a refund for my cancelled flight?",
    "Can I modify the passengers on my reservation?"
]

for query in queries:
    print(f"\n{'='*80}")
    print(f"Query: '{query}'")
    print(f"{'='*80}")

    # Fetch top 2 happy paths
    happy_results = collection.query(
        query_texts=[query],
        n_results=2,
        where={"path_type": "happy"}
    )

    # Fetch top 2 adversarial paths
    adversarial_results = collection.query(
        query_texts=[query],
        n_results=2,
        where={"path_type": "adversarial"}
    )

    # Display happy paths
    print(f"\n🟢 TOP 2 HAPPY PATHS (Policy-Compliant)")
    print("-" * 80)

    for idx, (doc, metadata) in enumerate(zip(happy_results['documents'][0], happy_results['metadatas'][0]), 1):
        print(f"\n--- Happy Path {idx} ---")
        print(f"Tool: {metadata['tool_name']}")
        print(f"Argument: {metadata['focused_argument']}")
        print(f"User utterance: {doc}")

        if args.show_details:
            print(f"\nPolicy reasoning:")
            print(f"  {metadata['policy_reasoning'][:200]}...")

            if metadata['tool_call'] != 'null':
                try:
                    tool_call = json.loads(metadata['tool_call'])
                    print(f"\nTool call:")
                    print(f"  {json.dumps(tool_call, indent=2)[:300]}...")
                except:
                    pass

    # Display adversarial paths
    print(f"\n🔴 TOP 2 ADVERSARIAL PATHS (Policy Violations)")
    print("-" * 80)

    for idx, (doc, metadata) in enumerate(zip(adversarial_results['documents'][0], adversarial_results['metadatas'][0]), 1):
        print(f"\n--- Adversarial Path {idx} ---")
        print(f"Tool: {metadata['tool_name']}")
        print(f"Argument: {metadata['focused_argument']}")
        print(f"User utterance: {doc}")

        if args.show_details:
            print(f"\nPolicy reasoning:")
            print(f"  {metadata['policy_reasoning'][:200]}...")

            print(f"\nRefusal: {metadata.get('refusal_message', 'N/A')[:150]}...")

print(f"\n{'='*80}")
print("INSPECTION COMPLETE")
print(f"{'='*80}")
print(f"\nTo see full details, run with --show-details flag")
print(f"To group differently, use --group-by [tool|argument|path]")
