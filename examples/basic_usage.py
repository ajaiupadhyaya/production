"""
Example script demonstrating how to use the trading platform.
"""
import asyncio
from datetime import datetime, timedelta
from backend.data_pipeline.market_data import MarketDataFetcher, FeatureEngine
from backend.strategies.base_strategy import MomentumStrategy, MeanReversionStrategy
from backend.ml_models.predictors import MLTradingModel
from backend.risk_management.risk_manager import RiskManager
from backend.execution.execution_engine import ExecutionEngine, PortfolioManager, Order, OrderType

async def main():
    """Main example function."""
    print("🚀 Quantitative Trading Platform Example\n")
    
    # 1. Fetch Market Data
    print("📊 Fetching market data...")
    fetcher = MarketDataFetcher()
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    
    data = fetcher.fetch_historical_data(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        interval='1d'
    )
    
    # 2. Calculate Technical Indicators
    print("\n📈 Calculating technical indicators...")
    for symbol, df in data.items():
        data[symbol] = fetcher.calculate_technical_indicators(df)
        print(f"  {symbol}: {len(df)} data points")
    
    # 3. Create Features for ML
    print("\n🔧 Engineering features...")
    feature_engine = FeatureEngine()
    for symbol, df in data.items():
        data[symbol] = feature_engine.create_features(df)
    
    # 4. Initialize Trading Strategies
    print("\n📋 Initializing strategies...")
    momentum_strategy = MomentumStrategy(parameters={
        'lookback_period': 20,
        'momentum_threshold': 0.02,
        'risk_per_trade': 0.02
    })
    
    mean_reversion_strategy = MeanReversionStrategy(parameters={
        'lookback_period': 20,
        'num_std': 2.0,
        'risk_per_trade': 0.02
    })
    
    # 5. Generate Trading Signals
    print("\n🎯 Generating trading signals...")
    for symbol, df in data.items():
        if len(df) > 50:  # Ensure enough data
            momentum_signal = momentum_strategy.generate_signal(df, symbol)
            mean_rev_signal = mean_reversion_strategy.generate_signal(df, symbol)
            
            print(f"\n  {symbol}:")
            print(f"    Momentum: {momentum_signal['action']} (confidence: {momentum_signal['confidence']:.2f})")
            print(f"    Mean Reversion: {mean_rev_signal['action']} (confidence: {mean_rev_signal['confidence']:.2f})")
    
    # 6. Risk Management
    print("\n⚠️  Risk Management Analysis...")
    risk_manager = RiskManager()
    
    portfolio_value = 100000
    signal_confidence = 0.8
    asset_price = 150.0
    asset_volatility = 0.02
    
    position_sizing = risk_manager.calculate_position_size(
        signal_confidence=signal_confidence,
        portfolio_value=portfolio_value,
        asset_price=asset_price,
        asset_volatility=asset_volatility
    )
    
    print(f"  Recommended position size: {position_sizing['num_shares']} shares")
    print(f"  Position value: ${position_sizing['position_value']:,.2f}")
    print(f"  Stop loss: ${position_sizing['stop_loss_price']:.2f}")
    
    # 7. Portfolio Management
    print("\n💼 Portfolio Management...")
    portfolio = PortfolioManager(initial_capital=100000)
    execution_engine = ExecutionEngine(trading_mode='paper')
    
    # Simulate a trade
    order = Order(
        symbol='AAPL',
        side='buy',
        quantity=10,
        order_type=OrderType.MARKET,
        strategy_id=1
    )
    
    result = execution_engine.submit_order(order)
    print(f"  Order result: {result['message']}")
    
    if result['success']:
        portfolio.update_position(
            symbol='AAPL',
            quantity_change=10,
            price=result['filled_price'],
            side='buy'
        )
        
        print(f"  Portfolio value: ${portfolio.get_portfolio_value():,.2f}")
        print(f"  Cash: ${portfolio.cash:,.2f}")
    
    # 8. ML Model Prediction (if needed)
    print("\n🤖 ML Model Example...")
    print("  (Note: Model requires training first - see documentation)")
    
    # 9. Performance Summary
    print("\n📊 Performance Summary:")
    pnl = portfolio.get_pnl()
    print(f"  Total P&L: ${pnl['total_pnl']:,.2f}")
    print(f"  Return: {pnl['return_pct']:.2f}%")
    
    print("\n✅ Example completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
