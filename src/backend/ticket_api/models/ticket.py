from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from database.session import Base


class Department(Base):
    __tablename__ = "departments"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_id = Column(UUID, ForeignKey("departments.id"))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    parent = relationship("Department", remote_side=[id], backref="children")
    users = relationship("User", back_populates="department")
    workflow_steps = relationship("WorkflowStep", back_populates="department")


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    full_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    department_id = Column(UUID, ForeignKey("departments.id"))
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    department = relationship("Department", back_populates="users")
    created_tickets = relationship("Ticket", foreign_keys="[Ticket.creator_id]", back_populates="creator")
    assigned_tickets = relationship("Ticket", foreign_keys="[Ticket.assignee_id]", back_populates="assignee")
    ticket_comments = relationship("TicketComment", back_populates="user")
    ticket_history = relationship("TicketHistory", back_populates="user")
    workflow_approvals = relationship("WorkflowApproval", back_populates="approver")
    notifications = relationship("Notification", back_populates="user")


class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    steps = relationship("WorkflowStep", back_populates="workflow", order_by="WorkflowStep.order")
    ticket_types = relationship("TicketType", back_populates="workflow")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID, ForeignKey("workflows.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    department_id = Column(UUID, ForeignKey("departments.id"))
    order = Column(Integer, nullable=False)
    requires_approval = Column(Boolean, nullable=False, default=False)
    is_final = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="steps")
    department = relationship("Department", back_populates="workflow_steps")
    approvals = relationship("WorkflowApproval", back_populates="workflow_step")
    tickets = relationship("Ticket", foreign_keys="[Ticket.current_workflow_step_id]", back_populates="current_workflow_step")


class TicketType(Base):
    __tablename__ = "ticket_types"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    workflow_id = Column(UUID, ForeignKey("workflows.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="ticket_types")
    tickets = relationship("Ticket", back_populates="ticket_type")


class TicketStatus(Base):
    __tablename__ = "ticket_statuses"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    color = Column(String(20), nullable=False)
    order = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tickets = relationship("Ticket", back_populates="ticket_status")


class TicketPriority(Base):
    __tablename__ = "ticket_priorities"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    color = Column(String(20), nullable=False)
    order = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tickets = relationship("Ticket", back_populates="ticket_priority")


class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    creator_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(UUID, ForeignKey("users.id"))
    ticket_type_id = Column(UUID, ForeignKey("ticket_types.id"), nullable=False)
    ticket_status_id = Column(UUID, ForeignKey("ticket_statuses.id"), nullable=False)
    ticket_priority_id = Column(UUID, ForeignKey("ticket_priorities.id"), nullable=False)
    current_workflow_step_id = Column(UUID, ForeignKey("workflow_steps.id"))
    due_date = Column(DateTime)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    closed_at = Column(DateTime)
    
    # Relationships
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_tickets")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tickets")
    ticket_type = relationship("TicketType", back_populates="tickets")
    ticket_status = relationship("TicketStatus", back_populates="tickets")
    ticket_priority = relationship("TicketPriority", back_populates="tickets")
    current_workflow_step = relationship("WorkflowStep", foreign_keys=[current_workflow_step_id], back_populates="tickets")
    attachments = relationship("TicketAttachment", back_populates="ticket")
    comments = relationship("TicketComment", back_populates="ticket")
    history = relationship("TicketHistory", back_populates="ticket")
    workflow_approvals = relationship("WorkflowApproval", back_populates="ticket")
    notifications = relationship("Notification", back_populates="ticket")


class TicketAttachment(Base):
    __tablename__ = "ticket_attachments"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID, ForeignKey("tickets.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    ticket = relationship("Ticket", back_populates="attachments")
    user = relationship("User")


class TicketComment(Base):
    __tablename__ = "ticket_comments"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID, ForeignKey("tickets.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    ticket = relationship("Ticket", back_populates="comments")
    user = relationship("User", back_populates="ticket_comments")


class TicketHistory(Base):
    __tablename__ = "ticket_history"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID, ForeignKey("tickets.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    changes = Column(JSONB)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    ticket = relationship("Ticket", back_populates="history")
    user = relationship("User", back_populates="ticket_history")


class WorkflowApproval(Base):
    __tablename__ = "workflow_approvals"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID, ForeignKey("tickets.id"), nullable=False)
    workflow_step_id = Column(UUID, ForeignKey("workflow_steps.id"), nullable=False)
    approver_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    is_approved = Column(Boolean)
    comment = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    ticket = relationship("Ticket", back_populates="workflow_approvals")
    workflow_step = relationship("WorkflowStep", back_populates="approvals")
    approver = relationship("User", back_populates="workflow_approvals")


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    ticket_id = Column(UUID, ForeignKey("tickets.id"), nullable=False)
    type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    read_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    ticket = relationship("Ticket", back_populates="notifications")