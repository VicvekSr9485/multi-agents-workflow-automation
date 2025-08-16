from typing import List, Dict, Any
# from services.serpapi_service import SerpApiService   # ❌ old
from services.serper_service import SerperService       # ✅ new
from services.fetcher import ContentFetcher
from logger import log_agent_start, log_agent_end


class ResearchAgent:
    def __init__(self):
        self.serp_service = SerperService()   # ✅ now uses Serper.dev
        self.fetcher = ContentFetcher()
    
    def research(self, topic: str, num_results: int = 5) -> List[Dict[str, Any]]:
        start_time = log_agent_start("ResearchAgent", {"topic": topic, "num_results": num_results})
        
        try:
            search_results = self.serp_service.search(topic, num_results)
            
            research_results = []
            for result in search_results:
                content_data = self.fetcher.fetch_content(result["url"])
                
                research_result = {
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "domain": result.get("domain", ""),             
                    "published_date": result.get("published_date", ""),
                    "content_preview": content_data.get("content_preview", ""),
                    "fetched_text_length": content_data.get("fetched_text_length", 0)
                }
                
                research_results.append(research_result)
            
            log_agent_end("ResearchAgent", start_time, research_results)
            return research_results
            
        except Exception as e:
            log_agent_end("ResearchAgent", start_time, None)
            raise Exception(f"Research failed: {str(e)}")
