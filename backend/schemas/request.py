from pydantic import BaseModel, Field

class ResearchRequest(BaseModel):
    topic: str = Field(..., description="Research topic to investigate")
    num_results: int = Field(5, ge=1, le=10, description="Number of search results to fetch")
    report_style: str = Field("concise", description="Style of the report (concise, detailed, academic)")