import pytest
from unittest.mock import MagicMock, patch

from src.backend.knowledge_api.models.document import Document
from src.backend.knowledge_api.models.question import Question
from src.backend.knowledge_api.services.search_service import SearchService


class TestSearchService:
    """
    搜索服務測試類
    """
    
    def test_search_all(self, db_session):
        """
        測試全文搜索（文檔和問題）
        """
        # 創建測試數據
        self._create_test_data(db_session)
        
        # 創建搜索服務
        search_service = SearchService(db_session)
        
        # 執行搜索
        results = search_service.search("測試", search_type="all", limit=10)
        
        # 驗證搜索結果
        assert len(results) > 0
        
        # 檢查結果中是否包含文檔和問題
        has_document = False
        has_question = False
        
        for result in results:
            if result.get("type") == "document":
                has_document = True
            elif result.get("type") == "question":
                has_question = True
        
        assert has_document
        assert has_question
    
    def test_search_documents_only(self, db_session):
        """
        測試僅搜索文檔
        """
        # 創建測試數據
        self._create_test_data(db_session)
        
        # 創建搜索服務
        search_service = SearchService(db_session)
        
        # 執行搜索
        results = search_service.search("測試", search_type="document", limit=10)
        
        # 驗證搜索結果
        assert len(results) > 0
        
        # 檢查結果中是否只包含文檔
        for result in results:
            assert result.get("type") == "document"
    
    def test_search_questions_only(self, db_session):
        """
        測試僅搜索問題
        """
        # 創建測試數據
        self._create_test_data(db_session)
        
        # 創建搜索服務
        search_service = SearchService(db_session)
        
        # 執行搜索
        results = search_service.search("測試", search_type="question", limit=10)
        
        # 驗證搜索結果
        assert len(results) > 0
        
        # 檢查結果中是否只包含問題
        for result in results:
            assert result.get("type") == "question"
    
    def test_search_with_category_filter(self, db_session, create_test_data):
        """
        測試帶有分類過濾的搜索
        """
        # 創建測試數據
        self._create_test_data(db_session)
        
        # 獲取測試分類
        category = create_test_data["category"]
        
        # 創建搜索服務
        search_service = SearchService(db_session)
        
        # 執行搜索
        results = search_service.search(
            "測試", search_type="all", category_id=category.id, limit=10
        )
        
        # 驗證搜索結果
        assert len(results) > 0
    
    def test_search_with_highlight(self, db_session):
        """
        測試帶有高亮的搜索
        """
        # 創建測試數據
        self._create_test_data(db_session)
        
        # 創建搜索服務
        search_service = SearchService(db_session)
        
        # 執行搜索
        results = search_service.search("測試", search_type="all", limit=10)
        
        # 驗證搜索結果
        assert len(results) > 0
        
        # 檢查結果中是否包含高亮片段
        for result in results:
            assert "highlight" in result
            assert result["highlight"] is not None
    
    def test_search_no_results(self, db_session):
        """
        測試沒有結果的搜索
        """
        # 創建搜索服務
        search_service = SearchService(db_session)
        
        # 執行搜索
        results = search_service.search("不存在的關鍵詞xyz123", search_type="all", limit=10)
        
        # 驗證搜索結果為空
        assert len(results) == 0
    
    def test_generate_highlights(self, db_session):
        """
        測試生成高亮片段
        """
        # 創建搜索服務
        search_service = SearchService(db_session)
        
        # 測試文本
        text = "這是一個測試文本，用於測試高亮功能。測試是否能夠正確高亮關鍵詞。"
        
        # 生成高亮片段
        highlight = search_service._generate_highlights(text, "測試")
        
        # 驗證高亮片段
        assert highlight is not None
        assert "<mark>測試</mark>" in highlight
    
    def _create_test_data(self, db_session):
        """
        創建測試數據
        """
        # 創建測試文檔
        test_document = Document(
            title="測試文檔",
            content="這是一個測試文檔，用於測試搜索功能。",
            created_by=1,
        )
        db_session.add(test_document)
        
        # 創建測試問題
        test_question = Question(
            title="測試問題",
            content="這是一個測試問題，用於測試搜索功能。",
            created_by=1,
        )
        db_session.add(test_question)
        
        # 提交更改
        db_session.commit()