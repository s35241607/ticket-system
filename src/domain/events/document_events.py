from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

from .base_event import DomainEvent


@dataclass
class DocumentCreated(DomainEvent):
    """文檔創建事件"""
    document_id: uuid.UUID
    creator_id: uuid.UUID
    title: str
    category_id: uuid.UUID
    timestamp: datetime = datetime.now()


@dataclass
class DocumentUpdated(DomainEvent):
    """文檔更新事件"""
    document_id: uuid.UUID
    updater_id: uuid.UUID
    changes: Dict[str, Any]
    timestamp: datetime = datetime.now()


@dataclass
class DocumentPublished(DomainEvent):
    """文檔發布事件"""
    document_id: uuid.UUID
    publisher_id: uuid.UUID
    timestamp: datetime = datetime.now()


@dataclass
class DocumentViewed(DomainEvent):
    """文檔瀏覽事件"""
    document_id: uuid.UUID
    viewer_id: Optional[uuid.UUID]
    timestamp: datetime = datetime.now()


@dataclass
class DocumentTagAdded(DomainEvent):
    """文檔標籤添加事件"""
    document_id: uuid.UUID
    tag_id: uuid.UUID
    user_id: uuid.UUID
    timestamp: datetime = datetime.now()


@dataclass
class DocumentTagRemoved(DomainEvent):
    """文檔標籤移除事件"""
    document_id: uuid.UUID
    tag_id: uuid.UUID
    user_id: uuid.UUID
    timestamp: datetime = datetime.now()


@dataclass
class DocumentCommentAdded(DomainEvent):
    """文檔評論添加事件"""
    document_id: uuid.UUID
    comment_id: uuid.UUID
    user_id: uuid.UUID
    content: str
    timestamp: datetime = datetime.now()