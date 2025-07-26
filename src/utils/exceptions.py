from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """
    API異常的基類
    """
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "服務器內部錯誤"

    def __init__(
        self,
        detail: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
            headers=headers,
        )


class NotFoundException(BaseAPIException):
    """
    資源未找到異常
    """
    status_code = status.HTTP_404_NOT_FOUND
    detail = "請求的資源不存在"


class BadRequestException(BaseAPIException):
    """
    錯誤請求異常
    """
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "請求參數錯誤"


class UnauthorizedException(BaseAPIException):
    """
    未授權異常
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "未授權訪問"


class ForbiddenException(BaseAPIException):
    """
    禁止訪問異常
    """
    status_code = status.HTTP_403_FORBIDDEN
    detail = "禁止訪問該資源"


class ConflictException(BaseAPIException):
    """
    資源衝突異常
    """
    status_code = status.HTTP_409_CONFLICT
    detail = "資源衝突"


class ValidationException(BaseAPIException):
    """
    數據驗證異常
    """
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "數據驗證失敗"


class DatabaseException(BaseAPIException):
    """
    數據庫操作異常
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "數據庫操作失敗"


class ExternalServiceException(BaseAPIException):
    """
    外部服務調用異常
    """
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "外部服務調用失敗"


class RateLimitException(BaseAPIException):
    """
    請求頻率限制異常
    """
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "請求頻率超過限制"


class FileUploadException(BaseAPIException):
    """
    文件上傳異常
    """
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "文件上傳失敗"


class SearchException(BaseAPIException):
    """
    搜索操作異常
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "搜索操作失敗"