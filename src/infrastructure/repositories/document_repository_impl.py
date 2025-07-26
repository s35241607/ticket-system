from typing import List, Optional, Dict, Any
import uuid
from sqlalchemy.orm import Session

from ...domain.entities.document import Document
from ...domain.repositories.document_repository import DocumentRepository
from ...domain.value_objects.document_status import DocumentStatus

# 假設這些是現有的 SQLAlchemy 模型
from ....backend.knowledge_api.models.knowledge import Document as DocumentModel
from ....backend.knowledge_api.models.knowledge import DocumentTag, Category


class SQLAlchemyDocumentRepository(DocumentRepository):
    """SQLAlchemy 文檔儲存庫實現"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, document: Document) -> Document:
        """保存文檔"""
        # 檢查是否存在
        db_document = self.session.query(DocumentModel).filter(DocumentModel.id == str(document.id)).first()
        
        if db_document:
            # 更新現有文檔
            db_document.title = document.title
            db_document.content = document.content
            db_document.summary = document.summary
            db_document.category_id = str(document.category_id)
            db_document.status = document.status.name
            db_document.view_count = document.view_count
            db_document.updated_at = document.updated_at
            db_document.published_at = document.published_at
            
            # 更新標籤
            current_tags = [tag.tag_id for tag in db_document.tags]
            for tag_id in document.tags:
                if str(tag_id) not in current_tags:
                    tag = DocumentTag(document_id=str(document.id), tag_id=str(tag_id))
                    self.session.add(tag)
            
            # 移除不再存在的標籤
            for tag in db_document.tags:
                if uuid.UUID(tag.tag_id) not in document.tags:
                    self.session.delete(tag)
        else:
            # 創建新文檔
            db_document = DocumentModel(
                id=str(document.id),
                title=document.title,
                content=document.content,
                summary=document.summary,
                category_id=str(document.category_id),
                creator_id=str(document.creator_id),
                status=document.status.name,
                view_count=document.view_count,
                created_at=document.created_at,
                updated_at=document.updated_at,
                published_at=document.published_at
            )
            self.session.add(db_document)
            
            # 添加標籤
            for tag_id in document.tags:
                tag = DocumentTag(document_id=str(document.id), tag_id=str(tag_id))
                self.session.add(tag)
        
        self.session.commit()
        return document
    
    def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        """根據ID獲取文檔"""
        db_document = self.session.query(DocumentModel).filter(DocumentModel.id == str(document_id)).first()
        if not db_document:
            return None
        
        return self._map_to_entity(db_document)
    
    def list(self, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[Document]:
        """獲取文檔列表"""
        query = self.session.query(DocumentModel)
        
        if filters:
            if 'category_id' in filters:
                query = query.filter(DocumentModel.category_id == str(filters['category_id']))
            if 'creator_id' in filters:
                query = query.filter(DocumentModel.creator_id == str(filters['creator_id']))
            if 'status' in filters:
                query = query.filter(DocumentModel.status == filters['status'].name)
        
        db_documents = query.offset(skip).limit(limit).all()
        return [self._map_to_entity(doc) for doc in db_documents]
    
    def delete(self, document_id: uuid.UUID) -> bool:
        """刪除文檔"""
        db_document = self.session.query(DocumentModel).filter(DocumentModel.id == str(document_id)).first()
        if not db_document:
            return False
        
        # 刪除相關標籤
        self.session.query(DocumentTag).filter(DocumentTag.document_id == str(document_id)).delete()
        
        # 刪除文檔
        self.session.delete(db_document)
        self.session.commit()
        return True
    
    def get_by_category(self, category_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Document]:
        """根據分類獲取文檔"""
        db_documents = self.session.query(DocumentModel)\
            .filter(DocumentModel.category_id == str(category_id))\
            .offset(skip).limit(limit).all()
        return [self._map_to_entity(doc) for doc in db_documents]
    
    def get_by_creator(self, creator_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Document]:
        """根據創建者獲取文檔"""
        db_documents = self.session.query(DocumentModel)\
            .filter(DocumentModel.creator_id == str(creator_id))\
            .offset(skip).limit(limit).all()
        return [self._map_to_entity(doc) for doc in db_documents]
    
    def get_by_tag(self, tag_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Document]:
        """根據標籤獲取文檔"""
        db_documents = self.session.query(DocumentModel)\
            .join(DocumentTag, DocumentModel.id == DocumentTag.document_id)\
            .filter(DocumentTag.tag_id == str(tag_id))\
            .offset(skip).limit(limit).all()
        return [self._map_to_entity(doc) for doc in db_documents]
    
    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Document]:
        """搜索文檔"""
        db_documents = self.session.query(DocumentModel)\
            .filter(
                DocumentModel.title.ilike(f'%{query}%') | 
                DocumentModel.content.ilike(f'%{query}%') | 
                DocumentModel.summary.ilike(f'%{query}%')
            )\
            .offset(skip).limit(limit).all()
        return [self._map_to_entity(doc) for doc in db_documents]
    
    def _map_to_entity(self, db_document: DocumentModel) -> Document:
        """將數據庫模型映射為領域實體"""
        # 映射標籤
        tags = [uuid.UUID(tag.tag_id) for tag in db_document.tags] if db_document.tags else []
        
        # 映射狀態
        status_map = {
            'DRAFT': DocumentStatus.DRAFT,
            'PUBLISHED': DocumentStatus.PUBLISHED,
            'ARCHIVED': DocumentStatus.ARCHIVED
        }
        status = status_map.get(db_document.status, DocumentStatus.DRAFT)
        
        return Document(
            id=uuid.UUID(db_document.id),
            title=db_document.title,
            content=db_document.content,
            summary=db_document.summary,
            category_id=uuid.UUID(db_document.category_id),
            creator_id=uuid.UUID(db_document.creator_id),
            status=status,
            view_count=db_document.view_count,
            created_at=db_document.created_at,
            updated_at=db_document.updated_at,
            published_at=db_document.published_at,
            tags=tags
        )