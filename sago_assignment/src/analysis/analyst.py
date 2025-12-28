import json
import logging
from typing import List, Dict, Any
from ..utils.llm_client import LLMClient

logger = logging.getLogger(__name__)

class Analyst:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def generate_report(self, processed_claims: List[Dict[str, Any]], portfolio_context: str = "") -> str:
        logger.info("Generating final analyst report...")
        
        claims_summary = json.dumps(processed_claims, indent=2)
        
        prompt = (
            "You are a Senior Partner at Sago Ventures. generating an investment memo.\n"
            "Your Goal: Determine if this opportunity matches our specific Investment Thesis and Portfolio Strategy.\n\n"
            f"=== SAGO PORTFOLIO CONTEXT ===\n{portfolio_context}\n\n"
            f"=== VERIFIED CLAIMS DATA ===\n{claims_summary}\n\n"
            "Task:\n"
            "1. **Thesis Fit**: Does this company align with Sago's Focus Areas? Explicitly mention if it falls into our 'Anti-Portfolio'.\n"
            "2. **Portfolio Check**: Identify potential conflicts or synergies with existing portfolio companies listed above.\n"
            "3. **Risk Analysis**: Summarize the verification findings (Red Flags/Contradictions).\n"
            "4. **Strategic Questions**: 3-5 sharp questions for the founder, specifically addressing Thesis Fit and Portfolio conflicts if any.\n"
            "   - **IMPORTANT**: If a specific claim in the question was 'Unverified' or 'Inconclusive', you MUST prefix that part of the question with **[UNVERIFIED CLAIM]**.\n\n"
            "Output Format: Professional Markdown Memo."
        )

        try:
            response = self.llm.chat_completion(
                messages=[
                    {"role": "system", "content": "You are a VC Partner at Sago Ventures."}, 
                    {"role": "user", "content": prompt}
                ],
                json_mode=False
            )
            return response
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return "Error generating report."
