"""Promote a passed candidate JSONL batch into the app's local reference corpus."""
import json
import sys
from pathlib import Path

API = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API))
from evaluate_reference_batch import evaluate

LIBRARY = API / "data/reference_library"


def library_row(row):
    """Batch candidates carry provenance in metadata (the evaluator reads it
    there); library records keep it top-level so metadata stays scalar."""
    row = json.loads(json.dumps(row))
    sources = row["metadata"].pop("provenance", [])
    merged = []
    for url in list(row.get("provenance", [])) + list(sources):
        if url not in merged:
            merged.append(url)
    row["provenance"] = merged
    return row


def promote(batch_path: Path):
    batch_path = batch_path.resolve()
    result = evaluate(batch_path, allow_existing_ids=True)
    if not result["passed"]:
        raise SystemExit("Batch evaluation failed; refusing promotion: " + "; ".join(result["errors"]))
    records_path = LIBRARY / "records.jsonl"
    batch_rows = [library_row(json.loads(line)) for line in batch_path.open(encoding="utf-8") if line.strip()]
    existing_ids = {json.loads(line)["id"] for line in records_path.open(encoding="utf-8") if line.strip()}
    rows_by_id = {json.loads(line)["id"]: json.loads(line) for line in records_path.open(encoding="utf-8") if line.strip()}
    collisions = [row for row in batch_rows if row["id"] in existing_ids and rows_by_id[row["id"]] != row]
    if collisions:
        raise SystemExit("A batch ID exists with different content; refusing promotion")
    new_rows = [row for row in batch_rows if row["id"] not in existing_ids]
    if new_rows:
        with records_path.open("a", encoding="utf-8") as out:
            for row in new_rows:
                out.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    from app.services.reference_library import eligible
    all_rows = [json.loads(line) for line in records_path.open(encoding="utf-8") if line.strip()]
    manifest_path = LIBRARY / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    from collections import Counter
    by_subject = Counter(row["metadata"]["subject"] for row in all_rows)
    manifest["record_count"] = len(all_rows)
    manifest["retrievable_count"] = sum(eligible(row) for row in all_rows)
    manifest["by_subject"] = dict(sorted(by_subject.items()))
    batch_status = {
        "name": batch_path.name, "count": len(batch_rows), "evaluation": "passed",
        "integration": "packaged-reference-library-lexical-retrieval",
        "embedding_rebuild": "not-run",
    }
    batches = manifest.setdefault("generated_batches", [])
    if batch_status not in batches:
        batches.append(batch_status)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    result.update({"promoted": True, "newly_appended": len(new_rows), "library_record_count": len(all_rows),
                   "library_retrievable_count": manifest["retrievable_count"],
                   "library_subject_counts": {s: by_subject[s] for s in sorted({r['metadata']['subject'] for r in batch_rows})},
                   "integration": "packaged-reference-library-lexical-retrieval",
                   "embedding_rebuild": "not-run"})
    report = batch_path.with_suffix(".evaluation.json")
    report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(promote(Path(sys.argv[1])), indent=2, ensure_ascii=False))
