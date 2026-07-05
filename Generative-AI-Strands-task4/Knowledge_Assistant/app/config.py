
# app/config.py
# --------------
# Central configuration for the Knowledge Assistant. All paths, model IDs,
# and tunable parameters live here so nothing is hard-coded elsewhere.
# Values can be overridden via environment variables / a .env file
# (see .env.example).

import os

from dotenv import load_dotenv

load_dotenv()  # loads .env if present; no-op otherwise

# ---------------------------------------------------------------------
# Paths ---------------------------------------------------------------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # KnowledgeAssistant/
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
VECTOR_DB_DIR = os.path.join(ROOT_DIR, "vector_db")  # ChromaDB persistent storage folder
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "knowledge_base")

# ---------------------------------------------------------------------
# AWS / Bedrock -------------------------------------------------------
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")

EMBED_MODEL_ID = os.environ.get("EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
EMBED_DIM = int(os.environ.get("EMBED_DIM", "1024"))  # Titan v2 supports 256 / 512 / 1024

AGENT_MODEL_ID = os.environ.get("AGENT_MODEL_ID", "global.anthropic.claude-sonnet-4-6")
AGENT_TEMPERATURE = float(os.environ.get("AGENT_TEMPERATURE", "0.2"))

# ---------------------------------------------------------------------
# Chunking / retrieval-------------------------------------------------

CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "800"))       
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "150"))  
DEFAULT_TOP_K = int(os.environ.get("DEFAULT_TOP_K", "4"))
MAX_RETRIEVAL_ATTEMPTS = int(os.environ.get("MAX_RETRIEVAL_ATTEMPTS", "3"))

SYSTEM_PROMPT = """\

You are the Knowledge Assistant, an agentic RAG assistant that answers \
questions using ONLY the documents in the knowledge base.

Rules you must follow on every turn:
1. Always call the `retrieve_knowledge` tool at least once before \
answering a factual question about the document set. Never answer from \
general knowledge alone.
2. Read the retrieved chunks and judge whether they are enough to fully \
answer the question. If they are not - because the results are off-topic, \
too shallow, or only partially relevant - call `retrieve_knowledge` again \
with a refined or narrower query. You may retrieve up to {max_attempts} \
times per question.
3. If, after retrying, you still cannot find relevant material, tell the \
user plainly that the knowledge base does not contain the answer. Do NOT \
guess or fall back on outside knowledge.
4. When you do answer, ground every claim in the retrieved chunks and cite \
all available metadata for each claim, including the source file, page, \
and section whenever present, e.g. \
"(source: guide.pdf, page 3, section: Overview)".
5. Keep answers concise and directly responsive to the question.
""".format(max_attempts=MAX_RETRIEVAL_ATTEMPTS)