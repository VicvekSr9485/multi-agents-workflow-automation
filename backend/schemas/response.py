from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class SearchResult(BaseModel):
    url: str
    title: str
    snippet: str
    content_preview: Optional[str] = None
    fetched_text_length: Optional[int] = None

class ResearchResponse(BaseModel):
    research_results: List[SearchResult]
    analysis_summary: str
    analysis_tables: Dict[str, Any]
    draft_report: str
    final_report: str
    review_notes: str
    processing_time: Optional[float] = None
    agent_logs: Optional[Dict[str, Dict[str, Any]]] = None