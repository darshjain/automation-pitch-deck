import pytest
from unittest.mock import MagicMock, patch
from src.main import AgentOrchestrator

@pytest.fixture
def mock_components():
    with patch('src.main.LLMClient') as MockLLM, \
         patch('src.main.SearchClient') as MockSearch, \
         patch('src.main.DBClient') as MockDB, \
         patch('src.main.PDFIngestor') as MockIngestor, \
         patch('src.main.ClaimExtractor') as MockExtractor, \
         patch('src.main.Verifier') as MockVerifier, \
         patch('src.main.Analyst') as MockAnalyst, \
         patch('src.main.PortfolioManager') as MockPortfolio:
        
        yield {
            'llm': MockLLM,
            'ingestor': MockIngestor,
            'extractor': MockExtractor,
            'verifier': MockVerifier,
            'analyst': MockAnalyst,
            'portfolio': MockPortfolio
        }

def test_orchestrator_initialization(mock_components):
    orchestrator = AgentOrchestrator()
    assert orchestrator.portfolio_manager is not None
    assert orchestrator.ingestor is not None

def test_run_success(mock_components):
    orchestrator = AgentOrchestrator()
    
    # Mock return values
    orchestrator.ingestor.extract_text.return_value = "Mock PDF Content"
    orchestrator.portfolio_manager.get_context.return_value = "Mock Context"
    orchestrator.extractor.extract_claims.return_value = [{'statement': 'Claim 1'}]
    orchestrator.verifier.verify_claim.return_value = {'statement': 'Claim 1', 'verification_status': 'Verified'}
    orchestrator.analyst.generate_report.return_value = "# Final Report"

    result = orchestrator.run("dummy.pdf")
    
    assert result['status'] == 'success'
    assert len(result['claims']) == 1
    assert result['report'] == "# Final Report"
    
    # Verify Portfolio Context was used
    orchestrator.portfolio_manager.get_context.assert_called_once()
    orchestrator.analyst.generate_report.assert_called_with(
        [{'statement': 'Claim 1', 'verification_status': 'Verified'}], 
        portfolio_context="Mock Context"
    )
