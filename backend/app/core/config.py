import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "BugTracer"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    
    # Security
    SECRET_KEY: str = "bugtracer-super-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    # Default to SQLite. For MySQL, set: mysql+aiomysql://user:password@localhost:3306/bugtracer?charset=utf8mb4
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/bugtracer.db"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
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
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )
    
    @property
    def sync_database_url(self) -> str:
        """Returns synchronous database URL for scripts or sync engines if needed."""
        url = self.DATABASE_URL
        if url.startswith("sqlite+aiosqlite:"):
            return url.replace("sqlite+aiosqlite:", "sqlite:")
        elif url.startswith("mysql+aiomysql:"):
            return url.replace("mysql+aiomysql:", "mysql+pymysql:")
        return url

settings = Settings()

# Ensure directories exist
os.makedirs("./data", exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
