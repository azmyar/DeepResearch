import os
import requests
from functools import lru_cache
from typing import Optional, Dict, Any, List

class FirecrawlConfigurationError(RuntimeError):
    """Raised when Firecrawl is not installed or misconfigured."""

class FirecrawlClient:
    def __init__(self, api_key: str, base_url: str = "https://api.firecrawl.dev"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=data, timeout=30)
            else:
                response = requests.post(url, headers=headers, json=data, timeout=30)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Firecrawl API request failed: {str(e)}")
    
    def search(self, query: str, limit: int = 10, scrape_options: Optional[Dict] = None):
        """Search the web using Firecrawl API"""
        data = {
            'query': query,
            'limit': limit
        }
        
        if scrape_options:
            data['scrapeOptions'] = scrape_options
        
        result = self._make_request('POST', '/v2/search', data)
        
        class SearchResponse:
            def __init__(self, data):
                self.web = []
                if 'data' in data and 'web' in data['data']:
                    for item in data['data']['web']:
                        web_item = type('WebResult', (), {})()
                        web_item.metadata = type('Metadata', (), {})()
                        web_item.metadata.title = item.get('title', 'Untitled')
                        web_item.metadata.url = item.get('url', '')
                        web_item.metadata.description = item.get('description', '')
                        web_item.summary = item.get('summary', '')
                        self.web.append(web_item)
                    
        return SearchResponse(result)
    
    def scrape(self, url: str, formats: Optional[List[str]] = None):
        """Scrape a webpage using Firecrawl API"""
        data = {
            'url': url
        }
        
        if formats:
            data['formats'] = formats
        
        result = self._make_request('POST', '/v2/scrape', data)

        print(result)
        
        class ScrapeResponse:
            def __init__(self, data):
                if 'data' in data:
                    if isinstance(data['data'], dict):
                        self.summary = data['data'].get('summary', '') or data['data'].get('markdown', '')
                    elif isinstance(data['data'], str):
                        self.summary = data['data']
                    else:
                        self.summary = ''
                else:
                    self.summary = ''
        
        return ScrapeResponse(result)

@lru_cache(maxsize=1)
def get_firecrawl_client():

    api_key = os.getenv("FIRECRAWL_API_KEY")

    if not api_key:
        raise FirecrawlConfigurationError("FIRECRAWL_API_KEY environment variable is not set")

    return FirecrawlClient(api_key=api_key)

