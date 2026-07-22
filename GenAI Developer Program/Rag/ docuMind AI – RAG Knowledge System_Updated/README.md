# DocuMind AI – RAG Knowledge System

A Retrieval-Augmented Generation (RAG) system that enables intelligent document analysis and question-answering capabilities using OpenAI's GPT-4o-mini model and ChromaDB vector database.

## Overview

DocuMind AI processes documents and creates a searchable knowledge base, allowing users to ask natural language questions and receive accurate, sourced answers based on the ingested documents. The system combines document retrieval with large language models for contextually relevant responses.

## Features

- 📄 **Document Ingestion**: Load and process various document formats
- 🧩 **Smart Chunking**: Intelligently split documents into manageable pieces
- 🔍 **Semantic Search**: Find relevant content using vector embeddings
- 🤖 **AI-Powered Responses**: Generate answers using GPT-4o-mini
- 📚 **Source Tracking**: Trace answers back to original documents and page numbers
- 💾 **Vector Storage**: Efficient storage and retrieval with ChromaDB

## Project Structure

```
DocuMind AI – RAG Knowledge System/
├── app/
│   ├── main.py                 # Entry point
│   ├── ingest/
│   │   ├── chunker.py         # Document chunking logic
│   │   └── loader.py          # Document loading
│   ├── llm/
│   │   └── model.py           # LLM integration and queries
│   └── rag/
│       ├── embedder.py        # Embedding generation
│       ├── retriever.py       # Document retrieval
│       └── vector_store.py    # Vector database management
├── data/
│   └── db/                     # ChromaDB storage
├── requirements.txt            # Python dependencies
├── pyrightconfig.json         # Pyright configuration
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- pip (Python package manager)

### Setup Steps

1. **Clone or extract the project**

   ```bash
   cd "DocuMind AI – RAG Knowledge System"
   ```

2. **Create a virtual environment** (optional but recommended)

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_key_here
   ```

## Usage

### Running Interactive Q&A

Start the interactive question-answering session:

```bash
python -m app.llm.model
```

Then type your questions when prompted:

```
Ask: What are the key features of the product described in the documents?
```

The system will respond with:

- An answer based on the ingested documents
- Sources with page references

### Example Queries

- "What are the key features of the product?"
- "What are payment failure scenarios?"
- "How does the system handle user authentication?"

## Components

### Ingest Module (`app/ingest/`)

- **loader.py**: Loads documents from various sources
- **chunker.py**: Splits documents into optimal chunks for embedding

### RAG Module (`app/rag/`)

- **embedder.py**: Converts text to vector embeddings
- **vector_store.py**: Manages ChromaDB storage and operations
- **retriever.py**: Retrieves relevant documents for queries

### LLM Module (`app/llm/`)

- **model.py**: Interfaces with OpenAI's GPT-4o-mini for answer generation

## Code Walkthrough

This section explains how the system processes documents and generates answers step by step.

### Architecture Overview

```
USER QUERY
    ↓
[FastAPI /query endpoint]
    ↓
[Retriever] → Finds relevant docs from vector DB
    ↓
[LLM/Model] → Generates answer using context
    ↓
[JSON Response] → Answer + Sources
```

### Stage 1: Document Ingestion (`app/ingest/`)

#### Step 1a: Load PDFs (`loader.py`)

```python
def load_all_pdfs(folder_path: str) -> list[RawDocument]:
```

**What it does:**

1. Scans the `data/` folder for all `.pdf` files
2. Opens each PDF using PyMuPDF (`pymupdf`)
3. Extracts text from **each page** separately
4. Stores each page with metadata (filename + page number)
5. Skips empty pages to reduce noise

**Example output:**

```python
{
    "content": "Payment failure scenarios include insufficient balance...",
    "metadata": {
        "source": "banking_custom.pdf",
        "page": 0
    }
}
```

---

#### Step 1b: Split into Chunks (`chunker.py`)

```python
def split_docs(raw_docs: list[RawDocument]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
```

**What it does:**

1. Takes extracted page content (could be 2000+ words)
2. Splits into **800-character chunks** for optimal embedding
3. Adds **100-character overlap** between chunks to preserve context
4. Maintains metadata (filename, page number) for each chunk

**Why chunking?**

- Vector embeddings work better with smaller, focused text
- Reduces noise and improves retrieval precision
- Overlap ensures context is preserved across boundaries

**Example:**

```
Original Page: "Payment failures include... insufficient balance...
               network timeout... fraud detected... [2000 chars]"

After Chunking:
├── Chunk 1: "Payment failures include... insufficient balance... [800 chars]"
├── Chunk 2: "...insufficient balance, network timeout... [800 chars]"
│            (overlaps 100 chars with Chunk 1)
└── Chunk 3: "...network timeout, fraud detected... [800 chars]"
             (overlaps 100 chars with Chunk 2)
```

