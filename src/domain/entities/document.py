from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from ..value_objects.document_status import DocumentStatus
from ..events.document_events import DocumentCreated, DocumentUpdated, DocumentPublished


@dataclass
class Document:
    """文檔實體"""
    id: uuid.UUID
    title: str
    content: str
    category_id: uuid.UUID
    creator_id: uuid.UUID
    status: DocumentStatus
    summary: Optional[str] = None
    view_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    tags: List[uuid.UUID] = field(default_factory=list)
    _events: List[Any] = field(default_factory=list, init=False)
    
    @classmethod
    def create(cls, title: str, content: str, category_id: uuid.UUID, 
               creator_id: uuid.UUID, summary: Optional[str] = None, 
               tags: List[uuid.UUID] = None) -> 'Document':
        """創建新文檔"""
        doc_id = uuid.uuid4()
        document = cls(
            id=doc_id,
            title=title,
            content=content,
            category_id=category_id,
            creator_id=creator_id,
            status=DocumentStatus.DRAFT,
            summary=summary,
            tags=tags or []
        )
        
        # 添加領域事件
        document._events.append(DocumentCreated(
            document_id=doc_id,
            creator_id=creator_id,
            title=title,
            category_id=category_id
        ))
        
        return document
    
    def update(self, title: Optional[str] = None, content: Optional[str] = None,
               summary: Optional[str] = None, category_id: Optional[uuid.UUID] = None) -> None:
        """更新文檔"""
        changes = {}
        
        if title is not None and title != self.title:
            changes['title'] = {'old': self.title, 'new': title}
            self.title = title
            
        if content is not None and content != self.content:
            changes['content'] = {'old': '...', 'new': '...'}
            self.content = content
            
        if summary is not None and summary != self.summary:
            changes['summary'] = {'old': self.summary, 'new': summary}
            self.summary = summary
            
        if category_id is not None and category_id != self.category_id:
            changes['category_id'] = {'old': str(self.category_id), 'new': str(category_id)}
            self.category_id = category_id
        
        if changes:
            self.updated_at = datetime.now()
            
            # 添加領域事件
            self._events.append(DocumentUpdated(
                document_id=self.id,
                updater_id=self.creator_id,  # 假設更新者是創建者
                changes=changes
            ))
    
    def publish(self) -> None:
        """發布文檔"""
        if self.status != DocumentStatus.PUBLISHED:
            self.status = DocumentStatus.PUBLISHED
            self.published_at = datetime.now()
            self.updated_at = datetime.now()
            
            # 添加領域事件
            self._events.append(DocumentPublished(
                document_id=self.id,
                publisher_id=self.creator_id
            ))
    
    def unpublish(self) -> None:
        """取消發布文檔"""
        if self.status == DocumentStatus.PUBLISHED:
            self.status = DocumentStatus.DRAFT
            self.updated_at = datetime.now()
    
    def add_tag(self, tag_id: uuid.UUID) -> None:
        """添加標籤"""
        if tag_id not in self.tags:
            self.tags.append(tag_id)
            self.updated_at = datetime.now()
    
    def remove_tag(self, tag_id: uuid.UUID) -> None:
        """移除標籤"""
        if tag_id in self.tags:
            self.tags.remove(tag_id)
            self.updated_at = datetime.now()
    
    def increment_view_count(self) -> None:
        """增加瀏覽次數"""
        self.view_count += 1
    
    def get_events(self) -> List[Any]:
        """獲取並清空事件列表"""
        events = self._events.copy()
        self._events.clear()
        return events