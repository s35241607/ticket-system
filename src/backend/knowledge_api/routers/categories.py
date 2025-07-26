from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

# 導入數據庫依賴
from database.session import get_db

# 導入模型和架構
from ..models.knowledge import Category
from ..schemas.category import (
    CategoryCreate, 
    CategoryUpdate, 
    CategoryResponse, 
    CategoryListResponse
)

# 導入服務
from ..services.category_service import CategoryService

# 創建路由
router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=CategoryListResponse)
async def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    parent_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """獲取分類列表，支持分頁、父分類篩選和搜索"""
    category_service = CategoryService(db)
    
    # 構建篩選條件
    filters = {}
    if parent_id:
        filters["parent_id"] = parent_id
    if search:
        filters["search"] = search
    
    categories = category_service.get_categories(skip=skip, limit=limit, filters=filters)
    total = category_service.count_categories(filters=filters)
    
    return {
        "items": categories,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """創建新分類"""
    category_service = CategoryService(db)
    
    # 檢查分類名稱是否已存在於同一級別
    if category_service.name_exists_at_level(category.name, category.parent_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="同一級別下已存在相同名稱的分類"
        )
    
    # 檢查父分類是否存在
    if category.parent_id:
        parent = category_service.get_category(category.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"父分類 {category.parent_id} 不存在"
            )
    
    return category_service.create_category(category)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: uuid.UUID, db: Session = Depends(get_db)):
    """獲取分類詳情"""
    category_service = CategoryService(db)
    category = category_service.get_category(category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分類 {category_id} 不存在"
        )
    
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: uuid.UUID, category_update: CategoryUpdate, db: Session = Depends(get_db)):
    """更新分類信息"""
    category_service = CategoryService(db)
    
    # 檢查分類是否存在
    existing_category = category_service.get_category(category_id)
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分類 {category_id} 不存在"
        )
    
    # 檢查分類名稱是否已被同級別其他分類使用
    parent_id = category_update.parent_id if category_update.parent_id is not None else existing_category.parent_id
    if category_update.name and category_update.name != existing_category.name:
        if category_service.name_exists_at_level(category_update.name, parent_id, exclude_id=category_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="同一級別下已存在相同名稱的分類"
            )
    
    # 檢查父分類是否存在
    if category_update.parent_id and category_update.parent_id != existing_category.parent_id:
        parent = category_service.get_category(category_update.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"父分類 {category_update.parent_id} 不存在"
            )
        
        # 檢查是否將分類設置為自己的子分類
        if category_update.parent_id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能將分類設置為自己的子分類"
            )
        
        # 檢查是否將分類設置為自己的後代分類
        if category_service.is_descendant(category_id, category_update.parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能將分類設置為自己的後代分類"
            )
    
    updated_category = category_service.update_category(category_id, category_update)
    return updated_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: uuid.UUID, db: Session = Depends(get_db)):
    """刪除分類"""
    category_service = CategoryService(db)
    
    # 檢查分類是否存在
    existing_category = category_service.get_category(category_id)
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"分類 {category_id} 不存在"
        )
    
    # 檢查分類是否有子分類
    if category_service.has_children(category_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無法刪除有子分類的分類"
        )
    
    # 檢查分類是否有關聯文檔
    if category_service.has_documents(category_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無法刪除有關聯文檔的分類"
        )
    
    success = category_service.delete_category(category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刪除分類失敗"
        )
    
    return None


@router.get("/tree/all", response_model=List[CategoryResponse])
async def get_category_tree(db: Session = Depends(get_db)):
    """獲取分類樹結構"""
    category_service = CategoryService(db)
    return category_service.get_category_tree()