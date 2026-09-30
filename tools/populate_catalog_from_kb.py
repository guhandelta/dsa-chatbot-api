"""Extracts curated topics from knowledge_base/dsa-knowledge-base.md into
data/content/language/ and data/content/algorithm/ so they appear as
interactive topics in the curriculum tracks.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
KB_FILE = ROOT / "knowledge_base" / "dsa-knowledge-base.md"
LANG_DIR = ROOT / "data" / "content" / "language"
ALGO_DIR = ROOT / "data" / "content" / "algorithm"


def populate():
    if not KB_FILE.is_file():
        print(f"Error: {KB_FILE} not found.")
        return

    LANG_DIR.mkdir(parents=True, exist_ok=True)
    ALGO_DIR.mkdir(parents=True, exist_ok=True)

    text = KB_FILE.read_text(encoding="utf-8")
    sections = text.split("\n### ")

    lang_count = 0
    algo_count = 0

    for s in sections[1:]:
        lines = s.strip().splitlines()
        if not lines:
            continue
        title = lines[0].strip()
        meta_line = next((l for l in lines[1:5] if l.startswith("Meta:")), "")
        m_dict = {}
        if meta_line:
            for pair in meta_line.replace("Meta:", "").split("|"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    m_dict[k.strip()] = v.strip()

        category = m_dict.get("category", "")
        topic = m_dict.get("topic", "")
        languages = m_dict.get("languages", "")

        if not topic:
            continue

        body_lines = [l for l in lines[1:] if not l.startswith("Meta:")]
        body = "\n".join(body_lines).strip()

        if category in ("language-fundamentals", "language-library"):
            lang = languages if languages != "all" else "python"
            target_file = LANG_DIR / f"{topic}.md"
            difficulty = "Easy"
            cat_name = "Fundamentals" if category == "language-fundamentals" else "Library & APIs"
            md_content = f"""---
track: language
difficulty: {difficulty}
language: {lang}
category: {cat_name}
source: authored
io_mode: function
---
# {title} — {difficulty} — {cat_name}

{body}
"""
            target_file.write_text(md_content, encoding="utf-8")
            lang_count += 1

        elif category in ("algorithm", "paradigm", "data-structure"):
            target_file = ALGO_DIR / f"{topic}.md"
            difficulty = "Easy" if category == "data-structure" else ("Hard" if category == "paradigm" else "Medium")
            cat_name = category.replace("-", " ").title()
            algo_tag = topic
            md_content = f"""---
track: algorithm
difficulty: {difficulty}
algorithms: {algo_tag}
category: {cat_name}
source: authored
io_mode: function
---
# {title} — {difficulty} — {cat_name}

{body}
"""
            target_file.write_text(md_content, encoding="utf-8")
            algo_count += 1

    print(f"Successfully generated {lang_count} language topics and {algo_count} algorithm topics.")


if __name__ == "__main__":
    populate()
