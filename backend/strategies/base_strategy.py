"""
Base strategy class and framework for implementing trading strategies.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger


class BaseStrategy(ABC):
    """Base class for all trading strategies."""
    
    def __init__(self, name: str, parameters: Optional[Dict[str, Any]] = None):
        """
        Initialize strategy.
        
        Args:
            name: Strategy name
            parameters: Strategy parameters
        """
        self.name = name
        self.parameters = parameters or {}
        self.positions = {}
        self.signals = []
        self.performance_metrics = {
            'total_pnl': 0.0,
            'win_rate': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'num_trades': 0
        }
        logger.info(f"Initialized strategy: {name}")
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """
        Generate trading signal based on market data.
        
        Args:
            data: Market data DataFrame
            symbol: Trading symbol
        
        Returns:
            Signal dictionary with keys: action, confidence, price, features
        """
        pass
    
    @abstractmethod
    def calculate_position_size(
        self,
        signal: Dict[str, Any],
        portfolio_value: float,
        current_price: float
    ) -> float:
        """
        Calculate position size based on risk management rules.
        
        Args:
            signal: Trading signal
            portfolio_value: Current portfolio value
            current_price: Current asset price
        
        Returns:
            Position size (number of shares/contracts)
        """
        pass
    
    def update_performance(self, pnl: float, trade_result: str):
        """
        Update strategy performance metrics.
        
        Args:
            pnl: Profit/loss from trade
            trade_result: 'win' or 'loss'
        """
        self.performance_metrics['total_pnl'] += pnl
        self.performance_metrics['num_trades'] += 1
        
        if trade_result == 'win':
            wins = self.performance_metrics.get('wins', 0) + 1
            self.performance_metrics['wins'] = wins
            self.performance_metrics['win_rate'] = wins / self.performance_metrics['num_trades']
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get strategy performance summary."""
        return self.performance_metrics.copy()


class MomentumStrategy(BaseStrategy):
    """Momentum-based trading strategy."""
    
    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        default_params = {
            'lookback_period': 20,
            'momentum_threshold': 0.02,
            'risk_per_trade': 0.02
        }
        params = {**default_params, **(parameters or {})}
        super().__init__("Momentum Strategy", params)
    
    def generate_signal(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Generate momentum-based signal."""
        if len(data) < self.parameters['lookback_period']:
            return {'action': 'hold', 'confidence': 0.0}
        
        # Calculate momentum
        lookback = self.parameters['lookback_period']
        current_price = data['Close'].iloc[-1]
        past_price = data['Close'].iloc[-lookback]
        momentum = (current_price - past_price) / past_price
        
        # Generate signal
        threshold = self.parameters['momentum_threshold']
        if momentum > threshold:
            action = 'buy'
            confidence = min(abs(momentum) / (2 * threshold), 1.0)
        elif momentum < -threshold:
            action = 'sell'
            confidence = min(abs(momentum) / (2 * threshold), 1.0)
        else:
            action = 'hold'
            confidence = 0.0
        
        return {
            'action': action,
            'confidence': confidence,
            'price': current_price,
            'features': {
                'momentum': momentum,
                'lookback': lookback
            }
        }
    
    def calculate_position_size(
        self,
        signal: Dict[str, Any],
        portfolio_value: float,
        current_price: float
    ) -> float:
        """Calculate position size using fixed risk percentage."""
        risk_amount = portfolio_value * self.parameters['risk_per_trade']
        position_size = int(risk_amount / current_price)
        return position_size


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion trading strategy."""
    
    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        default_params = {
            'lookback_period': 20,
            'num_std': 2.0,
            'risk_per_trade': 0.02
        }
        params = {**default_params, **(parameters or {})}
        super().__init__("Mean Reversion Strategy", params)
    
    def generate_signal(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Generate mean reversion signal using Bollinger Bands."""
        if len(data) < self.parameters['lookback_period']:
            return {'action': 'hold', 'confidence': 0.0}
        
        # Calculate moving average and standard deviation
        lookback = self.parameters['lookback_period']
        prices = data['Close'].iloc[-lookback:]
        mean_price = prices.mean()
        std_price = prices.std()
        current_price = data['Close'].iloc[-1]
        
        # Calculate z-score
        z_score = (current_price - mean_price) / std_price if std_price > 0 else 0
        
        # Generate signal
        num_std = self.parameters['num_std']
        if z_score < -num_std:
            action = 'buy'  # Price is too low, expect reversion
            confidence = min(abs(z_score) / (2 * num_std), 1.0)
        elif z_score > num_std:
            action = 'sell'  # Price is too high, expect reversion
            confidence = min(abs(z_score) / (2 * num_std), 1.0)
        else:
            action = 'hold'
            confidence = 0.0
        
        return {
            'action': action,
            'confidence': confidence,
            'price': current_price,
            'features': {
                'z_score': z_score,
                'mean_price': mean_price,
                'std_price': std_price
            }
        }
    
    def calculate_position_size(
        self,
        signal: Dict[str, Any],
        portfolio_value: float,
        current_price: float
    ) -> float:
        """Calculate position size using fixed risk percentage."""
        risk_amount = portfolio_value * self.parameters['risk_per_trade']
        position_size = int(risk_amount / current_price)
        return position_size
