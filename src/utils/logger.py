import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from src.config import settings

# 確保日誌目錄存在
log_dir = Path(settings.LOG_DIR)
log_dir.mkdir(parents=True, exist_ok=True)

# 獲取當前日期作為日誌文件名的一部分
current_date = datetime.now().strftime("%Y-%m-%d")

# 配置日誌格式
log_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# 創建控制台處理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)

# 創建文件處理器
file_handler = RotatingFileHandler(
    filename=os.path.join(settings.LOG_DIR, f"{current_date}.log"),
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding="utf-8",
)
file_handler.setFormatter(log_formatter)


def get_logger(name: str) -> logging.Logger:
    """
    獲取配置好的日誌記錄器

    Args:
        name: 日誌記錄器名稱，通常是模塊名稱

    Returns:
        配置好的日誌記錄器實例
    """
    logger = logging.getLogger(name)
    
    # 設置日誌級別
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # 添加處理器
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    # 防止日誌傳播到根日誌記錄器
    logger.propagate = False
    
    return logger