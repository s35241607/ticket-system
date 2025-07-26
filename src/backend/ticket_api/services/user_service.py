from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import logging
from passlib.context import CryptContext

# 導入模型和架構
from ..models.ticket import User, Department
from ..schemas.user import UserCreate, UserUpdate

# 配置日誌
logger = logging.getLogger("user_service")

# 密碼加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_users(self, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[User]:
        """獲取用戶列表，支持分頁和篩選"""
        query = self.db.query(User)

        # 應用篩選條件
        if filters:
            if filters.get("department_id"):
                query = query.filter(User.department_id == filters["department_id"])
            if filters.get("search"):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        User.username.ilike(search_term),
                        User.email.ilike(search_term),
                        User.full_name.ilike(search_term)
                    )
                )

        # 加載關聯數據
        query = query.options(joinedload(User.department))

        # 應用分頁
        query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)

        return query.all()

    def count_users(self, filters: Dict[str, Any] = None) -> int:
        """計算用戶總數，支持篩選"""
        query = self.db.query(func.count(User.id))

        # 應用篩選條件
        if filters:
            if filters.get("department_id"):
                query = query.filter(User.department_id == filters["department_id"])
            if filters.get("search"):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        User.username.ilike(search_term),
                        User.email.ilike(search_term),
                        User.full_name.ilike(search_term)
                    )
                )

        return query.scalar()

    def create_user(self, user_data: UserCreate) -> User:
        """創建新用戶"""
        # 檢查用戶名是否已存在
        existing_user = self.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"用戶名 {user_data.username} 已存在"
            )

        # 檢查郵箱是否已存在
        existing_email = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"郵箱 {user_data.email} 已被使用"
            )

        # 創建用戶數據字典
        user_dict = user_data.dict()
        
        # 加密密碼
        hashed_password = pwd_context.hash(user_dict.pop("password"))
        
        # 創建用戶
        user = User(**user_dict, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user(self, user_id: uuid.UUID) -> Optional[User]:
        """獲取用戶詳情"""
        return self.db.query(User).options(
            joinedload(User.department)
        ).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """通過用戶名獲取用戶"""
        return self.db.query(User).options(
            joinedload(User.department)
        ).filter(User.username == username).first()

    def update_user(self, user_id: uuid.UUID, user_update: UserUpdate) -> Optional[User]:
        """更新用戶"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # 更新字段
        update_data = user_update.dict(exclude_unset=True)
        
        # 如果更新密碼，需要加密
        if "password" in update_data:
            hashed_password = pwd_context.hash(update_data.pop("password"))
            user.hashed_password = hashed_password

        # 更新其他字段
        for key, value in update_data.items():
            setattr(user, key, value)

        user.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: uuid.UUID) -> bool:
        """刪除用戶"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        # 刪除用戶
        self.db.delete(user)
        self.db.commit()
        return True

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """驗證密碼"""
        return pwd_context.verify(plain_password, hashed_password)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """驗證用戶"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user