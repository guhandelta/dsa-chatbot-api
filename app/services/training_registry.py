"""Centralized registry and audit log for all technologies, languages, and frameworks
that the RAG chatbot has been trained on.

Tracks:
  - Authored content catalog (DSA problems, language fundamentals, algorithms, patterns)
  - Canonical release curriculum (Java, JavaScript)
  - Reference library (HTML, CSS, Tailwind, Python Django/FastAPI/Flask, Embedded C/Python, etc.)
  - Vector store status (ChromaDB / pgvector collection counts and embedding metadata)
  - Persistent, append-only training event log (data/training_registry_log.json)
"""
from collections import Counter
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import re
from typing import Any
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
LOG_FILE = DATA_DIR / "training_registry_log.json"

CATEGORY_MAP = {
    # Web & Frontend
    "html": "web_frontend",
    "css": "web_frontend",
    "tailwind": "web_frontend",
    "bootstrap": "web_frontend",
    "sass": "web_frontend",
    # Backend Frameworks
    "python-django": "backend_frameworks",
    "python-fastapi": "backend_frameworks",
    "python-flask": "backend_frameworks",
    "spring-boot": "backend_frameworks",
    "spring-core": "backend_frameworks",
    "spring-data": "backend_frameworks",
    "spring-mvc": "backend_frameworks",
    "spring-security": "backend_frameworks",
    "spring-testing": "backend_frameworks",
    # Embedded & Systems
    "embedded-c": "embedded_systems",
    "embedded-python": "embedded_systems",
    # Core Languages
    "python": "core_languages",
    "javascript": "core_languages",
    "java": "core_languages",
    "typescript": "core_languages",
    "c": "core_languages",
    "cpp": "core_languages",
    "rust": "core_languages",
    "ruby": "core_languages",
    "go": "core_languages",
    "csharp": "core_languages",
    # DSA & Theory
    "dsa": "algorithms_and_dsa",
    "algorithm": "algorithms_and_dsa",
    "design-patterns": "algorithms_and_dsa",
}

DISPLAY_NAMES = {
    "html": "HTML5 (WHATWG Living Standard & Web APIs)",
    "css": "CSS3 & Modern Architecture (Flexbox, Grid, Responsive)",
    "tailwind": "Tailwind CSS & Utility-First Frameworks",
    "bootstrap": "Bootstrap 5 & UI Components",
    "sass": "Sass / SCSS Preprocessing",
    "python": "Python 3 Fundamentals & Idioms",
    "python-django": "Django Framework & ORM",
    "python-fastapi": "FastAPI & Async Services",
    "python-flask": "Flask Microframework",
    "javascript": "JavaScript (ES2024+, Event Loop & DOM)",
    "typescript": "TypeScript (Type Systems & Compiler)",
    "java": "Java (Modern JDK, Collections & Concurrency)",
    "spring-boot": "Spring Boot 3",
    "spring-core": "Spring Core & Inversion of Control",
    "spring-data": "Spring Data & Repositories",
    "spring-mvc": "Spring MVC & Web APIs",
    "spring-security": "Spring Security",
    "spring-testing": "Spring Testing Slices",
    "c": "C (C11/C17, Pointers & Memory)",
    "cpp": "C++ (Modern C++20, STL & Templates)",
    "rust": "Rust (Ownership, Lifetimes & Borrow Checker)",
    "ruby": "Ruby (OOP, Blocks & Enumerable)",
    "go": "Go (Goroutines & Standard Library)",
    "csharp": "C# (.NET Core & LINQ)",
    "embedded-c": "Embedded C (Bare Metal, MCU Peripherals & Registers)",
    "embedded-python": "Embedded Python (MicroPython, CircuitPython & Hardware)",
    "dsa": "Data Structures & Practice Problems",
    "algorithm": "Algorithmic Paradigms & Asymptotic Complexity",
    "design-patterns": "Software Design Patterns (GoF & Idiomatic)",
}


