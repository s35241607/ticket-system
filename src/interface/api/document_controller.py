from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import uuid

# 應用層用例
from ...application.use_cases.document_use_cases import (
    CreateDocumentUseCase, UpdateDocumentUseCase, GetDocumentUseCase,
    ListDocumentsUseCase, PublishDocumentUseCase, UnpublishDocumentUseCase,
    DeleteDocumentUseCase, AddDocumentTagUseCase, RemoveDocumentTagUseCase
)

# 基礎設施層實現
from ...infrastructure.repositories.document_repository_impl import SQLAlchemyDocumentRepository
from ...infrastructure.events.event_publisher_impl import InMemoryEventPublisher

# 數據庫依賴
from ....backend.database import get_db

# 請求和響應模型
from ....backend.knowledge_api.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentListResponse,
    DocumentTagResponse, DocumentCommentCreate, DocumentCommentResponse,
    DocumentAttachmentResponse
)

# 創建路由器
router = APIRouter()

# 創建事件發布者
event_publisher = InMemoryEventPublisher()

# 註冊事件處理器
from ...infrastructure.events.event_publisher_impl import register_event_handlers
register_event_handlers(event_publisher)


# 依賴注入函數
def get_document_repository(db: Session = Depends(get_db)):
    return SQLAlchemyDocumentRepository(db)


def get_create_document_use_case(repo = Depends(get_document_repository)):
    return CreateDocumentUseCase(repo, event_publisher)


def get_update_document_use_case(repo = Depends(get_document_repository)):
    return UpdateDocumentUseCase(repo, event_publisher)


def get_get_document_use_case(repo = Depends(get_document_repository)):
    return GetDocumentUseCase(repo, event_publisher)


def get_list_documents_use_case(repo = Depends(get_document_repository)):
    return ListDocumentsUseCase(repo)


def get_publish_document_use_case(repo = Depends(get_document_repository)):
    return PublishDocumentUseCase(repo, event_publisher)


def get_unpublish_document_use_case(repo = Depends(get_document_repository)):
    return UnpublishDocumentUseCase(repo)


def get_delete_document_use_case(repo = Depends(get_document_repository)):
    return DeleteDocumentUseCase(repo)


def get_add_document_tag_use_case(repo = Depends(get_document_repository)):
    return AddDocumentTagUseCase(repo, event_publisher)


def get_remove_document_tag_use_case(repo = Depends(get_document_repository)):
    return RemoveDocumentTagUseCase(repo, event_publisher)


# API 路由
@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    use_case: CreateDocumentUseCase = Depends(get_create_document_use_case)
):
    """創建文檔"""
    try:
        # 將請求模型轉換為用例參數
        created_document = use_case.execute(
            title=document.title,
            content=document.content,
            category_id=uuid.UUID(document.category_id),
            creator_id=uuid.UUID(document.creator_id),
            summary=document.summary,
            tags=[uuid.UUID(tag_id) for tag_id in document.tags] if document.tags else None
        )
        
        # 將領域實體轉換為響應模型
        return _document_entity_to_response(created_document)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    category_id: Optional[str] = None,
    creator_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    use_case: ListDocumentsUseCase = Depends(get_list_documents_use_case)
):
    """獲取文檔列表"""
    # 構建過濾條件
    filters = {}
    if category_id:
        filters['category_id'] = uuid.UUID(category_id)
    if creator_id:
        filters['creator_id'] = uuid.UUID(creator_id)
    if status:
        from ...domain.value_objects.document_status import DocumentStatus
        filters['status'] = DocumentStatus[status.upper()]
    
    # 獲取文檔列表
    documents = use_case.execute(filters, skip, limit)
    
    # 將領域實體轉換為響應模型
    items = [_document_entity_to_response(doc) for doc in documents]
    return {"items": items, "total": len(items)}


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    use_case: GetDocumentUseCase = Depends(get_get_document_use_case)
):
    """獲取文檔詳情"""
    document = use_case.execute(uuid.UUID(document_id))
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return _document_entity_to_response(document)


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document: DocumentUpdate,
    use_case: UpdateDocumentUseCase = Depends(get_update_document_use_case)
):
    """更新文檔"""
    updated_document = use_case.execute(
        document_id=uuid.UUID(document_id),
        title=document.title,
        content=document.content,
        summary=document.summary,
        category_id=uuid.UUID(document.category_id) if document.category_id else None
    )
    
    if not updated_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return _document_entity_to_response(updated_document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    use_case: DeleteDocumentUseCase = Depends(get_delete_document_use_case)
):
    """刪除文檔"""
    success = use_case.execute(uuid.UUID(document_id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )


@router.post("/{document_id}/publish", response_model=DocumentResponse)
async def publish_document(
    document_id: str,
    use_case: PublishDocumentUseCase = Depends(get_publish_document_use_case)
):
    """發布文檔"""
    published_document = use_case.execute(uuid.UUID(document_id))
    if not published_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return _document_entity_to_response(published_document)


@router.post("/{document_id}/unpublish", response_model=DocumentResponse)
async def unpublish_document(
    document_id: str,
    use_case: UnpublishDocumentUseCase = Depends(get_unpublish_document_use_case)
):
    """取消發布文檔"""
    unpublished_document = use_case.execute(uuid.UUID(document_id))
    if not unpublished_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return _document_entity_to_response(unpublished_document)


@router.post("/{document_id}/tags/{tag_id}", response_model=DocumentResponse)
async def add_document_tag(
    document_id: str,
    tag_id: str,
    user_id: str,  # 假設從請求中獲取用戶ID
    use_case: AddDocumentTagUseCase = Depends(get_add_document_tag_use_case)
):
    """添加文檔標籤"""
    updated_document = use_case.execute(
        document_id=uuid.UUID(document_id),
        tag_id=uuid.UUID(tag_id),
        user_id=uuid.UUID(user_id)
    )
    
    if not updated_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return _document_entity_to_response(updated_document)


@router.delete("/{document_id}/tags/{tag_id}", response_model=DocumentResponse)
async def remove_document_tag(
    document_id: str,
    tag_id: str,
    user_id: str,  # 假設從請求中獲取用戶ID
    use_case: RemoveDocumentTagUseCase = Depends(get_remove_document_tag_use_case)
):
    """移除文檔標籤"""
    updated_document = use_case.execute(
        document_id=uuid.UUID(document_id),
        tag_id=uuid.UUID(tag_id),
        user_id=uuid.UUID(user_id)
    )
    
    if not updated_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return _document_entity_to_response(updated_document)


# 輔助函數
def _document_entity_to_response(document):
    """將文檔實體轉換為響應模型"""
    return {
        "id": str(document.id),
        "title": document.title,
        "content": document.content,
        "summary": document.summary,
        "category_id": str(document.category_id),
        "creator_id": str(document.creator_id),
        "status": document.status.name,
        "view_count": document.view_count,
        "created_at": document.created_at,
        "updated_at": document.updated_at,
        "published_at": document.published_at,
        "tags": [str(tag_id) for tag_id in document.tags]
    }