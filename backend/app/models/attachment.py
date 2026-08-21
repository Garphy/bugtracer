from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bug_id = Column(Integer, ForeignKey("bugs.id", ondelete="CASCADE"), nullable=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    uploader_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    original_name = Column(String(255), nullable=False)
    stored_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0, nullable=False)
    mime_type = Column(String(100), default="", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    bug = relationship("Bug", back_populates="attachments")
    project = relationship("Project", back_populates="attachments")
    uploader = relationship("User")
