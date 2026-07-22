import warnings
warnings.filterwarnings("ignore")

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import get_settings
from app.rag.retriever import get_retriever


# -----------------------------
# Internal LLM call
# -----------------------------
def ask_llm(context: str, question: str) -> str:
    load_dotenv()
    settings = get_settings()
    settings.require_openai_api_key()

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=0,
        api_key=settings.OPENAI_API_KEY,
        timeout=settings.OPENAI_TIMEOUT,
    )

    response = llm.invoke([
        SystemMessage(
            content=(
                "Answer ONLY using the provided context. "
                "If the answer is not available, say 'I don't know'."
            )
        ),
        HumanMessage(
            content=f"Context:\n{context}\n\nQuestion:\n{question}"
        ),
    ])

    return str(response.content)


# -----------------------------
# Core RAG (existing logic)
# -----------------------------
def ask(question: str) -> str:
    retriever = get_retriever()

    docs = retriever.invoke(question)

    context = "\n\n".join(d.page_content for d in docs)

    sources = []
    for d in docs:
        full_path = d.metadata.get("source", "unknown")
        file_name = os.path.basename(full_path)
        page = d.metadata.get("page", "?")
        sources.append(f"- {file_name} (page {page})")

    answer = ask_llm(context, question)

    sources_text = "\n".join(set(sources))

    return f"""
Answer:
{answer}

Sources:
{sources_text}
"""


# -----------------------------
# API function (USED BY FASTAPI)
# -----------------------------
def generate(query: str, docs: list):
    context = "\n\n".join(d.page_content for d in docs)

    answer = ask_llm(context, query)

    sources = []
    for d in docs:
        full_path = d.metadata.get("source", "unknown")
        file_name = os.path.basename(full_path)
        page = d.metadata.get("page", "?")
        sources.append(f"{file_name} (page {page})")

    return {
        "answer": answer,
        "sources": list(set(sources))
    }


# -----------------------------
# CLI mode (optional)
# -----------------------------
if __name__ == "__main__":
    while True:
        q = input("\nAsk: ").strip()

        if not q:
            print("Please enter a valid question.")
            continue

        print(ask(q))

# user prompt: "What are the key features of the product described in the documents?"   
    # Answer : 1. **Functional Behavior Identification**: The Use-Case Documents are designed to identify the functional behavior of the system, outlining how users will interact with the system and what functionalities it will provide.

    # 2. **Specific Feature Definition**: The Supplementary Requirements Specification Documents define the features of the system in specific terms, detailing the requirements and characteristics that the system must fulfill.

    # These documents collectively help in understanding both the functional aspects and the specific requirements of the system.

    # Sources:
    # - prd.pdf (page 9)
# User prompt: "What are payment failure scenarios?"
#   #  Answer : 1. Insufficient balance: The account does not have enough funds to complete the transaction.
    # 2. Network timeout: There is a delay or failure in the network connection, preventing the transaction from being processed.
    # 3. Fraud detected: The transaction is flagged as potentially fraudulent, leading to its rejection for security reasons.
