import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import time

class ContentFetcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.timeout = 10  # seconds
    
    def fetch_content(self, url: str) -> Dict[str, str]:
        """
        Fetch and clean content from a URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with content preview and full text
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Create preview (first 300 characters)
            preview = text[:300] + "..." if len(text) > 300 else text
            
            return {
                "content_preview": preview,
                "fetched_text": text,
                "fetched_text_length": len(text)
            }
            
        except Exception as e:
            return {
                "content_preview": f"Error fetching content: {str(e)}",
                "fetched_text": "",
                "fetched_text_length": 0
            }