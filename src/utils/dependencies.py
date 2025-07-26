from typing import Annotated, List, Optional

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from src.config import settings
from src.database.db import get_db
from src.utils.security import get_current_active_user


# 數據庫會話依賴
DBSession = Annotated[Session, Depends(get_db)]

# 當前用戶依賴
CurrentUser = Annotated[dict, Depends(get_current_active_user)]


# 分頁參數依賴
def pagination_params(
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="每頁大小",
    ),
) -> dict:
    """
    分頁參數依賴

    Args:
        page: 頁碼，默認為1
        page_size: 每頁大小，默認為配置中的DEFAULT_PAGE_SIZE

    Returns:
        包含分頁參數的字典
    """
    return {"page": page, "page_size": page_size}


# 搜索參數依賴
def search_params(
    q: Optional[str] = Query(None, min_length=1, max_length=100, description="搜索關鍵詞"),
    limit: int = Query(
        settings.SEARCH_RESULT_LIMIT,
        ge=1,
        le=100,
        description="結果數量限制",
    ),
) -> dict:
    """
    搜索參數依賴

    Args:
        q: 搜索關鍵詞
        limit: 結果數量限制

    Returns:
        包含搜索參數的字典
    """
    return {"q": q, "limit": limit}


# 排序參數依賴
def sort_params(
    sort_by: Optional[str] = Query(None, description="排序字段"),
    sort_order: Optional[str] = Query(
        "desc", pattern="^(asc|desc)$", description="排序順序 (asc 或 desc)"
    ),
) -> dict:
    """
    排序參數依賴

    Args:
        sort_by: 排序字段
        sort_order: 排序順序 (asc 或 desc)

    Returns:
        包含排序參數的字典
    """
    return {"sort_by": sort_by, "sort_order": sort_order}


# 過濾參數依賴
def filter_params(
    category_id: Optional[int] = Query(None, ge=1, description="分類ID"),
    status: Optional[str] = Query(None, description="狀態"),
    created_by: Optional[int] = Query(None, ge=1, description="創建者ID"),
    department_id: Optional[int] = Query(None, ge=1, description="部門ID"),
    priority: Optional[str] = Query(None, description="優先級"),
    date_from: Optional[str] = Query(None, description="開始日期 (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="結束日期 (YYYY-MM-DD)"),
) -> dict:
    """
    過濾參數依賴

    Args:
        category_id: 分類ID
        status: 狀態
        created_by: 創建者ID
        department_id: 部門ID
        priority: 優先級
        date_from: 開始日期 (YYYY-MM-DD)
        date_to: 結束日期 (YYYY-MM-DD)

    Returns:
        包含過濾參數的字典
    """
    return {
        "category_id": category_id,
        "status": status,
        "created_by": created_by,
        "department_id": department_id,
        "priority": priority,
        "date_from": date_from,
        "date_to": date_to,
    }