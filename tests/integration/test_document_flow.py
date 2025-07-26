import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.domain.entities.document import Document
from src.domain.repositories.document_repository import DocumentRepository
from src.infrastructure.repositories.document_repository_impl import SQLAlchemyDocumentRepository
from src.infrastructure.events.event_publisher_impl import InMemoryEventPublisher
from src.application.use_cases.document_use_cases import (
    CreateDocumentUseCase, GetDocumentUseCase, UpdateDocumentUseCase,
    PublishDocumentUseCase, DeleteDocumentUseCase
)


@pytest.fixture
def event_publisher():
    """事件發布者夾具"""
    publisher = InMemoryEventPublisher()
    return publisher


@pytest.fixture
def document_repository(db_session):
    """文檔儲存庫夾具"""
    return SQLAlchemyDocumentRepository(db_session)


@pytest.fixture
def create_document_use_case(document_repository, event_publisher):
    """創建文檔用例夾具"""
    return CreateDocumentUseCase(document_repository, event_publisher)


@pytest.fixture
def get_document_use_case(document_repository, event_publisher):
    """獲取文檔用例夾具"""
    return GetDocumentUseCase(document_repository, event_publisher)


@pytest.fixture
def update_document_use_case(document_repository, event_publisher):
    """更新文檔用例夾具"""
    return UpdateDocumentUseCase(document_repository, event_publisher)


@pytest.fixture
def publish_document_use_case(document_repository, event_publisher):
    """發布文檔用例夾具"""
    return PublishDocumentUseCase(document_repository, event_publisher)


@pytest.fixture
def delete_document_use_case(document_repository):
    """刪除文檔用例夾具"""
    return DeleteDocumentUseCase(document_repository)


@pytest.fixture
def sample_document_data():
    """樣本文檔數據夾具"""
    return {
        "title": "Test Document",
        "content": "This is a test document content",
        "summary": "Test document summary",
        "category_id": str(uuid.uuid4()),
        "creator_id": str(uuid.uuid4()),
        "tags": [str(uuid.uuid4()), str(uuid.uuid4())]
    }


class TestDocumentFlow:
    """文檔流程整合測試"""
    
    def test_document_lifecycle(self, create_document_use_case, get_document_use_case,
                               update_document_use_case, publish_document_use_case,
                               delete_document_use_case, sample_document_data):
        """測試文檔生命週期"""
        # 1. 創建文檔
        document = create_document_use_case.execute(
            title=sample_document_data["title"],
            content=sample_document_data["content"],
            category_id=uuid.UUID(sample_document_data["category_id"]),
            creator_id=uuid.UUID(sample_document_data["creator_id"]),
            summary=sample_document_data["summary"],
            tags=[uuid.UUID(tag) for tag in sample_document_data["tags"]]
        )
        
        assert document is not None
        assert document.title == sample_document_data["title"]
        document_id = document.id
        
        # 2. 獲取文檔
        retrieved_document = get_document_use_case.execute(document_id)
        assert retrieved_document is not None
        assert retrieved_document.id == document_id
        assert retrieved_document.view_count == 1  # 瀏覽次數應該增加
        
        # 3. 更新文檔
        updated_title = "Updated Document Title"
        updated_content = "Updated document content"
        updated_document = update_document_use_case.execute(
            document_id=document_id,
            title=updated_title,
            content=updated_content
        )
        
        assert updated_document is not None
        assert updated_document.title == updated_title
        assert updated_document.content == updated_content
        
        # 4. 發布文檔
        published_document = publish_document_use_case.execute(document_id)
        assert published_document is not None
        assert published_document.status.name == "PUBLISHED"
        assert published_document.published_at is not None
        
        # 5. 刪除文檔
        delete_result = delete_document_use_case.execute(document_id)
        assert delete_result is True
        
        # 確認文檔已被刪除
        deleted_document = get_document_use_case.execute(document_id)
        assert deleted_document is None


@pytest.mark.integration
def test_document_api_flow(client, auth_headers, test_category):
    """測試文檔 API 流程"""
    # 1. 創建文檔
    create_data = {
        "title": "API Test Document",
        "content": "This is a test document created via API",
        "summary": "API test summary",
        "category_id": test_category["id"],
        "creator_id": auth_headers["user_id"],
        "tags": []
    }
    
    response = client.post("/api/knowledge/documents/", json=create_data, headers=auth_headers)
    assert response.status_code == 201
    document_data = response.json()
    assert document_data["title"] == create_data["title"]
    document_id = document_data["id"]
    
    # 2. 獲取文檔
    response = client.get(f"/api/knowledge/documents/{document_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == document_id
    
    # 3. 更新文檔
    update_data = {
        "title": "Updated API Document",
        "content": "Updated content via API",
        "summary": "Updated summary",
        "category_id": test_category["id"]
    }
    
    response = client.put(f"/api/knowledge/documents/{document_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    updated_data = response.json()
    assert updated_data["title"] == update_data["title"]
    
    # 4. 發布文檔
    response = client.post(f"/api/knowledge/documents/{document_id}/publish", headers=auth_headers)
    assert response.status_code == 200
    published_data = response.json()
    assert published_data["status"] == "PUBLISHED"
    
    # 5. 獲取文檔列表
    response = client.get("/api/knowledge/documents/", headers=auth_headers)
    assert response.status_code == 200
    documents = response.json()["items"]
    assert len(documents) >= 1
    assert any(doc["id"] == document_id for doc in documents)
    
    # 6. 刪除文檔
    response = client.delete(f"/api/knowledge/documents/{document_id}", headers=auth_headers)
    assert response.status_code == 204
    
    # 確認文檔已被刪除
    response = client.get(f"/api/knowledge/documents/{document_id}", headers=auth_headers)
    assert response.status_code == 404