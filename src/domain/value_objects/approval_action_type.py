from enum import Enum


class ApprovalActionType(Enum):
    """審批行為類型"""
    APPROVE = "approve"                 # 批准
    REJECT = "reject"                   # 拒絕
    REQUEST_CHANGES = "request_changes" # 要求修改
    ESCALATE = "escalate"               # 升級
    AUTO_APPROVE = "auto_approve"       # 自動批准