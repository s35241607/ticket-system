from typing import List, Optional, Dict, Any
import uuid

from ...domain.entities.document import Document
from ...domain.repositories.document_repository import DocumentRepository
from ...domain.events.event_publisher import EventPublisher
from ...domain.events.document_events import DocumentViewed, DocumentTagAdded, DocumentTagRemoved


class CreateDocumentUseCase:
    """創建文檔用例"""
    
    def __init__(self, document_repository: DocumentRepository, event_publisher: EventPublisher):
        self.document_repository = document_repository
        self.event_publisher = event_publisher
    
    def execute(self, title: str, content: str, category_id: uuid.UUID, 
                creator_id: uuid.UUID, summary: Optional[str] = None, 
                tags: List[uuid.UUID] = None) -> Document:
        # 創建文檔實體
        document = Document.create(
            title=title,
            content=content,
            category_id=category_id,
            creator_id=creator_id,
            summary=summary,
            tags=tags
        )
        
        # 保存文檔
        saved_document = self.document_repository.save(document)
        
        # 發布事件
        events = document.get_events()
        self.event_publisher.publish_all(events)
        
        return saved_document


class UpdateDocumentUseCase:
    """更新文檔用例"""
    
    def __init__(self, document_repository: DocumentRepository, event_publisher: EventPublisher):
        self.document_repository = document_repository
        self.event_publisher = event_publisher
    
    def execute(self, document_id: uuid.UUID, title: Optional[str] = None, 
                content: Optional[str] = None, summary: Optional[str] = None, 
                category_id: Optional[uuid.UUID] = None) -> Optional[Document]:
        # 獲取文檔
        document = self.document_repository.get_by_id(document_id)
        if not document:
            return None
        
        # 更新文檔
        document.update(
            title=title,
            content=content,
            summary=summary,
            category_id=category_id
        )
        
        # 保存文檔
        updated_document = self.document_repository.save(document)
        
        # 發布事件
        events = document.get_events()
        self.event_publisher.publish_all(events)
        
        return updated_document


class GetDocumentUseCase:
    """獲取文檔用例"""
    
    def __init__(self, document_repository: DocumentRepository, event_publisher: EventPublisher):
        self.document_repository = document_repository
        self.event_publisher = event_publisher
    
    def execute(self, document_id: uuid.UUID, viewer_id: Optional[uuid.UUID] = None) -> Optional[Document]:
        # 獲取文檔
        document = self.document_repository.get_by_id(document_id)
        if not document:
            return None
        
        # 增加瀏覽次數
        document.increment_view_count()
        updated_document = self.document_repository.save(document)
        
        # 發布瀏覽事件
        view_event = DocumentViewed(
            document_id=document_id,
            viewer_id=viewer_id
        )
        self.event_publisher.publish(view_event)
        
        return updated_document


class ListDocumentsUseCase:
    """獲取文檔列表用例"""
    
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository
    
    def execute(self, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[Document]:
        return self.document_repository.list(filters, skip, limit)


class PublishDocumentUseCase:
    """發布文檔用例"""
    
    def __init__(self, document_repository: DocumentRepository, event_publisher: EventPublisher):
        self.document_repository = document_repository
        self.event_publisher = event_publisher
    
    def execute(self, document_id: uuid.UUID) -> Optional[Document]:
        # 獲取文檔
        document = self.document_repository.get_by_id(document_id)
        if not document:
            return None
        
        # 發布文檔
        document.publish()
        published_document = self.document_repository.save(document)
        
        # 發布事件
        events = document.get_events()
        self.event_publisher.publish_all(events)
        
        return published_document


class UnpublishDocumentUseCase:
    """取消發布文檔用例"""
    
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository
    
    def execute(self, document_id: uuid.UUID) -> Optional[Document]:
        # 獲取文檔
        document = self.document_repository.get_by_id(document_id)
        if not document:
            return None
        
        # 取消發布文檔
        document.unpublish()
        return self.document_repository.save(document)


class DeleteDocumentUseCase:
    """刪除文檔用例"""
    
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository
    
    def execute(self, document_id: uuid.UUID) -> bool:
        return self.document_repository.delete(document_id)


class AddDocumentTagUseCase:
    """添加文檔標籤用例"""
    
    def __init__(self, document_repository: DocumentRepository, event_publisher: EventPublisher):
        self.document_repository = document_repository
        self.event_publisher = event_publisher
    
    def execute(self, document_id: uuid.UUID, tag_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Document]:
        # 獲取文檔
        document = self.document_repository.get_by_id(document_id)
        if not document:
            return None
        
        # 添加標籤
        document.add_tag(tag_id)
        updated_document = self.document_repository.save(document)
        
        # 發布事件
        tag_event = DocumentTagAdded(
            document_id=document_id,
            tag_id=tag_id,
            user_id=user_id
        )
        self.event_publisher.publish(tag_event)
        
        return updated_document


class RemoveDocumentTagUseCase:
    """移除文檔標籤用例"""
    
    def __init__(self, document_repository: DocumentRepository, event_publisher: EventPublisher):
        self.document_repository = document_repository
        self.event_publisher = event_publisher
    
    def execute(self, document_id: uuid.UUID, tag_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Document]:
        # 獲取文檔
        document = self.document_repository.get_by_id(document_id)
        if not document:
            return None
        
        # 移除標籤
        document.remove_tag(tag_id)
        updated_document = self.document_repository.save(document)
        
        # 發布事件
        tag_event = DocumentTagRemoved(
            document_id=document_id,
            tag_id=tag_id,
            user_id=user_id
        )
        self.event_publisher.publish(tag_event)
        
        return updated_document