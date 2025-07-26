import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    請求日誌中間件，記錄每個請求的處理時間和狀態碼
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 獲取請求信息
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else "unknown"
        
        # 處理請求
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            status_code = response.status_code
            
            # 記錄請求信息
            logger.info(
                f"Request: {method} {url} | Status: {status_code} | "
                f"Client: {client_host} | Time: {process_time:.3f}s"
            )
            
            # 添加處理時間頭
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request: {method} {url} | Error: {str(e)} | "
                f"Client: {client_host} | Time: {process_time:.3f}s"
            )
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    速率限制中間件，限制每個IP的請求頻率
    
    注意：這是一個簡單的實現，生產環境中應使用更強大的解決方案，如Redis
    """
    def __init__(self, app: FastAPI, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
        self.window_size = 60  # 窗口大小（秒）

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 獲取客戶端IP
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # 清理過期記錄
        self._clean_expired_records(current_time)
        
        # 檢查請求頻率
        if self._is_rate_limited(client_ip, current_time):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                content="請求頻率超過限制，請稍後再試",
                status_code=429,
                media_type="text/plain",
            )
        
        # 處理請求
        return await call_next(request)
    
    def _clean_expired_records(self, current_time: float) -> None:
        """
        清理過期記錄
        """
        expired_time = current_time - self.window_size
        for ip, requests in list(self.request_counts.items()):
            self.request_counts[ip] = [
                req_time for req_time in requests if req_time > expired_time
            ]
            if not self.request_counts[ip]:
                del self.request_counts[ip]
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """
        檢查是否超過速率限制
        """
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        # 添加當前請求時間
        self.request_counts[client_ip].append(current_time)
        
        # 檢查請求數量是否超過限制
        return len(self.request_counts[client_ip]) > self.requests_per_minute


def setup_middleware(app: FastAPI) -> None:
    """
    設置中間件

    Args:
        app: FastAPI應用實例
    """
    # 添加CORS中間件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加請求日誌中間件
    app.add_middleware(RequestLoggingMiddleware)
    
    # 添加速率限制中間件（僅在生產環境中啟用）
    if settings.ENVIRONMENT == "production":
        app.add_middleware(RateLimitMiddleware, requests_per_minute=60)