"""
Basic tests for strategy implementations.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backend.strategies.base_strategy import MomentumStrategy, MeanReversionStrategy


def create_sample_data(days=100, start_price=100):
    """Create sample market data for testing."""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    prices = start_price + np.cumsum(np.random.randn(days) * 2)
    
    df = pd.DataFrame({
        'Open': prices,
        'High': prices * 1.02,
        'Low': prices * 0.98,
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, days)
    }, index=dates)
    
    return df


class TestMomentumStrategy:
    """Test momentum strategy."""
    
    def test_initialization(self):
        """Test strategy initialization."""
        strategy = MomentumStrategy()
        assert strategy.name == "Momentum Strategy"
        assert strategy.parameters['lookback_period'] == 20
    
    def test_signal_generation(self):
        """Test signal generation."""
        strategy = MomentumStrategy()
        data = create_sample_data()
        
        signal = strategy.generate_signal(data, 'TEST')
        
        assert 'action' in signal
        assert signal['action'] in ['buy', 'sell', 'hold']
        assert 'confidence' in signal
        assert 0 <= signal['confidence'] <= 1
    
    def test_position_sizing(self):
        """Test position size calculation."""
        strategy = MomentumStrategy()
        
        signal = {'action': 'buy', 'confidence': 0.8}
        portfolio_value = 100000
        current_price = 150
        
        size = strategy.calculate_position_size(signal, portfolio_value, current_price)
        
        assert isinstance(size, (int, float))
        assert size >= 0


class TestMeanReversionStrategy:
    """Test mean reversion strategy."""
    
    def test_initialization(self):
        """Test strategy initialization."""
        strategy = MeanReversionStrategy()
        assert strategy.name == "Mean Reversion Strategy"
        assert strategy.parameters['lookback_period'] == 20
    
    def test_signal_generation(self):
        """Test signal generation."""
        strategy = MeanReversionStrategy()
        data = create_sample_data()
        
        signal = strategy.generate_signal(data, 'TEST')
        
        assert 'action' in signal
        assert signal['action'] in ['buy', 'sell', 'hold']
        assert 'confidence' in signal
        assert 0 <= signal['confidence'] <= 1
        assert 'features' in signal
        assert 'z_score' in signal['features']
