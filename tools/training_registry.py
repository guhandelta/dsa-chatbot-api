"""CLI tool to inspect the RAG chatbot's trained technologies, languages,
frameworks, and training event audit log.

Usage:
  python tools/training_registry.py
  python tools/training_registry.py --json
  python tools/training_registry.py --history
"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.training_registry import (
    get_training_history,
    get_training_registry,
    get_trained_technologies,
)


def print_report():
    reg = get_training_registry()
    summary = reg["summary"]
    vs = summary["vector_store"]

    print("=" * 72)
    print(" RAG CHATBOT — TRAINED TECHNOLOGIES & KNOWLEDGE REGISTRY")
    print("=" * 72)
    print(f"Total Technologies Trained : {summary['total_technologies_trained']}")
    print(f"Total Knowledge Records    : {summary['total_knowledge_records']:,}")
    print(f"Total Retrievable Chunks   : {summary['total_retrievable_chunks']:,}")
    print(f"Vector Store Backend       : {vs.get('backend', 'unknown')} ({vs.get('status', 'unknown')})")
    print(f"Total Vectors Indexed      : {vs.get('vector_count', 0):,}")
    print(f"Embedding Provider         : {summary.get('embedding_provider', 'unknown')}")
    print(f"Last Trained At            : {summary.get('last_trained_at', 'unknown')}")
    print("-" * 72)

    # Group by category
    categories: dict[str, list] = {}
    for t in reg["technologies"]:
        cat = t["category"].replace("_", " ").title()
        categories.setdefault(cat, []).append(t)

    for cat_name, items in sorted(categories.items()):
        print(f"\n[{cat_name}] ({len(items)} technologies)")
        print(f"  {'Technology':<32} {'Total Records':<15} {'Retrievable Chunks':<20}")
        print(f"  {'-'*30:<32} {'-'*13:<15} {'-'*18:<20}")
        for item in sorted(items, key=lambda x: -x["total_records"]):
            name = item["display_name"]
            if len(name) > 30:
                name = name[:27] + "..."
            print(f"  {name:<32} {item['total_records']:<15} {item['retrievable_records']:<20}")

    print("\n" + "=" * 72)
    print(" RECENT INGESTION & TRAINING AUDIT LOG")
    print("=" * 72)
    events = reg.get("recent_training_events", [])
    if not events:
        print("  (No training events recorded yet)")
    else:
        for evt in events[:5]:
            ts = evt.get("timestamp", "unknown")
            tech = evt.get("technology", "unknown")
            action = evt.get("action", "unknown")
            records = evt.get("record_count", 0)
            print(f"  [{ts}] {tech.upper()} | action: {action} | records: {records} | status: {evt.get('status')}")
    print("=" * 72 + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Output full registry as JSON")
    parser.add_argument("--history", action="store_true", help="Output training audit history as JSON")
    parser.add_argument("--technologies", action="store_true", help="Output list of trained technologies as JSON")
    args = parser.parse_args()

    if args.json:
        print(json.dumps(get_training_registry(), indent=2))
    elif args.history:
        print(json.dumps(get_training_history(), indent=2))
    elif args.technologies:
        print(json.dumps(get_trained_technologies(), indent=2))
    else:
        print_report()


if __name__ == "__main__":
    main()
