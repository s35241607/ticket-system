from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 密碼上下文，用於密碼加密和驗證
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2密碼承載器，用於從請求中提取令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")


class TokenPayload(BaseModel):
    """
    令牌載荷模型
    """
    sub: str  # 用戶ID
    exp: int  # 過期時間
    iat: int  # 簽發時間
    type: str  # 令牌類型
    jti: str  # JWT ID
    username: str  # 用戶名
    role: Optional[str] = None  # 用戶角色


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    驗證密碼

    Args:
        plain_password: 明文密碼
        hashed_password: 哈希密碼

    Returns:
        密碼是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    獲取密碼哈希

    Args:
        password: 明文密碼

    Returns:
        密碼哈希
    """
    return pwd_context.hash(password)


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    創建訪問令牌

    Args:
        data: 令牌數據
        expires_delta: 過期時間增量

    Returns:
        JWT令牌
    """
    to_encode = data.copy()
    
    # 設置過期時間
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # 添加標準聲明
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access_token",
    })
    
    # 編碼JWT
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    獲取當前用戶

    Args:
        token: JWT令牌

    Returns:
        當前用戶信息

    Raises:
        HTTPException: 令牌無效或過期時拋出
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證憑據",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解碼JWT
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        
        # 驗證令牌載荷
        token_data = TokenPayload(**payload)
        
        # 檢查令牌是否過期
        if datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
            raise credentials_exception
        
        # 返回用戶信息
        return {
            "id": token_data.sub,
            "username": token_data.username,
            "role": token_data.role,
        }
    except (JWTError, ValidationError) as e:
        logger.error(f"令牌驗證失敗: {str(e)}")
        raise credentials_exception


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    獲取當前活動用戶

    Args:
        current_user: 當前用戶信息

    Returns:
        當前活動用戶信息

    Raises:
        HTTPException: 用戶不活躍時拋出
    """
    # 這裡可以添加額外的用戶狀態檢查，例如檢查用戶是否被禁用
    # 如果用戶不活躍，可以拋出異常
    # if current_user.get("is_active") is False:
    #     raise HTTPException(status_code=400, detail="用戶不活躍")
    
    return current_user