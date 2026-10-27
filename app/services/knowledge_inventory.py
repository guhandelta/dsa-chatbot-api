"""Read-only inventory of packaged knowledge sources and their evidence state.

Presence and publication indicate retrieval availability only. This module does
not certify correctness, execution, pedagogical quality, or provenance beyond
the metadata actually stored with each source.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path

from app.services import content_catalog

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _file_record(relative: str, *, rows: int, by_language: dict, by_subject: dict,
                 provenance: str) -> dict:
    path = DATA_DIR / relative
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return {
        "source_id": relative.replace("/", ":"),
        "source_type": "packaged_file",
        "path": relative,
        "content_sha256": digest,
        "record_count": rows,
        "by_language": dict(sorted(by_language.items())),
        "by_subject": dict(sorted(by_subject.items())),
        "provenance": provenance,
        "retrieval_status": "available" if path.is_file() else "missing",
        "publication_review": "not_applicable",
        "executable_examples": "not_recorded",
        "pedagogical_review": "not_recorded",
        "quality_status": "not_certified",
    }


def _jsonl_inventory(relative: str, source_summary: str) -> dict | None:
    path = DATA_DIR / relative
    if not path.is_file():
        return None
    languages, subjects, sources, versions = Counter(), Counter(), Counter(), Counter()
    count = provenance_rows = 0
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            row = json.loads(line)
            metadata = row.get("metadata", {})
            languages[str(metadata.get("language") or "unknown")] += 1
            subjects[str(metadata.get("subject") or metadata.get("language") or "unknown")] += 1
            record_provenance = row.get("provenance") or metadata.get("source")
            if record_provenance:
                provenance_rows += 1
                if isinstance(record_provenance, list):
                    sources.update(str(value) for value in record_provenance if value)
                else:
                    sources[str(record_provenance)] += 1
            version = next((metadata[key] for key in (
                "version", "runtime_version", "rust_edition", "framework_version")
                if metadata.get(key) is not None), "not_recorded")
            versions[str(version)] += 1
            count += 1
    record = _file_record(relative, rows=count, by_language=languages, by_subject=subjects,
                          provenance=source_summary)
    record["provenance_coverage"] = {
        "records_with_provenance": provenance_rows,
        "records_without_provenance": count - provenance_rows,
        "distinct_labels": len(sources),
    }
    # A source row may list multiple origin files. Count rows independently of
    # label count; individual labels stay in the corpus to avoid huge payloads.
    record["by_declared_version"] = dict(versions.most_common(8))
    return record


def _json_inventory(relative: str, provenance: str, rows_key: str) -> dict | None:
    path = DATA_DIR / relative
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload if isinstance(payload, list) else payload.get(rows_key, [])
    if not isinstance(rows, list):
        rows = []
    default_language = payload.get("language", "not_recorded") if isinstance(payload, dict) else "not_recorded"
    languages, subjects = Counter(), Counter()
    for row in rows:
        if not isinstance(row, dict):
            continue
        languages[str(row.get("language") or default_language)] += 1
        subjects[str(row.get("subject") or row.get("track") or rows_key)] += 1
    record = _file_record(relative, rows=len(rows), by_language=languages,
                          by_subject=subjects, provenance=provenance)
    record["declared_version"] = payload.get("version", payload.get("schema_version")) if isinstance(payload, dict) else None
    record["declared_status"] = payload.get("status") if isinstance(payload, dict) else None
    return record


def _authored_inventory() -> dict:
    # The catalog also synthesizes entries from canonical JSONL; keep this
    # source count and digest limited to authored Markdown files only.
    entries = [item for item in content_catalog.list_content() if item.source != "curriculum"]
    languages, subjects, kinds, executable, sources = Counter(), Counter(), Counter(), Counter(), Counter()
    for item in entries:
        language = item.language or "all_languages"
        languages[language] += 1
        subjects[f"{item.track}:{language}"] += 1
        kinds[item.track] += 1
        sources[item.source] += 1
        # Presence of fixtures is not evidence that a run passed.
        executable["fixtures_present" if item.has_tests else "no_fixture_metadata"] += 1
    content_paths = [path for directory in content_catalog._all_dirs()
                     for path in directory.glob("*.md")]
    paths = sorted(set(content_paths))
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(DATA_DIR).as_posix().encode())
        digest.update(path.read_bytes())
    return {
        "source_id": "authored:content-catalog",
        "source_type": "authored_markdown",
        "path": "data/content + data/dsa_problems",
        "content_sha256": digest.hexdigest(),
        "record_count": len(entries),
        "by_language": dict(sorted(languages.items())),
        "by_subject": dict(sorted(subjects.items())),
        "by_track": dict(sorted(kinds.items())),
        "by_recorded_provenance": dict(sorted(sources.items())),
        "fixture_metadata": dict(sorted(executable.items())),
        "provenance": "Repository-authored curriculum and problem files; individual source metadata may identify external origins.",
        "retrieval_status": "available",
        "publication_review": "not_applicable",
        "executable_examples": "fixtures_present_is_not_execution_evidence",
        "pedagogical_review": "not_recorded",
        "quality_status": "not_certified",
    }


def build_inventory() -> dict:
    """Return concise, file-version-bound inventory; never executes source code."""
    sources = [
        _authored_inventory(),
        *[record for record in (
            _jsonl_inventory("curriculum/java-javascript.jsonl",
                             "Packaged canonical Java/JavaScript curriculum; inspect per-record provenance metadata."),
            _jsonl_inventory("curriculum/spring-starter.jsonl",
                             "Packaged Spring starter references; inspect per-record provenance metadata."),
            _jsonl_inventory("reference_library/records.jsonl",
                             "Curated supplemental reference corpus; inspect per-record provenance metadata."),
        ) if record],
        *[record for record in (
            _json_inventory("curriculum/course-outlines.json",
                            "Packaged course/pathway outlines; outline presence does not certify lesson completion.", "courses"),
            _json_inventory("curriculum/debug-challenges.json",
                            "Packaged debug challenge bank; verification status is not inferred from stored code.", "items"),
            _json_inventory("debug/knowledge-base.json",
                            "Packaged debug challenge bank; verification status is not inferred from stored code.", "items"),
            _json_inventory("explain/javascript.json",
                            "Packaged JavaScript explain-path content; pedagogical review is not recorded here.", "units"),
        ) if record],
    ]
    quiz_dir = DATA_DIR / "curriculum" / "quiz"
    if quiz_dir.is_dir():
        for path in sorted(quiz_dir.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                rows = payload if isinstance(payload, list) else payload.get("items", payload.get("questions", []))
                if not isinstance(rows, list):
                    rows = []
                sources.append(_file_record(
                    path.relative_to(DATA_DIR).as_posix(), rows=len(rows),
                    by_language={path.stem: len(rows)}, by_subject={f"quiz:{path.stem}": len(rows)},
                    provenance="Packaged quiz bank; individual answer correctness and review are not certified by inventory."))
            except (OSError, json.JSONDecodeError):
                sources.append(_file_record(
                    path.relative_to(DATA_DIR).as_posix(), rows=0, by_language={}, by_subject={},
                    provenance="Unreadable quiz source; requires repair."))
                sources[-1]["retrieval_status"] = "invalid"
    return {
        "generated_from": "current local data files",
        "semantics": {
            "available": "Source can be considered by its corresponding retrieval/learning path.",
            "published": "Retrieval availability only; not a correctness, execution, or teaching-quality claim.",
            "not_recorded": "No version-bound evidence is stored; this does not mean verified or failed.",
        },
        "sources": sources,
        "limitations": [
            "The inventory is read-only and does not execute examples or call an LLM.",
            "A source digest binds this summary to file content; it is not external provenance or a review signature.",
            "Fixture presence, indexing, and publication do not prove examples passed or explanations are pedagogically sound.",
            "Uploaded sources are reported separately by GET /teach/documents with per-document fingerprints.",
        ],
    }
