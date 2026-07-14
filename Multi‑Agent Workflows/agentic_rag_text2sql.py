# ==========================================================
# STEP 1 - IMPORT REQUIRED LIBRARIES
# ==========================================================

# Used to call OpenAI LLM and Embedding model
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Chroma Vector Database
from langchain_chroma import Chroma

# Document object used to store knowledge
from langchain_core.documents import Document

# Used to read environment variables
import os
from dotenv import load_dotenv

# ==========================================================
# STEP 2 - LOAD .ENV FILE
# ==========================================================
# Reads OPENAI_API_KEY from .env file

load_dotenv()

# Optional check

print("API Key Loaded:", os.getenv("OPENAI_API_KEY") is not None)


# ==========================================================
# STEP 3 - CREATE KNOWLEDGE BASE
# ==========================================================
# These documents simulate schema documentation.
#
# In real projects these may come from:
# - PDF documents
# - Confluence
# - Database metadata
# - Company wiki
#
# BREAKPOINT #1
# ==========================================================

documents = [
    Document(page_content="""
        Table: users
        Columns: id, email, status
        """),
    Document(page_content="""
        Table: orders
        Columns: order_id, user_id, total_amount
        """),
]


# ==========================================================
# STEP 4 - CREATE EMBEDDING MODEL
# ==========================================================
#
# Embeddings convert text into vectors.
#
# Example:
#
# "users table"
#
# becomes
#
# [0.123, 0.87, 0.45 ....]
#
# BREAKPOINT #2
# ==========================================================

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


# ==========================================================
# STEP 5 - STORE DOCUMENTS INSIDE CHROMA
# ==========================================================
#
# Chroma stores vector representations.
#
# BREAKPOINT #3
# ==========================================================

vector_store = Chroma.from_documents(documents=documents, embedding=embeddings)


# ==========================================================
# STEP 6 - CREATE RETRIEVER
# ==========================================================
#
# Retriever performs semantic search.
#
# BREAKPOINT #4
# ==========================================================

retriever = vector_store.as_retriever()

print()
# ==========================================================
# STEP 7 - USER QUESTION
# ==========================================================
#
# User asks a question.
#
# BREAKPOINT #5
# ==========================================================

question = "Give me emails of users who spent more than 500"

print("\nUser Question:")
print(question)


# ==========================================================
# STEP 8 - RAG RETRIEVAL
# ==========================================================
#
# Semantic search happens here.
#
# Retriever searches the Vector DB.
#
# BREAKPOINT #6
# ==========================================================

docs = retriever.invoke(question)

print("\nRetrieved Documents Object:")
print(docs)


# ==========================================================
# STEP 9 - CREATE CONTEXT
# ==========================================================
#
# Combine retrieved documents into one string.
#
# BREAKPOINT #7
# ==========================================================

schema = "\n".join([doc.page_content for doc in docs])

print("\nRetrieved Schema:\n")
print(schema)


# ==========================================================
# STEP 10 - CREATE LLM
# ==========================================================
#
# GPT-4o will generate SQL.
#
# BREAKPOINT #8
# ==========================================================

llm = ChatOpenAI(model="gpt-4o", temperature=0)


# ==========================================================
# STEP 11 - BUILD FINAL PROMPT
# ==========================================================
#
# RAG Context + User Question
#
# BREAKPOINT #9
# ==========================================================

prompt = f"""
You are an expert SQL engineer.

Schema:
{schema}

Question:
{question}

Generate SQL only.
"""

print("\nPrompt Sent To LLM:\n")
print(prompt)


# ==========================================================
# STEP 12 - CALL LLM
# ==========================================================
#
# GPT receives:
#
# Schema
# +
# User Question
#
# and generates SQL.
#
# BREAKPOINT #10
# ==========================================================

response = llm.invoke(prompt)


# ==========================================================
# STEP 13 - PRINT RESPONSE
# ==========================================================
#
# BREAKPOINT #11
# ==========================================================

print("\nGenerated SQL:\n")
print(response.content)
