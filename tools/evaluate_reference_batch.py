"""Offline quality gate for generated learner reference batches."""
import json
import re
import sys
from pathlib import Path

API = Path(__file__).resolve().parents[1]
LIBRARY = API / "data/reference_library"

# Official documentation, specifications and standards bodies for the languages and
# frameworks the library covers. Secondary sources (Wikipedia, blogs, papers) are excluded.
TRUSTED_PREFIXES = (
    # Go, .NET, Java, web platform, Node.js
    "https://go.dev/", "https://pkg.go.dev/", "https://learn.microsoft.com/", "https://docs.oracle.com/",
    "https://developer.mozilla.org/", "https://nodejs.org/", "https://docs.npmjs.com/",
    "https://html.spec.whatwg.org/", "https://dom.spec.whatwg.org/", "https://www.w3.org/",
    # Python and its frameworks/tools
    "https://docs.python.org/", "https://peps.python.org/", "https://typing.python.org/",
    "https://packaging.python.org/", "https://pip.pypa.io/", "https://docs.pytest.org/",
    "https://mypy.readthedocs.io/", "https://docs.pydantic.dev/", "https://docs.djangoproject.com/",
    "https://fastapi.tiangolo.com/", "https://flask.palletsprojects.com/",
    "https://flask-sqlalchemy.readthedocs.io/",
    # C and C++ (cppreference and CERT are the de facto references; eel.is hosts the C++ draft)
    "https://en.cppreference.com/", "https://isocpp.github.io/", "https://eel.is/c++draft/",
    "https://gcc.gnu.org/", "https://clang.llvm.org/", "https://libcxx.llvm.org/", "https://sourceware.org/",
    "https://wiki.sei.cmu.edu/confluence/display/c/",
    # Rust
    "https://doc.rust-lang.org/", "https://rust-lang.github.io/", "https://docs.rs/",
    # Ruby
    "https://docs.ruby-lang.org/", "https://bundler.io/", "https://guides.rubygems.org/",
    "https://rspec.info/", "https://docs.seattlerb.org/",
    # Deno runtime, its JSR standard library, and the V8 engine team's documentation
    "https://docs.deno.com/", "https://jsr.io/@std/", "https://v8.dev/",
    # TypeScript, Java ecosystem
    "https://www.typescriptlang.org/", "https://docs.spring.io/", "https://docs.jboss.org/hibernate/",
    "https://junit.org/", "https://docs.junit.org/", "https://maven.apache.org/",
    # CSS frameworks and UI libraries
    "https://sass-lang.com/", "https://getbootstrap.com/", "https://tailwindcss.com/", "https://bulma.io/",
    "https://ui.shadcn.com/", "https://www.radix-ui.com/",
    # Embedded
    "https://docs.micropython.org/", "https://docs.circuitpython.org/", "https://learn.adafruit.com/",
    "https://gpiozero.readthedocs.io/", "https://www.raspberrypi.com/documentation/",
    "https://developer.arm.com/", "https://arm-software.github.io/",
)

# A standalone TODO marker ("TODO", "TODO:", "// TODO"), not an identifier such as Go's context.TODO().
PLACEHOLDER_TODO = re.compile(r"(?<![\w.])TODO(?![\w(])")


def evaluate(batch_path: Path, existing_path: Path | None = None, allow_existing_ids: bool = False):
    # Iterate physical LF-delimited lines. str.splitlines() also splits on
    # Unicode separators that can legitimately occur inside JSON strings.
    rows = [json.loads(line) for line in batch_path.open(encoding="utf-8") if line.strip()]
    existing_path = existing_path or LIBRARY / "records.jsonl"
    existing = [json.loads(line) for line in existing_path.open(encoding="utf-8") if line.strip()]
    errors, warnings = [], []
    ids = [r.get("id") for r in rows]
    existing_ids = {r.get("id") for r in existing}
    if len(ids) != len(set(ids)): errors.append("duplicate IDs within batch")
    if existing_ids.intersection(ids) and not allow_existing_ids: errors.append("batch ID already exists in active library")
    texts = set()
    for row in rows:
        meta = row.get("metadata", {})
        rid = row.get("id", "<missing>")
        document = row.get("document", "")
        normalized = re.sub(r"\s+", " ", document).strip().casefold()
        if normalized in texts: errors.append(f"{rid}: duplicate text in batch")
        texts.add(normalized)
        if not document.strip() or len(document) < 500: errors.append(f"{rid}: missing or undersized teaching content")
        for field in ("language", "subject", "kind", "review_status", "origin"):
            if not meta.get(field): errors.append(f"{rid}: missing metadata.{field}")
        if meta.get("kind") not in {"reference", "concept"}: errors.append(f"{rid}: not a retrievable reference/concept")
        if meta.get("contains_answer") is not False: errors.append(f"{rid}: reference must explicitly contain no answer")
        if meta.get("executable") is not False or meta.get("verified") is not False:
            errors.append(f"{rid}: unexecuted generated prose must not claim verified/executable")
        sources = meta.get("provenance", [])
        if not sources or any(not s.startswith(TRUSTED_PREFIXES) for s in sources):
            errors.append(f"{rid}: provenance must point to scoped official documentation")
        if len(document.split()) < 80: errors.append(f"{rid}: fewer than 80 words")
        if PLACEHOLDER_TODO.search(document) or "lorem ipsum" in document.lower(): errors.append(f"{rid}: placeholder content")
        if "not_expert_certified" not in meta.get("review_status", ""):
            warnings.append(f"{rid}: certification status is not explicit")
    if not rows: errors.append("empty batch")
    return {"batch": batch_path.name, "record_count": len(rows), "passed": not errors,
            "errors": errors, "warnings": warnings,
            "checks": ["JSONL/schema", "unique IDs", "nonempty self-contained prose", "reference-safe flags",
                       "official-domain provenance", "honest execution/review status"],
            "limitations": ["No code execution", "No expert claim-by-claim certification", "No LLM-answer quality or vector recall test"]}


if __name__ == "__main__":
    report = evaluate(Path(sys.argv[1]))
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
