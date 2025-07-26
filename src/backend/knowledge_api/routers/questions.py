from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

# 導入數據庫依賴
from database.session import get_db

# 導入模型和架構
from ..models.knowledge import Question, Answer, AnswerVote
from ..schemas.question import (
    QuestionCreate, 
    QuestionUpdate, 
    QuestionResponse, 
    QuestionListResponse,
    AnswerCreate,
    AnswerUpdate,
    AnswerResponse,
    AnswerVoteCreate
)

# 導入服務
from ..services.question_service import QuestionService

# 創建路由
router = APIRouter()

# 獲取問答服務實例
def get_question_service(db: Session = Depends(get_db)):
    return QuestionService(db)


@router.get("/", response_model=List[QuestionListResponse])
async def get_questions(
    skip: int = Query(0, description="跳過的記錄數"),
    limit: int = Query(100, description="返回的最大記錄數"),
    document_id: Optional[uuid.UUID] = Query(None, description="按文檔篩選"),
    user_id: Optional[uuid.UUID] = Query(None, description="按用戶篩選"),
    is_resolved: Optional[bool] = Query(None, description="按解決狀態篩選"),
    search: Optional[str] = Query(None, description="搜索標題和內容"),
    question_service: QuestionService = Depends(get_question_service)
):
    """獲取問題列表，支持分頁和篩選"""
    filters = {
        "document_id": document_id,
        "user_id": user_id,
        "is_resolved": is_resolved,
        "search": search
    }
    return question_service.get_questions(skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question: QuestionCreate,
    question_service: QuestionService = Depends(get_question_service)
):
    """創建新問題"""
    return question_service.create_question(question)


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: uuid.UUID = Path(..., description="問題ID"),
    question_service: QuestionService = Depends(get_question_service)
):
    """獲取問題詳情"""
    question = question_service.get_question(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"問題 {question_id} 不存在"
        )
    return question


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: uuid.UUID = Path(..., description="問題ID"),
    question_update: QuestionUpdate = Body(...),
    question_service: QuestionService = Depends(get_question_service)
):
    """更新問題"""
    question = question_service.update_question(question_id, question_update)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"問題 {question_id} 不存在"
        )
    return question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: uuid.UUID = Path(..., description="問題ID"),
    question_service: QuestionService = Depends(get_question_service)
):
    """刪除問題"""
    success = question_service.delete_question(question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"問題 {question_id} 不存在"
        )
    return None


@router.post("/{question_id}/resolve", response_model=QuestionResponse)
async def resolve_question(
    question_id: uuid.UUID = Path(..., description="問題ID"),
    question_service: QuestionService = Depends(get_question_service)
):
    """將問題標記為已解決"""
    question = question_service.resolve_question(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"問題 {question_id} 不存在"
        )
    return question


@router.post("/{question_id}/unresolve", response_model=QuestionResponse)
async def unresolve_question(
    question_id: uuid.UUID = Path(..., description="問題ID"),
    question_service: QuestionService = Depends(get_question_service)
):
    """將問題標記為未解決"""
    question = question_service.unresolve_question(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"問題 {question_id} 不存在"
        )
    return question


@router.post("/{question_id}/answers", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def create_answer(
    question_id: uuid.UUID = Path(..., description="問題ID"),
    answer: AnswerCreate = Body(...),
    question_service: QuestionService = Depends(get_question_service)
):
    """添加回答"""
    return question_service.create_answer(question_id, answer)


@router.get("/{question_id}/answers", response_model=List[AnswerResponse])
async def get_answers(
    question_id: uuid.UUID = Path(..., description="問題ID"),
    skip: int = Query(0, description="跳過的記錄數"),
    limit: int = Query(100, description="返回的最大記錄數"),
    question_service: QuestionService = Depends(get_question_service)
):
    """獲取問題的回答列表"""
    return question_service.get_answers(question_id, skip, limit)


@router.put("/{question_id}/answers/{answer_id}", response_model=AnswerResponse)
async def update_answer(
    question_id: uuid.UUID = Path(..., description="問題ID"),
    answer_id: uuid.UUID = Path(..., description="回答ID"),
    answer_update: AnswerUpdate = Body(...),
    question_service: QuestionService = Depends(get_question_service)
):
    """更新回答"""
    answer = question_service.update_answer(answer_id, answer_update)
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"回答 {answer_id} 不存在"
        )
    return answer


@router.delete("/{question_id}/answers/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(
    question_id: uuid.UUID = Path(..., description="問題ID"),
    answer_id: uuid.UUID = Path(..., description="回答ID"),
    question_service: QuestionService = Depends(get_question_service)
):
    """刪除回答"""
    success = question_service.delete_answer(answer_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"回答 {answer_id} 不存在"
        )
    return None


@router.post("/{question_id}/answers/{answer_id}/accept", response_model=AnswerResponse)
async def accept_answer(
    question_id: uuid.UUID = Path(..., description="問題ID"),
    answer_id: uuid.UUID = Path(..., description="回答ID"),
    question_service: QuestionService = Depends(get_question_service)
):
    """接受回答為最佳答案"""
    answer = question_service.accept_answer(question_id, answer_id)
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"問題 {question_id} 或回答 {answer_id} 不存在"
        )
    return answer


@router.post("/{question_id}/answers/{answer_id}/unaccept", response_model=AnswerResponse)
async def unaccept_answer(
    question_id: uuid.UUID = Path(..., description="問題ID"),
    answer_id: uuid.UUID = Path(..., description="回答ID"),
    question_service: QuestionService = Depends(get_question_service)
):
    """取消接受回答為最佳答案"""
    answer = question_service.unaccept_answer(question_id, answer_id)
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"問題 {question_id} 或回答 {answer_id} 不存在"
        )
    return answer


@router.post("/{question_id}/answers/{answer_id}/vote", response_model=AnswerResponse)
async def vote_answer(
    question_id: uuid.UUID = Path(..., description="問題ID"),
    answer_id: uuid.UUID = Path(..., description="回答ID"),
    vote: AnswerVoteCreate = Body(...),
    question_service: QuestionService = Depends(get_question_service)
):
    """對回答進行投票（贊成或反對）"""
    answer = question_service.vote_answer(answer_id, vote)
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"回答 {answer_id} 不存在"
        )
    return answer