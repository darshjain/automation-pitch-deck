import pytest
from src.analysis.portfolio_manager import PortfolioManager

def test_portfolio_context_retrieval():
    pm = PortfolioManager()
    context = pm.get_context()
    
    assert "Sago Investment Thesis" in context
    assert "Focus Areas" in context
    assert "DevTools" in context

def test_conflict_detection():
    pm = PortfolioManager()
    
    # Should detect conflict
    conflicts = pm.check_conflict("DevTools")
    assert len(conflicts) > 0
    assert "CloudScale" in conflicts[0]

    # Should NOT detect conflict
    conflicts_idx = pm.check_conflict("Agriculture")
    assert len(conflicts_idx) == 0
