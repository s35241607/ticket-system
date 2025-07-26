from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.orm import relationship
import uuid

from database.session import Base


# 文檔與標籤的多對多關聯表
document_tag = Table(
    "document_tag",
    Base.metadata,
    Column("document_id", UUID, ForeignKey("documents.id"), primary_key=True),
    Column("tag_id", UUID, ForeignKey("document_tags.id"), primary_key=True),
)


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_id = Column(UUID, ForeignKey("categories.id"))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 關聯
    parent = relationship("Category", remote_side=[id], backref="children")
    documents = relationship("Document", back_populates="category")


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    category_id = Column(UUID, ForeignKey("categories.id"), nullable=False)
    creator_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    is_published = Column(Boolean, nullable=False, default=False)
    view_count = Column(Integer, nullable=False, default=0)
    search_vector = Column(TSVECTOR)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime)
    
    # 關聯
    category = relationship("Category", back_populates="documents")
    creator = relationship("User")
    attachments = relationship("DocumentAttachment", back_populates="document")
    comments = relationship("DocumentComment", back_populates="document")
    history = relationship("DocumentHistory", back_populates="document")
    tags = relationship("DocumentTag", secondary=document_tag, back_populates="documents")
    questions = relationship("Question", back_populates="document")


class DocumentAttachment(Base):
    __tablename__ = "document_attachments"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID, ForeignKey("documents.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # 關聯
    document = relationship("Document", back_populates="attachments")
    user = relationship("User")


class DocumentComment(Base):
    __tablename__ = "document_comments"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID, ForeignKey("documents.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 關聯
    document = relationship("Document", back_populates="comments")
    user = relationship("User")


class DocumentHistory(Base):
    __tablename__ = "document_history"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID, ForeignKey("documents.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    changes = Column(JSONB)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # 關聯
    document = relationship("Document", back_populates="history")
    user = relationship("User")


class DocumentTag(Base):
    __tablename__ = "document_tags"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 關聯
    documents = relationship("Document", secondary=document_tag, back_populates="tags")


class Question(Base):
    __tablename__ = "questions"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    document_id = Column(UUID, ForeignKey("documents.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    is_resolved = Column(Boolean, nullable=False, default=False)
    view_count = Column(Integer, nullable=False, default=0)
    search_vector = Column(TSVECTOR)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime)
    
    # 關聯
    document = relationship("Document", back_populates="questions")
    user = relationship("User")
    answers = relationship("Answer", back_populates="question")


class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID, ForeignKey("questions.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_accepted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    accepted_at = Column(DateTime)
    
    # 關聯
    question = relationship("Question", back_populates="answers")
    user = relationship("User")
    votes = relationship("AnswerVote", back_populates="answer")


class AnswerVote(Base):
    __tablename__ = "answer_votes"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    answer_id = Column(UUID, ForeignKey("answers.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    is_upvote = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 關聯
    answer = relationship("Answer", back_populates="votes")
    user = relationship("User")