import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

# Determine absolute project root
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
DEFAULT_DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DEFAULT_DB_PATH = os.path.join(DEFAULT_DATA_DIR, "bugtracer.db")
DEFAULT_UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")

class Settings(BaseSettings):
    PROJECT_NAME: str = "BugTracer"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    
    # Security
    SECRET_KEY: str = "bugtracer-super-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DEFAULT_DB_PATH}"
    
    # File Storage
    UPLOAD_DIR: str = DEFAULT_UPLOAD_DIR
    MAX_UPLOAD_SIZE: int = 20 * 1024 * 1024  # 20MB
    ALLOWED_EXTENSIONS: List[str] = [
        "jpg", "jpeg", "png", "gif", "webp", "svg", "bmp",
        "txt", "md", "log", "json", "xml", "pdf",
        "doc", "docx", "xls", "xlsx", "ppt", "pptx",
        "zip", "rar", "tar", "gz", "7z"
    ]
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 5002
    
    # MCP Settings
    MCP_ENABLED: bool = True
    MCP_SERVER_NAME: str = "BugTracer"
    
    # Initial Admin
    INITIAL_ADMIN_USERNAME: str = "admin"
    INITIAL_ADMIN_PASSWORD: str = "123456"
    INITIAL_ADMIN_FULLNAME: str = "系统管理员"
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(PROJECT_ROOT, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )
    
    @property
    def effective_database_url(self) -> str:
        """Resolves relative SQLite URLs to absolute paths based on PROJECT_ROOT."""
        url = self.DATABASE_URL
        if url.startswith("sqlite+aiosqlite:///./"):
            rel_path = url[len("sqlite+aiosqlite:///./"):]
            abs_path = os.path.join(PROJECT_ROOT, rel_path)
            return f"sqlite+aiosqlite:///{abs_path}"
        elif url.startswith("sqlite:///./"):
            rel_path = url[len("sqlite:///./"):]
            abs_path = os.path.join(PROJECT_ROOT, rel_path)
            return f"sqlite:///{abs_path}"
        return url

    @property
    def effective_upload_dir(self) -> str:
        """Resolves relative upload directories to absolute paths."""
        if not os.path.isabs(self.UPLOAD_DIR):
            return os.path.join(PROJECT_ROOT, self.UPLOAD_DIR)
        return self.UPLOAD_DIR

    @property
    def sync_database_url(self) -> str:
        """Returns synchronous database URL for scripts or sync engines if needed."""
        url = self.effective_database_url
        if url.startswith("sqlite+aiosqlite:"):
            return url.replace("sqlite+aiosqlite:", "sqlite:")
        elif url.startswith("mysql+aiomysql:"):
            return url.replace("mysql+aiomysql:", "mysql+pymysql:")
        return url

settings = Settings()

# Ensure directories exist using absolute paths
os.makedirs(DEFAULT_DATA_DIR, exist_ok=True)
os.makedirs(settings.effective_upload_dir, exist_ok=True)
