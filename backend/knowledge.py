"""Turns the files in data/ into plain text the LLM can read."""

from pathlib import Path

from docx import Document  # from the python-docx package
from pypdf import PdfReader


def _read_docx(path: Path) -> str:
    doc = Document(str(path))
    lines = [p.text for p in doc.paragraphs]
    # Resumes often put content in tables, so read table cells too.
    for table in doc.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                lines.append(" | ".join(cells))
    return "\n".join(line for line in lines if line.strip())


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# Which reader function to use for each file extension.
READERS = {".docx": _read_docx, ".pdf": _read_pdf, ".md": _read_text}


def load_knowledge(data_dir: Path) -> str:
    """Read every supported file in data_dir and join them into one block of text.

    Each file gets a header with its name, so the LLM knows where each fact came from.
    """
    sections = []
    for path in sorted(data_dir.iterdir()):
        reader = READERS.get(path.suffix.lower())
        # Skip unsupported files and Word's temporary "~$" lock files.
        if reader is None or path.name.startswith("~$"):
            continue
        text = reader(path).strip()
        if text:
            sections.append(f"=== {path.name} ===\n{text}")

    if not sections:
        raise RuntimeError(f"No readable .docx, .pdf or .md files found in {data_dir}")
    return "\n\n".join(sections)
