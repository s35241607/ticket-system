from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from src.config import settings

# 創建SQLAlchemy引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 確保連接池中的連接是有效的
    echo=settings.DEBUG,  # 在開發環境中輸出SQL語句
)

# 創建會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 創建Base類，所有模型類都將繼承此類
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    獲取數據庫會話的依賴函數，用於FastAPI依賴注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()