# Parses uploaded documents (.txt, .md, .pdf, .docx, .doc) into plain text
# for ingestion into the Chroma/pgvector knowledge base.
import io
import re
from pathlib import Path


def parse_text_or_markdown(content: bytes) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return content.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return content.decode("utf-8", errors="replace")


def parse_docx(content: bytes) -> str:
    # 1. Try python-docx if installed
    try:
        import docx

        doc = docx.Document(io.BytesIO(content))
        paragraphs = [p.text for p in doc.paragraphs if p.text]
        for table in doc.tables:
            for row in table.rows:
                row_text = " ".join(c.text.strip() for c in row.cells if c.text.strip())
                if row_text:
                    paragraphs.append(row_text)
        if paragraphs:
            return "\n\n".join(paragraphs)
    except Exception:
        pass

    # 2. Native ZIP + XML parse (standard library, zero dependencies).
    # Match <w:t> runs exactly (a bare endswith("t") also catches
    # <w:instrText> field codes) and keep paragraph breaks for the splitter.
    try:
        import xml.etree.ElementTree as ET
        import zipfile

        w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            tree = ET.fromstring(z.read("word/document.xml"))
        paras = []
        for p in tree.iter(f"{w}p"):
            line = "".join(t.text or "" for t in p.iter(f"{w}t"))
            if line.strip():
                paras.append(line)
        return "\n\n".join(paras)
    except Exception:
        return ""


def parse_pdf(content: bytes) -> str:
    # No byte-scraping fallback: PDF text lives in compressed streams, so
    # scraping printable runs indexes operators and binary noise instead of
    # prose. Better to reject than to poison retrieval.
    try:
        import pypdf
    except ImportError:
        raise ValueError("PDF support requires the 'pypdf' package (pip install -r requirements.txt).")

    reader = pypdf.PdfReader(io.BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(p.strip() for p in pages if p.strip())


def parse_doc(content: bytes) -> str:
    # Many modern .doc files are actually .docx or RTF
    text = parse_docx(content)
    if text.strip():
        return text

    # Fallback: extract ASCII / printable sequences
    pattern = rb"[\x20-\x7E\t\n\r]{4,}"
    matches = re.findall(pattern, content)
    return "\n".join(m.decode("latin-1", errors="ignore") for m in matches)


ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".doc"}


def extract_text_from_file(filename: str, content: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file format '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}"
        )

    if ext in (".txt", ".md"):
        return parse_text_or_markdown(content)
    elif ext == ".pdf":
        return parse_pdf(content)
    elif ext == ".docx":
        return parse_docx(content)
    elif ext == ".doc":
        return parse_doc(content)
    else:
        return parse_text_or_markdown(content)
