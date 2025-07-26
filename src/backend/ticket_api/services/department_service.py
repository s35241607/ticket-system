from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import logging

# 導入模型和架構
from ..models.ticket import Department, User
from ..schemas.department import DepartmentCreate, DepartmentUpdate

# 配置日誌
logger = logging.getLogger("department_service")


class DepartmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_departments(self, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[Department]:
        """獲取部門列表，支持分頁和篩選"""
        query = self.db.query(Department)

        # 應用篩選條件
        if filters and filters.get("search"):
            search_term = f"%{filters['search']}%"
            query = query.filter(
                or_(
                    Department.name.ilike(search_term),
                    Department.description.ilike(search_term)
                )
            )

        # 應用分頁
        query = query.order_by(Department.name).offset(skip).limit(limit)

        return query.all()

    def count_departments(self, filters: Dict[str, Any] = None) -> int:
        """計算部門總數，支持篩選"""
        query = self.db.query(func.count(Department.id))

        # 應用篩選條件
        if filters and filters.get("search"):
            search_term = f"%{filters['search']}%"
            query = query.filter(
                or_(
                    Department.name.ilike(search_term),
                    Department.description.ilike(search_term)
                )
            )

        return query.scalar()

    def create_department(self, department_data: DepartmentCreate) -> Department:
        """創建新部門"""
        department = Department(**department_data.dict())
        self.db.add(department)
        self.db.commit()
        self.db.refresh(department)
        return department

    def get_department(self, department_id: uuid.UUID) -> Optional[Department]:
        """獲取部門詳情"""
        return self.db.query(Department).filter(Department.id == department_id).first()

    def get_department_by_name(self, name: str) -> Optional[Department]:
        """通過名稱獲取部門"""
        return self.db.query(Department).filter(Department.name == name).first()

    def update_department(self, department_id: uuid.UUID, department_update: DepartmentUpdate) -> Optional[Department]:
        """更新部門"""
        department = self.db.query(Department).filter(Department.id == department_id).first()
        if not department:
            return None

        # 更新字段
        update_data = department_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(department, key, value)

        department.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(department)
        return department

    def delete_department(self, department_id: uuid.UUID) -> bool:
        """刪除部門"""
        department = self.db.query(Department).filter(Department.id == department_id).first()
        if not department:
            return False

        # 刪除部門
        self.db.delete(department)
        self.db.commit()
        return True

    def has_users(self, department_id: uuid.UUID) -> bool:
        """檢查部門是否有關聯用戶"""
        return self.db.query(User).filter(User.department_id == department_id).count() > 0