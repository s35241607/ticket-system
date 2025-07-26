import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.ticket_api.models.user import User
from src.backend.ticket_api.services.user_service import UserService
from src.utils.exceptions import ConflictException, NotFoundException
from src.utils.security import verify_password


class TestUserService:
    """
    用戶服務測試類
    """
    
    def test_create_user(self, db_session, create_test_data):
        """
        測試創建用戶
        """
        # 獲取測試部門
        department = create_test_data["department"]
        
        # 創建用戶服務
        user_service = UserService(db_session)
        
        # 創建用戶數據
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "新用戶",
            "department_id": department.id,
            "is_admin": False,
        }
        
        # 創建用戶
        user = user_service.create_user(user_data)
        
        # 驗證用戶數據
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.full_name == user_data["full_name"]
        assert user.department_id == user_data["department_id"]
        assert user.is_admin == user_data["is_admin"]
        
        # 驗證密碼已加密
        assert user.hashed_password != user_data["password"]
        assert verify_password(user_data["password"], user.hashed_password)
    
    def test_create_user_duplicate_username(self, db_session, create_test_data):
        """
        測試創建用戶時用戶名重複
        """
        # 獲取測試部門和用戶
        department = create_test_data["department"]
        existing_user = create_test_data["user"]
        
        # 創建用戶服務
        user_service = UserService(db_session)
        
        # 創建用戶數據（使用已存在的用戶名）
        user_data = {
            "username": existing_user.username,  # 已存在的用戶名
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "新用戶",
            "department_id": department.id,
            "is_admin": False,
        }
        
        # 嘗試創建用戶，應該拋出異常
        with pytest.raises(ConflictException):
            user_service.create_user(user_data)
    
    def test_get_user_by_id(self, db_session, create_test_data):
        """
        測試通過ID獲取用戶
        """
        # 獲取測試用戶
        existing_user = create_test_data["user"]
        
        # 創建用戶服務
        user_service = UserService(db_session)
        
        # 獲取用戶
        user = user_service.get_user_by_id(existing_user.id)
        
        # 驗證用戶數據
        assert user.id == existing_user.id
        assert user.username == existing_user.username
        assert user.email == existing_user.email
    
    def test_get_user_by_id_not_found(self, db_session):
        """
        測試通過不存在的ID獲取用戶
        """
        # 創建用戶服務
        user_service = UserService(db_session)
        
        # 嘗試獲取不存在的用戶，應該拋出異常
        with pytest.raises(NotFoundException):
            user_service.get_user_by_id(999)
    
    def test_get_user_by_username(self, db_session, create_test_data):
        """
        測試通過用戶名獲取用戶
        """
        # 獲取測試用戶
        existing_user = create_test_data["user"]
        
        # 創建用戶服務
        user_service = UserService(db_session)
        
        # 獲取用戶
        user = user_service.get_user_by_username(existing_user.username)
        
        # 驗證用戶數據
        assert user.id == existing_user.id
        assert user.username == existing_user.username
        assert user.email == existing_user.email
    
    def test_get_users(self, db_session, create_test_data):
        """
        測試獲取用戶列表
        """
        # 創建用戶服務
        user_service = UserService(db_session)
        
        # 獲取用戶列表
        users = user_service.get_users()
        
        # 驗證用戶列表
        assert len(users) > 0
    
    def test_update_user(self, db_session, create_test_data):
        """
        測試更新用戶
        """
        # 獲取測試用戶
        existing_user = create_test_data["user"]
        
        # 創建用戶服務
        user_service = UserService(db_session)
        
        # 更新用戶數據
        update_data = {
            "full_name": "更新的用戶名",
            "email": "updated@example.com",
        }
        
        # 更新用戶
        updated_user = user_service.update_user(existing_user.id, update_data)
        
        # 驗證更新後的用戶數據
        assert updated_user.id == existing_user.id
        assert updated_user.full_name == update_data["full_name"]
        assert updated_user.email == update_data["email"]
        assert updated_user.username == existing_user.username  # 用戶名未更改
    
    def test_delete_user(self, db_session, create_test_data):
        """
        測試刪除用戶
        """
        # 獲取測試用戶
        existing_user = create_test_data["user"]
        
        # 創建用戶服務
        user_service = UserService(db_session)
        
        # 刪除用戶
        user_service.delete_user(existing_user.id)
        
        # 嘗試獲取已刪除的用戶，應該拋出異常
        with pytest.raises(NotFoundException):
            user_service.get_user_by_id(existing_user.id)
    
    def test_authenticate_user(self, db_session, create_test_data):
        """
        測試用戶認證
        """
        # 創建用戶服務
        user_service = UserService(db_session)
        
        # 認證用戶（使用正確的密碼）
        user = user_service.authenticate_user("testuser", "testpassword")
        
        # 驗證認證成功
        assert user is not None
        assert user.username == "testuser"
    
    def test_authenticate_user_wrong_password(self, db_session, create_test_data):
        """
        測試用戶認證（密碼錯誤）
        """
        # 創建用戶服務
        user_service = UserService(db_session)
        
        # 認證用戶（使用錯誤的密碼）
        user = user_service.authenticate_user("testuser", "wrongpassword")
        
        # 驗證認證失敗
        assert user is None
    
    def test_authenticate_user_not_found(self, db_session):
        """
        測試用戶認證（用戶不存在）
        """
        # 創建用戶服務
        user_service = UserService(db_session)
        
        # 認證用戶（使用不存在的用戶名）
        user = user_service.authenticate_user("nonexistentuser", "password")
        
        # 驗證認證失敗
        assert user is None