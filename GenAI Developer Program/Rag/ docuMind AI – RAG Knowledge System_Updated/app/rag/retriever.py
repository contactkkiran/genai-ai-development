from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever

from app.rag.embedder import get_embeddings


def get_retriever() -> VectorStoreRetriever:
    db = Chroma(
        persist_directory="data/db",
        embedding_function=get_embeddings()
    )

    # ✅ strict similarity matching (near similarity only)
    return db.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 5, "score_threshold": 0.7}
    )


# 🔥 API function
def retrieve(query: str):
    retriever = get_retriever()

    docs = retriever.invoke(query)

    # ✅ ensure it's a list before slicing
    docs = list(docs)

    return docs