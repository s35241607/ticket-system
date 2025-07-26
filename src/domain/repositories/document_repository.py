from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import uuid

from ..entities.document import Document


class DocumentRepository(ABC):
    """文檔儲存庫介面"""
    
    @abstractmethod
    def save(self, document: Document) -> Document:
        """保存文檔"""
        pass
    
    @abstractmethod
    def get_by_id(self, document_id: uuid.UUID) -> Optional[Document]:
        """根據ID獲取文檔"""
        pass
    
    @abstractmethod
    def list(self, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[Document]:
        """獲取文檔列表"""
        pass
    
    @abstractmethod
    def delete(self, document_id: uuid.UUID) -> bool:
        """刪除文檔"""
        pass
    
    @abstractmethod
    def get_by_category(self, category_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Document]:
        """根據分類獲取文檔"""
        pass
    
    @abstractmethod
    def get_by_creator(self, creator_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Document]:
        """根據創建者獲取文檔"""
        pass
    
    @abstractmethod
    def get_by_tag(self, tag_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Document]:
        """根據標籤獲取文檔"""
        pass
    
    @abstractmethod
    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Document]:
        """搜索文檔"""
        pass