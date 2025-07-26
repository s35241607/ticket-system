from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import logging

# 導入模型和架構
from ..models.ticket import Workflow, WorkflowStep, Ticket
from ..schemas.workflow import WorkflowCreate, WorkflowUpdate, WorkflowStepCreate, WorkflowStepUpdate

# 配置日誌
logger = logging.getLogger("workflow_service")


class WorkflowService:
    def __init__(self, db: Session):
        self.db = db

    def get_workflows(self, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[Workflow]:
        """獲取工作流列表，支持分頁和篩選"""
        query = self.db.query(Workflow)

        # 應用篩選條件
        if filters and filters.get("search"):
            search_term = f"%{filters['search']}%"
            query = query.filter(
                or_(
                    Workflow.name.ilike(search_term),
                    Workflow.description.ilike(search_term)
                )
            )

        # 加載關聯數據
        query = query.options(joinedload(Workflow.steps))

        # 應用分頁
        query = query.order_by(Workflow.name).offset(skip).limit(limit)

        return query.all()

    def count_workflows(self, filters: Dict[str, Any] = None) -> int:
        """計算工作流總數，支持篩選"""
        query = self.db.query(func.count(Workflow.id))

        # 應用篩選條件
        if filters and filters.get("search"):
            search_term = f"%{filters['search']}%"
            query = query.filter(
                or_(
                    Workflow.name.ilike(search_term),
                    Workflow.description.ilike(search_term)
                )
            )

        return query.scalar()

    def create_workflow(self, workflow_data: WorkflowCreate) -> Workflow:
        """創建新工作流"""
        workflow = Workflow(**workflow_data.dict())
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def get_workflow(self, workflow_id: uuid.UUID) -> Optional[Workflow]:
        """獲取工作流詳情"""
        return self.db.query(Workflow).options(
            joinedload(Workflow.steps)
        ).filter(Workflow.id == workflow_id).first()

    def get_workflow_by_name(self, name: str) -> Optional[Workflow]:
        """通過名稱獲取工作流"""
        return self.db.query(Workflow).filter(Workflow.name == name).first()

    def update_workflow(self, workflow_id: uuid.UUID, workflow_update: WorkflowUpdate) -> Optional[Workflow]:
        """更新工作流"""
        workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            return None

        # 更新字段
        update_data = workflow_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(workflow, key, value)

        workflow.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def delete_workflow(self, workflow_id: uuid.UUID) -> bool:
        """刪除工作流"""
        workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            return False

        # 刪除工作流步驟
        self.db.query(WorkflowStep).filter(WorkflowStep.workflow_id == workflow_id).delete()
        
        # 刪除工作流
        self.db.delete(workflow)
        self.db.commit()
        return True

    def has_tickets(self, workflow_id: uuid.UUID) -> bool:
        """檢查工作流是否有關聯工單"""
        return self.db.query(Ticket).filter(Ticket.workflow_id == workflow_id).count() > 0

    def create_workflow_step(self, workflow_id: uuid.UUID, step_data: WorkflowStepCreate) -> WorkflowStep:
        """為工作流添加步驟"""
        step = WorkflowStep(**step_data.dict(), workflow_id=workflow_id)
        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)
        return step

    def get_workflow_steps(self, workflow_id: uuid.UUID) -> List[WorkflowStep]:
        """獲取工作流的所有步驟"""
        return self.db.query(WorkflowStep).filter(
            WorkflowStep.workflow_id == workflow_id
        ).order_by(WorkflowStep.order).all()

    def get_workflow_step(self, step_id: uuid.UUID) -> Optional[WorkflowStep]:
        """獲取工作流步驟詳情"""
        return self.db.query(WorkflowStep).filter(WorkflowStep.id == step_id).first()

    def update_workflow_step(self, step_id: uuid.UUID, step_update: WorkflowStepUpdate) -> Optional[WorkflowStep]:
        """更新工作流步驟"""
        step = self.db.query(WorkflowStep).filter(WorkflowStep.id == step_id).first()
        if not step:
            return None

        # 更新字段
        update_data = step_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(step, key, value)

        step.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(step)
        return step

    def delete_workflow_step(self, step_id: uuid.UUID) -> bool:
        """刪除工作流步驟"""
        step = self.db.query(WorkflowStep).filter(WorkflowStep.id == step_id).first()
        if not step:
            return False

        # 刪除步驟
        self.db.delete(step)
        self.db.commit()
        return True

    def step_order_exists(self, workflow_id: uuid.UUID, order: int, exclude_step_id: uuid.UUID = None) -> bool:
        """檢查工作流步驟順序是否已存在"""
        query = self.db.query(WorkflowStep).filter(
            WorkflowStep.workflow_id == workflow_id,
            WorkflowStep.order == order
        )
        
        if exclude_step_id:
            query = query.filter(WorkflowStep.id != exclude_step_id)
            
        return query.count() > 0