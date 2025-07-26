from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, and_
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import logging

# 導入模型和架構
from ..models.knowledge import (
    Question, 
    Answer, 
    AnswerVote,
    Document
)
from ..schemas.question import (
    QuestionCreate, 
    QuestionUpdate, 
    AnswerCreate,
    AnswerUpdate,
    AnswerVoteCreate
)

# 配置日誌
logger = logging.getLogger("question_service")


class QuestionService:
    def __init__(self, db: Session):
        self.db = db

    def get_questions(self, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[Question]:
        """獲取問題列表，支持分頁和篩選"""
        query = self.db.query(Question)

        # 應用篩選條件
        if filters:
            if filters.get("document_id"):
                query = query.filter(Question.document_id == filters["document_id"])
            if filters.get("user_id"):
                query = query.filter(Question.user_id == filters["user_id"])
            if filters.get("is_resolved") is not None:
                query = query.filter(Question.is_resolved == filters["is_resolved"])
            if filters.get("search"):
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Question.title.ilike(search_term),
                        Question.content.ilike(search_term)
                    )
                )

        # 加載關聯數據
        query = query.options(
            joinedload(Question.user),
            joinedload(Question.document)
        )

        # 應用分頁
        query = query.order_by(Question.created_at.desc()).offset(skip).limit(limit)

        return query.all()

    def create_question(self, question_data: QuestionCreate) -> Question:
        """創建新問題"""
        # 檢查文檔是否存在
        document = self.db.query(Document).filter(Document.id == question_data.document_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"文檔 {question_data.document_id} 不存在"
            )

        # 創建問題
        question = Question(**question_data.dict())
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def get_question(self, question_id: uuid.UUID) -> Optional[Question]:
        """獲取問題詳情"""
        question = self.db.query(Question).options(
            joinedload(Question.user),
            joinedload(Question.document),
            joinedload(Question.answers).joinedload(Answer.user)
        ).filter(Question.id == question_id).first()

        if question:
            # 增加瀏覽次數
            question.view_count += 1
            self.db.commit()
            self.db.refresh(question)

        return question

    def update_question(self, question_id: uuid.UUID, question_update: QuestionUpdate) -> Optional[Question]:
        """更新問題"""
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return None

        # 更新字段
        update_data = question_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(question, key, value)

        # 如果解決狀態變更為已解決，設置解決時間
        if "is_resolved" in update_data and update_data["is_resolved"] and not question.resolved_at:
            question.resolved_at = datetime.now()
        elif "is_resolved" in update_data and not update_data["is_resolved"]:
            question.resolved_at = None

        self.db.commit()
        self.db.refresh(question)
        return question

    def delete_question(self, question_id: uuid.UUID) -> bool:
        """刪除問題"""
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return False

        # 刪除相關數據
        for answer in question.answers:
            self.db.query(AnswerVote).filter(AnswerVote.answer_id == answer.id).delete()
        self.db.query(Answer).filter(Answer.question_id == question_id).delete()
        
        self.db.delete(question)
        self.db.commit()
        return True

    def resolve_question(self, question_id: uuid.UUID) -> Optional[Question]:
        """將問題標記為已解決"""
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return None

        question.is_resolved = True
        question.resolved_at = datetime.now()
        self.db.commit()
        self.db.refresh(question)
        return question

    def unresolve_question(self, question_id: uuid.UUID) -> Optional[Question]:
        """將問題標記為未解決"""
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return None

        question.is_resolved = False
        question.resolved_at = None
        self.db.commit()
        self.db.refresh(question)
        return question

    def create_answer(self, question_id: uuid.UUID, answer_data: AnswerCreate) -> Answer:
        """添加回答"""
        # 檢查問題是否存在
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"問題 {question_id} 不存在"
            )

        answer = Answer(**answer_data.dict())
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def get_answers(self, question_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Answer]:
        """獲取問題的回答列表"""
        return self.db.query(Answer).options(
            joinedload(Answer.user),
            joinedload(Answer.votes)
        ).filter(Answer.question_id == question_id).order_by(
            Answer.is_accepted.desc(),
            func.count(AnswerVote.id).filter(AnswerVote.is_upvote == True).desc(),
            Answer.created_at.desc()
        ).offset(skip).limit(limit).all()

    def update_answer(self, answer_id: uuid.UUID, answer_update: AnswerUpdate) -> Optional[Answer]:
        """更新回答"""
        answer = self.db.query(Answer).filter(Answer.id == answer_id).first()
        if not answer:
            return None

        # 更新字段
        update_data = answer_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(answer, key, value)

        self.db.commit()
        self.db.refresh(answer)
        return answer

    def delete_answer(self, answer_id: uuid.UUID) -> bool:
        """刪除回答"""
        answer = self.db.query(Answer).filter(Answer.id == answer_id).first()
        if not answer:
            return False

        # 刪除相關數據
        self.db.query(AnswerVote).filter(AnswerVote.answer_id == answer_id).delete()
        
        self.db.delete(answer)
        self.db.commit()
        return True

    def accept_answer(self, question_id: uuid.UUID, answer_id: uuid.UUID) -> Optional[Answer]:
        """接受回答為最佳答案"""
        question = self.db.query(Question).filter(Question.id == question_id).first()
        answer = self.db.query(Answer).filter(
            Answer.id == answer_id,
            Answer.question_id == question_id
        ).first()

        if not question or not answer:
            return None

        # 取消其他回答的接受狀態
        self.db.query(Answer).filter(
            Answer.question_id == question_id,
            Answer.is_accepted == True
        ).update({"is_accepted": False, "accepted_at": None})

        # 設置當前回答為已接受
        answer.is_accepted = True
        answer.accepted_at = datetime.now()

        # 將問題標記為已解決
        question.is_resolved = True
        question.resolved_at = datetime.now()

        self.db.commit()
        self.db.refresh(answer)
        return answer

    def unaccept_answer(self, question_id: uuid.UUID, answer_id: uuid.UUID) -> Optional[Answer]:
        """取消接受回答為最佳答案"""
        question = self.db.query(Question).filter(Question.id == question_id).first()
        answer = self.db.query(Answer).filter(
            Answer.id == answer_id,
            Answer.question_id == question_id,
            Answer.is_accepted == True
        ).first()

        if not question or not answer:
            return None

        # 取消接受狀態
        answer.is_accepted = False
        answer.accepted_at = None

        # 如果沒有其他已接受的回答，將問題標記為未解決
        other_accepted = self.db.query(Answer).filter(
            Answer.question_id == question_id,
            Answer.is_accepted == True,
            Answer.id != answer_id
        ).first()

        if not other_accepted:
            question.is_resolved = False
            question.resolved_at = None

        self.db.commit()
        self.db.refresh(answer)
        return answer

    def vote_answer(self, answer_id: uuid.UUID, vote_data: AnswerVoteCreate) -> Optional[Answer]:
        """對回答進行投票（贊成或反對）"""
        answer = self.db.query(Answer).filter(Answer.id == answer_id).first()
        if not answer:
            return None

        # 檢查用戶是否已經投過票
        existing_vote = self.db.query(AnswerVote).filter(
            AnswerVote.answer_id == answer_id,
            AnswerVote.user_id == vote_data.user_id
        ).first()

        if existing_vote:
            # 如果投票類型相同，則刪除投票（取消投票）
            if existing_vote.is_upvote == vote_data.is_upvote:
                self.db.delete(existing_vote)
            else:
                # 如果投票類型不同，則更新投票類型
                existing_vote.is_upvote = vote_data.is_upvote
                existing_vote.updated_at = datetime.now()
        else:
            # 創建新投票
            vote = AnswerVote(**vote_data.dict())
            self.db.add(vote)

        self.db.commit()
        self.db.refresh(answer)
        return answer