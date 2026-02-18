"""
Tests for risk management.
"""
import pytest
import pandas as pd
import numpy as np
from backend.risk_management.risk_manager import RiskManager


class TestRiskManager:
    """Test risk management functionality."""
    
    def test_initialization(self):
        """Test risk manager initialization."""
        risk_manager = RiskManager()
        assert risk_manager.max_position_size == 0.1
        assert risk_manager.max_portfolio_risk == 0.02
    
    def test_position_sizing(self):
        """Test position size calculation."""
        risk_manager = RiskManager()
        
        result = risk_manager.calculate_position_size(
            signal_confidence=0.8,
            portfolio_value=100000,
            asset_price=150,
            asset_volatility=0.02
        )
        
        assert 'num_shares' in result
        assert 'position_value' in result
        assert 'stop_loss_price' in result
        assert result['num_shares'] >= 0
        assert result['position_value'] >= 0
    
    def test_risk_limits(self):
        """Test risk limit checks."""
        risk_manager = RiskManager()
        
        proposed_position = {
            'position_fraction': 0.05,
            'position_risk': 1000
        }
        
        current_positions = []
        
        result = risk_manager.check_risk_limits(
            proposed_position=proposed_position,
            current_positions=current_positions,
            portfolio_value=100000
        )
        
        assert 'approved' in result
        assert 'violations' in result
        assert isinstance(result['approved'], bool)
    
    def test_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        risk_manager = RiskManager()
        
        returns = pd.Series(np.random.randn(252) * 0.01)
        sharpe = risk_manager.calculate_sharpe_ratio(returns)
        
        assert isinstance(sharpe, float)
    
    def test_var_calculation(self):
        """Test VaR calculation."""
        risk_manager = RiskManager()
        
        positions = [
            {'position_value': 10000, 'volatility': 0.02},
            {'position_value': 15000, 'volatility': 0.03}
        ]
        
        var = risk_manager.calculate_var(positions, confidence_level=0.95)
        
        assert isinstance(var, float)
        assert var >= 0
