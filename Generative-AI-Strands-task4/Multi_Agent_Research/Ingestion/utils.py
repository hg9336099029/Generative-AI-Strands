import re
from dataclasses import dataclass
from typing import List, Tuple
from pypdf import PdfReader


@dataclass
class PageText:
    page_number: int  # 1-indexed; 0 for non-paginated formats (.md/.txt)
    text: str


def read_pdf(path: str) -> List[PageText]:
    """Extract text from a PDF, one entry per page."""
    reader = PdfReader(path)

    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        # strip remove whitespaces from begining and end
        if text.strip():
            pages.append(PageText(page_number=i, text=text))
    return pages


def read_text_file(path: str) -> List[PageText]:
    """Read a plain .md/.txt file as a single 'page' (page_number=0)."""
    with open(path, "r", encoding="utf-8") as f:
        return [PageText(page_number=0, text=f.read())]


def load_file(path: str) -> List[PageText]:
    """Dispatch to the right reader based on file extension."""
    lower = path.lower()
    if lower.endswith(".pdf"):
        return read_pdf(path)
    
    if lower.endswith((".md", ".txt")):
        return read_text_file(path)
    
    raise ValueError(f"Unsupported file type: {path}")


def guess_section(chunk: str) -> str:
    # Best-effort section label: nearest markdown heading in the chunk,
    # if any (PDFs won't have markdown headings, so this is usually empty
    # for them and metadata falls back to the page number instead).
    
    headings = re.findall(r"^#{1,6}\s+(.*)$", chunk, flags=re.MULTILINE)
    return headings[0] if headings else ""


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:

    # Sliding-window character chunker with overlap. Tries not to cut
    # mid-sentence by extending to the next newline within a small window.

    chunks, start, text = [], 0, text.strip()
    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end < len(text):
            next_break = text.find("\n", end)
            if next_break != -1 and next_break - end < 200:
                end = next_break

        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def chunk_pages(pages: List[PageText], chunk_size: int = 800, overlap: int = 150) -> List[Tuple[str, int]]:

    # Chunk each page independently so page numbers stay attached to
    # the right chunk. Returns (chunk_text, page_number) pairs.
    result = []
    for page in pages:
        for piece in chunk_text(page.text, chunk_size, overlap):
            result.append((piece, page.page_number))
    return result