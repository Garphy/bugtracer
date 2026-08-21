from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

STATUS_MAP = {
    0: "closed",
    1: "new",
    2: "key",
    3: "part_fixed",
    4: "fixed",
    5: "wont_fix",
    6: "todo",
    7: "idea"
}

STATUS_NAMES = {
    0: "已关闭",
    1: "新增",
    2: "重要",
    3: "部分处理",
    4: "已解决",
    5: "不处理",
    6: "待办",
    7: "备忘"
}

class Bug(Base):
    __tablename__ = "bugs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="SET NULL"), nullable=True, index=True)
    
    status = Column(Integer, default=1, nullable=False, index=True)  # 0~7
    ver = Column(String(50), default="", nullable=False)
    title = Column(String(255), default="", nullable=False)  # Derived/optional short title
    content = Column(Text, nullable=False)
    
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, default=0, index=True)
    last_changer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    priority = Column(Integer, default=0, nullable=False)  # 0: normal, 1: high, 2: critical
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    fixed_at = Column(DateTime, nullable=True)
    close_reason = Column(Text, default="", nullable=False)

    # Relationships
    project = relationship("Project", back_populates="bugs")
    module = relationship("Module", back_populates="bugs")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_bugs")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_bugs")
    last_changer = relationship("User", foreign_keys=[last_changer_id])
    attachments = relationship("Attachment", back_populates="bug", cascade="all, delete-orphan", order_by="Attachment.id")
    comments = relationship("Comment", back_populates="bug", cascade="all, delete-orphan", order_by="Comment.created_at")
    activities = relationship("Activity", back_populates="bug", cascade="all, delete-orphan", order_by="Activity.created_at.desc()")

    @property
    def status_name(self) -> str:
        return STATUS_NAMES.get(self.status, "未知")

    @property
    def status_code(self) -> str:
        return STATUS_MAP.get(self.status, "unknown")
