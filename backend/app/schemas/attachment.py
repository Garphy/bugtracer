from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class AttachmentResponse(BaseModel):
    id: int
    bug_id: Optional[int] = None
    project_id: int
    original_name: str
    stored_name: str
    file_size: int
    mime_type: str
    url: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UploadResponse(BaseModel):
    success: bool
    filename: str
    original_name: str
    url: str
    id: Optional[int] = None
    error: Optional[str] = None
