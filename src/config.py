import os
from typing import Any, Dict, List, Optional, Union

try:
    # Try Pydantic v1 import
    from pydantic import BaseSettings, validator
    PYDANTIC_V2 = False
except ImportError:
    # Fallback to Pydantic v2 import
    from pydantic_settings import BaseSettings
    from pydantic import field_validator
    PYDANTIC_V2 = True


class Settings(BaseSettings):
    """
    應用程序配置設置，使用pydantic進行環境變量驗證和類型轉換
    """
    # 數據庫配置
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5433/ticket_knowledge_db"

    # Redis配置
    REDIS_URL: str = "redis://localhost:6380/0"

    # 安全配置
    SECRET_KEY: str = "your_secret_key_here_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 環境配置
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API配置
    API_PREFIX: str = "/api/v1"
    TICKET_API_PORT: int = 8000
    KNOWLEDGE_API_PORT: int = 8001

    # CORS配置
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    if PYDANTIC_V2:
        @field_validator("ALLOWED_ORIGINS", mode="before")
        @classmethod
        def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
            if isinstance(v, str):
                return [origin.strip() for origin in v.split(",") if origin.strip()]
            return v
    else:
        @validator("ALLOWED_ORIGINS", pre=True)
        def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
            if isinstance(v, str):
                return [origin.strip() for origin in v.split(",") if origin.strip()]
            return v

    # 文件上傳配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB in bytes

    # 日誌配置
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./logs"

    # Elasticsearch配置
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_USERNAME: Optional[str] = None
    ELASTICSEARCH_PASSWORD: Optional[str] = None

    # Kafka配置
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_PREFIX: str = "ticket_knowledge"
    KAFKA_CONSUMER_GROUP_ID: str = "ticket_knowledge_group"
    KAFKA_AUTO_OFFSET_RESET: str = "earliest"

    # 郵件配置
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None

    # 分頁配置
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    # 搜索配置
    SEARCH_RESULT_LIMIT: int = 20
    HIGHLIGHT_TAG_OPEN: str = "<mark>"
    HIGHLIGHT_TAG_CLOSE: str = "</mark>"

    if PYDANTIC_V2:
        model_config = {
            "env_file": ".env",
            "env_file_encoding": "utf-8",
            "case_sensitive": True,
        }
    else:
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = True


# 創建全局設置實例
settings = Settings()


def get_settings() -> Settings:
    """
    獲取應用程序設置的依賴函數，用於FastAPI依賴注入
    """
    return settings