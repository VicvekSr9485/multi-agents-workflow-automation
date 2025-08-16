import os
import json
import requests
from typing import List, Dict, Any

class SerperService:
    def __init__(self):
        self.api_key = os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("SERPER_API_KEY environment variable not set")
        
        self.endpoint = "https://google.serper.dev/search"

    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "q": query,
            "num": num_results
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            results = response.json()

            organic_results = results.get("organic", [])
            formatted_results = []

            for result in organic_results[:num_results]:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "published_date": result.get("date", ""),
                    "domain": result.get("source", "")
                })
            
            return formatted_results

        except Exception as e:
            raise Exception(f"Serper.dev search failed: {str(e)}")
