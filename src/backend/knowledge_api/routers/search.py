from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

# 導入數據庫依賴
from database.session import get_db

# 導入模型和架構
from ..schemas.search import SearchResponse, SearchResult

# 導入服務
from ..services.search_service import SearchService

# 創建路由
router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2, description="搜索關鍵詞"),
    type: Optional[str] = Query(None, description="搜索類型，可選值：document, question, all"),
    category_id: Optional[uuid.UUID] = Query(None, description="分類ID，用於篩選結果"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """全文搜索文檔和問題"""
    search_service = SearchService(db)
    
    # 確定搜索類型
    search_type = type.lower() if type else "all"
    if search_type not in ["document", "question", "all"]:
        search_type = "all"
    
    # 構建篩選條件
    filters = {}
    if category_id:
        filters["category_id"] = category_id
    
    # 執行搜索
    results, total = search_service.search(
        query=q,
        search_type=search_type,
        filters=filters,
        skip=skip,
        limit=limit
    )
    
    return {
        "query": q,
        "type": search_type,
        "results": results,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/documents", response_model=SearchResponse)
async def search_documents(
    q: str = Query(..., min_length=2, description="搜索關鍵詞"),
    category_id: Optional[uuid.UUID] = Query(None, description="分類ID，用於篩選結果"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """搜索文檔"""
    search_service = SearchService(db)
    
    # 構建篩選條件
    filters = {}
    if category_id:
        filters["category_id"] = category_id
    
    # 執行搜索
    results, total = search_service.search(
        query=q,
        search_type="document",
        filters=filters,
        skip=skip,
        limit=limit
    )
    
    return {
        "query": q,
        "type": "document",
        "results": results,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/questions", response_model=SearchResponse)
async def search_questions(
    q: str = Query(..., min_length=2, description="搜索關鍵詞"),
    category_id: Optional[uuid.UUID] = Query(None, description="分類ID，用於篩選結果"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """搜索問題"""
    search_service = SearchService(db)
    
    # 構建篩選條件
    filters = {}
    if category_id:
        filters["category_id"] = category_id
    
    # 執行搜索
    results, total = search_service.search(
        query=q,
        search_type="question",
        filters=filters,
        skip=skip,
        limit=limit
    )
    
    return {
        "query": q,
        "type": "question",
        "results": results,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }