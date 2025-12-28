import logging
import argparse
import sys
import os
import time
from typing import Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ingestion.pdf_processor import PDFIngestor
from src.analysis.claim_extractor import ClaimExtractor
from src.analysis.verifier import Verifier
from src.analysis.analyst import Analyst
from src.utils.llm_client import LLMClient
from src.utils.search_client import SearchClient
from src.utils.db_client import DBClient
from src.analysis.portfolio_manager import PortfolioManager

import logging

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("SagoAgent")

# ... (Logging config remains same)

class AgentOrchestrator:
    """
    Orchestrates the multi-agent workflow:
    Ingestion -> Extraction -> Verification -> Analysis -> Output
    """
    def __init__(self):
        self.llm_client = LLMClient()
        self.search_client = SearchClient()
        self.db_client = DBClient() # Initialize Persistence
        self.portfolio_manager = PortfolioManager() # Initialize Portfolio Context
        
        # Initialize Agents
        self.ingestor = PDFIngestor()
        self.extractor = ClaimExtractor(self.llm_client)
        self.verifier = Verifier(self.llm_client, self.search_client)
        self.analyst = Analyst(self.llm_client)

    
    def run(self, pdf_path: str, user_context: Dict[str, str] = None) -> Dict[str, Any]:
        start_time = time.time()
        user_context = user_context or {"user_id": "cli_user", "source": "cli"}
        
        logger.info(f"Starting Sago Agent for: {pdf_path}")
        logger.info(f"User Context: {user_context}")

        try:
            logger.info("--- Step 1: Ingestion ---")
            text_content = self.ingestor.extract_text(pdf_path)
            logger.info("PDF Text Extracted.")
            
            logger.info("--- Step 1.5: Portfolio Context ---")
            portfolio_ctx = self.portfolio_manager.get_context()

            logger.info("--- Step 2: Claim Extraction ---")
            claims = self.extractor.extract_claims(text_content)
            logger.info(f"Extracted {len(claims)} verifyable claims.")

            logger.info("--- Step 3: Verification (Parallel-Simulated) ---")
            verified_claims = []
            for claim in claims:
                result = self.verifier.verify_claim(claim)
                verified_claims.append(result)
                logger.info(f"Verified: {result.get('statement')} -> {result.get('verification_status')}")

            logger.info("--- Step 4: Analyst Review ---")
            final_report = self.analyst.generate_report(verified_claims, portfolio_context=portfolio_ctx)
            
            execution_time = int((time.time() - start_time) * 1000)
            logger.info(f"--- Step 5: Persistence ({execution_time}ms) ---")
            
            metadata = {
                "user_id": user_context.get("user_id"),
                "source": user_context.get("source"),
                "filename": os.path.basename(pdf_path),
                "execution_time_ms": execution_time
            }
            
            self.db_client.save_analysis(
                metadata=metadata,
                claims=verified_claims,
                report=final_report
            )
            
            return {
                "claims": verified_claims,
                "report": final_report,
                "status": "success",
                "metrics": {"time_ms": execution_time}
            }

        except Exception as e:
            logger.error(f"Orchestration Error: {str(e)}")
            # In a real system, we might alert the user via Slack here
            return {
                "claims": [],
                "report": f"Analysis Failed: {str(e)}",
                "status": "error"
            }

    def close(self):
        """Clean up resources"""
        if self.db_client:
            self.db_client.close()


def main():
    parser = argparse.ArgumentParser(description="Sago Pitch Deck Verifier Agent")
    parser.add_argument("--input", required=True, help="Path to the pitch deck PDF")
    parser.add_argument("--output", default="output_report.md", help="Path to save the output report")
    parser.add_argument("--user", default="admin@sago.vc", help="User ID (email) triggering the agent")
    args = parser.parse_args()

    orchestrator = AgentOrchestrator()
    
    try:
        # Simulate user context from CLI args
        user_context = {"user_id": args.user, "source": "cli_tool"}
        results = orchestrator.run(args.input, user_context=user_context)
        
        # Output Handling
        with open(args.output, "w") as f:
            f.write(results["report"])
        
        logger.info(f"Analysis Complete. Report saved to {args.output}")
        logger.info(f"Execution Time: {results.get('metrics', {}).get('time_ms')}ms")
        print("\n" + "="*50 + "\n")
        print(results["report"])
        print("\n" + "="*50 + "\n")

    except Exception as e:
        logger.error(f"Workflow Failed: {e}")
        sys.exit(1)
    finally:
        orchestrator.close()

if __name__ == "__main__":
    main()
