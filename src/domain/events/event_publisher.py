from abc import ABC, abstractmethod
from typing import List

from .base_event import DomainEvent


class EventPublisher(ABC):
    """事件發布者介面"""
    
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """發布單個事件"""
        pass
    
    @abstractmethod
    def publish_all(self, events: List[DomainEvent]) -> None:
        """批量發布事件"""
        pass