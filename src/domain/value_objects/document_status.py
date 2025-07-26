from enum import Enum, auto


class DocumentStatus(Enum):
    """文檔狀態"""
    DRAFT = auto()       # 草稿
    PUBLISHED = auto()   # 已發布
    ARCHIVED = auto()    # 已歸檔