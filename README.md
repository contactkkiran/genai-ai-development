# Gen AI, Agentic AI, RAG, and ML Mastery Roadmap

This workspace is a learning roadmap with hands-on projects for Python, LLM foundations, RAG, agentic AI workflows, FastAPI services, and machine learning basics.

The repo is organized as multiple independent practice areas. Some folders contain runnable code, some contain notes or experiments, and some are placeholders for future work.

## Project Index

| Area | Project or Subproject | What It Is | Status |
| --- | --- | --- | --- |
| `phase 1 - python/` | Python basics | Introductory Python scripts, sample text files, and LLM model notes. | In progress |
| `phase 1 - python/fastapi/` | FastAPI sample app | Basic FastAPI service with example endpoints and Pydantic request models. | Runnable learning sample |
| `phase2 - LLMFoundations/` | LLM foundations | Experiments for context windows, token usage, cost, latency, throughput, and model routing. | Runnable scripts |
| `Phase - Machine Learning/Scikit-learn/` | Scikit-learn practice | Linear regression examples, notes, and rough experiments for supervised learning. | Runnable learning sample |
| `Multi-Agent Workflows/` | Agentic AI fundamentals | Top-level scripts for basic agent concepts, OpenAI agents, and RAG plus text-to-SQL experiments. | In progress |
| `Multi-Agent Workflows/phase1/` | Agentic AI phase 1 | Early agent workflow prototypes and API-oriented examples. | Prototype |
| `Multi-Agent Workflows/phase1/real-api-postgresql/` | Real API PostgreSQL examples | Event-loop examples for single-agent single-task and multi-task flows with PostgreSQL-oriented patterns. | Prototype |
| `Multi-Agent Workflows/phase2/fastapi-agentic-rag-Project/` | FastAPI agentic RAG app | FastAPI, LangChain, ChromaDB, OpenAI, PostgreSQL logging, PDF retrieval, and agent orchestration. | Main runnable project |
| `GenAI Developer Program/genai-foundation/` | GenAI foundation exercises | API tests, embeddings, token examples, and prompt engineering basics. | Runnable scripts |
| `GenAI Developer Program/pdf_chunking_project/` | PDF chunking project | PDF loading, text chunking, utility functions, and sample PDF processing. | In progress |
| `GenAI Developer Program/Rag/production-rag/` | Production RAG | Insurance-policy RAG system with PDF loading, chunking, BM25 retrieval, semantic retrieval, hybrid retrieval, routing, and Chroma storage. | Main runnable project |
| `Claudeai/agentic/` | Claude agentic experiments | Basic Claude API calls, tool definition examples, and agentic workflow notes. | In progress |
| `Claudeai/agentic/Agentic RAG Workflow for Automation/` | Agentic RAG automation | Notes and a mini project combining RAG, Selenium tooling, and an automation agent. | Prototype |
| `Agentic Development/` | Agentic development area | Placeholder for future agentic development work. | In progress, no code yet |
| `ML:Deep Learning/` | Deep learning area | Placeholder for future deep learning projects. | In progress, no code yet |
| `MLOps:Data Engineering /` | MLOps and data engineering area | Placeholder for future MLOps and data engineering projects. | In progress, no code yet |

## Main Learning Tracks

### Python and API Basics

- `phase 1 - python/`
- `phase 1 - python/fastapi/`

Use this area to practice Python syntax, simple files, and basic FastAPI service patterns.

### LLM Foundations

- `phase2 - LLMFoundations/`
- `GenAI Developer Program/genai-foundation/`

Use this area to learn prompt basics, token counting, embeddings, latency, throughput, model selection, and API usage.

### RAG and Document Retrieval

- `GenAI Developer Program/pdf_chunking_project/`
- `GenAI Developer Program/Rag/production-rag/`
- `Multi-Agent Workflows/phase2/fastapi-agentic-rag-Project/`

Use this area to learn document loading, PDF parsing, chunking, embeddings, vector stores, BM25 search, semantic search, hybrid retrieval, and FastAPI-based RAG services.

### Agentic AI and Automation

- `Multi-Agent Workflows/`
- `Multi-Agent Workflows/phase1/`
- `Claudeai/agentic/`
- `Claudeai/agentic/Agentic RAG Workflow for Automation/`

Use this area to explore agents, tools, orchestration, event loops, text-to-SQL patterns, and automation workflows.

### Machine Learning

- `Phase - Machine Learning/Scikit-learn/`
- `ML:Deep Learning/`

Use this area for traditional machine learning practice first, then expand into deep learning later.

### MLOps and Data Engineering

- `MLOps:Data Engineering /`

This area is currently a placeholder for future work around production data pipelines, deployment, monitoring, and MLOps practices.

## Suggested Path

1. Start with `phase 1 - python/` for Python and FastAPI basics.
2. Move to `phase2 - LLMFoundations/` and `GenAI Developer Program/genai-foundation/` for LLM fundamentals.
3. Practice ML basics in `Phase - Machine Learning/Scikit-learn/`.
4. Work through `GenAI Developer Program/pdf_chunking_project/` to understand document loading and chunking.
5. Explore `GenAI Developer Program/Rag/production-rag/` for retrieval architecture.
6. Build on that with `Multi-Agent Workflows/phase2/fastapi-agentic-rag-Project/`.
7. Continue into `Multi-Agent Workflows/` and `Claudeai/agentic/` for agentic workflows and automation.

## Notes

- Many folders are learning projects, so some scripts are intentionally experimental or rough.
- Folders with `README.md` files include more detailed setup and running instructions.
- Folders containing only notes or no code are marked as in progress.
- Local caches, virtual environments, `__pycache__`, Chroma databases, and sample data may exist inside project folders.
- Move API keys, database credentials, and other secrets into `.env` files before sharing or deploying any project.
