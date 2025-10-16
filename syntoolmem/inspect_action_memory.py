"""
Inspect the action memory database created by build_action_memory.py
"""

import chromadb
import json
import argparse
from pathlib import Path
from pprint import pprint

# Parse command line arguments
parser = argparse.ArgumentParser(description="Inspect action memory database")
parser.add_argument(
    "--env",
    type=str,
    choices=["airline", "retail"],
    default="airline",
    help="Environment to inspect (default: airline)"
)
args = parser.parse_args()

# Connect to ChromaDB (persistent)
script_dir = Path(__file__).parent
db_path = script_dir / f"chroma_db_{args.env}"
client = chromadb.PersistentClient(path=str(db_path))

# Get the collection
collection_name = f"action_memory_{args.env}"
try:
    collection = client.get_collection(collection_name)
except:
    print(f"Collection '{collection_name}' not found in {db_path}.")
    print(f"Run: uv run python -m syntoolmem.build_action_memory --env {args.env}")
    exit(1)

print("=" * 80)
print(f"ACTION MEMORY INSPECTION - {args.env.upper()} ENVIRONMENT")
print("=" * 80)

# Get collection stats
count = collection.count()
print(f"\nTotal entries: {count}")

# Get all items
result = collection.get()

print(f"\nShowing all {count} entries:")
print("=" * 80)

# Group by action type
actions_by_type = {}
for i, (doc_id, document, metadata) in enumerate(zip(result['ids'], result['documents'], result['metadatas']), 1):
    action_name = metadata['action_name']
    if action_name not in actions_by_type:
        actions_by_type[action_name] = []

    actions_by_type[action_name].append({
        'id': doc_id,
        'description': document,
        'action': json.loads(metadata['action'])
    })

# Display by action type
for action_name in sorted(actions_by_type.keys()):
    entries = actions_by_type[action_name]
    print(f"\n{'='*80}")
    print(f"ACTION TYPE: {action_name} ({len(entries)} entries)")
    print(f"{'='*80}")

    for idx, entry in enumerate(entries, 1):
        print(f"\n[{idx}] ID: {entry['id']}")
        print(f"    Description: {entry['description']}")
        print(f"    Action kwargs: {json.dumps(entry['action']['kwargs'], indent=6)[:200]}...")
        print()

print("\n" + "=" * 80)
print("TESTING QUERIES")
print("=" * 80)

if args.env == "airline":
    queries = [
        "I want to modify my economy class reservation",
        "Cancel my flight",
        "Add baggage with gift card",
        "Book a business class flight",
        "Update flight dates"
    ]
else:  # retail
    queries = [
        "I want to return items from my order",
        "Cancel my pending order",
        "Modify my order address",
        "Exchange items in my delivered order",
        "Change payment method"
    ]

for query in queries:
    print(f"\n{'='*80}")
    print(f"Query: '{query}'")
    print(f"{'='*80}")

    results = collection.query(query_texts=[query], n_results=2)

    print("\n# Similar Actions from Memory\n")
    print("Here are some relevant action examples from past trajectories:\n")

    for idx, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        action = json.loads(metadata['action'])
        print(f"\n## Example {idx}")
        print(f"Description: {doc}")
        print(f"Action: {action['name']}")
        print(f"Parameters: {json.dumps(action['kwargs'], indent=2)}")
