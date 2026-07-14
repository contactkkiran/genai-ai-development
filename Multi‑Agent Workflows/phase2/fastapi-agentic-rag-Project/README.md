# FastAPI Agentic RAG Project

This project is a Retrieval-Augmented Generation (RAG) application built with FastAPI, LangChain, ChromaDB, and OpenAI.

## Folder structure

- `app/` — Main application code.
  - `main.py` — FastAPI entry point.
  - `database/` — PostgreSQL logging and storage.
  - `rag/` — PDF ingestion and vector store builder.
  - `agent/` — Agent orchestration and PDF retrieval tool.
  - `models/` — Request models.
- `data/` — Document corpus for ingestion (for example, a training manual PDF).
- `chroma_db/` — Persisted vector database.
- `requirements.txt` — Project dependencies.

## Features

- FastAPI endpoints to verify service health and invoke agent queries.
- PostgreSQL logging for incoming questions and AI responses.
- PDF retrieval tool that searches knowledge documents using Chroma embeddings.
- LangChain agent with OpenAI model support.

## Requirements

- Python 3.11+ recommended
- FastAPI
- Uvicorn
- psycopg2 or `psycopg2-binary`
- langchain
- langchain-openai
- langchain-chroma
- chromadb
- PyMuPDF
- OpenAI API credentials

## Run locally

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install fastapi uvicorn psycopg2-binary langchain langchain-openai langchain-chroma chromadb PyMuPDF
```

3. Run the FastAPI app:

```bash
uvicorn app.main:app --reload
```

4. Open the docs at:

```
http://127.0.0.1:8000/docs
```

## Notes

- The project expects a PDF in `data/` for building the Chroma vector store.
- The vector store is persisted in `chroma_db/`.
- Move any database credentials into a secure `.env` file before production use.
