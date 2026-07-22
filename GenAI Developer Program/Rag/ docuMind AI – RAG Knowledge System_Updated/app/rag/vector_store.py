from langchain_chroma import Chroma
from app.rag.embedder import get_embeddings

# persistent DB path
DB_PATH = "data/db"

# create DB connection
def get_vector_store():
    return Chroma(
        persist_directory=DB_PATH,
        embedding_function=get_embeddings()
    )


# used during ingestion
def store_docs(chunks, embeddings):
    db = get_vector_store()
    db.add_documents(chunks)

    