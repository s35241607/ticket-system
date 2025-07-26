from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_, desc, text
from typing import List, Dict, Any, Optional, Tuple
import uuid
import logging

# 導入模型和架構
from ..models.knowledge import Document, Question, Category, User
from ..schemas.search import SearchResult

# 配置日誌
logger = logging.getLogger("search_service")


class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def search(self, query: str, search_type: str = "all", filters: Dict[str, Any] = None, skip: int = 0, limit: int = 20) -> Tuple[List[SearchResult], int]:
        """執行全文搜索"""
        results = []
        total = 0
        
        # 根據搜索類型執行不同的搜索
        if search_type in ["all", "document"]:
            doc_results, doc_total = self._search_documents(query, filters, skip, limit if search_type == "document" else limit // 2)
            results.extend(doc_results)
            total += doc_total
            
        if search_type in ["all", "question"]:
            # 如果是混合搜索，調整問題搜索的分頁參數
            q_skip = 0 if search_type == "question" else skip
            q_limit = limit if search_type == "question" else limit - len(results)
            
            if q_limit > 0:
                q_results, q_total = self._search_questions(query, filters, q_skip, q_limit)
                results.extend(q_results)
                if search_type == "question":
                    total = q_total
                else:
                    total += q_total
        
        # 按相關性得分排序
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results, total

    def _search_documents(self, query: str, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 20) -> Tuple[List[SearchResult], int]:
        """搜索文檔"""
        # 構建基本查詢
        base_query = self.db.query(
            Document,
            func.ts_rank_cd(
                Document.search_vector,
                func.plainto_tsquery('chinese', query)
            ).label('rank')
        ).filter(
            Document.search_vector.op('@@')(func.plainto_tsquery('chinese', query)),
            Document.is_published == True  # 只搜索已發布的文檔
        )
        
        # 應用篩選條件
        if filters:
            if filters.get("category_id"):
                base_query = base_query.filter(Document.category_id == filters["category_id"])
        
        # 計算總數
        total = base_query.count()
        
        # 獲取結果並排序
        documents = base_query.order_by(desc('rank')).offset(skip).limit(limit).all()
        
        # 構建結果列表
        results = []
        for doc, rank in documents:
            # 獲取用戶和分類信息
            user = self.db.query(User).filter(User.id == doc.user_id).first()
            category = self.db.query(Category).filter(Category.id == doc.category_id).first() if doc.category_id else None
            
            # 生成高亮片段
            highlights = self._generate_highlights(query, doc.content)
            
            # 創建搜索結果
            result = SearchResult(
                id=doc.id,
                type="document",
                title=doc.title,
                content=doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                highlight={"content": highlights},
                category_id=doc.category_id,
                category_name=category.name if category else None,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
                user_id=doc.user_id,
                user_name=user.full_name if user else "未知用戶",
                score=rank,
                is_published=doc.is_published,
                published_at=doc.published_at,
                view_count=doc.view_count
            )
            results.append(result)
        
        return results, total

    def _search_questions(self, query: str, filters: Dict[str, Any] = None, skip: int = 0, limit: int = 20) -> Tuple[List[SearchResult], int]:
        """搜索問題"""
        # 構建基本查詢
        base_query = self.db.query(
            Question,
            func.ts_rank_cd(
                Question.search_vector,
                func.plainto_tsquery('chinese', query)
            ).label('rank')
        ).filter(
            Question.search_vector.op('@@')(func.plainto_tsquery('chinese', query))
        )
        
        # 應用篩選條件
        if filters:
            if filters.get("category_id"):
                # 通過文檔關聯查詢分類
                base_query = base_query.join(Document).filter(Document.category_id == filters["category_id"])
        
        # 計算總數
        total = base_query.count()
        
        # 獲取結果並排序
        questions = base_query.order_by(desc('rank')).offset(skip).limit(limit).all()
        
        # 構建結果列表
        results = []
        for q, rank in questions:
            # 獲取用戶信息
            user = self.db.query(User).filter(User.id == q.user_id).first()
            
            # 獲取文檔和分類信息
            document = self.db.query(Document).filter(Document.id == q.document_id).first() if q.document_id else None
            category = None
            if document and document.category_id:
                category = self.db.query(Category).filter(Category.id == document.category_id).first()
            
            # 獲取回答數量
            answer_count = self.db.query(func.count("*")).select_from(text("answers")).where(text(f"question_id = '{q.id}'")).scalar()
            
            # 生成高亮片段
            title_highlights = self._generate_highlights(query, q.title)
            content_highlights = self._generate_highlights(query, q.content)
            
            # 創建搜索結果
            result = SearchResult(
                id=q.id,
                type="question",
                title=q.title,
                content=q.content[:200] + "..." if len(q.content) > 200 else q.content,
                highlight={
                    "title": title_highlights,
                    "content": content_highlights
                },
                category_id=document.category_id if document else None,
                category_name=category.name if category else None,
                created_at=q.created_at,
                updated_at=q.updated_at,
                user_id=q.user_id,
                user_name=user.full_name if user else "未知用戶",
                score=rank,
                is_resolved=q.is_resolved,
                resolved_at=q.resolved_at,
                answer_count=answer_count
            )
            results.append(result)
        
        return results, total

    def _generate_highlights(self, query: str, text: str) -> List[str]:
        """生成高亮片段"""
        # 簡單實現，實際項目中可以使用更複雜的高亮算法
        highlights = []
        words = query.lower().split()
        
        # 將文本分成段落
        paragraphs = text.split("\n")
        
        for paragraph in paragraphs:
            # 檢查段落是否包含查詢詞
            if any(word.lower() in paragraph.lower() for word in words):
                # 如果段落太長，截取包含查詢詞的部分
                if len(paragraph) > 100:
                    for word in words:
                        word_lower = word.lower()
                        pos = paragraph.lower().find(word_lower)
                        if pos >= 0:
                            start = max(0, pos - 50)
                            end = min(len(paragraph), pos + len(word) + 50)
                            snippet = paragraph[start:end]
                            if start > 0:
                                snippet = "..." + snippet
                            if end < len(paragraph):
                                snippet = snippet + "..."
                            highlights.append(snippet)
                else:
                    highlights.append(paragraph)
                    
        # 如果沒有找到高亮片段，返回文本的前100個字符
        if not highlights and text:
            highlights = [text[:100] + "..." if len(text) > 100 else text]
            
        return highlights[:3]  # 最多返回3個高亮片段