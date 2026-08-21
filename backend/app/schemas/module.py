from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class ModuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    sort_order: int = Field(default=0)

class ModuleCreate(ModuleBase):
    project_id: int

class ModuleUpdate(BaseModel):
    name: Optional[str] = None
    sort_order: Optional[int] = None

class ModuleResponse(ModuleBase):
    id: int
    project_id: int
    bug_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)
