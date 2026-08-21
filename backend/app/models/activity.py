from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bug_id = Column(Integer, ForeignKey("bugs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action_type = Column(String(50), nullable=False)  # status_change, assign, create, edit, upload, comment
    old_value = Column(String(255), default="", nullable=False)
    new_value = Column(String(255), default="", nullable=False)
    detail = Column(Text, default="", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    bug = relationship("Bug", back_populates="activities")
    user = relationship("User", back_populates="activities")
