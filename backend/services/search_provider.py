import os
from services.serper_service import SerperService
from services.serpapi_service import SerpApiService

class SearchProviderFactory:
    @staticmethod
    def get_service():
        provider = os.getenv("SEARCH_PROVIDER", "serper").lower()

        if provider == "serpapi":
            return SerpApiService()
        elif provider == "serper":
            return SerperService()
        else:
            raise ValueError(f"Unsupported SEARCH_PROVIDER: {provider}")
