# Multi Agent Research

This project is a multi-agent research assistant built with FastAPI, Strands agents, and a Chroma-based vector database. It can ingest documents, create embeddings, retrieve relevant context, and answer questions through a simple API.

## Features

- Ingest documents from a folder into a vector store
- Generate embeddings for retrieval-augmented generation
- Run a multi-agent workflow for planning, research, writing, and critique
- Expose a REST API for question answering

## Project structure

- app.py: FastAPI application entry point
- ingest.py: builds the knowledge index from documents
- agent/: agent implementations for planner, researcher, writer, critic, coordinator, and aggregator
- Ingestion/: document loading, chunking, embedding, and vector store logic
- tools/: retrieval helpers used by the agents
- docs/: source documents for ingestion
- vector_db/: local vector store output

## Setup

1. Create and activate a virtual environment
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies
   ```bash
   pip install -r Requirements.txt
   ```

3. Set the required environment variables
   - AWS_REGION
   - EMBED_MODEL_ID
   - AGENT_MODEL_ID
   - COLLECTION_NAME (optional)

4. Ingest documents
   ```bash
   python ingest.py --docs ./docs
   ```

5. Run the API server
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

## API endpoints

- GET /health: health check
- POST /ask: ask a question and receive an answer

Example:
```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"What does this project do?\"}"
```

## Notes

The app depends on AWS Bedrock-compatible models and a local Chroma vector database. Make sure your environment is configured before running ingestion or the API.
