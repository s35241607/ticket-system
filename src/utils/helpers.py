import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fastapi import UploadFile
from slugify import slugify

from src.config import settings
from src.utils.exceptions import FileUploadException
from src.utils.logger import get_logger

logger = get_logger(__name__)


def generate_uuid() -> str:
    """
    生成UUID字符串

    Returns:
        UUID字符串
    """
    return str(uuid.uuid4())


def get_current_timestamp() -> int:
    """
    獲取當前UTC時間戳（秒）

    Returns:
        當前UTC時間戳（秒）
    """
    return int(datetime.now(timezone.utc).timestamp())


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期時間

    Args:
        dt: 日期時間對象
        format_str: 格式化字符串

    Returns:
        格式化後的日期時間字符串
    """
    return dt.strftime(format_str)


def create_slug(text: str) -> str:
    """
    創建URL友好的slug

    Args:
        text: 原始文本

    Returns:
        URL友好的slug
    """
    return slugify(text)


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除不安全字符

    Args:
        filename: 原始文件名

    Returns:
        清理後的文件名
    """
    # 移除路徑分隔符和其他不安全字符
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # 限制長度
    if len(sanitized) > 100:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:100 - len(ext)] + ext
    return sanitized


async def save_upload_file(upload_file: UploadFile, directory: str) -> str:
    """
    保存上傳的文件

    Args:
        upload_file: 上傳的文件
        directory: 保存目錄

    Returns:
        保存後的文件路徑

    Raises:
        FileUploadException: 文件上傳失敗時拋出
    """
    try:
        # 確保目錄存在
        upload_dir = Path(directory)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成安全的文件名
        original_filename = upload_file.filename or "unnamed_file"
        safe_filename = sanitize_filename(original_filename)
        
        # 添加UUID前綴避免文件名衝突
        unique_filename = f"{generate_uuid()[:8]}_{safe_filename}"
        file_path = upload_dir / unique_filename
        
        # 保存文件
        content = await upload_file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise FileUploadException(f"文件大小超過限制 {settings.MAX_UPLOAD_SIZE} bytes")
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        return str(file_path)
    except Exception as e:
        logger.error(f"文件上傳失敗: {str(e)}")
        raise FileUploadException(f"文件上傳失敗: {str(e)}")


def paginate_results(items: List[Any], page: int, page_size: int) -> Dict[str, Any]:
    """
    對結果進行分頁

    Args:
        items: 結果列表
        page: 頁碼
        page_size: 每頁大小

    Returns:
        分頁後的結果字典
    """
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        "items": items[start:end],
        "total": len(items),
        "page": page,
        "page_size": page_size,
        "pages": (len(items) + page_size - 1) // page_size,
    }


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    截斷文本，超過最大長度時添加省略號

    Args:
        text: 原始文本
        max_length: 最大長度

    Returns:
        截斷後的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."