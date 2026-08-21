from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.schemas.bug import BugListItem

class MemberStat(BaseModel):
    user_id: int
    fullname: str
    username: str
    role: str
    active_count: int = 0
    fixed_count: int = 0
    key_count: int = 0
    total_count: int = 0

class ModuleStat(BaseModel):
    module_id: int
    module_name: str
    active_count: int = 0
    fixed_count: int = 0
    total_count: int = 0

class ProjectStatsReport(BaseModel):
    project_id: int
    project_name: str
    total_bugs: int
    active_bugs: int
    fixed_bugs: int
    closed_bugs: int
    key_bugs: int
    member_stats: List[MemberStat]
    module_stats: List[ModuleStat]
    status_distribution: Dict[str, int]
    daily_trend: List[Dict[str, Any]] = []

class FullProjectReportResponse(BaseModel):
    project_id: int
    project_name: str
    stats: ProjectStatsReport
    bugs_by_module: Dict[str, List[BugListItem]]
