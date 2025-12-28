import logging
import json
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PortfolioManager:
    """
    Simulates a Vector Database / Knowledge Base of the VC's portfolio and thesis.
    """
    def __init__(self):
        # Mock Data representing Sago's specific investment thesis and existing portfolio
        self.thesis = {
            "focus_sectors": ["B2B SaaS", "DevTools", "Climate Tech", "Vertical AI"],
            "avoid_sectors": ["Crypto", "D2C", "Gaming", "Real Estate"],
            "check_size": "$1M - $5M (Seed to Series A)",
            "geography": "North America, Europe"
        }
        
        self.portfolio_companies = [
            {"name": "CloudScale", "sector": "DevTools", "description": "Serverless infrastructure scaling"},
            {"name": "GreenGrid", "sector": "Climate Tech", "description": "AI for energy grid optimization"},
            {"name": "DocuFlow", "sector": "B2B SaaS", "description": "Legal document automation"}
        ]

    def get_context(self) -> str:
        """
        Retrieves relevant context for the Analyst agent.
        In a real system, this would do a semantic search related to the pitch deck's content.
        """
        logger.info("Retrieving Portfolio Context...")
        
        context_str = (
            "## Sago Investment Thesis\n"
            f"- **Focus Areas**: {', '.join(self.thesis['focus_sectors'])}\n"
            f"- **Anti-Portfolio**: {', '.join(self.thesis['avoid_sectors'])}\n"
            f"- **Sweet Spot**: {self.thesis['check_size']}\n\n"
            "## Existing Portfolio Conflicts/Synergies\n"
        )
        
        for co in self.portfolio_companies:
            context_str += f"- {co['name']} ({co['sector']}): {co['description']}\n"
            
        return context_str

    def check_conflict(self, startup_sector: str) -> List[str]:
        """
        Simple keyword check for conflicts.
        """
        conflicts = []
        for co in self.portfolio_companies:
            if startup_sector.lower() in co['sector'].lower():
                conflicts.append(f"Potential overlap with portfolio company: {co['name']}")
        return conflicts
