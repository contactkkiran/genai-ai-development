from fastapi import FastAPI, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import time
from typing import Optional

from app.config import get_settings
from app.logger import setup_logging, get_logger
from app.ingest.loader import load_all_pdfs
from app.ingest.chunker import split_docs
from app.rag.embedder import get_embeddings
from app.rag.vector_store import store_docs
from app.rag.retriever import retrieve
from app.llm.model import generate

# Setup logging
logger = setup_logging()
app_logger = get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    app_logger.info(f"Starting DocuMind AI in {settings.ENVIRONMENT} environment")
    yield
    app_logger.info("Shutting down DocuMind AI")


# Initialize FastAPI app
app = FastAPI(
    title="DocuMind AI - RAG Knowledge System",
    description="Intelligent document analysis and Q&A system using RAG",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.DEBUG else "/docs",
    redoc_url="/redoc" if not settings.DEBUG else None,
)

# Security: CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Security: Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_ORIGINS
)


# Health check
@app.get("/health", tags=["Health"])
def health():
    """Health check endpoint"""
    try:
        app_logger.debug("Health check called")
        return {
            "status": "ok",
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0"
        }
    except Exception as e:
        app_logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

# Request counter for rate limiting
request_times = {}


def ensure_openai_configured():
    """Return a clear API error before calling OpenAI-backed services."""
    try:
        settings.require_openai_api_key()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


def check_rate_limit(client_id: str) -> bool:
    """Simple in-memory rate limiter"""
    if not settings.RATE_LIMIT_ENABLED:
        return True
    
    current_time = time.time()
    minute_ago = current_time - 60
    
    if client_id in request_times:
        request_times[client_id] = [t for t in request_times[client_id] if t > minute_ago]
    else:
        request_times[client_id] = []
    
    if len(request_times[client_id]) >= settings.RATE_LIMIT_PER_MINUTE:
        return False
    
    request_times[client_id].append(current_time)
    return True


# =====================================
# Ingestion Endpoint
# =====================================
@app.post("/ingest", tags=["Ingest"])
def ingest(x_api_key: Optional[str] = Header(None)):
    """Ingest documents into the vector database"""
    try:
        if settings.ENVIRONMENT == "production" and settings.API_KEY_SECRET:
            if not x_api_key or x_api_key != settings.API_KEY_SECRET:
                app_logger.warning("Unauthorized ingest attempt")
                raise HTTPException(status_code=403, detail="Invalid API key")
        
        app_logger.info("Starting document ingestion")
        ensure_openai_configured()
        
        docs = load_all_pdfs("data")
        app_logger.info(f"Loaded {len(docs)} documents")
        
        chunks = split_docs(docs)
        app_logger.info(f"Created {len(chunks)} chunks")
        
        embeddings = get_embeddings()
        store_docs(chunks, embeddings)
        
        app_logger.info("Document ingestion completed")
        return {
            "status": "success",
            "message": "Documents stored in DB",
            "documents_count": len(docs),
            "chunks_count": len(chunks)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.exception(f"Error in /ingest: {str(e)}")
        raise HTTPException(status_code=500, detail="Ingestion failed")


# =====================================
# Query Endpoint
# =====================================
@app.post("/query", tags=["Query"])
def query(
    q: str,
    x_api_key: Optional[str] = Header(None),
    x_client_id: Optional[str] = Header("anonymous")
):
    """Query the knowledge base"""
    try:
        start_time = time.time()
        
        if not check_rate_limit(x_client_id):
            app_logger.warning(f"Rate limit exceeded for {x_client_id}")
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        if settings.ENVIRONMENT == "production" and settings.API_KEY_SECRET:
            if not x_api_key or x_api_key != settings.API_KEY_SECRET:
                app_logger.warning(f"Unauthorized query from {x_client_id}")
                raise HTTPException(status_code=403, detail="Invalid API key")
        
        if not q or not q.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if len(q) > 1000:
            raise HTTPException(status_code=400, detail="Query too long (max 1000 chars)")
        
        ensure_openai_configured()
        app_logger.info(f"Processing query: {q[:50]}...")
        
        docs = retrieve(q)
        
        if not docs:
            return {
                "answer": "No relevant information found",
                "sources": [],
                "query": q,
                "processing_time_ms": round((time.time() - start_time) * 1000, 2)
            }
        
        result = generate(q, docs)
        result["query"] = q
        result["processing_time_ms"] = round((time.time() - start_time) * 1000, 2)
        result["documents_retrieved"] = len(docs)
        
        app_logger.info(f"Query processed in {time.time() - start_time:.2f}s")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.exception(f"Error in /query: {str(e)}")
        raise HTTPException(status_code=500, detail="Query failed")


# =====================================
# CLI Fallback
# =====================================
def main() -> None:
    """CLI mode"""
    try:
        app_logger.info("Starting CLI mode")
        docs = load_all_pdfs("data")
        chunks = split_docs(docs)
        embeddings = get_embeddings()
        store_docs(chunks, embeddings)
        app_logger.info("Documents stored")
    except Exception as e:
        app_logger.exception(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
