import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import time
import random

class ContentFetcher:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.timeout = 10  # seconds
        
        # Add a list of user agents to rotate through
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
    
    def fetch_content(self, url: str) -> Dict[str, str]:
        """
        Fetch and clean content from a URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with content preview and full text
        """
        try:
            # Rotate user agents
            headers = self.headers.copy()
            headers["User-Agent"] = random.choice(self.user_agents)
            
            # Add a small delay to avoid rate limiting
            time.sleep(random.uniform(0.5, 1.5))
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            
            # Remove common non-content elements
            for element in soup(["header", "footer", "nav", "aside"]):
                element.extract()
            
            # Remove elements with common non-content classes
            for element in soup.find_all(class_=["navigation", "menu", "sidebar", "comments", "related"]):
                element.extract()
            
            # Get text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Check if the content is meaningful (not just login walls)
            if self._is_login_wall(text):
                return {
                    "content_preview": "Content requires login to access",
                    "fetched_text": "",
                    "fetched_text_length": 0
                }
            
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
    
    def _is_login_wall(self, text: str) -> bool:
        """Check if the text is primarily a login wall."""
        # Common login wall indicators
        login_indicators = [
            "sign in",
            "log in",
            "create account",
            "join now",
            "subscribe to read",
            "please login",
            "log in to continue",
            "create a free account"
        ]
        
        # Count how many login indicators appear in the text
        login_count = sum(1 for indicator in login_indicators if indicator.lower() in text.lower())
        
        # If there are multiple login indicators and the text is short, it's likely a login wall
        if login_count >= 2 and len(text) < 1000:
            return True
        
        # If the text contains "sign in" and "continue" or "access", it's likely a login wall
        if ("sign in" in text.lower() or "log in" in text.lower()) and \
           ("continue" in text.lower() or "access" in text.lower()) and \
           len(text) < 1500:
            return True
        
        return False