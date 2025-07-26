from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import logging

# 導入模型和架構
from ..models.knowledge import Category, Document
from ..schemas.category import CategoryCreate, CategoryUpdate

# 配置日誌
logger = logging.getLogger("category_service")


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_categories(self, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[Category]:
        """獲取分類列表，支持分頁和篩選"""
        query = self.db.query(Category)

        # 應用篩選條件
        if filters:
            if filters.get("parent_id") is not None:
                query = query.filter(Category.parent_id == filters["parent_id"])
            if filters.get("search"):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Category.name.ilike(search_term),
                        Category.description.ilike(search_term)
                    )
                )

        # 應用分頁
        query = query.order_by(Category.name).offset(skip).limit(limit)

        return query.all()

    def count_categories(self, filters: Dict[str, Any] = None) -> int:
        """計算分類總數，支持篩選"""
        query = self.db.query(func.count(Category.id))

        # 應用篩選條件
        if filters:
            if filters.get("parent_id") is not None:
                query = query.filter(Category.parent_id == filters["parent_id"])
            if filters.get("search"):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Category.name.ilike(search_term),
                        Category.description.ilike(search_term)
                    )
                )

        return query.scalar()

    def create_category(self, category_data: CategoryCreate) -> Category:
        """創建新分類"""
        category = Category(**category_data.dict())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_category(self, category_id: uuid.UUID) -> Optional[Category]:
        """獲取分類詳情"""
        return self.db.query(Category).filter(Category.id == category_id).first()

    def update_category(self, category_id: uuid.UUID, category_update: CategoryUpdate) -> Optional[Category]:
        """更新分類"""
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None

        # 更新字段
        update_data = category_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(category, key, value)

        category.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category_id: uuid.UUID) -> bool:
        """刪除分類"""
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return False

        # 刪除分類
        self.db.delete(category)
        self.db.commit()
        return True

    def name_exists_at_level(self, name: str, parent_id: Optional[uuid.UUID], exclude_id: Optional[uuid.UUID] = None) -> bool:
        """檢查同一級別下是否已存在相同名稱的分類"""
        query = self.db.query(Category).filter(
            Category.name == name,
            Category.parent_id == parent_id
        )
        
        if exclude_id:
            query = query.filter(Category.id != exclude_id)
            
        return query.count() > 0

    def has_children(self, category_id: uuid.UUID) -> bool:
        """檢查分類是否有子分類"""
        return self.db.query(Category).filter(Category.parent_id == category_id).count() > 0

    def has_documents(self, category_id: uuid.UUID) -> bool:
        """檢查分類是否有關聯文檔"""
        return self.db.query(Document).filter(Document.category_id == category_id).count() > 0

    def is_descendant(self, ancestor_id: uuid.UUID, descendant_id: uuid.UUID) -> bool:
        """檢查一個分類是否是另一個分類的後代"""
        if ancestor_id == descendant_id:
            return True
            
        descendant = self.db.query(Category).filter(Category.id == descendant_id).first()
        if not descendant or not descendant.parent_id:
            return False
            
        if descendant.parent_id == ancestor_id:
            return True
            
        return self.is_descendant(ancestor_id, descendant.parent_id)

    def get_category_tree(self) -> List[Category]:
        """獲取分類樹結構"""
        # 獲取所有頂級分類
        root_categories = self.db.query(Category).filter(Category.parent_id.is_(None)).all()
        
        # 遞歸加載子分類
        for category in root_categories:
            self._load_children(category)
            
        return root_categories

    def _load_children(self, category: Category) -> None:
        """遞歸加載子分類"""
        children = self.db.query(Category).filter(Category.parent_id == category.id).all()
        category.children = children
        
        for child in children:
            self._load_children(child)