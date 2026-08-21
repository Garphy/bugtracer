from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from backend.app.schemas.user import UserSimple

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)

class CommentResponse(BaseModel):
    id: int
    bug_id: int
    user_id: Optional[int] = None
    user: Optional[UserSimple] = None
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ActivityResponse(BaseModel):
    id: int
    bug_id: int
    user_id: Optional[int] = None
    user: Optional[UserSimple] = None
    action_type: str
    old_value: str
    new_value: str
    detail: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
