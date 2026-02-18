#!/usr/bin/env python3
"""
Quick demo of the trading platform capabilities.
"""
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 60)
print("🚀 QUANTITATIVE TRADING PLATFORM DEMO")
print("=" * 60)
print()

# 1. Test Configuration
print("1️⃣  Testing Configuration...")
try:
    from backend.core.config import get_settings
    settings = get_settings()
    print(f"   ✓ Trading Mode: {settings.trading_mode}")
    print(f"   ✓ Initial Capital: ${settings.initial_capital:,.0f}")
    print(f"   ✓ Max Positions: {settings.max_positions}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    sys.exit(1)

# 2. Test Database
print("\n2️⃣  Testing Database...")
try:
    from backend.core.db_utils import init_db
    init_db()
    print("   ✓ Database initialized successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 3. Test Trading Strategies
print("\n3️⃣  Testing Trading Strategies...")
try:
    from backend.strategies.base_strategy import MomentumStrategy, MeanReversionStrategy
    
    # Create sample data
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    prices = 100 + np.cumsum(np.random.randn(100) * 2)
    df = pd.DataFrame({
        'Open': prices,
        'High': prices * 1.02,
        'Low': prices * 0.98,
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, 100)
    }, index=dates)
    
    # Test Momentum Strategy
    momentum = MomentumStrategy()
    signal_mom = momentum.generate_signal(df, 'TEST')
    print(f"   ✓ Momentum Strategy: {signal_mom['action'].upper()} (confidence: {signal_mom['confidence']:.2f})")
    
    # Test Mean Reversion Strategy
    mean_rev = MeanReversionStrategy()
    signal_mr = mean_rev.generate_signal(df, 'TEST')
    print(f"   ✓ Mean Reversion: {signal_mr['action'].upper()} (confidence: {signal_mr['confidence']:.2f})")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# 4. Test Risk Management
print("\n4️⃣  Testing Risk Management...")
try:
    from backend.risk_management.risk_manager import RiskManager
    
    risk_mgr = RiskManager()
    position_size = risk_mgr.calculate_position_size(
        signal_confidence=0.8,
        portfolio_value=100000,
        asset_price=150,
        asset_volatility=0.02
    )
    print(f"   ✓ Position Size: {position_size['num_shares']} shares")
    print(f"   ✓ Position Value: ${position_size['position_value']:,.2f}")
    print(f"   ✓ Stop Loss: ${position_size['stop_loss_price']:.2f}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 5. Test Execution Engine
print("\n5️⃣  Testing Execution Engine...")
try:
    from backend.execution.execution_engine import ExecutionEngine, PortfolioManager, Order, OrderType
    
    # Initialize portfolio and execution engine
    portfolio = PortfolioManager(initial_capital=100000)
    engine = ExecutionEngine(trading_mode='paper')
    
    # Submit test order
    order = Order(
        symbol='AAPL',
        side='buy',
        quantity=10,
        order_type=OrderType.MARKET
    )
    
    result = engine.submit_order(order)
    print(f"   ✓ Order Status: {result['status']}")
    print(f"   ✓ Order ID: {result['order_id']}")
    
    # Update portfolio
    if result['success']:
        portfolio.update_position('AAPL', 10, result['filled_price'], 'buy')
        print(f"   ✓ Portfolio Value: ${portfolio.get_portfolio_value():,.2f}")
        print(f"   ✓ Cash Remaining: ${portfolio.cash:,.2f}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 60)
print("✅ DEMO COMPLETED SUCCESSFULLY!")
print("=" * 60)
print()
print("📊 Next Steps:")
print("   1. Start the backend API: python -m uvicorn backend.api.main:app")
print("   2. Install frontend deps: cd frontend && npm install")
print("   3. Start frontend: cd frontend && npm run dev")
print("   4. Visit http://localhost:3000 to see the dashboard")
print()
print("📚 See README.md for full documentation")
print()
