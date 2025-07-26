from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

# 導入數據庫依賴
from database.session import get_db

# 導入模型和架構
from ..models.ticket import Workflow, WorkflowStep
from ..schemas.workflow import (
    WorkflowCreate, 
    WorkflowUpdate, 
    WorkflowResponse, 
    WorkflowListResponse,
    WorkflowStepCreate,
    WorkflowStepUpdate,
    WorkflowStepResponse
)

# 導入服務
from ..services.workflow_service import WorkflowService

# 創建路由
router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/", response_model=WorkflowListResponse)
async def get_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """獲取工作流列表，支持分頁和搜索"""
    workflow_service = WorkflowService(db)
    
    # 構建篩選條件
    filters = {}
    if search:
        filters["search"] = search
    
    workflows = workflow_service.get_workflows(skip=skip, limit=limit, filters=filters)
    total = workflow_service.count_workflows(filters=filters)
    
    return {
        "items": workflows,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit
    }


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    """創建新工作流"""
    workflow_service = WorkflowService(db)
    
    # 檢查工作流名稱是否已存在
    existing_workflow = workflow_service.get_workflow_by_name(workflow.name)
    if existing_workflow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="工作流名稱已存在"
        )
    
    return workflow_service.create_workflow(workflow)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: uuid.UUID, db: Session = Depends(get_db)):
    """獲取工作流詳情"""
    workflow_service = WorkflowService(db)
    workflow = workflow_service.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作流 {workflow_id} 不存在"
        )
    
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(workflow_id: uuid.UUID, workflow_update: WorkflowUpdate, db: Session = Depends(get_db)):
    """更新工作流信息"""
    workflow_service = WorkflowService(db)
    
    # 檢查工作流是否存在
    existing_workflow = workflow_service.get_workflow(workflow_id)
    if not existing_workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作流 {workflow_id} 不存在"
        )
    
    # 檢查工作流名稱是否已被其他工作流使用
    if workflow_update.name and workflow_update.name != existing_workflow.name:
        name_workflow = workflow_service.get_workflow_by_name(workflow_update.name)
        if name_workflow and name_workflow.id != workflow_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="工作流名稱已被使用"
            )
    
    updated_workflow = workflow_service.update_workflow(workflow_id, workflow_update)
    return updated_workflow


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(workflow_id: uuid.UUID, db: Session = Depends(get_db)):
    """刪除工作流"""
    workflow_service = WorkflowService(db)
    
    # 檢查工作流是否存在
    existing_workflow = workflow_service.get_workflow(workflow_id)
    if not existing_workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作流 {workflow_id} 不存在"
        )
    
    # 檢查工作流是否有關聯工單
    if workflow_service.has_tickets(workflow_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無法刪除有關聯工單的工作流"
        )
    
    success = workflow_service.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刪除工作流失敗"
        )
    
    return None


@router.post("/{workflow_id}/steps", response_model=WorkflowStepResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow_step(workflow_id: uuid.UUID, step: WorkflowStepCreate, db: Session = Depends(get_db)):
    """為工作流添加步驟"""
    workflow_service = WorkflowService(db)
    
    # 檢查工作流是否存在
    existing_workflow = workflow_service.get_workflow(workflow_id)
    if not existing_workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作流 {workflow_id} 不存在"
        )
    
    # 檢查步驟順序是否已存在
    if workflow_service.step_order_exists(workflow_id, step.order):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"工作流步驟順序 {step.order} 已存在"
        )
    
    return workflow_service.create_workflow_step(workflow_id, step)


@router.get("/{workflow_id}/steps", response_model=List[WorkflowStepResponse])
async def get_workflow_steps(workflow_id: uuid.UUID, db: Session = Depends(get_db)):
    """獲取工作流的所有步驟"""
    workflow_service = WorkflowService(db)
    
    # 檢查工作流是否存在
    existing_workflow = workflow_service.get_workflow(workflow_id)
    if not existing_workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作流 {workflow_id} 不存在"
        )
    
    return workflow_service.get_workflow_steps(workflow_id)


@router.put("/{workflow_id}/steps/{step_id}", response_model=WorkflowStepResponse)
async def update_workflow_step(workflow_id: uuid.UUID, step_id: uuid.UUID, step_update: WorkflowStepUpdate, db: Session = Depends(get_db)):
    """更新工作流步驟"""
    workflow_service = WorkflowService(db)
    
    # 檢查工作流是否存在
    existing_workflow = workflow_service.get_workflow(workflow_id)
    if not existing_workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作流 {workflow_id} 不存在"
        )
    
    # 檢查步驟是否存在
    existing_step = workflow_service.get_workflow_step(step_id)
    if not existing_step or existing_step.workflow_id != workflow_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作流步驟 {step_id} 不存在"
        )
    
    # 檢查步驟順序是否已被其他步驟使用
    if step_update.order and step_update.order != existing_step.order:
        if workflow_service.step_order_exists(workflow_id, step_update.order, exclude_step_id=step_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"工作流步驟順序 {step_update.order} 已存在"
            )
    
    updated_step = workflow_service.update_workflow_step(step_id, step_update)
    return updated_step


@router.delete("/{workflow_id}/steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow_step(workflow_id: uuid.UUID, step_id: uuid.UUID, db: Session = Depends(get_db)):
    """刪除工作流步驟"""
    workflow_service = WorkflowService(db)
    
    # 檢查工作流是否存在
    existing_workflow = workflow_service.get_workflow(workflow_id)
    if not existing_workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作流 {workflow_id} 不存在"
        )
    
    # 檢查步驟是否存在
    existing_step = workflow_service.get_workflow_step(step_id)
    if not existing_step or existing_step.workflow_id != workflow_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工作流步驟 {step_id} 不存在"
        )
    
    success = workflow_service.delete_workflow_step(step_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刪除工作流步驟失敗"
        )
    
    return None