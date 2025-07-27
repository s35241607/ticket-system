from enum import Enum


class ApprovalStatus(Enum):
    """審批狀態"""
    PENDING = "pending"           # 待審批
    IN_PROGRESS = "in_progress"   # 審批中
    APPROVED = "approved"         # 已批准
    REJECTED = "rejected"         # 已拒絕
    REQUIRES_CHANGES = "requires_changes"  # 需要修改
    CANCELLED = "cancelled"       # 已取消