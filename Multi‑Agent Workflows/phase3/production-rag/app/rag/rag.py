"""
===========================================================
 RAG Service - Vector Store Builder
===========================================================

Purpose:
    Responsible for building the Retrieval Augmented
    Generation (RAG) knowledge layer.

Responsibilities:
    - Load PDF documents
    - Extract text content
    - Split content into chunks
    - Generate embeddings
    - Store vectors into Chroma DB

Flow:

PDF Document
      |
      v
Text Extraction
      |
      v
Text Chunking
      |
      v
OpenAI Embeddings
      |
      v
Chroma Vector Store

===========================================================
"""

import fitz  # PyMuPDF

from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# =========================================================
# Project Directory Configuration
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent


PDF_PATH = BASE_DIR / "data" / "Training_Manual.pdf"


CHROMA_DB_PATH = BASE_DIR / "chroma_db"


# =========================================================
# Build Vector Store
# =========================================================


def build_vectorstore():
    """
    Creates Chroma Vector Store from PDF content.

    Returns:
        Chroma:
            Vector database instance
            used by Agent Retriever Tool
    """

    # -----------------------------------------------------
    # Step 1:
    # Load PDF Document
    # -----------------------------------------------------

    document = fitz.open(PDF_PATH)

    extracted_text = ""

    # -----------------------------------------------------
    # Step 2:
    # Extract text from each PDF page
    # -----------------------------------------------------

    for page in document:

        page_text = page.get_text("text")

        extracted_text += str(page_text)

    # -----------------------------------------------------
    # Step 3:
    # Split document into chunks
    # -----------------------------------------------------

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    chunks = splitter.split_text(extracted_text)

    # -----------------------------------------------------
    # Step 4:
    # Generate Embeddings
    # -----------------------------------------------------

    embeddings = OpenAIEmbeddings()

    # -----------------------------------------------------
    # Step 5:
    # Store embeddings into Chroma DB
    # -----------------------------------------------------

    vectorstore = Chroma.from_texts(
        texts=chunks, embedding=embeddings, persist_directory=str(CHROMA_DB_PATH)
    )

    return vectorstore
