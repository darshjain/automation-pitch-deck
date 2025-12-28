import json
import logging
from typing import List, Dict
from ..utils.llm_client import LLMClient

logger = logging.getLogger(__name__)

class ClaimExtractor:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def extract_claims(self, text: str) -> List[Dict[str, str]]:
        logger.info("Extracting claims from text...")
        
        system_prompt = (
            "You are a Diligent Investment Analyst. Your goal is to extract specific, verifiable claims "
            "from a pitch deck. Focus on: \n"
            "1. Market Size (TAM/SAM/SOM)\n"
            "2. Financials (Revenue, growth rates, margins)\n"
            "3. Tractions (User numbers, partnerships, contracts)\n"
            "4. Competitors (Claims about being better/unique)\n"
            "Do NOT extract generic marketing fluff (e.g., 'We are the best').\n"
            "Output JSON format: {'claims': [{'statement': 'We have 50k DAU', 'category': 'Traction', 'confidence_score': 0.9}]}"
        )
        
        user_prompt = f"Here is the pitch deck text:\n\n{text[:15000]}" 

        try:
            response = self.llm.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                json_mode=True
            )
            data = json.loads(response)
            return data.get("claims", [])
        except Exception as e:
            logger.error(f"Claim extraction failed: {str(e)}")
            return []
