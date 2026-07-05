# app/ingestion.py
# -----------------
# Orchestrates the ingestion pipeline: read every file in docs/ (PDF, .md,
# .txt), chunk it, embed the chunks, and build/save the FAISS index via
# app.vector_store. This is what ingest.py (the CLI entrypoint) calls.

import os
from typing import List

from .config import CHUNK_OVERLAP, CHUNK_SIZE, DOCS_DIR
from .embeddings import embed_batch
from .utils import chunk_pages, guess_section, load_file
from .vector_store import Chunk, VectorStore

SUPPORTED_EXTENSIONS = (".pdf", ".md", ".txt")

def discover_documents(docs_dir: str = DOCS_DIR) -> List[str]:

    """Return full paths to every supported file in docs_dir."""

    if not os.path.isdir(docs_dir):
        raise SystemExit(f"docs folder not found: {docs_dir}")
    
    files = [
        os.path.join(docs_dir, f)
        for f in sorted(os.listdir(docs_dir))
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
    ]
    if not files:
        raise SystemExit(f"No .pdf/.md/.txt files found in {docs_dir}")
    return files


def build_index(docs_dir: str = DOCS_DIR,chunk_size: int = CHUNK_SIZE,overlap: int = CHUNK_OVERLAP,) -> None:
    # Full ingestion pipeline: load -> chunk -> embed -> index -> save.

    file_paths = discover_documents(docs_dir)

    all_chunks: List[Chunk] = []
    all_texts: List[str] = []
    chunk_id = 0

    for path in file_paths:

        fname = os.path.basename(path)
        pages = load_file(path)
        page_chunks = chunk_pages(pages, chunk_size=chunk_size, overlap=overlap)

        for i, (piece, page_number) in enumerate(page_chunks):
            all_chunks.append(Chunk(id=chunk_id,text=piece,source=fname,page=page_number,section=guess_section(piece),chunk_index=i,))
            all_texts.append(piece)
            chunk_id += 1

        print(f"  {fname}: {len(pages)} page(s) -> {len(page_chunks)} chunk(s)")

    print(f"\nTotal: {len(file_paths)} document(s) -> {len(all_chunks)} chunk(s).")
    print("Embedding chunks with Amazon Titan Text Embeddings V2 ...")
    vectors = embed_batch(all_texts)

    store = VectorStore()
    store.build(all_chunks, vectors)
    store.save()
    print(f"Index built and saved to vector_db/ ({len(all_chunks)} vectors).")