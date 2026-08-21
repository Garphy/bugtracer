import re
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel

class ParsedSearchQuery(BaseModel):
    is_empty: bool = False
    is_report_all: bool = False
    bug_ids: Optional[List[int]] = None
    creator_id: Optional[int] = None
    assignee_id: Optional[int] = None
    exclude_assignee_id: Optional[int] = None
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    keyword: Optional[str] = None
    raw_query: str = ""

def parse_search_query(query_str: Optional[str]) -> ParsedSearchQuery:
    """
    Parses BugTracer search syntax:
    - empty/None: normal list
    - 'alll': full report trigger
    - '123' or '123,456': by Bug ID(s)
    - '(12)': created by user 12
    - '{12}': assigned to user 12
    - '!{12}': assigned to someone other than user 12
    - '{2026-01-01~2026-02-01}': updated in time range
    - 'keyword': fulltext match
    """
    if not query_str or not query_str.strip():
        return ParsedSearchQuery(is_empty=True, raw_query="")
    
    query = query_str.strip()
    result = ParsedSearchQuery(raw_query=query)
    
    if query.lower() == "alll":
        result.is_report_all = True
        return result
    
    # Comma-separated or single numbers: "123" or "123,456, 789"
    if re.match(r"^(\d+)(,\s*\d+)*$", query):
        ids = [int(x.strip()) for x in query.split(",") if x.strip().isdigit()]
        if ids:
            result.bug_ids = ids
            return result
            
    # Created by: (12)
    m_creator = re.match(r"^\((\d+)\)$", query)
    if m_creator:
        result.creator_id = int(m_creator.group(1))
        return result
        
    # Assigned to: {12}
    m_assignee = re.match(r"^\{(\d+)\}$", query)
    if m_assignee:
        result.assignee_id = int(m_assignee.group(1))
        return result
        
    # Excluded assignee: !{12}
    m_not_assignee = re.match(r"^!\{(\d+)\}$", query)
    if m_not_assignee:
        result.exclude_assignee_id = int(m_not_assignee.group(1))
        return result
        
    # Date range: {2026-01-01~2026-02-01} or {2026-1-1~2026-2-1}
    m_date = re.match(r"^\{(\d{4}-\d{1,2}-\d{1,2})~(\d{4}-\d{1,2}-\d{1,2})\}$", query)
    if m_date:
        try:
            start_str, end_str = m_date.group(1), m_date.group(2)
            start_dt = datetime.strptime(start_str, "%Y-%m-%d")
            # End of day or start of next day
            end_dt = datetime.strptime(end_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            result.time_start = start_dt
            result.time_end = end_dt
            return result
        except ValueError:
            pass
            
    # Default: keyword search
    result.keyword = query
    return result
