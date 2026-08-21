from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="modules")
    bugs = relationship("Bug", back_populates="module")
