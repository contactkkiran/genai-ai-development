"""
agent.py

Responsibility:
    Agent Orchestration Layer

Flow:

FastAPI
   |
   v
run_agent()
   |
   v
LangChain Agent
   |
   +--> PDFRetriever Tool
             |
             v
        Chroma Vector DB
             |
             v
        Relevant PDF Chunks
             |
             v
        GPT Response
"""

# =====================================================
# STEP 1:
# Import required LangChain components.
# =====================================================

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from app.rag.rag import build_vectorstore

# =====================================================
# STEP 2:
# Load the existing Chroma Vector Database.
# =====================================================

vectorstore = build_vectorstore()


# =====================================================
# STEP 3:
# Create a PDF retrieval tool that the agent can invoke.
# =====================================================


@tool
def PDFRetriever(query: str) -> str:
    """
    Search the PDF knowledge base and return relevant content.
    """

    docs = vectorstore.similarity_search(query)

    context = "\n\n".join(doc.page_content for doc in docs)

    return context


# =====================================================
# STEP 4:
# Create the Large Language Model (LLM).
# =====================================================

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# =====================================================
# STEP 5:
# Create the LangChain Agent with its available tools.
# =====================================================

agent = create_agent(model=llm, tools=[PDFRetriever])


# =====================================================
# STEP 6:
# Execute the agent and return the final response.
# =====================================================


def run_agent(query: str):

    result = agent.invoke({"messages": [{"role": "user", "content": query}]})

    return result["messages"][-1].content