---

### Stage 2: Vector Database Storage (`app/rag/`)

#### Step 2a: Create Embeddings (`embedder.py`)

```python
def get_embeddings() -> OpenAIEmbeddings:
    load_dotenv()
    return OpenAIEmbeddings()
```

**What it does:**

1. Initializes OpenAI's embedding model
2. Converts **text → numerical vectors** (1536-dimensional arrays)
3. Similar text produces similar vectors (mathematically)

**How embeddings work:**

```
Text: "Payment failure due to insufficient balance"
      ↓ [OpenAI Embedding API]
Vector: [0.12, -0.45, 0.89, ..., 0.23]  (1536 numbers)

Text: "Not enough funds in account"
      ↓ [OpenAI Embedding API]
Vector: [0.11, -0.46, 0.88, ..., 0.24]  (very similar!)
```

---

#### Step 2b: Store in Vector Database (`vector_store.py`)

```python
def store_docs(chunks, embeddings):
    db = get_vector_store()
    db.add_documents(chunks)
```

**What it does:**

1. Connects to ChromaDB (persistent SQLite database)
2. For each document chunk:
   - Generates its embedding vector (using OpenAI API)
   - Stores the text + vector + metadata
   - Persists to `data/db/` folder
3. Creates indexed structures for fast similarity search

**Database structure:**

```
ChromaDB (data/db/)
├── Chunk 1
│   ├── Content: "Payment failure..."
│   ├── Vector: [0.12, -0.45, 0.89, ...]
│   ├── Source: "banking_custom.pdf"
│   └── Page: 1
├── Chunk 2
│   ├── Content: "Network timeout..."
│   ├── Vector: [0.18, -0.42, 0.91, ...]
│   ├── Source: "sre.pdf"
│   └── Page: 23
└── ... (more chunks)
```

---

### Stage 3: Query & Retrieval (`app/rag/retriever.py`)

```python
def retrieve(query: str):
    retriever = get_retriever()
    docs = retriever.invoke(query)
    return list(docs)
```

**What happens behind the scenes:**

1. **Convert query to vector:**

   ```
   Query: "What are payment failure scenarios?"
           ↓ [OpenAI Embedding API]
   Vector: [0.14, -0.43, 0.88, ...]
   ```

2. **Search for similar vectors in ChromaDB:**

   ```python
   search_type="similarity_score_threshold"
   search_kwargs={"k": 5, "score_threshold": 0.7}
   ```

   - Considers top 5 candidates from database
   - Keeps only those with 70%+ similarity
   - Filters out loosely related documents (near-similarity matching ✅)

3. **Return matched chunks:**
   ```python
   [
       Document(
           content="Payment failures: insufficient balance, network timeout, fraud",
           metadata={"source": "banking_custom.pdf", "page": 1}
       )
   ]
   ```

---

### Stage 4: LLM Answer Generation (`app/llm/model.py`)

#### Step 4a: Build Context

```python
def generate(query: str, docs: list):
    context = "\n\n".join(d.page_content for d in docs)
```

**What it does:**

- Combines all retrieved chunks into a single context text block
- Example:
  ```
  Context: "Payment failures: insufficient balance, network timeout, fraud detected"
  ```

---

#### Step 4b: Call OpenAI GPT-4o-mini

```python
def ask_llm(context: str, question: str) -> str:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    response = llm.invoke([
        SystemMessage(
            content="Answer ONLY using the provided context. "
                    "If the answer is not available, say 'I don't know'."
        ),
        HumanMessage(
            content=f"Context:\n{context}\n\nQuestion:\n{question}"
        ),
    ])
```

**What it does:**

1. **System Message**: Instructs LLM to use ONLY provided context (prevents hallucination)
2. **Human Message**: Provides both context and question
3. **Temperature=0**: Ensures deterministic responses (same answer every time)

**Example:**

```
System: "Answer ONLY using context. If not available, say 'I don't know.'"
Human: "Context: Payment failures: insufficient balance, network timeout, fraud detected.
        Question: What are payment failure scenarios?"

LLM Response: "Payment failure scenarios include insufficient balance,
              network timeout, and fraud detected."
```

---

#### Step 4c: Extract Sources

```python
sources = []
for d in docs:
    full_path = d.metadata.get("source", "unknown")
    file_name = os.path.basename(full_path)
    page = d.metadata.get("page", "?")
    sources.append(f"{file_name} (page {page})")

return {
    "answer": answer,
    "sources": list(set(sources))  # Remove duplicates
}
```

**What it does:**

