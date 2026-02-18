"""
Tests for execution engine.
"""
import pytest
from backend.execution.execution_engine import (
    ExecutionEngine,
    PortfolioManager,
    Order,
    OrderType
)


class TestExecutionEngine:
    """Test execution engine."""
    
    def test_initialization(self):
        """Test engine initialization."""
        engine = ExecutionEngine(trading_mode='paper')
        assert engine.trading_mode == 'paper'
    
    def test_order_submission(self):
        """Test order submission."""
        engine = ExecutionEngine(trading_mode='paper')
        
        order = Order(
            symbol='AAPL',
            side='buy',
            quantity=10,
            order_type=OrderType.MARKET
        )
        
        result = engine.submit_order(order)
        
        assert 'success' in result
        assert result['success'] is True
        assert 'order_id' in result


class TestPortfolioManager:
    """Test portfolio management."""
    
    def test_initialization(self):
        """Test portfolio initialization."""
        portfolio = PortfolioManager(initial_capital=100000)
        assert portfolio.initial_capital == 100000
        assert portfolio.cash == 100000
    
    def test_position_update_buy(self):
        """Test buying a position."""
        portfolio = PortfolioManager(initial_capital=100000)
        
        portfolio.update_position(
            symbol='AAPL',
            quantity_change=10,
            price=150,
            side='buy'
        )
        
        assert 'AAPL' in portfolio.positions
        assert portfolio.positions['AAPL']['quantity'] == 10
        assert portfolio.cash == 100000 - 1500
    
    def test_position_update_sell(self):
        """Test selling a position."""
        portfolio = PortfolioManager(initial_capital=100000)
        
        # First buy
        portfolio.update_position('AAPL', 10, 150, 'buy')
        
        # Then sell
        portfolio.update_position('AAPL', 10, 160, 'sell')
        
        assert 'AAPL' not in portfolio.positions
        assert portfolio.realized_pnl == 100  # (160 - 150) * 10
    
    def test_portfolio_value(self):
        """Test portfolio value calculation."""
        portfolio = PortfolioManager(initial_capital=100000)
        
        portfolio.update_position('AAPL', 10, 150, 'buy')
        portfolio.positions['AAPL']['current_price'] = 160
        
        value = portfolio.get_portfolio_value()
        expected = portfolio.cash + 10 * 160
        
        assert value == expected
    
    def test_pnl_calculation(self):
        """Test P&L calculation."""
        portfolio = PortfolioManager(initial_capital=100000)
        
        portfolio.update_position('AAPL', 10, 150, 'buy')
        portfolio.positions['AAPL']['current_price'] = 160
        
        pnl = portfolio.get_pnl()
        
        assert 'realized_pnl' in pnl
        assert 'unrealized_pnl' in pnl
        assert 'total_pnl' in pnl
        assert pnl['unrealized_pnl'] == 100  # (160 - 150) * 10
