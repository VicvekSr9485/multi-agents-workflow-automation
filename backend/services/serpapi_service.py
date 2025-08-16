import os
import requests
from typing import List, Dict, Any
from urllib.parse import urlparse

class SerpApiService:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY environment variable not set")
        
        self.endpoint = "https://serpapi.com/search"

    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        params = {
            "q": query,
            "api_key": self.api_key
        }

        try:
            response = requests.get(self.endpoint, params=params)
            response.raise_for_status()
            results = response.json()

            organic_results = results.get("organic_results", [])
            formatted_results = []

            for result in organic_results[:num_results]:
                url = result.get("link", "")
                domain = urlparse(url).netloc if url else ""
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": url,
                    "snippet": result.get("snippet", ""),
                    "published_date": result.get("date", ""),  # may be missing often
                    "domain": domain
                })
            
            return formatted_results

        except Exception as e:
            raise Exception(f"SerpApi search failed: {str(e)}")
