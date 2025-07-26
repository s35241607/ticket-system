from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

# 導入數據庫依賴
from database.session import get_db

# 導入模型和架構
from ..models.ticket import Department
from ..schemas.department import (
    DepartmentCreate, 
    DepartmentUpdate, 
    DepartmentResponse, 
    DepartmentListResponse
)

# 導入服務
from ..services.department_service import DepartmentService

# 創建路由
router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("/", response_model=DepartmentListResponse)
async def get_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """獲取部門列表，支持分頁和搜索"""
    department_service = DepartmentService(db)
    
    # 構建篩選條件
    filters = {}
    if search:
        filters["search"] = search
    
    departments = department_service.get_departments(skip=skip, limit=limit, filters=filters)
    total = department_service.count_departments(filters=filters)
    
    return {
        "items": departments,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(department: DepartmentCreate, db: Session = Depends(get_db)):
    """創建新部門"""
    department_service = DepartmentService(db)
    
    # 檢查部門名稱是否已存在
    existing_department = department_service.get_department_by_name(department.name)
    if existing_department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部門名稱已存在"
        )
    
    return department_service.create_department(department)


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(department_id: uuid.UUID, db: Session = Depends(get_db)):
    """獲取部門詳情"""
    department_service = DepartmentService(db)
    department = department_service.get_department(department_id)
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"部門 {department_id} 不存在"
        )
    
    return department


@router.put("/{department_id}", response_model=DepartmentResponse)
async def update_department(department_id: uuid.UUID, department_update: DepartmentUpdate, db: Session = Depends(get_db)):
    """更新部門信息"""
    department_service = DepartmentService(db)
    
    # 檢查部門是否存在
    existing_department = department_service.get_department(department_id)
    if not existing_department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"部門 {department_id} 不存在"
        )
    
    # 檢查部門名稱是否已被其他部門使用
    if department_update.name and department_update.name != existing_department.name:
        name_department = department_service.get_department_by_name(department_update.name)
        if name_department and name_department.id != department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部門名稱已被使用"
            )
    
    updated_department = department_service.update_department(department_id, department_update)
    return updated_department


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(department_id: uuid.UUID, db: Session = Depends(get_db)):
    """刪除部門"""
    department_service = DepartmentService(db)
    
    # 檢查部門是否存在
    existing_department = department_service.get_department(department_id)
    if not existing_department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"部門 {department_id} 不存在"
        )
    
    # 檢查部門是否有關聯用戶
    if department_service.has_users(department_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無法刪除有關聯用戶的部門"
        )
    
    success = department_service.delete_department(department_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刪除部門失敗"
        )
    
    return None


@router.get("/by-name/{name}", response_model=DepartmentResponse)
async def get_department_by_name(name: str, db: Session = Depends(get_db)):
    """通過名稱獲取部門"""
    department_service = DepartmentService(db)
    department = department_service.get_department_by_name(name)
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"部門名稱 {name} 不存在"
        )
    
    return department