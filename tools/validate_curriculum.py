"""Validate dsa_curriculum.jsonl before ingestion. Works for any number of languages.

Usage: python validate_jsonl.py dsa_curriculum.jsonl
Exit code 1 on errors. Checks: unique ids, scalar-only metadata, required fields per kind,
canonical lenses, links that resolve inside the same language, no prerequisite cycles, every
exercise attached to a concept, answers never placed in the embedded text, and document length.
"""
import collections, json, sys
from pathlib import Path

LENSES = {"mental-model", "creation", "access", "mutation", "insertion-and-deletion", "iteration", "equality",
          "ordering", "transformation", "complexity", "edge-cases", "fit-and-alternatives", "patterns", "testing"}
CONCEPT = ["id", "kind", "language", "concept_family", "data_structure", "lens", "level", "concept", "prerequisites",
           "misconception", "explanation", "example_bad", "example_good", "complexity", "related_problems",
           "follow_up", "verified"]
EXERCISE = ["id", "kind", "language", "concept_id", "data_structure", "format", "level", "modes", "prompt",
            "answer", "grading"]
META_ALWAYS = ["source", "kind", "language", "data_structure", "doc", "doc_url", "contains_answer"]
KINDS = {"concept", "exercise", "reference", "lens", "gotcha", "curriculum", "exercise_format"}
MAX_TOKENS = 600  # rough: characters / 3.6


def main(path):
    errors, warnings = [], []
    recs = [json.loads(line) for line in open(path, encoding="utf-8")]
    ids = collections.Counter(r["id"] for r in recs)
    errors += [f"duplicate id {i}" for i, n in ids.items() if n > 1]
    chunks = {r["id"]: r for r in recs if r["metadata"]["source"] == "chunk"}
    for r in recs:
        m, rid = r["metadata"], r["id"]
        for k in META_ALWAYS:
            if k not in m:
                errors.append(f"{rid}: metadata missing {k}")
        for k, v in m.items():
            if not isinstance(v, (str, int, float, bool)):
                errors.append(f"{rid}: metadata {k} is {type(v).__name__}, must be a scalar")
        if m.get("kind") not in KINDS:
            errors.append(f"{rid}: unknown kind {m.get('kind')}")
        if not r["document"].strip():
            errors.append(f"{rid}: empty document")
        if len(r["document"]) / 3.6 > MAX_TOKENS:
            warnings.append(f"{rid}: about {len(r['document']) / 3.6:.0f} tokens; small embedding models will truncate it")
        if m["source"] != "chunk":
            continue
        p = r["payload"]
        need = CONCEPT if p.get("kind") == "concept" else EXERCISE
        missing = [f for f in need if f not in p]
        if missing:
            errors.append(f"{rid}: payload missing {missing}")
        if p.get("kind") == "concept" and p.get("lens") not in LENSES:
            errors.append(f"{rid}: lens {p.get('lens')} is not canonical")
        ans = str(p.get("answer", "")).strip()
        if p.get("kind") == "exercise" and len(ans) >= 8 and ans in r["document"]:  # short answers can echo the prompt
            errors.append(f"{rid}: the answer appears in the embedded text")
        for t in list(p.get("prerequisites") or []) + [p.get("follow_up"), p.get("concept_id")]:
            if not t:
                continue
            if t not in chunks:
                errors.append(f"{rid}: links to missing chunk {t}")
            elif chunks[t]["metadata"]["language"] != m["language"]:
                errors.append(f"{rid}: links across languages to {t}")
        if p.get("kind") == "exercise" and p.get("concept_id") in chunks and chunks[p["concept_id"]]["payload"]["kind"] != "concept":
            errors.append(f"{rid}: concept_id {p['concept_id']} is not a concept")

    state = {}
    def visit(n, path):
        if state.get(n) == 1:
            errors.append("prerequisite cycle: " + " -> ".join(path + [n])); return
        if state.get(n) == 2 or n not in chunks: return
        state[n] = 1
        for q in chunks[n]["payload"].get("prerequisites") or []:
            visit(q, path + [n])
        state[n] = 2
    for n in chunks:
        visit(n, [])

    kinds = collections.Counter((r["metadata"]["language"], r["metadata"]["kind"]) for r in recs)
    print(f"{len(recs)} records")
    for (lang, kind), n in sorted(kinds.items()):
        print(f"  {lang:<11} {kind:<16} {n}")
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print("OK" if not errors else f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parents[1] / "data/curriculum/java-javascript.jsonl")))
