from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="", nullable=False)
    default_version = Column(String(50), default="", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    modules = relationship("Module", back_populates="project", cascade="all, delete-orphan", order_by="Module.sort_order")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    bugs = relationship("Bug", back_populates="project", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="project", cascade="all, delete-orphan")

class ProjectMember(Base):
    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_project_user"),)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_in_project = Column(String(20), default="member", nullable=False)  # lead, member
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")
