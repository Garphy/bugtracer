from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    fullname = Column(String(50), nullable=False)
    role = Column(String(20), default="coder", nullable=False)  # admin, coder, tester, guest
    api_key = Column(String(100), unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    created_bugs = relationship("Bug", back_populates="creator", foreign_keys="Bug.creator_id")
    assigned_bugs = relationship("Bug", back_populates="assignee", foreign_keys="Bug.assignee_id")
    project_memberships = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "fullname": self.fullname,
            "role": self.role,
            "is_active": self.is_active,
            "api_key": self.api_key,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
