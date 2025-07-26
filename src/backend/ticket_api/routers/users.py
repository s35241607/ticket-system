from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

# 導入數據庫依賴
from database.session import get_db

# 導入模型和架構
from ..models.ticket import User, Department
from ..schemas.user import (
    UserCreate, 
    UserUpdate, 
    UserResponse, 
    UserListResponse
)

# 導入服務
from ..services.user_service import UserService

# 創建路由
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    department_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """獲取用戶列表，支持分頁、部門篩選和搜索"""
    user_service = UserService(db)
    
    # 構建篩選條件
    filters = {}
    if department_id:
        filters["department_id"] = department_id
    if search:
        filters["search"] = search
    
    users = user_service.get_users(skip=skip, limit=limit, filters=filters)
    total = user_service.count_users(filters=filters)
    
    return {
        "items": users,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """創建新用戶"""
    user_service = UserService(db)
    
    # 檢查用戶名是否已存在
    existing_user = user_service.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用戶名已存在"
        )
    
    # 檢查部門是否存在
    if user.department_id:
        department = db.query(Department).filter(Department.id == user.department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"部門 {user.department_id} 不存在"
            )
    
    return user_service.create_user(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """獲取用戶詳情"""
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用戶 {user_id} 不存在"
        )
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: uuid.UUID, user_update: UserUpdate, db: Session = Depends(get_db)):
    """更新用戶信息"""
    user_service = UserService(db)
    
    # 檢查用戶是否存在
    existing_user = user_service.get_user(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用戶 {user_id} 不存在"
        )
    
    # 檢查用戶名是否已被其他用戶使用
    if user_update.username and user_update.username != existing_user.username:
        username_user = user_service.get_user_by_username(user_update.username)
        if username_user and username_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用戶名已被使用"
            )
    
    # 檢查部門是否存在
    if user_update.department_id:
        department = db.query(Department).filter(Department.id == user_update.department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"部門 {user_update.department_id} 不存在"
            )
    
    updated_user = user_service.update_user(user_id, user_update)
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """刪除用戶"""
    user_service = UserService(db)
    
    # 檢查用戶是否存在
    existing_user = user_service.get_user(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用戶 {user_id} 不存在"
        )
    
    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刪除用戶失敗"
        )
    
    return None


@router.get("/by-username/{username}", response_model=UserResponse)
async def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """通過用戶名獲取用戶"""
    user_service = UserService(db)
    user = user_service.get_user_by_username(username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用戶名 {username} 不存在"
        )
    
    return user