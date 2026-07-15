# Production RAG

A retrieval-augmented generation project for searching insurance policy PDF documents.

The current implementation focuses on the retrieval layer. It loads PDF files from the `data/` folder, builds a BM25 index, chooses a retrieval strategy, filters policy-specific results, and prints matching documents in the terminal.

## Current Status

Implemented:

- PDF document loading with PyMuPDF
- BM25 keyword retrieval with `rank-bm25`
- Policy identifier detection such as `CAR-120`, `MED-500`, and `LIFE-101`
- Retrieval orchestration between BM25, semantic, and hybrid strategies
- Policy-family filtering so a `CAR-*` query returns car-related documents
- Command-line execution through `rag_service.py`

Not yet implemented:

- Semantic vector search
- Hybrid BM25 plus semantic reranking
- FastAPI application endpoint
- PostgreSQL persistence

## Project Structure

```text
production-rag/
├── app/
│   ├── orchestrator/
│   │   └── retrieval_orchestrator.py
│   ├── retrievers/
│   │   ├── bm25_retriever.py
│   │   ├── hybridRetriever.py
│   │   └── semantic_retriever.py
│   └── services/
│       └── rag_service.py
├── data/
│   ├── Car_Insurance.pdf
│   ├── Health_Insurance.pdf
│   ├── Home_Insurance.pdf
│   ├── Life_Insurance.pdf
│   ├── Travel_Insurance.pdf
│   └── ...
├── requirements.txt
└── README.md
```

## How It Works

1. `RAGService` starts the retrieval workflow.
2. `BM25Retriever` loads all PDF documents from `data/`.
3. `BM25Retriever` extracts text from each PDF and builds a BM25 index.
4. `RetrievalOrchestrator` checks the user query.
5. If the query contains a policy ID like `CAR-120`, the orchestrator selects BM25.
6. `RAGService` filters results by policy family.
7. Matching results with score are printed in the terminal.

Example:

```text
Does CAR-120 cover engine damage?
```

The orchestrator extracts:

```text
CAR
```

Then the service returns only car-related documents, such as:

```text
Car_Insurance.pdf
```

## Setup

From the `production-rag` folder, create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run The RAG Service

Make sure you are inside the `production-rag` folder:

```bash
pwd
```

You should see a path ending with:

```text
production-rag
```

Run the service:

```bash
python3 -m app.services.rag_service
```

Do not run this command from the parent roadmap folder unless you also set `PYTHONPATH`.

## Example Output

```text
================================================================================
Query : Show policy MED-500
================================================================================
Rank     : 1
Score    : 0.00
Document : Health_Insurance.pdf
--------------------------------------------------------------------------------
Health Insurance
...
================================================================================
```

`Rank` is the result position after sorting. `Score` is the BM25 relevance score. The service clamps negative display scores to `0.00` to keep terminal output readable.

## Change The Test Query

Open:

```text
app/services/rag_service.py
```

Update the query inside the `__main__` block:

```python
query = "Does CAR-120 cover engine damage?"
```

Then run:

```bash
python3 -m app.services.rag_service
```

## Retrieval Strategy Rules

The strategy is selected in:

```text
app/orchestrator/retrieval_orchestrator.py
```

Current behavior:

| Query Type            | Example                          | Strategy |
| --------------------- | -------------------------------- | -------- |
| Contains policy ID    | `CAR-120`                        | BM25     |
| Natural language only | `Explain engine damage coverage` | SEMANTIC |

Important: `SemanticRetriever` is currently a placeholder and raises `NotImplementedError`. For now, use queries with policy IDs so BM25 is selected.

## Supported Policy Prefixes

Current policy-family filters are defined in `RAGService`:

| Prefix   | Document Family     |
| -------- | ------------------- |
| `CAR`    | Car, vehicle, motor |
| `MED`    | Health, medical     |
| `LIFE`   | Life                |
| `HOME`   | Home                |
| `TRAVEL` | Travel              |

## Notes

- Keep PDF files inside the `data/` folder.
- Run the module with `python3 -m app.services.rag_service` so Python can resolve the `app` package imports.
- The semantic and hybrid retrievers are scaffolded for future work but are not active yet.
