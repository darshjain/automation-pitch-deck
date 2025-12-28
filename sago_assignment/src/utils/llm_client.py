import os
import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. LLM calls will fail unless mocked.")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.model = model

    def chat_completion(self, messages: List[Dict[str, str]], json_mode: bool = False) -> str:
        if not self.client:
            logger.warning("No API Key. Using MOCK response.")
            return self._get_mock_response(messages, json_mode)

        try:
            params: Dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.0,
            }
            if json_mode:
                params["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**params)
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Received empty response from LLM.")
            return content

        except Exception as e:
            logger.error(f"LLM API Call failed: {str(e)}")
            raise

    def _get_mock_response(self, messages: List[Dict[str, str]], json_mode: bool) -> str:
        last_msg = messages[-1]['content']
        
        if "extract specific, verifiable claims" in messages[0]['content']:
            return '''
            {
                "claims": [
                    {
                        "statement": "The global waste management market is projected to reach $2000 Trillion by 2030.",
                        "category": "Market Size",
                        "confidence_score": 0.95
                    },
                    {
                        "statement": "Partnered with Waste Management Inc (WM).",
                        "category": "Traction",
                        "confidence_score": 1.0
                    },
                    {
                        "statement": "Generated $5M in ARR in our first year.",
                        "category": "Financials",
                        "confidence_score": 0.9
                    },
                     {
                        "statement": "We are the only company using AI for waste sorting.",
                        "category": "Competitors",
                        "confidence_score": 0.8
                    }
                ]
            }
            '''
        
        if "Generate 2 specific google search queries" in last_msg:
            return '''
            {
                "queries": ["waste management market size 2030 projection", "EcoStream AI Waste Management Inc partnership"]
            }
            '''

        if "Based on these results, verify the claim" in last_msg:
            if "2000 Trillion" in last_msg:
                return '''
                {
                    "verification_status": "Contradicted",
                    "reasoning": "Market research indicates the market is in the billions, not trillions. $2000 Trillion is likely a hallucination or typo.",
                    "sources": ["https://grandviewresearch.com/waste-management"]
                }
                '''
            elif "Partnered with" in last_msg:
                return '''
                {
                    "verification_status": "Verified",
                    "reasoning": "Press releases confirm the pilot partnership with WM in 2024.",
                    "sources": ["https://techcrunch.com/ecostream-wm-partnership"]
                }
                '''
            elif "only company" in last_msg:
                 return '''
                {
                    "verification_status": "Contradicted",
                    "reasoning": "Multiple competitors like AMP Robotics exist in this space.",
                    "sources": ["https://amprobotics.com"]
                }
                '''
            else:
                 return '''
                {
                    "verification_status": "Inconclusive",
                    "reasoning": "No public financial records found for private company ARR.",
                    "sources": []
                }
                '''

        if "Summarize the verification findings" in last_msg:
            return """
# Investment Analysis: EcoStream AI

## Executive Summary
The technology is promising, but the pitch deck contains significant inaccuracies regarding market size and competitive landscape. The claim of a **$2000 Trillion** market is factually incorrect (likely $2T). The claim of being the "only company" is false given competitors like AMP Robotics. However, the **WM Partnership** appears legitimate, which is a strong signal.

## Strategic Questions for Founder
1. **Market Sizing**: "Your deck mentions a $2000T market size. Can you walk us through your TAM calculation? This seems to deviate significantly from standard industry reports ($1-2T)."
2. **Competitive Moat**: "You claim to be the only AI player, but how do you differentiate from established players like AMP Robotics who are already at scale?"
3. **Financial Verification**: "Congratulations on the $5M ARR. Since this isn't publicly verifiable yet, can you share your unit economics and a breakdown of that revenue concentration (e.g., how much is from the WM pilot)?"
            """
            
        return "{}"
