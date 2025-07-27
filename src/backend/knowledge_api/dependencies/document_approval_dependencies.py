from fastapi import Depends
from sqlalchemy.orm import Session

from ....database.session import get_db
from ....domain.repositories.document_approval_workflow_repository import DocumentApprovalWorkflowRepository
from ....domain.repositories.document_approval_repository import DocumentApprovalRepository
from ....domain.repositories.document_approval_action_repository import DocumentApprovalActionRepository
from ....infrastructure.repositories.document_approval_workflow_repository_impl import DocumentApprovalWorkflowRepositoryImpl
from ....infrastructure.repositories.document_approval_repository_impl import DocumentApprovalRepositoryImpl
from ....infrastructure.repositories.document_approval_action_repository_impl import DocumentApprovalActionRepositoryImpl


def get_document_approval_workflow_repository(
    db: Session = Depends(get_db)
) -> DocumentApprovalWorkflowRepository:
    """獲取文檔審批工作流儲存庫"""
    return DocumentApprovalWorkflowRepositoryImpl(db)


def get_document_approval_repository(
    db: Session = Depends(get_db)
) -> DocumentApprovalRepository:
    """獲取文檔審批儲存庫"""
    return DocumentApprovalRepositoryImpl(db)


def get_document_approval_action_repository(
    db: Session = Depends(get_db)
) -> DocumentApprovalActionRepository:
    """獲取文檔審批行為儲存庫"""
    return DocumentApprovalActionRepositoryImpl(db)