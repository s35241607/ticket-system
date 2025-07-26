import os
import sys
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.db import Base, get_db
from src.backend.ticket_api.main import app as ticket_app
from src.backend.knowledge_api.main import app as knowledge_app
from src.utils.security import get_password_hash

# 使用內存數據庫進行測試
SQLITE_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    創建一個新的數據庫會話用於測試
    """
    # 創建數據庫表
    Base.metadata.create_all(bind=engine)
    
    # 創建會話
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # 清理數據庫表
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def ticket_client(db_session):
    """
    創建一個測試客戶端用於Ticket API
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # 覆蓋依賴
    ticket_app.dependency_overrides[get_db] = override_get_db
    
    # 創建測試客戶端
    with TestClient(ticket_app) as client:
        yield client
    
    # 清理依賴覆蓋
    ticket_app.dependency_overrides = {}


@pytest.fixture(scope="function")
def knowledge_client(db_session):
    """
    創建一個測試客戶端用於Knowledge API
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # 覆蓋依賴
    knowledge_app.dependency_overrides[get_db] = override_get_db
    
    # 創建測試客戶端
    with TestClient(knowledge_app) as client:
        yield client
    
    # 清理依賴覆蓋
    knowledge_app.dependency_overrides = {}


@pytest.fixture(scope="function")
def create_test_data(db_session):
    """
    創建測試數據
    """
    from src.backend.ticket_api.models.department import Department
    from src.backend.ticket_api.models.user import User
    from src.backend.ticket_api.models.workflow import Workflow, WorkflowStep
    from src.backend.knowledge_api.models.category import Category
    
    # 創建測試部門
    test_dept = Department(name="測試部門", description="用於測試的部門")
    db_session.add(test_dept)
    db_session.flush()
    
    # 創建測試用戶
    test_user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="測試用戶",
        department_id=test_dept.id,
    )
    db_session.add(test_user)
    db_session.flush()
    
    # 創建測試工作流
    test_workflow = Workflow(name="測試工作流", description="用於測試的工作流")
    db_session.add(test_workflow)
    db_session.flush()
    
    # 創建工作流步驟
    steps = [
        WorkflowStep(name="步驟1", description="第一步", order=1, workflow_id=test_workflow.id),
        WorkflowStep(name="步驟2", description="第二步", order=2, workflow_id=test_workflow.id),
    ]
    db_session.add_all(steps)
    
    # 創建測試分類
    test_category = Category(name="測試分類", description="用於測試的分類")
    db_session.add(test_category)
    
    # 提交所有更改
    db_session.commit()
    
    # 返回創建的測試數據
    return {
        "department": test_dept,
        "user": test_user,
        "workflow": test_workflow,
        "category": test_category,
    }


@pytest.fixture(scope="function")
def auth_headers(db_session, create_test_data):
    """
    創建帶有認證令牌的請求頭
    """
    from src.utils.security import create_access_token
    
    # 獲取測試用戶
    user = create_test_data["user"]
    
    # 創建訪問令牌
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "jti": "test-jti",
    }
    access_token = create_access_token(token_data)
    
    # 返回帶有認證令牌的請求頭
    return {"Authorization": f"Bearer {access_token}"}