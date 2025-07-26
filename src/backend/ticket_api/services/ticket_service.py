from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_
from fastapi import UploadFile, HTTPException, status
from typing import List, Dict, Any, Optional
import uuid
import os
import shutil
from datetime import datetime
import logging

# 導入模型和架構
from ..models.ticket import (
    Ticket, 
    TicketAttachment, 
    TicketComment, 
    TicketHistory, 
    WorkflowApproval,
    User,
    Department,
    Workflow,
    WorkflowStep,
    TicketType,
    TicketStatus,
    TicketPriority
)
from ..schemas.ticket import (
    TicketCreate, 
    TicketUpdate, 
    TicketCommentCreate,
    WorkflowApprovalCreate
)

# 配置日誌
logger = logging.getLogger("ticket_service")


class TicketService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = os.path.join("static", "uploads", "tickets")
        os.makedirs(self.upload_dir, exist_ok=True)

    def get_tickets(self, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[Ticket]:
        """獲取工單列表，支持分頁和篩選"""
        query = self.db.query(Ticket)

        # 應用篩選條件
        if filters:
            if filters.get("status_id"):
                query = query.filter(Ticket.ticket_status_id == filters["status_id"])
            if filters.get("priority_id"):
                query = query.filter(Ticket.ticket_priority_id == filters["priority_id"])
            if filters.get("type_id"):
                query = query.filter(Ticket.ticket_type_id == filters["type_id"])
            if filters.get("assignee_id"):
                query = query.filter(Ticket.assignee_id == filters["assignee_id"])
            if filters.get("creator_id"):
                query = query.filter(Ticket.creator_id == filters["creator_id"])
            if filters.get("search"):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Ticket.title.ilike(search_term),
                        Ticket.description.ilike(search_term)
                    )
                )

        # 加載關聯數據
        query = query.options(
            joinedload(Ticket.creator),
            joinedload(Ticket.assignee),
            joinedload(Ticket.ticket_type),
            joinedload(Ticket.ticket_status),
            joinedload(Ticket.ticket_priority),
            joinedload(Ticket.current_workflow_step)
        )

        # 應用分頁
        query = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit)

        return query.all()

    def create_ticket(self, ticket_data: TicketCreate) -> Ticket:
        """創建新工單"""
        # 獲取工單類型對應的工作流
        ticket_type = self.db.query(TicketType).filter(TicketType.id == ticket_data.ticket_type_id).first()
        if not ticket_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"工單類型 {ticket_data.ticket_type_id} 不存在"
            )

        # 獲取工作流的第一個步驟
        first_step = self.db.query(WorkflowStep).filter(
            WorkflowStep.workflow_id == ticket_type.workflow_id,
            WorkflowStep.order == 1
        ).first()

        # 創建工單
        ticket_dict = ticket_data.dict()
        ticket_dict["current_workflow_step_id"] = first_step.id if first_step else None
        
        ticket = Ticket(**ticket_dict)
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        # 記錄歷史
        history = TicketHistory(
            ticket_id=ticket.id,
            user_id=ticket_data.creator_id,
            action="created",
            changes={"ticket": "created"}
        )
        self.db.add(history)
        self.db.commit()

        return ticket

    def get_ticket(self, ticket_id: uuid.UUID) -> Optional[Ticket]:
        """獲取工單詳情"""
        return self.db.query(Ticket).options(
            joinedload(Ticket.creator),
            joinedload(Ticket.assignee),
            joinedload(Ticket.ticket_type),
            joinedload(Ticket.ticket_status),
            joinedload(Ticket.ticket_priority),
            joinedload(Ticket.current_workflow_step)
        ).filter(Ticket.id == ticket_id).first()

    def update_ticket(self, ticket_id: uuid.UUID, ticket_update: TicketUpdate) -> Optional[Ticket]:
        """更新工單"""
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return None

        # 記錄變更前的數據
        old_data = {}
        update_data = ticket_update.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            if hasattr(ticket, key) and getattr(ticket, key) != value:
                old_data[key] = getattr(ticket, key)
                setattr(ticket, key, value)

        # 如果狀態變為已關閉，設置關閉時間
        if "ticket_status_id" in update_data:
            status = self.db.query(TicketStatus).filter(TicketStatus.id == update_data["ticket_status_id"]).first()
            if status and status.name.lower() in ["closed", "resolved", "completed"]:
                ticket.closed_at = datetime.now()

        self.db.commit()
        self.db.refresh(ticket)

        # 記錄歷史
        if old_data:
            history = TicketHistory(
                ticket_id=ticket.id,
                user_id=update_data.get("user_id", ticket.creator_id),  # 假設更新者ID在請求中提供
                action="updated",
                changes={"old": old_data, "new": update_data}
            )
            self.db.add(history)
            self.db.commit()

        return ticket

    def delete_ticket(self, ticket_id: uuid.UUID) -> bool:
        """刪除工單"""
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return False

        # 刪除相關數據
        self.db.query(TicketAttachment).filter(TicketAttachment.ticket_id == ticket_id).delete()
        self.db.query(TicketComment).filter(TicketComment.ticket_id == ticket_id).delete()
        self.db.query(TicketHistory).filter(TicketHistory.ticket_id == ticket_id).delete()
        self.db.query(WorkflowApproval).filter(WorkflowApproval.ticket_id == ticket_id).delete()
        
        self.db.delete(ticket)
        self.db.commit()
        return True

    def add_comment(self, ticket_id: uuid.UUID, comment_data: TicketCommentCreate) -> TicketComment:
        """添加工單評論"""
        # 檢查工單是否存在
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"工單 {ticket_id} 不存在"
            )

        comment = TicketComment(**comment_data.dict())
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)

        # 記錄歷史
        history = TicketHistory(
            ticket_id=ticket_id,
            user_id=comment_data.user_id,
            action="commented",
            changes={"comment_id": str(comment.id)}
        )
        self.db.add(history)
        self.db.commit()

        return comment

    def get_comments(self, ticket_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[TicketComment]:
        """獲取工單評論列表"""
        return self.db.query(TicketComment).options(
            joinedload(TicketComment.user)
        ).filter(TicketComment.ticket_id == ticket_id).order_by(
            TicketComment.created_at.desc()
        ).offset(skip).limit(limit).all()

    def add_attachment(self, ticket_id: uuid.UUID, user_id: uuid.UUID, file: UploadFile) -> TicketAttachment:
        """上傳工單附件"""
        # 檢查工單是否存在
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"工單 {ticket_id} 不存在"
            )

        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 獲取文件類型和大小
        file_type = file.content_type
        file_size = os.path.getsize(file_path)

        # 創建附件記錄
        attachment = TicketAttachment(
            ticket_id=ticket_id,
            user_id=user_id,
            filename=file.filename,
            file_path=os.path.join("uploads", "tickets", unique_filename),
            file_type=file_type,
            file_size=file_size
        )
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)

        # 記錄歷史
        history = TicketHistory(
            ticket_id=ticket_id,
            user_id=user_id,
            action="attached_file",
            changes={"attachment_id": str(attachment.id), "filename": file.filename}
        )
        self.db.add(history)
        self.db.commit()

        return attachment

    def get_attachments(self, ticket_id: uuid.UUID) -> List[TicketAttachment]:
        """獲取工單附件列表"""
        return self.db.query(TicketAttachment).options(
            joinedload(TicketAttachment.user)
        ).filter(TicketAttachment.ticket_id == ticket_id).order_by(
            TicketAttachment.created_at.desc()
        ).all()

    def submit_approval(self, ticket_id: uuid.UUID, approval_data: WorkflowApprovalCreate) -> WorkflowApproval:
        """提交工作流審批"""
        # 檢查工單是否存在
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"工單 {ticket_id} 不存在"
            )

        # 檢查工作流步驟是否存在
        step = self.db.query(WorkflowStep).filter(WorkflowStep.id == approval_data.workflow_step_id).first()
        if not step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"工作流步驟 {approval_data.workflow_step_id} 不存在"
            )

        # 創建審批記錄
        approval = WorkflowApproval(**approval_data.dict())
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)

        # 如果審批通過，且當前工單的工作流步驟與審批的步驟相同，則更新工單的工作流步驟
        if approval.is_approved and ticket.current_workflow_step_id == approval_data.workflow_step_id:
            # 獲取下一個工作流步驟
            next_step = self.db.query(WorkflowStep).filter(
                WorkflowStep.workflow_id == step.workflow_id,
                WorkflowStep.order == step.order + 1
            ).first()

            if next_step:
                ticket.current_workflow_step_id = next_step.id
                self.db.commit()
                self.db.refresh(ticket)

                # 記錄歷史
                history = TicketHistory(
                    ticket_id=ticket_id,
                    user_id=approval_data.approver_id,
                    action="workflow_advanced",
                    changes={
                        "from_step_id": str(step.id),
                        "from_step_name": step.name,
                        "to_step_id": str(next_step.id),
                        "to_step_name": next_step.name
                    }
                )
                self.db.add(history)
                self.db.commit()
            elif step.is_final:
                # 如果是最後一個步驟，將工單標記為已完成
                closed_status = self.db.query(TicketStatus).filter(
                    TicketStatus.name.ilike("completed")
                ).first()
                
                if closed_status:
                    ticket.ticket_status_id = closed_status.id
                    ticket.closed_at = datetime.now()
                    self.db.commit()
                    self.db.refresh(ticket)

                    # 記錄歷史
                    history = TicketHistory(
                        ticket_id=ticket_id,
                        user_id=approval_data.approver_id,
                        action="workflow_completed",
                        changes={
                            "final_step_id": str(step.id),
                            "final_step_name": step.name
                        }
                    )
                    self.db.add(history)
                    self.db.commit()

        # 記錄審批歷史
        history = TicketHistory(
            ticket_id=ticket_id,
            user_id=approval_data.approver_id,
            action="approval_submitted",
            changes={
                "approval_id": str(approval.id),
                "step_id": str(step.id),
                "step_name": step.name,
                "is_approved": approval.is_approved
            }
        )
        self.db.add(history)
        self.db.commit()

        return approval

    def get_approvals(self, ticket_id: uuid.UUID) -> List[WorkflowApproval]:
        """獲取工單審批歷史"""
        return self.db.query(WorkflowApproval).options(
            joinedload(WorkflowApproval.approver),
            joinedload(WorkflowApproval.workflow_step)
        ).filter(WorkflowApproval.ticket_id == ticket_id).order_by(
            WorkflowApproval.created_at.desc()
        ).all()

    def get_history(self, ticket_id: uuid.UUID) -> List[Dict[str, Any]]:
        """獲取工單歷史記錄"""
        history_records = self.db.query(TicketHistory).options(
            joinedload(TicketHistory.user)
        ).filter(TicketHistory.ticket_id == ticket_id).order_by(
            TicketHistory.created_at.desc()
        ).all()

        # 轉換為更易讀的格式
        result = []
        for record in history_records:
            item = {
                "id": record.id,
                "user_id": record.user_id,
                "user_name": record.user.full_name if record.user else None,
                "action": record.action,
                "changes": record.changes,
                "created_at": record.created_at
            }
            result.append(item)

        return result