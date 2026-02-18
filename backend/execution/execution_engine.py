"""
Order execution engine for managing trade execution.
Implements various execution algorithms.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from loguru import logger
from backend.core.config import get_settings

settings = get_settings()


class OrderType(Enum):
    """Order types."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LIMIT = "stop_limit"


class ExecutionAlgorithm(Enum):
    """Execution algorithms."""
    IMMEDIATE = "immediate"
    TWAP = "twap"  # Time-Weighted Average Price
    VWAP = "vwap"  # Volume-Weighted Average Price
    ICEBERG = "iceberg"
    SMART = "smart"


class Order:
    """Order object."""
    
    def __init__(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: OrderType = OrderType.MARKET,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        strategy_id: Optional[int] = None
    ):
        """Initialize order."""
        self.symbol = symbol
        self.side = side  # buy or sell
        self.quantity = quantity
        self.order_type = order_type
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.strategy_id = strategy_id
        self.status = "pending"
        self.filled_quantity = 0.0
        self.filled_price = None
        self.created_at = datetime.now()
        self.filled_at = None
        self.order_id = None


class ExecutionEngine:
    """Order execution engine."""
    
    def __init__(self, trading_mode: str = "paper"):
        """
        Initialize execution engine.
        
        Args:
            trading_mode: 'paper' or 'live'
        """
        self.trading_mode = trading_mode
        self.pending_orders = []
        self.filled_orders = []
        logger.info(f"Initialized Execution Engine in {trading_mode} mode")
    
    def submit_order(
        self,
        order: Order,
        algorithm: ExecutionAlgorithm = ExecutionAlgorithm.IMMEDIATE
    ) -> Dict[str, Any]:
        """
        Submit order for execution.
        
        Args:
            order: Order object
            algorithm: Execution algorithm to use
        
        Returns:
            Order execution result
        """
        logger.info(f"Submitting {order.side} order for {order.quantity} {order.symbol}")
        
        if algorithm == ExecutionAlgorithm.IMMEDIATE:
            return self._execute_immediate(order)
        elif algorithm == ExecutionAlgorithm.TWAP:
            return self._execute_twap(order)
        elif algorithm == ExecutionAlgorithm.VWAP:
            return self._execute_vwap(order)
        else:
            return self._execute_immediate(order)
    
    def _execute_immediate(self, order: Order) -> Dict[str, Any]:
        """Execute order immediately at market price."""
        # In paper trading mode, simulate execution
        if self.trading_mode == "paper":
            # Simulate market execution
            order.status = "filled"
            order.filled_quantity = order.quantity
            # In real implementation, get actual market price
            order.filled_price = order.limit_price if order.limit_price else 100.0
            order.filled_at = datetime.now()
            order.order_id = f"SIM_{datetime.now().timestamp()}"
            
            self.filled_orders.append(order)
            
            logger.info(f"Paper trade executed: {order.symbol} {order.side} {order.quantity} @ {order.filled_price}")
            
            return {
                'success': True,
                'order_id': order.order_id,
                'status': order.status,
                'filled_quantity': order.filled_quantity,
                'filled_price': order.filled_price,
                'message': 'Order filled (simulated)'
            }
        else:
            # Live trading would integrate with broker API
            logger.warning("Live trading not yet implemented")
            return {
                'success': False,
                'message': 'Live trading not implemented'
            }
    
    def _execute_twap(self, order: Order, duration_minutes: int = 30) -> Dict[str, Any]:
        """
        Execute order using TWAP algorithm.
        Splits order into equal parts over time.
        
        Args:
            order: Order object
            duration_minutes: Duration to spread order over
        
        Returns:
            Execution result
        """
        num_slices = min(10, duration_minutes)  # Max 10 slices
        slice_size = order.quantity / num_slices
        
        logger.info(f"Executing TWAP: {num_slices} slices of {slice_size} over {duration_minutes} minutes")
        
        # In production, would schedule these executions
        # For now, simulate immediate execution
        return self._execute_immediate(order)
    
    def _execute_vwap(self, order: Order) -> Dict[str, Any]:
        """
        Execute order using VWAP algorithm.
        Matches execution to volume profile.
        
        Args:
            order: Order object
        
        Returns:
            Execution result
        """
        logger.info(f"Executing VWAP for {order.symbol}")
        
        # Would use historical volume profile to schedule executions
        # For now, simulate immediate execution
        return self._execute_immediate(order)
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel pending order.
        
        Args:
            order_id: Order ID to cancel
        
        Returns:
            Cancellation result
        """
        for order in self.pending_orders:
            if order.order_id == order_id:
                order.status = "cancelled"
                self.pending_orders.remove(order)
                logger.info(f"Cancelled order {order_id}")
                return {
                    'success': True,
                    'message': f'Order {order_id} cancelled'
                }
        
        return {
            'success': False,
            'message': f'Order {order_id} not found'
        }
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get status of an order.
        
        Args:
            order_id: Order ID
        
        Returns:
            Order status
        """
        # Check pending orders
        for order in self.pending_orders:
            if order.order_id == order_id:
                return {
                    'order_id': order_id,
                    'status': order.status,
                    'filled_quantity': order.filled_quantity,
                    'filled_price': order.filled_price
                }
        
        # Check filled orders
        for order in self.filled_orders:
            if order.order_id == order_id:
                return {
                    'order_id': order_id,
                    'status': order.status,
                    'filled_quantity': order.filled_quantity,
                    'filled_price': order.filled_price
                }
        
        return {
            'order_id': order_id,
            'status': 'not_found'
        }