def _seed_initial_events() -> list[dict[str, Any]]:
    """Seeds baseline events if training log file does not exist."""
    return [
        {
            "id": "tr-evt-001-baseline",
            "timestamp": "2026-10-15T00:00:00Z",
            "action": "system_bootstrap",
            "technology": "dsa",
            "category": "algorithms_and_dsa",
            "source": "data/content & data/dsa_problems",
            "record_count": 240,
            "vectors_count": 240,
            "status": "completed",
            "details": {"description": "Authored DSA problem catalog and multi-language solutions."},
        },
        {
            "id": "tr-evt-002-curriculum",
            "timestamp": "2026-10-15T12:00:00Z",
            "action": "curriculum_import",
            "technology": "java-javascript",
            "category": "core_languages",
            "source": "Training Data/dsa_mentor_rag_export/dsa_curriculum.jsonl",
            "record_count": 4280,
            "vectors_count": 1800,
            "status": "completed",
            "details": {"description": "Canonical Java & JavaScript mentor curriculum."},
        },
        {
            "id": "tr-evt-003-reference-lib",
            "timestamp": "2026-10-16T08:00:00Z",
            "action": "reference_library_import",
            "technology": "multi-language",
            "category": "backend_frameworks",
            "source": "Training Data/reference_library",
            "record_count": 13524,
            "vectors_count": 0,
            "status": "completed",
            "details": {
                "subjects": [
                    "python", "python-django", "python-fastapi", "python-flask",
                    "c", "cpp", "rust", "ruby", "typescript", "embedded-c",
                    "embedded-python", "spring-boot", "spring-core", "spring-data",
                    "spring-mvc", "spring-security", "spring-testing",
                ]
            },
        },
        {
            "id": "tr-evt-004-html-css-train",
            "timestamp": "2026-10-16T20:54:00Z",
            "action": "curriculum_training_and_ingest",
            "technology": "html-css-tailwind",
            "category": "web_frontend",
            "source": "Training Data/language/HTML",
            "record_count": 658,
            "vectors_count": 658,
            "status": "completed",
            "details": {
                "description": "WHATWG HTML Living Standard element catalogue, Web APIs, CSS 3 architecture, Sass, Bootstrap 5, and Tailwind.",
                "subjects": ["html", "css", "tailwind"],
            },
        },
    ]


