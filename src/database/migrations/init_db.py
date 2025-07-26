import os
import sys
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from src.config import settings
from src.database.db import engine, Base
from src.utils.logger import get_logger
from src.utils.security import get_password_hash

# 導入所有模型以確保它們被註冊到Base中
from src.backend.ticket_api.models.department import Department
from src.backend.ticket_api.models.user import User
from src.backend.ticket_api.models.workflow import Workflow, WorkflowStep
from src.backend.ticket_api.models.ticket import Ticket, TicketComment, TicketAttachment

from src.backend.knowledge_api.models.category import Category
from src.backend.knowledge_api.models.document import Document, DocumentVersion, DocumentAttachment
from src.backend.knowledge_api.models.question import Question, Answer, Vote

# 創建日誌記錄器
logger = get_logger(__name__)


def create_directories():
    """
    創建必要的目錄結構
    """
    directories = [
        "static",
        "uploads",
        "uploads/documents",
        "uploads/tickets",
        "logs",
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"創建目錄: {dir_path}")


def create_tables():
    """
    創建數據庫表
    """
    try:
        # 創建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("數據庫表創建成功")
    except SQLAlchemyError as e:
        logger.error(f"創建數據庫表時出錯: {str(e)}")
        sys.exit(1)


def create_initial_data():
    """
    創建初始數據
    """
    from sqlalchemy.orm import Session
    
    try:
        with Session(engine) as session:
            # 檢查是否已有管理員部門
            admin_dept = session.query(Department).filter_by(name="管理部門").first()
            if not admin_dept:
                admin_dept = Department(name="管理部門", description="系統管理部門")
                session.add(admin_dept)
                session.flush()
                logger.info("創建管理部門")
            
            # 檢查是否已有管理員用戶
            admin_user = session.query(User).filter_by(username="admin").first()
            if not admin_user:
                admin_user = User(
                    username="admin",
                    email="admin@example.com",
                    hashed_password=get_password_hash("admin123"),
                    full_name="系統管理員",
                    department_id=admin_dept.id,
                    is_admin=True,
                )
                session.add(admin_user)
                logger.info("創建管理員用戶")
            
            # 檢查是否已有默認工作流
            default_workflow = session.query(Workflow).filter_by(name="默認工作流").first()
            if not default_workflow:
                default_workflow = Workflow(
                    name="默認工作流",
                    description="默認的工單處理流程",
                )
                session.add(default_workflow)
                session.flush()
                
                # 創建工作流步驟
                steps = [
                    WorkflowStep(name="提交", description="工單提交", order=1, workflow_id=default_workflow.id),
                    WorkflowStep(name="處理中", description="工單處理中", order=2, workflow_id=default_workflow.id),
                    WorkflowStep(name="完成", description="工單完成", order=3, workflow_id=default_workflow.id),
                ]
                session.add_all(steps)
                logger.info("創建默認工作流和步驟")
            
            # 檢查是否已有根分類
            root_category = session.query(Category).filter_by(name="根分類", parent_id=None).first()
            if not root_category:
                root_category = Category(
                    name="根分類",
                    description="知識庫根分類",
                )
                session.add(root_category)
                logger.info("創建根分類")
            
            # 提交所有更改
            session.commit()
            logger.info("初始數據創建成功")
    except SQLAlchemyError as e:
        logger.error(f"創建初始數據時出錯: {str(e)}")
        sys.exit(1)


def main():
    """
    主函數
    """
    logger.info("開始初始化數據庫")
    
    # 創建目錄
    create_directories()
    
    # 創建表
    create_tables()
    
    # 創建初始數據
    create_initial_data()
    
    logger.info("數據庫初始化完成")


if __name__ == "__main__":
    main()