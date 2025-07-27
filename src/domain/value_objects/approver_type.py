from enum import Enum


class ApproverType(Enum):
    """審批者類型"""
    ROLE = "role"                       # 基於角色
    DEPARTMENT = "department"           # 基於部門
    INDIVIDUAL = "individual"           # 個人
    CREATOR_MANAGER = "creator_manager" # 創建者的主管