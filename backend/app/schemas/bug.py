from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, Field, ConfigDict
from backend.app.schemas.user import UserSimple
from backend.app.schemas.module import ModuleResponse
from backend.app.schemas.attachment import AttachmentResponse
from backend.app.schemas.comment import CommentResponse, ActivityResponse

class BugBase(BaseModel):
    project_id: int
    module_id: Optional[int] = None
    ver: str = Field(default="")
    content: str = Field(..., min_length=1)
    assignee_id: Optional[int] = 0
    priority: int = Field(default=0)  # 0: normal, 1: high, 2: critical

class BugCreate(BugBase):
    status: int = Field(default=1)  # default new (1)
    attachment_ids: Optional[List[int]] = Field(default_factory=list)
    files: Optional[List[str]] = Field(default_factory=list)

class BugUpdate(BaseModel):
    project_id: Optional[int] = None
    module_id: Optional[int] = None
    ver: Optional[str] = None
    content: Optional[str] = None
    assignee_id: Optional[int] = None
    priority: Optional[int] = None
    status: Optional[int] = None
    close_reason: Optional[str] = None
    attachment_ids: Optional[List[int]] = None
    files: Optional[List[str]] = None

class BugStatusUpdate(BaseModel):
    status: int = Field(..., ge=0, le=7)
    close_reason: Optional[str] = ""

class BugAssignUpdate(BaseModel):
    assignee_id: int

class BugListItem(BaseModel):
    id: int
    project_id: int
    project_name: Optional[str] = ""
    module_id: Optional[int] = None
    module_name: Optional[str] = ""
    status: int
    status_code: str
    status_name: str
    ver: str
    content: str
    has_attachment: bool = False
    creator_id: Optional[int] = None
    creator_name: Optional[str] = ""
    assignee_id: Optional[int] = None
    assignee_name: Optional[str] = ""
    last_changer_name: Optional[str] = ""
    is_assigned_to_me: bool = False
    priority: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BugDetailResponse(BaseModel):
    id: int
    project_id: int
    project_name: Optional[str] = ""
    module_id: Optional[int] = None
    module_name: Optional[str] = ""
    status: int
    status_code: str
    status_name: str
    ver: str
    content: str
    creator_id: Optional[int] = None
    creator: Optional[UserSimple] = None
    assignee_id: Optional[int] = None
    assignee: Optional[UserSimple] = None
    last_changer_id: Optional[int] = None
    last_changer: Optional[UserSimple] = None
    priority: int = 0
    close_reason: Optional[str] = ""
    created_at: datetime
    updated_at: datetime
    fixed_at: Optional[datetime] = None
    attachments: List[AttachmentResponse] = []
    comments: List[CommentResponse] = []
    activities: List[ActivityResponse] = []

    model_config = ConfigDict(from_attributes=True)

class BugListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[BugListItem]
    counts_summary: dict = {}
