from dataclasses import dataclass
from typing import List, Dict, Any
import chromadb
import numpy as np
from config import COLLECTION_NAME, VECTOR_DB_DIR

# @dataclass is a decorator that automatically creates common methods for a class.
# Without @dataclass, you have to write constructors yourself.
@dataclass
class Chunk:
    id: int
    text: str
    source: str
    page: int
    section: str
    chunk_index: int


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
        self.collection = None

    # Build and store vectors
    def build(self, chunks: List[Chunk], vectors: np.ndarray):
        try:
            self.client.delete_collection(COLLECTION_NAME)
        except:
            pass
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

        ids = [str(chunk.id) for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        embeddings = vectors.tolist()

        metadatas = [
            {
                "source": chunk.source,
                "page": chunk.page,
                "section": chunk.section,
                "chunk_index": chunk.chunk_index,
            }

            for chunk in chunks
        ]

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )


    # ChromaDB saves automatically
    def save(self):
        if self.collection is None:
            raise RuntimeError("No collection found.")

    # Load existing collection
    def load(self):
        try:
            self.collection = self.client.get_collection(COLLECTION_NAME)
        except:
            raise FileNotFoundError(
                "Vector database not found. Run ingest.py first."
            )



    # Search similar chunks
    def search(self, query_vector: np.ndarray, top_k: int = 4) -> List[Dict[str, Any]]:
        if self.collection is None:
            self.load()

        result = self.collection.query(
            query_embeddings=query_vector.reshape(1, -1).tolist(),
            # tolist() converts a NumPy array into a normal Python list.
            # ChromaDB expects embeddings as a Python list, not a NumPy array.
            n_results=top_k,
        )

        output = []

        ids = result["ids"][0]
        docs = result["documents"][0]
        metas = result["metadatas"][0]
        distances = result["distances"][0]


        for doc, meta, distance in zip(docs, metas, distances):
            output.append(
                {
                    "text": doc,
                    "source": meta["source"],
                    "page": meta["page"],
                    "section": meta["section"],
                    "chunk_index": meta["chunk_index"],
                    "score": 1 - distance,
                }
            )

        return output