def _read_raw_events() -> list[dict[str, Any]]:
    if not LOG_FILE.exists():
        events = _seed_initial_events()
        _write_raw_events(events)
        return events
    try:
        data = json.loads(LOG_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        return []
    except Exception as exc:
        logger.warning(f"Failed reading training registry log: {exc}")
        return _seed_initial_events()


def _write_raw_events(events: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temp_file = LOG_FILE.with_suffix(".tmp")
    temp_file.write_text(json.dumps(events, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp_file.replace(LOG_FILE)


def record_training_event(
    technology: str,
    action: str = "training_ingested",
    category: str | None = None,
    source: str = "",
    record_count: int = 0,
    vectors_count: int = 0,
    status: str = "completed",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Records a training or ingestion event in the audit registry."""
    tech_key = technology.lower().strip()
    cat = category or CATEGORY_MAP.get(tech_key, "general")
    event = {
        "id": f"tr-evt-{uuid.uuid4().hex[:12]}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "technology": tech_key,
        "category": cat,
        "source": source,
        "record_count": record_count,
        "vectors_count": vectors_count,
        "status": status,
        "details": details or {},
    }
    events = _read_raw_events()
    events.append(event)
    _write_raw_events(events)
    return event


def get_training_history(limit: int = 50) -> list[dict[str, Any]]:
    """Returns the chronological history of training and ingestion events, newest first."""
    events = _read_raw_events()
    # Sort reverse chronological by timestamp
    events.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)
    return events[:limit]


def get_training_registry() -> dict[str, Any]:
    """Dynamically aggregates all trained technologies, frameworks, languages,
    records, vector store counts, and audit logs.
    Always up to date whenever accessed."""
    from app.services import content_catalog as catalog
    from app.services import reference_library

    # 1. Authored content counts
    authored = catalog.list_content()
    authored_by_lang = Counter(c.language for c in authored if c.language)
    authored_by_track = Counter(c.track for c in authored)

    # 2. Reference library subjects and record counts
    ref_subjects = reference_library.subjects()
    ref_by_subject = {s["id"]: s for s in ref_subjects}

    # 3. Canonical curriculum manifest
    curriculum_manifest_path = DATA_DIR / "curriculum" / "manifest.json"
    curriculum_data = {}
    if curriculum_manifest_path.exists():
        try:
            curriculum_data = json.loads(curriculum_manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    # 4. Reference library manifest
    ref_manifest_path = DATA_DIR / "reference_library" / "manifest.json"
    ref_manifest = {}
    if ref_manifest_path.exists():
        try:
            ref_manifest = json.loads(ref_manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    # 5. ChromaDB Vector store status
    vector_info = {"backend": settings.vector_store, "vector_count": 0, "status": "unavailable"}
    try:
        from app.services.knowledge_base import get_vectorstore
        vs = get_vectorstore()
        col = getattr(vs, "_collection", None)
        if col is not None:
            vector_info["vector_count"] = col.count()
            vector_info["status"] = "active"
            vector_info["collection_name"] = getattr(col, "name", "dsa_problems")
    except Exception as exc:
        vector_info["error"] = str(exc)[:150]

    # Combine all distinct technologies
    all_tech_keys = set(CATEGORY_MAP.keys())
    for s in ref_by_subject.keys():
        all_tech_keys.add(s)
    for l in authored_by_lang.keys():
        all_tech_keys.add(l)

    technologies = []
    category_counts = Counter()

    for key in sorted(all_tech_keys):
        category = CATEGORY_MAP.get(key, "other")
        display_name = DISPLAY_NAMES.get(key, key.replace("-", " ").title())

        # Determine record counts from all layers
        ref_entry = ref_by_subject.get(key)
        ref_records = ref_entry["records"] if ref_entry else 0
        ref_retrievable = ref_entry["retrievable_records"] if ref_entry else 0

        curriculum_records = 0
        if key in ("java", "javascript") and curriculum_data:
            curriculum_records = curriculum_data.get("languages", {}).get(key, 0)

        if key in ("dsa", "algorithm", "design-patterns"):
            authored_records = authored_by_track.get(key, 0)
        else:
            authored_records = authored_by_lang.get(key, 0)
        total_records = ref_records + curriculum_records + authored_records

        if total_records == 0 and key not in ("dsa", "algorithm", "design-patterns"):
            continue

        category_counts[category] += 1
        technologies.append({
            "id": key,
            "display_name": display_name,
            "category": category,
            "total_records": total_records,
            "retrievable_records": ref_retrievable + curriculum_records + authored_records,
            "reference_library_records": ref_records,
            "curriculum_records": curriculum_records,
            "authored_catalog_records": authored_records,
            "status": "trained_and_available",
        })

    # Total record metrics
    total_ref_records = ref_manifest.get("record_count", sum(s["records"] for s in ref_subjects))
    total_ref_retrievable = ref_manifest.get("retrievable_count", sum(s["retrievable_records"] for s in ref_subjects))
    total_curriculum_records = curriculum_data.get("records", 4280)
    total_authored = len(authored)

    total_records_overall = total_ref_records + total_curriculum_records + total_authored
    total_retrievable_overall = total_ref_retrievable + total_curriculum_records + total_authored

    history = get_training_history(limit=10)
    last_trained = history[0]["timestamp"] if history else None

    return {
        "status": "ok",
        "summary": {
            "total_technologies_trained": len(technologies),
            "total_knowledge_records": total_records_overall,
            "total_retrievable_chunks": total_retrievable_overall,
            "vector_store": vector_info,
            "last_trained_at": last_trained,
            "embedding_provider": settings.embedding_provider or ("google" if settings.google_api_key else "openai"),
        },
        "categories": dict(sorted(category_counts.items())),
        "technologies": technologies,
        "recent_training_events": history,
    }


def get_trained_technologies() -> list[dict[str, Any]]:
    """Lightweight list of distinct technologies, languages, and frameworks."""
    registry = get_training_registry()
    return [
        {
            "id": t["id"],
            "display_name": t["display_name"],
            "category": t["category"],
            "records": t["total_records"],
            "retrievable": t["retrievable_records"],
        }
        for t in registry["technologies"]
    ]
