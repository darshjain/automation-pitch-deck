import logging
from typing import List, Dict
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

class SearchClient:
    def __init__(self):
        self.ddgs = DDGS()

    def search(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        try:
            logger.info(f"Searching web for: {query}")
            results = list(self.ddgs.text(query, max_results=max_results))
            return results
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {str(e)}")
            return []