class PortfolioManager:
    """Manage portfolio positions and P&L."""
    
    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize portfolio manager.
        
        Args:
            initial_capital: Starting capital
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # symbol -> {quantity, avg_price, current_price}
        self.realized_pnl = 0.0
        logger.info(f"Initialized Portfolio Manager with ${initial_capital:,.2f}")
    
    def update_position(
        self,
        symbol: str,
        quantity_change: float,
        price: float,
        side: str
    ):
        """
        Update position after trade execution.
        
        Args:
            symbol: Trading symbol
            quantity_change: Change in quantity
            price: Execution price
            side: 'buy' or 'sell'
        """
        if symbol not in self.positions:
            self.positions[symbol] = {
                'quantity': 0,
                'avg_price': 0,
                'current_price': price
            }
        
        pos = self.positions[symbol]
        
        if side == 'buy':
            # Calculate new average price
            total_cost = pos['quantity'] * pos['avg_price'] + quantity_change * price
            new_quantity = pos['quantity'] + quantity_change
            pos['avg_price'] = total_cost / new_quantity if new_quantity > 0 else 0
            pos['quantity'] = new_quantity
            self.cash -= quantity_change * price
        else:  # sell
            # Realize P&L
            pnl = quantity_change * (price - pos['avg_price'])
            self.realized_pnl += pnl
            pos['quantity'] -= quantity_change
            self.cash += quantity_change * price
            
            if pos['quantity'] <= 0:
                del self.positions[symbol]
        
        logger.info(f"Updated position: {symbol} quantity={pos.get('quantity', 0)}, avg_price={pos.get('avg_price', 0)}")
    
    def get_portfolio_value(self) -> float:
        """Get total portfolio value."""
        positions_value = sum(
            pos['quantity'] * pos['current_price']
            for pos in self.positions.values()
        )
        return self.cash + positions_value
    
    def get_pnl(self) -> Dict[str, float]:
        """Get P&L breakdown."""
        unrealized_pnl = sum(
            pos['quantity'] * (pos['current_price'] - pos['avg_price'])
            for pos in self.positions.values()
        )
        
        return {
            'realized_pnl': self.realized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'total_pnl': self.realized_pnl + unrealized_pnl,
            'return_pct': ((self.get_portfolio_value() - self.initial_capital) / self.initial_capital) * 100
        }
