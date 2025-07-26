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
from ..models.knowledge import (
    Document, 
    DocumentAttachment, 
    DocumentComment, 
    DocumentHistory, 
    DocumentTag,
    Category,
    document_tag
)
from ..schemas.document import (
    DocumentCreate, 
    DocumentUpdate, 
    DocumentCommentCreate
)

# 配置日誌
logger = logging.getLogger("document_service")


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = os.path.join("static", "uploads", "documents")
        os.makedirs(self.upload_dir, exist_ok=True)

    def get_documents(self, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[Document]:
        """獲取文檔列表，支持分頁和篩選"""
        query = self.db.query(Document)

        # 應用篩選條件
        if filters:
            if filters.get("category_id"):
                query = query.filter(Document.category_id == filters["category_id"])
            if filters.get("creator_id"):
                query = query.filter(Document.creator_id == filters["creator_id"])
            if filters.get("is_published") is not None:
                query = query.filter(Document.is_published == filters["is_published"])
            if filters.get("tag_id"):
                query = query.join(document_tag).filter(document_tag.c.tag_id == filters["tag_id"])
            if filters.get("search"):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Document.title.ilike(search_term),
                        Document.content.ilike(search_term),
                        Document.summary.ilike(search_term)
                    )
                )

        # 加載關聯數據
        query = query.options(
            joinedload(Document.creator),
            joinedload(Document.category)
        )

        # 應用分頁
        query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)

        return query.all()

    def create_document(self, document_data: DocumentCreate) -> Document:
        """創建新文檔"""
        # 檢查分類是否存在
        category = self.db.query(Category).filter(Category.id == document_data.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"分類 {document_data.category_id} 不存在"
            )

        # 創建文檔
        document_dict = document_data.dict(exclude={"tag_ids"})
        if document_dict["is_published"]:
            document_dict["published_at"] = datetime.now()
        
        document = Document(**document_dict)
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        # 添加標籤
        if document_data.tag_ids:
            for tag_id in document_data.tag_ids:
                tag = self.db.query(DocumentTag).filter(DocumentTag.id == tag_id).first()
                if tag:
                    document.tags.append(tag)
            self.db.commit()
            self.db.refresh(document)

        # 記錄歷史
        history = DocumentHistory(
            document_id=document.id,
            user_id=document_data.creator_id,
            content=document.content,
            changes={"document": "created"}
        )
        self.db.add(history)
        self.db.commit()

        return document

    def get_document(self, document_id: uuid.UUID) -> Optional[Document]:
        """獲取文檔詳情"""
        document = self.db.query(Document).options(
            joinedload(Document.creator),
            joinedload(Document.category),
            joinedload(Document.tags)
        ).filter(Document.id == document_id).first()

        if document:
            # 增加瀏覽次數
            document.view_count += 1
            self.db.commit()
            self.db.refresh(document)

        return document

    def update_document(self, document_id: uuid.UUID, document_update: DocumentUpdate) -> Optional[Document]:
        """更新文檔"""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return None

        # 記錄變更前的數據
        old_data = {}
        update_data = document_update.dict(exclude_unset=True)
        
        for key, value in update_data.items():
            if hasattr(document, key) and getattr(document, key) != value:
                old_data[key] = getattr(document, key)
                setattr(document, key, value)

        # 如果發布狀態變更為已發布，設置發布時間
        if "is_published" in update_data and update_data["is_published"] and not document.published_at:
            document.published_at = datetime.now()

        self.db.commit()
        self.db.refresh(document)

        # 記錄歷史
        if old_data or "content" in update_data:
            history = DocumentHistory(
                document_id=document.id,
                user_id=update_data.get("user_id", document.creator_id),  # 假設更新者ID在請求中提供
                content=document.content,
                changes={"old": old_data, "new": update_data}
            )
            self.db.add(history)
            self.db.commit()

        return document

    def delete_document(self, document_id: uuid.UUID) -> bool:
        """刪除文檔"""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False

        # 刪除相關數據
        self.db.query(DocumentAttachment).filter(DocumentAttachment.document_id == document_id).delete()
        self.db.query(DocumentComment).filter(DocumentComment.document_id == document_id).delete()
        self.db.query(DocumentHistory).filter(DocumentHistory.document_id == document_id).delete()
        
        # 清除標籤關聯
        document.tags = []
        self.db.commit()
        
        self.db.delete(document)
        self.db.commit()
        return True

    def publish_document(self, document_id: uuid.UUID) -> Optional[Document]:
        """發布文檔"""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return None

        document.is_published = True
        document.published_at = datetime.now()
        self.db.commit()
        self.db.refresh(document)
        return document

    def unpublish_document(self, document_id: uuid.UUID) -> Optional[Document]:
        """取消發布文檔"""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return None

        document.is_published = False
        self.db.commit()
        self.db.refresh(document)
        return document

    def add_comment(self, document_id: uuid.UUID, comment_data: DocumentCommentCreate) -> DocumentComment:
        """添加文檔評論"""
        # 檢查文檔是否存在
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"文檔 {document_id} 不存在"
            )

        comment = DocumentComment(**comment_data.dict())
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_comments(self, document_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[DocumentComment]:
        """獲取文檔評論列表"""
        return self.db.query(DocumentComment).options(
            joinedload(DocumentComment.user)
        ).filter(DocumentComment.document_id == document_id).order_by(
            DocumentComment.created_at.desc()
        ).offset(skip).limit(limit).all()

    def add_attachment(self, document_id: uuid.UUID, user_id: uuid.UUID, file: UploadFile) -> DocumentAttachment:
        """上傳文檔附件"""
        # 檢查文檔是否存在
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"文檔 {document_id} 不存在"
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
        attachment = DocumentAttachment(
            document_id=document_id,
            user_id=user_id,
            filename=file.filename,
            file_path=os.path.join("uploads", "documents", unique_filename),
            file_type=file_type,
            file_size=file_size
        )
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        return attachment

    def get_attachments(self, document_id: uuid.UUID) -> List[DocumentAttachment]:
        """獲取文檔附件列表"""
        return self.db.query(DocumentAttachment).options(
            joinedload(DocumentAttachment.user)
        ).filter(DocumentAttachment.document_id == document_id).order_by(
            DocumentAttachment.created_at.desc()
        ).all()

    def get_history(self, document_id: uuid.UUID) -> List[Dict[str, Any]]:
        """獲取文檔歷史記錄"""
        history_records = self.db.query(DocumentHistory).options(
            joinedload(DocumentHistory.user)
        ).filter(DocumentHistory.document_id == document_id).order_by(
            DocumentHistory.created_at.desc()
        ).all()

        # 轉換為更易讀的格式
        result = []
        for record in history_records:
            item = {
                "id": record.id,
                "user_id": record.user_id,
                "user_name": record.user.full_name if record.user else None,
                "content": record.content,
                "changes": record.changes,
                "created_at": record.created_at
            }
            result.append(item)

        return result

    def get_tags(self, document_id: uuid.UUID) -> List[DocumentTag]:
        """獲取文檔標籤"""
        document = self.db.query(Document).options(
            joinedload(Document.tags)
        ).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"文檔 {document_id} 不存在"
            )
            
        return document.tags

    def add_tag(self, document_id: uuid.UUID, tag_id: uuid.UUID) -> bool:
        """添加文檔標籤"""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        tag = self.db.query(DocumentTag).filter(DocumentTag.id == tag_id).first()
        
        if not document or not tag:
            return False
            
        if tag not in document.tags:
            document.tags.append(tag)
            self.db.commit()
            
        return True

    def remove_tag(self, document_id: uuid.UUID, tag_id: uuid.UUID) -> bool:
        """移除文檔標籤"""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        tag = self.db.query(DocumentTag).filter(DocumentTag.id == tag_id).first()
        
        if not document or not tag:
            return False
            
        if tag in document.tags:
            document.tags.remove(tag)
            self.db.commit()
            
        return True