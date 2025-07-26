from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

# 導入數據庫依賴
from database.session import get_db

# 導入模型和架構
from ..models.ticket import Ticket, TicketAttachment, TicketComment, TicketHistory, WorkflowApproval
from ..schemas.ticket import (
    TicketCreate, 
    TicketUpdate, 
    TicketResponse, 
    TicketListResponse,
    TicketCommentCreate,
    TicketCommentResponse,
    TicketAttachmentResponse,
    WorkflowApprovalCreate,
    WorkflowApprovalResponse
)

# 導入服務
from ..services.ticket_service import TicketService

# 創建路由
router = APIRouter()

# 獲取工單服務實例
def get_ticket_service(db: Session = Depends(get_db)):
    return TicketService(db)


@router.get("/", response_model=List[TicketListResponse])
async def get_tickets(
    skip: int = Query(0, description="跳過的記錄數"),
    limit: int = Query(100, description="返回的最大記錄數"),
    status_id: Optional[uuid.UUID] = Query(None, description="按狀態篩選"),
    priority_id: Optional[uuid.UUID] = Query(None, description="按優先級篩選"),
    type_id: Optional[uuid.UUID] = Query(None, description="按類型篩選"),
    assignee_id: Optional[uuid.UUID] = Query(None, description="按負責人篩選"),
    creator_id: Optional[uuid.UUID] = Query(None, description="按創建者篩選"),
    search: Optional[str] = Query(None, description="搜索標題和描述"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """獲取工單列表，支持分頁和篩選"""
    filters = {
        "status_id": status_id,
        "priority_id": priority_id,
        "type_id": type_id,
        "assignee_id": assignee_id,
        "creator_id": creator_id,
        "search": search
    }
    return ticket_service.get_tickets(skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket: TicketCreate,
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """創建新工單"""
    return ticket_service.create_ticket(ticket)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: uuid.UUID = Path(..., description="工單ID"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """獲取工單詳情"""
    ticket = ticket_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工單 {ticket_id} 不存在"
        )
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: uuid.UUID = Path(..., description="工單ID"),
    ticket_update: TicketUpdate = Body(...),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """更新工單"""
    ticket = ticket_service.update_ticket(ticket_id, ticket_update)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工單 {ticket_id} 不存在"
        )
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: uuid.UUID = Path(..., description="工單ID"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """刪除工單"""
    success = ticket_service.delete_ticket(ticket_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"工單 {ticket_id} 不存在"
        )
    return None


@router.post("/{ticket_id}/comments", response_model=TicketCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket_comment(
    ticket_id: uuid.UUID = Path(..., description="工單ID"),
    comment: TicketCommentCreate = Body(...),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """添加工單評論"""
    return ticket_service.add_comment(ticket_id, comment)


@router.get("/{ticket_id}/comments", response_model=List[TicketCommentResponse])
async def get_ticket_comments(
    ticket_id: uuid.UUID = Path(..., description="工單ID"),
    skip: int = Query(0, description="跳過的記錄數"),
    limit: int = Query(100, description="返回的最大記錄數"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """獲取工單評論列表"""
    return ticket_service.get_comments(ticket_id, skip, limit)


@router.post("/{ticket_id}/attachments", response_model=TicketAttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_ticket_attachment(
    ticket_id: uuid.UUID = Path(..., description="工單ID"),
    file: UploadFile = File(...),
    user_id: uuid.UUID = Query(..., description="上傳用戶ID"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """上傳工單附件"""
    return ticket_service.add_attachment(ticket_id, user_id, file)


@router.get("/{ticket_id}/attachments", response_model=List[TicketAttachmentResponse])
async def get_ticket_attachments(
    ticket_id: uuid.UUID = Path(..., description="工單ID"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """獲取工單附件列表"""
    return ticket_service.get_attachments(ticket_id)


@router.post("/{ticket_id}/approvals", response_model=WorkflowApprovalResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow_approval(
    ticket_id: uuid.UUID = Path(..., description="工單ID"),
    approval: WorkflowApprovalCreate = Body(...),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """提交工作流審批"""
    return ticket_service.submit_approval(ticket_id, approval)


@router.get("/{ticket_id}/approvals", response_model=List[WorkflowApprovalResponse])
async def get_workflow_approvals(
    ticket_id: uuid.UUID = Path(..., description="工單ID"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """獲取工單審批歷史"""
    return ticket_service.get_approvals(ticket_id)


@router.get("/{ticket_id}/history", response_model=List[dict])
async def get_ticket_history(
    ticket_id: uuid.UUID = Path(..., description="工單ID"),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """獲取工單歷史記錄"""
    return ticket_service.get_history(ticket_id)