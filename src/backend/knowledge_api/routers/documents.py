from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

# 導入數據庫依賴
from database.session import get_db

# 導入模型和架構
from ..models.knowledge import Document, DocumentAttachment, DocumentComment, DocumentHistory, DocumentTag
from ..schemas.document import (
    DocumentCreate, 
    DocumentUpdate, 
    DocumentResponse, 
    DocumentListResponse,
    DocumentCommentCreate,
    DocumentCommentResponse,
    DocumentAttachmentResponse,
    DocumentTagResponse
)

# 導入服務
from ..services.document_service import DocumentService

# 創建路由
router = APIRouter()

# 獲取文檔服務實例
def get_document_service(db: Session = Depends(get_db)):
    return DocumentService(db)


@router.get("/", response_model=List[DocumentListResponse])
async def get_documents(
    skip: int = Query(0, description="跳過的記錄數"),
    limit: int = Query(100, description="返回的最大記錄數"),
    category_id: Optional[uuid.UUID] = Query(None, description="按分類篩選"),
    creator_id: Optional[uuid.UUID] = Query(None, description="按創建者篩選"),
    is_published: Optional[bool] = Query(None, description="按發布狀態篩選"),
    tag_id: Optional[uuid.UUID] = Query(None, description="按標籤篩選"),
    search: Optional[str] = Query(None, description="搜索標題和內容"),
    document_service: DocumentService = Depends(get_document_service)
):
    """獲取文檔列表，支持分頁和篩選"""
    filters = {
        "category_id": category_id,
        "creator_id": creator_id,
        "is_published": is_published,
        "tag_id": tag_id,
        "search": search
    }
    return document_service.get_documents(skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    document_service: DocumentService = Depends(get_document_service)
):
    """創建新文檔"""
    return document_service.create_document(document)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID = Path(..., description="文檔ID"),
    document_service: DocumentService = Depends(get_document_service)
):
    """獲取文檔詳情"""
    document = document_service.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文檔 {document_id} 不存在"
        )
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: uuid.UUID = Path(..., description="文檔ID"),
    document_update: DocumentUpdate = Body(...),
    document_service: DocumentService = Depends(get_document_service)
):
    """更新文檔"""
    document = document_service.update_document(document_id, document_update)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文檔 {document_id} 不存在"
        )
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID = Path(..., description="文檔ID"),
    document_service: DocumentService = Depends(get_document_service)
):
    """刪除文檔"""
    success = document_service.delete_document(document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文檔 {document_id} 不存在"
        )
    return None


@router.post("/{document_id}/publish", response_model=DocumentResponse)
async def publish_document(
    document_id: uuid.UUID = Path(..., description="文檔ID"),
    document_service: DocumentService = Depends(get_document_service)
):
    """發布文檔"""
    document = document_service.publish_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文檔 {document_id} 不存在"
        )
    return document


@router.post("/{document_id}/unpublish", response_model=DocumentResponse)
async def unpublish_document(
    document_id: uuid.UUID = Path(..., description="文檔ID"),
    document_service: DocumentService = Depends(get_document_service)
):
    """取消發布文檔"""
    document = document_service.unpublish_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文檔 {document_id} 不存在"
        )
    return document


@router.post("/{document_id}/comments", response_model=DocumentCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_document_comment(
    document_id: uuid.UUID = Path(..., description="文檔ID"),
    comment: DocumentCommentCreate = Body(...),
    document_service: DocumentService = Depends(get_document_service)
):
    """添加文檔評論"""
    return document_service.add_comment(document_id, comment)


@router.get("/{document_id}/comments", response_model=List[DocumentCommentResponse])
async def get_document_comments(
    document_id: uuid.UUID = Path(..., description="文檔ID"),
    skip: int = Query(0, description="跳過的記錄數"),
    limit: int = Query(100, description="返回的最大記錄數"),
    document_service: DocumentService = Depends(get_document_service)
):
    """獲取文檔評論列表"""
    return document_service.get_comments(document_id, skip, limit)


@router.post("/{document_id}/attachments", response_model=DocumentAttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document_attachment(
    document_id: uuid.UUID = Path(..., description="文檔ID"),
    file: UploadFile = File(...),
    user_id: uuid.UUID = Query(..., description="上傳用戶ID"),
    document_service: DocumentService = Depends(get_document_service)
):
    """上傳文檔附件"""
    return document_service.add_attachment(document_id, user_id, file)


@router.get("/{document_id}/attachments", response_model=List[DocumentAttachmentResponse])
async def get_document_attachments(
    document_id: uuid.UUID = Path(..., description="文檔ID"),
    document_service: DocumentService = Depends(get_document_service)
):
    """獲取文檔附件列表"""
    return document_service.get_attachments(document_id)


@router.get("/{document_id}/history", response_model=List[dict])
async def get_document_history(
    document_id: uuid.UUID = Path(..., description="文檔ID"),
    document_service: DocumentService = Depends(get_document_service)
):
    """獲取文檔歷史記錄"""
    return document_service.get_history(document_id)


@router.get("/{document_id}/tags", response_model=List[DocumentTagResponse])
async def get_document_tags(
    document_id: uuid.UUID = Path(..., description="文檔ID"),
    document_service: DocumentService = Depends(get_document_service)
):
    """獲取文檔標籤"""
    return document_service.get_tags(document_id)


@router.post("/{document_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_document_tag(
    document_id: uuid.UUID = Path(..., description="文檔ID"),
    tag_id: uuid.UUID = Path(..., description="標籤ID"),
    document_service: DocumentService = Depends(get_document_service)
):
    """添加文檔標籤"""
    success = document_service.add_tag(document_id, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文檔 {document_id} 或標籤 {tag_id} 不存在"
        )
    return None


@router.delete("/{document_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_document_tag(
    document_id: uuid.UUID = Path(..., description="文檔ID"),
    tag_id: uuid.UUID = Path(..., description="標籤ID"),
    document_service: DocumentService = Depends(get_document_service)
):
    """移除文檔標籤"""
    success = document_service.remove_tag(document_id, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文檔 {document_id} 或標籤 {tag_id} 不存在"
        )
    return None