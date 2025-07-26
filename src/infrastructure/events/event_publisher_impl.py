from typing import List, Dict, Type, Callable, Any
import logging

from ...domain.events.base_event import DomainEvent
from ...domain.events.event_publisher import EventPublisher
from ...domain.events.document_events import (
    DocumentCreated, DocumentUpdated, DocumentPublished, 
    DocumentViewed, DocumentTagAdded, DocumentTagRemoved,
    DocumentCommentAdded
)


class InMemoryEventPublisher(EventPublisher):
    """內存事件發布者實現"""
    
    def __init__(self):
        self.handlers: Dict[Type[DomainEvent], List[Callable[[DomainEvent], None]]] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_handler(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        """註冊事件處理器"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def publish(self, event: DomainEvent) -> None:
        """發布單個事件"""
        event_type = type(event)
        self.logger.info(f"Publishing event: {event_type.__name__}")
        
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"Error handling event {event_type.__name__}: {str(e)}")
    
    def publish_all(self, events: List[DomainEvent]) -> None:
        """批量發布事件"""
        for event in events:
            self.publish(event)


class AsyncEventPublisher(EventPublisher):
    """異步事件發布者實現（使用消息隊列）"""
    
    def __init__(self, message_queue_client: Any):
        self.message_queue_client = message_queue_client
        self.logger = logging.getLogger(__name__)
        
        # 事件類型到隊列名稱的映射
        self.event_queues = {
            DocumentCreated: "document.created",
            DocumentUpdated: "document.updated",
            DocumentPublished: "document.published",
            DocumentViewed: "document.viewed",
            DocumentTagAdded: "document.tag.added",
            DocumentTagRemoved: "document.tag.removed",
            DocumentCommentAdded: "document.comment.added"
        }
    
    def publish(self, event: DomainEvent) -> None:
        """發布單個事件到消息隊列"""
        event_type = type(event)
        queue_name = self.event_queues.get(event_type)
        
        if not queue_name:
            self.logger.warning(f"No queue defined for event type: {event_type.__name__}")
            return
        
        try:
            # 將事件序列化並發送到消息隊列
            # 這裡假設 message_queue_client 有一個 send_message 方法
            self.message_queue_client.send_message(queue_name, self._serialize_event(event))
            self.logger.info(f"Event {event_type.__name__} sent to queue {queue_name}")
        except Exception as e:
            self.logger.error(f"Failed to publish event {event_type.__name__} to queue {queue_name}: {str(e)}")
    
    def publish_all(self, events: List[DomainEvent]) -> None:
        """批量發布事件到消息隊列"""
        for event in events:
            self.publish(event)
    
    def _serialize_event(self, event: DomainEvent) -> Dict[str, Any]:
        """將事件序列化為字典"""
        # 這裡使用簡單的字典序列化，實際應用中可能需要更複雜的序列化邏輯
        event_dict = event.__dict__.copy()
        
        # 處理特殊類型
        for key, value in event_dict.items():
            if isinstance(value, uuid.UUID):
                event_dict[key] = str(value)
            elif isinstance(value, datetime):
                event_dict[key] = value.isoformat()
        
        # 添加事件類型
        event_dict['event_type'] = type(event).__name__
        
        return event_dict


# 為了示例完整性，添加一些事件處理器
def document_created_handler(event: DocumentCreated) -> None:
    """處理文檔創建事件"""
    logger = logging.getLogger(__name__)
    logger.info(f"Document created: {event.document_id} by {event.creator_id}")
    # 這裡可以添加更多邏輯，如發送通知、更新索引等


def document_published_handler(event: DocumentPublished) -> None:
    """處理文檔發布事件"""
    logger = logging.getLogger(__name__)
    logger.info(f"Document published: {event.document_id} by {event.publisher_id}")
    # 這裡可以添加更多邏輯，如發送通知、更新索引等


def document_viewed_handler(event: DocumentViewed) -> None:
    """處理文檔瀏覽事件"""
    logger = logging.getLogger(__name__)
    viewer_id = event.viewer_id if event.viewer_id else "anonymous"
    logger.info(f"Document viewed: {event.document_id} by {viewer_id}")
    # 這裡可以添加更多邏輯，如更新熱門文檔排行等


# 註冊事件處理器的示例
def register_event_handlers(publisher: InMemoryEventPublisher) -> None:
    """註冊事件處理器"""
    publisher.register_handler(DocumentCreated, document_created_handler)
    publisher.register_handler(DocumentPublished, document_published_handler)
    publisher.register_handler(DocumentViewed, document_viewed_handler)
    # 可以註冊更多事件處理器