"""
Inspect the action memory database created by build_action_memory.py
"""

import chromadb
import json
from pathlib import Path
from pprint import pprint

# Connect to ChromaDB (persistent)
script_dir = Path(__file__).parent
db_path = script_dir / "chroma_db"
client = chromadb.PersistentClient(path=str(db_path))

# Get the collection
try:
    collection = client.get_collection("action_memory")
except:
    print("Collection 'action_memory' not found. Run build_action_memory.py first.")
    exit(1)

print("=" * 80)
print("ACTION MEMORY INSPECTION")
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

queries = [
    "I want to modify my economy class reservation",
    "Cancel my flight",
    "Add baggage with gift card",
    "Book a business class flight",
    "Update flight dates"
]

for query in queries:
    print(f"\nQuery: '{query}'")
    results = collection.query(query_texts=[query], n_results=2)

    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        action_name = metadata['action_name']
        print(doc)
        print(metadata)
