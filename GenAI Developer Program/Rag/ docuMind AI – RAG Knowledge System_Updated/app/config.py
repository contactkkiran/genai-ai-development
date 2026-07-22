import os
import logging
from enum import Enum
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings:
    # Application
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "text")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "4"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TIMEOUT: int = int(os.getenv("OPENAI_TIMEOUT", "60"))
    
    # Database
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "data/db")
    CHROMA_PERSISTENCE_ENABLED: bool = os.getenv("CHROMA_PERSISTENCE_ENABLED", "true").lower() == "true"
    
    # Security
    API_KEY_SECRET: str = os.getenv("API_KEY_SECRET", "")
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "localhost,127.0.0.1").split(",")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Caching
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    
    # AWS
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "")
    AWS_LOGS_ENABLED: bool = os.getenv("AWS_LOGS_ENABLED", "false").lower() == "true"
    
    # Sentry (Error Tracking)
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    
    def validate(self):
        """Validate critical configuration"""
        if self.ENVIRONMENT not in [e.value for e in Environment]:
            raise ValueError(f"ENVIRONMENT must be one of: {[e.value for e in Environment]}")

    def require_openai_api_key(self):
        """Ensure OpenAI-dependent endpoints have a configured API key."""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if self.OPENAI_API_KEY.startswith("OPENAI_API_KEY="):
            raise ValueError("OPENAI_API_KEY must contain only the key value, not 'OPENAI_API_KEY='")
        if not self.OPENAI_API_KEY.startswith("sk-"):
            raise ValueError("OPENAI_API_KEY must start with 'sk-'")
    
    @classmethod
    def get_log_level(cls):
        """Get logging level"""
        return getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO)


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    settings = Settings()
    settings.validate()
    return settings
