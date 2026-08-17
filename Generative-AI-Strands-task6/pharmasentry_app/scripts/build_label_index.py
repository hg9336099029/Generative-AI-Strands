#!/usr/bin/env python
"""
Build the BM25 label index from the curated label corpus.

Usage:
    python scripts/build_label_index.py

The script reads every .txt file under data/labels/ (or a single file if
specified), splits the text into overlapping chunks, and writes a JSON index
to data/index/label_index.json that label_search.py can load at runtime.

Scoped products for this capstone: lisinopril, metformin, sertraline.
We use the existing app/Lisinopril.txt file as the initial corpus.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Add project root to path so we can import app modules if needed
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

LABEL_DIR = ROOT / "app" / "labels"
INDEX_DIR = ROOT / "data" / "index"
INDEX_PATH = INDEX_DIR / "label_index.json"

# Fallback: also look for the single Lisinopril.txt in app/
FALLBACK_FILES = [
    ROOT / "app" / "Lisinopril.txt",
]

CHUNK_SIZE = 400   # characters per chunk
CHUNK_OVERLAP = 80  # overlap between consecutive chunks


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        start += size - overlap
    return [c for c in chunks if c]


def infer_product(filename: str) -> str:
    """Derive a product name from the file stem (lowercase)."""
    stem = Path(filename).stem.lower()
    # Normalise known variants
    aliases = {
        "lisinopril": "lisinopril",
        "metformin": "metformin",
        "sertraline": "sertraline",
        "zoloft": "sertraline",
        "glucophage": "metformin",
        "prinivil": "lisinopril",
        "zestril": "lisinopril",
    }
    return aliases.get(stem, stem)


def infer_section(chunk_text_lower: str) -> str:
    """Best-effort section label based on keywords in the chunk."""
    section_keywords = {
        "boxed_warning": ["boxed warning", "black box"],
        "contraindications": ["contraindication"],
        "warnings": ["warning", "precaution"],
        "adverse_reactions": ["adverse reaction", "side effect", "undesirable effect"],
        "drug_interactions": ["drug interaction", "concomitant"],
        "dosage_and_administration": ["dosage", "administration", "dose"],
        "indications_and_usage": ["indication", "indicated for", "used to treat"],
    }
    for section, keywords in section_keywords.items():
        if any(kw in chunk_text_lower for kw in keywords):
            return section
    return "general"


def build_index() -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    source_files: list[Path] = []

    # Look in data/labels/
    if LABEL_DIR.exists():
        source_files.extend(LABEL_DIR.glob("*.txt"))

    # Fallback: app/Lisinopril.txt
    for f in FALLBACK_FILES:
        if f.exists() and f not in source_files:
            source_files.append(f)

    if not source_files:
        print("No label files found. Add .txt files to data/labels/ or app/.")
        return

    chunks: list[dict] = []
    chunk_id = 0

    for filepath in source_files:
        product = infer_product(filepath.name)
        text = filepath.read_text(encoding="utf-8", errors="replace")
        text_chunks = chunk_text(text)
        for chunk in text_chunks:
            section = infer_section(chunk.lower())
            chunks.append(
                {
                    "chunk_id": f"{product}-{chunk_id:04d}",
                    "product": product,
                    "section": section,
                    "text": chunk,
                    "source_file": filepath.name,
                }
            )
            chunk_id += 1

    payload = {"chunks": chunks, "total_chunks": len(chunks)}
    INDEX_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Built index with {len(chunks)} chunks from {len(source_files)} file(s).")
    print(f"Index written to: {INDEX_PATH}")

    # Summary by product
    by_product: dict[str, int] = {}
    for c in chunks:
        by_product[c["product"]] = by_product.get(c["product"], 0) + 1
    for prod, count in sorted(by_product.items()):
        print(f"  {prod}: {count} chunks")


if __name__ == "__main__":
    build_index()
