from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from app.config import get_settings


def get_embeddings() -> OpenAIEmbeddings:
    load_dotenv()
    settings = get_settings()
    settings.require_openai_api_key()
    return OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
