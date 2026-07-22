from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.ingest.loader import RawDocument


def split_docs(raw_docs: list[RawDocument]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    documents = [
        Document(page_content=d["content"], metadata=d["metadata"])
        for d in raw_docs
    ]

    return splitter.split_documents(documents)
