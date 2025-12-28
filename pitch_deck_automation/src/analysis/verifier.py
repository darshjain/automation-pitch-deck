import json
import logging
from typing import List, Dict, Any
from ..utils.llm_client import LLMClient
from ..utils.search_client import SearchClient

logger = logging.getLogger(__name__)

class Verifier:
    def __init__(self, llm_client: LLMClient, search_client: SearchClient):
        self.llm = llm_client
        self.search = search_client

    def verify_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        statement = claim.get('statement')
        logger.info(f"Verifying claim: {statement}")

        if not statement:
            return claim

        queries = self._generate_search_queries(statement)
        
        search_results = []
        for q in queries[:2]: 
            results = self.search.search(q, max_results=3)
            search_results.extend(results)

        verification_result = self._synthesize_verification(statement, search_results)
        
        claim.update(verification_result)
        return claim

    def _generate_search_queries(self, statement: str) -> List[str]:
        prompt = (
            f"You are a researcher. Generate 2 specific google search queries to verify this claim: '{statement}'.\n"
            "Output JSON: {'queries': ['query 1', 'query 2']}"
        )
        try:
            response = self.llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                json_mode=True
            )
            data = json.loads(response)
            return data.get('queries', [])
        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            return [statement]

    def _synthesize_verification(self, statement: str, search_results: List[Dict[str, str]]) -> Dict[str, Any]:
        if not search_results:
            return {
                "verification_status": "Unverified",
                "reasoning": "No search results found.",
                "sources": []
            }
        
        context = "\n".join([f"- {r['title']}: {r['body']} ({r['href']})" for r in search_results])
        
        prompt = (
            f"Claim: '{statement}'\n\n"
            f"Search Results:\n{context}\n\n"
            "Based on these results, verify the claim.\n"
            "Status options: 'Verified' (Results support it), 'Contradicted' (Results oppose it), 'Inconclusive' (Not enough info/Ambiguous).\n"
            "Output JSON: {'verification_status': '...', 'reasoning': '...', 'sources': ['url1', 'url2']}"
        )

        try:
            response = self.llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                json_mode=True
            )
            return json.loads(response)
        except Exception as e:
            logger. error(f"Synthesis failed: {e}")
            return {
                "verification_status": "Error",
                "reasoning": "LLM Synthesis failed.",
                "sources": []
            }
