from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from backend.app.schemas.user import UserSimple
from backend.app.schemas.module import ModuleResponse

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="")
    default_version: str = Field(default="")
    is_active: bool = Field(default=True)

class ProjectCreate(ProjectBase):
    member_ids: Optional[List[int]] = Field(default_factory=list)
    modules: Optional[List[str]] = Field(default_factory=list)

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    default_version: Optional[str] = None
    is_active: Optional[bool] = None
    member_ids: Optional[List[int]] = None

class ProjectResponse(ProjectBase):
    id: int
    created_at: Optional[datetime] = None
    active_bugs_count: Optional[int] = 0
    my_bugs_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class ProjectDetail(ProjectResponse):
    modules: List[ModuleResponse] = []
    members: List[UserSimple] = []
