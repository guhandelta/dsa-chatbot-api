"""Propose and apply safe scopes for published uploaded knowledge.

Dry-run is the default and never changes the database. Applying updates the
relational language scope and rebuilds only the affected upload vectors.
"""
import argparse
import asyncio
import json
from pathlib import Path

from sqlalchemy import select

from app.db.database import SessionLocal
from app.db.models import KnowledgeDocument
from app.services.knowledge_base import index_uploaded_document, remove_chunks
from app.services.uploaded_knowledge import ALL_LANGUAGES

NEUTRAL = {
    "3sum.md", "reverse-linked-list.md", "coin-change.md", "contains-duplicate.md",
    "combination-sum-iv.md", "container-with-most-water.md", "longest-common-subsequence.md",
    "longest-increasing-subsequence.md", "word-break.md", "search-in-rotated-sorted-array.md",
    "reverse-bits.md", "binary-search.md", "sum-of-two-integers.md", "maximum-subarray.md",
    "maximum-product-subarray.md", "product-of-array-except-self.md", "missing-number.md",
    "counting-bits.md", "find-minimum-in-rotated-sorted-array.md",
    "best-time-to-buy-and-sell-stock.md", "climbing-stairs.md", "number-of-1-bits.md",
    "matrix-and-grid.md",
}

def classify(filename: str) -> tuple[str, str]:
    n = filename.lower()
    base = Path(n).name
    if base in NEUTRAL:
        return ALL_LANGUAGES, "language-neutral DSA material"
    # Resolve names whose language token contains another token (JavaScript
    # contains Java) or whose framework name is otherwise ambiguous.
    if "javascript" in n or "react-native" in n:
        return "javascript", "filename evidence"
    if "typescript" in n:
        return "typescript", "filename evidence"
    if any(x in n for x in ("spring",)):
        return "java", "framework implies Java"
    if any(x in n for x in ("django", "fastapi", "flask")):
        return "python", "framework implies Python"
    rules = [
        ("typescript", ("typescript", "-ts-", "ts-")),
        ("javascript", ("javascript", "react-native", "-js-", "js-")),
        ("php", ("php", "laravel")), ("dart", ("dart", "flutter")),
        ("kotlin", ("kotlin", "android")), ("swift", ("swift",)),
        ("scala", ("scala",)), ("haskell", ("haskell",)),
        ("java", ("java", "spring")), ("csharp", ("csharp", "dotnet", ".net")),
        ("python", ("python", "django", "fastapi", "flask")),
        ("ruby", ("ruby", "rails")), ("go", ("golang", "-go-", "go-")),
        ("rust", ("rust",)), ("cpp", ("cpp", "c++")), ("c", ("-c-", "c-debug")),
        ("html", ("html",)), ("css", ("css", "bootstrap", "tailwind", "bulma", "shadcn")),
    ]
    matches = [lang for lang, needles in rules if any(x in n for x in needles)]
    if len(matches) == 1:
        return matches[0], "filename evidence"
    return ALL_LANGUAGES, "no unambiguous language evidence"

async def build(output: str):
    async with SessionLocal() as session:
        rows = (await session.scalars(select(KnowledgeDocument).where(KnowledgeDocument.status == "published"))).all()
        proposals = []
        for row in rows:
            current = row.language or ""
            # Existing explicit metadata is authoritative. The classifier only
            # proposes values for legacy rows with no scope.
            if current:
                continue
            proposed, reason = classify(row.filename)
            proposals.append({"document_id": row.id, "filename": row.filename,
                              "current_language": None,
                              "proposed_language": proposed, "reason": reason})
    payload = {"version": 1, "proposals": proposals}
    Path(output).write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Wrote {len(proposals)} proposals to {output}")

async def apply(path: str, reindex: bool = False):
    payload = json.loads(Path(path).read_text())
    proposals = payload.get("proposals", [])
    if not isinstance(proposals, list):
        raise SystemExit("Invalid proposals file: expected a proposals array")
    async with SessionLocal() as session:
        for item in proposals:
            row = await session.get(KnowledgeDocument, item["document_id"])
            if not row or row.status != "published":
                continue
            expected = item.get("proposed_language")
            if not expected:
                continue
            # Upload retrieval reconstructs the safe projection from the
            # relational document, so metadata application does not require a
            # paid embedding call. Reindex only when explicitly requested.
            row.language = expected
            if reindex:
                old_ids = json.loads(row.chunk_ids or "[]")
                if old_ids:
                    await asyncio.to_thread(remove_chunks, old_ids)
                new_ids = await asyncio.to_thread(index_uploaded_document, row.id, row.filename, row.text, row.track, row.owner_id, expected)
                row.chunk_ids = json.dumps(new_ids)
        await session.commit()
    print(f"Applied {len(proposals)} proposals")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", default="/tmp/uploaded-knowledge-proposals.json")
    parser.add_argument("--apply")
    parser.add_argument("--reindex", action="store_true", help="also rebuild upload vectors; requires embedding quota")
    args = parser.parse_args()
    if bool(args.dry_run) == bool(args.apply):
        parser.error("choose exactly one of --dry-run or --apply FILE")
    asyncio.run(build(args.output) if args.dry_run else apply(args.apply, args.reindex))

if __name__ == "__main__":
    main()
