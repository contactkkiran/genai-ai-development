"""
===============================================================
 FastAPI Application
===============================================================

Purpose:
    Entry point of the Agentic RAG application.

Responsibilities:
    - Expose REST APIs
    - Receive user requests
    - Invoke LangChain Agent
    - Persist conversations into PostgreSQL
    - Retrieve conversation history

Application Flow:

                Client / Swagger
                        |
                        v
                 FastAPI Endpoints
                        |
          +-------------+-------------+
          |                           |
          v                           v
     /ask Endpoint              /history Endpoint
          |                           |
          v                           v
     LangChain Agent          PostgreSQL Database
          |
          v
     PDFRetriever Tool
          |
          v
    Chroma Vector Store
          |
          v
     Semantic Search
          |
          v
     GPT-4o-mini Response
          |
          v
     PostgreSQL Logging

===============================================================
"""

# ============================================================
# STEP 1 - IMPORT REQUIRED MODULES
# ============================================================

from fastapi import FastAPI

from app.agent.agent import run_agent
from app.database.database import log_query, cur
from app.models.query import QueryRequest

# ============================================================
# STEP 2 - CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI()


# ============================================================
# STEP 3 - HEALTH CHECK ENDPOINT
# ============================================================
#
# Purpose:
#     Verify that the FastAPI application
#     is running successfully.
#
# Endpoint:
#     GET /
# ============================================================


@app.get("/")
def home():

    return {"message": "FastAPI is working!"}


# ============================================================
# STEP 4 - DATABASE CONNECTION TEST
# ============================================================
#
# Purpose:
#     Verify PostgreSQL connectivity by
#     inserting a sample record.
#
# Endpoint:
#     POST /testdb
# ============================================================


@app.post("/testdb")
def test_db():

    log_query("Hello?", "Database connected!")

    return {"status": "Logged successfully"}


# ============================================================
# STEP 5 - AGENT EXECUTION ENDPOINT
# ============================================================
#
# Purpose:
#     Receives user questions,
#     invokes the LangChain Agent,
#     stores the conversation,
#     and returns the AI response.
#
# Flow:
#
# User
#   |
#   v
# FastAPI
#   |
#   v
# run_agent()
#   |
#   v
# LangChain Agent
#   |
#   v
# PDFRetriever Tool
#   |
#   v
# Chroma Semantic Search
#   |
#   v
# GPT Response
#   |
#   v
# PostgreSQL Logging
#
# Endpoint:
#     POST /ask
# ============================================================


@app.post("/ask")
def ask_question(request: QueryRequest):

    query = request.query

    answer = run_agent(query)

    log_query(query, answer)

    return {"answer": answer}


# ============================================================
# STEP 6 - CONVERSATION HISTORY ENDPOINT
# ============================================================
#
# Purpose:
#     Retrieve previously asked questions
#     and generated AI responses.
#
# Features:
#     - Returns latest conversations
#     - Configurable history limit
#     - Ordered by latest records
#
# Endpoint:
#     GET /history
#
# Example:
#
#     /history
#
#     /history?limit=20
#
# ============================================================


@app.get("/history")
def get_history(limit: int = 10):

    cur.execute(
        """
        SELECT
            question,
            answer,
            created_at
        FROM queries
        ORDER BY id DESC
        LIMIT %s
        """,
        (limit,),
    )

    rows = cur.fetchall()

    return [
        {
            "question": question,
            "answer": answer,
            "created_at": created_at,
        }
        for (question, answer, created_at) in rows
    ]
