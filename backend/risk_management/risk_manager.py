"""
Risk management system for the trading platform.
Implements position sizing, stop-loss, and portfolio risk controls.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
from loguru import logger
from backend.core.config import get_settings

settings = get_settings()


class RiskManager:
    """Comprehensive risk management system."""
    
    def __init__(
        self,
        max_position_size: float = 0.1,
        max_portfolio_risk: float = 0.02,
        max_correlation: float = 0.7,
        stop_loss_pct: float = 0.02
    ):
        """
        Initialize risk manager.
        
        Args:
            max_position_size: Maximum position size as fraction of portfolio
            max_portfolio_risk: Maximum portfolio risk as fraction
            max_correlation: Maximum correlation between positions
            stop_loss_pct: Stop loss percentage
        """
        self.max_position_size = max_position_size
        self.max_portfolio_risk = max_portfolio_risk
        self.max_correlation = max_correlation
        self.stop_loss_pct = stop_loss_pct
        logger.info("Initialized Risk Manager")
    
    def calculate_position_size(
        self,
        signal_confidence: float,
        portfolio_value: float,
        asset_price: float,
        asset_volatility: float
    ) -> Dict[str, Any]:
        """
        Calculate optimal position size using Kelly Criterion and risk constraints.
        
        Args:
            signal_confidence: Confidence in trading signal (0-1)
            portfolio_value: Current portfolio value
            asset_price: Current asset price
            asset_volatility: Asset volatility (standard deviation of returns)
        
        Returns:
            Position sizing recommendation
        """
        # Kelly Criterion for position sizing
        win_rate = signal_confidence
        loss_rate = 1 - win_rate
        
        # Simplified Kelly: f = (p - q) / b, where b is odds
        # Assuming 1:1 risk/reward for simplicity
        kelly_fraction = win_rate - loss_rate
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
        
        # Volatility-adjusted sizing
        vol_adjustment = 1 / (1 + asset_volatility * 10)  # Reduce size for high volatility
        
        # Combined position size
        position_size_fraction = kelly_fraction * vol_adjustment * 0.5  # Half-Kelly for safety
        position_size_fraction = min(position_size_fraction, self.max_position_size)
        
        # Calculate number of shares
        position_value = portfolio_value * position_size_fraction
        num_shares = int(position_value / asset_price)
        
        # Calculate risk metrics
        position_risk = position_value * self.stop_loss_pct
        
        return {
            'num_shares': num_shares,
            'position_value': num_shares * asset_price,
            'position_fraction': (num_shares * asset_price) / portfolio_value,
            'position_risk': position_risk,
            'stop_loss_price': asset_price * (1 - self.stop_loss_pct),
            'kelly_fraction': kelly_fraction,
            'vol_adjustment': vol_adjustment
        }
    
    def check_risk_limits(
        self,
        proposed_position: Dict[str, Any],
        current_positions: List[Dict[str, Any]],
        portfolio_value: float
    ) -> Dict[str, Any]:
        """
        Check if proposed position violates risk limits.
        
        Args:
            proposed_position: Proposed position details
            current_positions: List of current positions
            portfolio_value: Current portfolio value
        
        Returns:
            Risk check results
        """
        violations = []
        
        # Check position size limit
        if proposed_position['position_fraction'] > self.max_position_size:
            violations.append({
                'type': 'position_size',
                'message': f"Position size {proposed_position['position_fraction']:.2%} exceeds limit {self.max_position_size:.2%}"
            })
        
        # Check total portfolio risk
        total_risk = proposed_position['position_risk']
        for pos in current_positions:
            total_risk += pos.get('position_risk', 0)
        
        portfolio_risk_fraction = total_risk / portfolio_value
        if portfolio_risk_fraction > self.max_portfolio_risk:
            violations.append({
                'type': 'portfolio_risk',
                'message': f"Total portfolio risk {portfolio_risk_fraction:.2%} exceeds limit {self.max_portfolio_risk:.2%}"
            })
        
        # Check number of positions
        if len(current_positions) >= settings.max_positions:
            violations.append({
                'type': 'max_positions',
                'message': f"Maximum number of positions ({settings.max_positions}) reached"
            })
        
        return {
            'approved': len(violations) == 0,
            'violations': violations,
            'total_risk': total_risk,
            'portfolio_risk_fraction': portfolio_risk_fraction
        }
    
    def calculate_var(
        self,
        positions: List[Dict[str, Any]],
        confidence_level: float = 0.95,
        time_horizon: int = 1
    ) -> float:
        """
        Calculate Value at Risk (VaR) for the portfolio.
        
        Args:
            positions: List of current positions
            confidence_level: Confidence level for VaR
            time_horizon: Time horizon in days
        
        Returns:
            VaR estimate
        """
        if not positions:
            return 0.0
        
        # Simplified VaR calculation
        # In production, use historical simulation or Monte Carlo
        total_value = sum(pos.get('position_value', 0) for pos in positions)
        avg_volatility = np.mean([pos.get('volatility', 0.02) for pos in positions])
        
        # VaR = Portfolio Value * Volatility * Z-score * sqrt(time_horizon)
        z_score = 1.645 if confidence_level == 0.95 else 2.326  # 95% or 99%
        var = total_value * avg_volatility * z_score * np.sqrt(time_horizon)
        
        return var
    
    def calculate_sharpe_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: float = 0.02
    ) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate
        
        Returns:
            Sharpe ratio
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns.mean() - (risk_free_rate / 252)  # Daily risk-free rate
        sharpe = excess_returns / returns.std() * np.sqrt(252)  # Annualized
        
        return sharpe
    
    def calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """
        Calculate maximum drawdown.
        
        Args:
            equity_curve: Series of portfolio values
        
        Returns:
            Maximum drawdown as percentage
        """
        if len(equity_curve) == 0:
            return 0.0
        
        cumulative_max = equity_curve.expanding().max()
        drawdown = (equity_curve - cumulative_max) / cumulative_max
        max_drawdown = drawdown.min()
        
        return abs(max_drawdown)
    
    def generate_risk_report(
        self,
        positions: List[Dict[str, Any]],
        portfolio_value: float,
        returns: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive risk report.
        
        Args:
            positions: Current positions
            portfolio_value: Current portfolio value
            returns: Historical returns
        
        Returns:
            Risk report dictionary
        """
        report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'portfolio_value': portfolio_value,
            'num_positions': len(positions),
            'var_95': self.calculate_var(positions, confidence_level=0.95),
            'var_99': self.calculate_var(positions, confidence_level=0.99),
        }
        
        if returns is not None and len(returns) > 0:
            report['sharpe_ratio'] = self.calculate_sharpe_ratio(returns)
            report['max_drawdown'] = self.calculate_max_drawdown(pd.Series(returns.cumsum()))
            report['volatility'] = returns.std() * np.sqrt(252)  # Annualized
        
        # Position concentration
        if positions:
            position_values = [pos.get('position_value', 0) for pos in positions]
            total_invested = sum(position_values)
            report['concentration'] = max(position_values) / total_invested if total_invested > 0 else 0
            report['cash_ratio'] = (portfolio_value - total_invested) / portfolio_value
        
        return report