- Extracts filename and page number from each retrieved document
- Removes duplicate sources using `set()`
- Returns clean JSON response

---

### Stage 5: FastAPI Web Server (`app/main.py`)

```python
@app.post("/query")
def query(q: str):
    try:
        if not q or not q.strip():
            return {"error": "Query cannot be empty"}

        docs = retrieve(q)           # Stage 3: Get relevant docs

        if not docs:
            return {"error": "No relevant documents found"}

        result = generate(q, docs)   # Stage 4: Generate answer
        return result                # Return JSON
    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}
```

**Complete query flow:**

```
POST /query?q=Your+question
    ↓
1. VALIDATE INPUT
   - Check if query is not empty
    ↓
2. RETRIEVE DOCUMENTS
   - Convert query to vector
   - Search ChromaDB with threshold
   - Return 1-5 similar documents
    ↓
3. GENERATE ANSWER
   - Build context from documents
   - Call GPT-4o-mini with context
   - Extract sources
    ↓
4. RETURN JSON RESPONSE
   {
     "answer": "Payment failure scenarios...",
     "sources": ["banking_custom.pdf (page 1)"]
   }
```

---

### Complete Query Example

**User Query:** `"What are payment failure scenarios?"`

**Step-by-step execution:**

```
1. RETRIEVAL PHASE
   ├─ Query vector: [0.14, -0.43, 0.88, ...]
   ├─ Search ChromaDB top 5
   ├─ Calculate similarity scores:
   │  ├─ banking_custom.pdf (page 1): 98% ✅ KEEP
   │  └─ sre.pdf (page 6): 65% ❌ REJECT (below 70%)
   └─ Retrieved: 1 document

2. CONTEXT BUILDING
   ├─ Document 1 content: "Payment failures: insufficient balance,
   │                       network timeout, fraud detected"
   └─ Final context: "Payment failures: insufficient balance,
                      network timeout, fraud detected"

3. LLM GENERATION
   ├─ Send to GPT-4o-mini:
   │  ├─ System: "Answer ONLY using context"
   │  ├─ Context: "Payment failures..."
   │  └─ Question: "What are payment failure scenarios?"
   └─ Response: "Payment failure scenarios include insufficient
               balance, network timeout, and fraud detected."

4. SOURCE EXTRACTION
   ├─ Document 1 source: "banking_custom.pdf (page 1)"
   └─ Final sources: ["banking_custom.pdf (page 1)"]

5. JSON RESPONSE
   {
     "answer": "Payment failure scenarios include insufficient balance,
               network timeout, and fraud detected.",
     "sources": ["banking_custom.pdf (page 1)"]
   }
```

---

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    INGESTION PHASE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PDFs in /data/                                                 │
│      │                                                           │
│      ├─ loader.py: Extract text from each page                 │
│      │                                                           │
│      ├─ chunker.py: Split into 800-char chunks (100 overlap)   │
│      │                                                           │
│      ├─ embedder.py: Convert each chunk to vector              │
│      │                                                           │
│      └─ vector_store.py: Store in ChromaDB (/data/db/)         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    QUERY PHASE                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Query: "What are payment failure scenarios?"             │
│      │                                                           │
│      ├─ retriever.py: Convert to vector, search ChromaDB        │
│      │  (k=5, score_threshold=0.7)                             │
│      │                                                           │
│      ├─ model.py.generate(): Build context from docs           │
│      │                                                           │
│      ├─ model.py.ask_llm(): Call GPT-4o-mini                  │
│      │                                                           │
│      ├─ Extract: Answer + Sources                              │
│      │                                                           │
│      └─ main.py: Return JSON response                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration

- **LLM Model**: GPT-4o-mini (configurable in `app/llm/model.py`)
- **Temperature**: Set to 0 for deterministic responses
- **Vector Database**: ChromaDB (local SQLite-based storage in `data/db/`)

## Dependencies

Key packages include:

- `langchain-openai`: OpenAI integration
- `langchain-core`: Core LangChain functionality
- `chromadb`: Vector database
- `python-dotenv`: Environment variable management

See `requirements.txt` for the complete list.

## Troubleshooting

### OpenAI API Errors

- Verify your `OPENAI_API_KEY` is correctly set in the `.env` file
- Check that your OpenAI account has sufficient credits

### No Results Found

- Ensure documents have been ingested into the vector store
- Try rephrasing your question with different keywords

### Performance Issues

- Reduce document chunk size for faster retrieval
- Consider indexing performance of your ChromaDB instance

## Future Enhancements

- Support for additional document formats
- Multiple language support
- Custom embedding models
- Web interface for document management
- Batch document processing
- Query caching and optimization

## License

[Add your license here]

## Support

For issues or questions, please refer to the project documentation or contact the development team.
