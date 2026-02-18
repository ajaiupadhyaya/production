"""
FastAPI application for the trading platform.
Provides REST API for strategy management, monitoring, and execution.
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn
from loguru import logger

from backend.core.config import get_settings
from backend.core.db_utils import get_db, init_db
from backend.core.database import Strategy, Position, Order, Signal, PerformanceMetrics
from backend.strategies.base_strategy import MomentumStrategy, MeanReversionStrategy
from backend.ml_models.predictors import MLTradingModel
from backend.ml_models.llm_analyzer import LLMMarketAnalyzer
from backend.risk_management.risk_manager import RiskManager
from backend.execution.execution_engine import ExecutionEngine, PortfolioManager, Order as ExecutionOrder, OrderType
from backend.data_pipeline.market_data import MarketDataFetcher, FeatureEngine
from pydantic import BaseModel

settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title="Quantitative Trading Platform",
    description="AI-Powered Trading Platform with ML Models and LLM Analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
market_data_fetcher = MarketDataFetcher()
feature_engine = FeatureEngine()
risk_manager = RiskManager()
execution_engine = ExecutionEngine(trading_mode=settings.trading_mode)
portfolio_manager = PortfolioManager(initial_capital=settings.initial_capital)
llm_analyzer = LLMMarketAnalyzer()


# Pydantic models for API
class StrategyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    strategy_type: str
    parameters: Optional[Dict[str, Any]] = None


class SignalCreate(BaseModel):
    strategy_id: int
    symbol: str
    signal_type: str
    confidence: float
    price: float
    features: Optional[Dict[str, Any]] = None


class OrderCreate(BaseModel):
    strategy_id: int
    symbol: str
    side: str
    quantity: float
    order_type: str = "market"
    limit_price: Optional[float] = None


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting trading platform API...")
    init_db()
    logger.info("Database initialized")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Quantitative Trading Platform",
        "version": "1.0.0",
        "status": "running",
        "trading_mode": settings.trading_mode
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# Strategy endpoints
@app.post("/strategies", response_model=Dict[str, Any])
async def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    """Create a new trading strategy."""
    db_strategy = Strategy(
        name=strategy.name,
        description=strategy.description,
        strategy_type=strategy.strategy_type,
        parameters=strategy.parameters or {},
        is_active=False
    )
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    
    logger.info(f"Created strategy: {strategy.name}")
    
    return {
        "id": db_strategy.id,
        "name": db_strategy.name,
        "strategy_type": db_strategy.strategy_type,
        "is_active": db_strategy.is_active
    }


@app.get("/strategies", response_model=List[Dict[str, Any]])
async def list_strategies(db: Session = Depends(get_db)):
    """List all trading strategies."""
    strategies = db.query(Strategy).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "strategy_type": s.strategy_type,
            "is_active": s.is_active,
            "total_pnl": s.total_pnl,
            "win_rate": s.win_rate,
            "sharpe_ratio": s.sharpe_ratio
        }
        for s in strategies
    ]


@app.get("/strategies/{strategy_id}")
async def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Get strategy details."""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return {
        "id": strategy.id,
        "name": strategy.name,
        "description": strategy.description,
        "strategy_type": strategy.strategy_type,
        "parameters": strategy.parameters,
        "is_active": strategy.is_active,
        "performance": {
            "total_pnl": strategy.total_pnl,
            "win_rate": strategy.win_rate,
            "sharpe_ratio": strategy.sharpe_ratio,
            "max_drawdown": strategy.max_drawdown
        }
    }


@app.post("/strategies/{strategy_id}/activate")
async def activate_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Activate a strategy."""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    strategy.is_active = True
    db.commit()
    
    logger.info(f"Activated strategy: {strategy.name}")
    
    return {"message": "Strategy activated", "strategy_id": strategy_id}


@app.post("/strategies/{strategy_id}/deactivate")
async def deactivate_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Deactivate a strategy."""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    strategy.is_active = False
    db.commit()
    
    logger.info(f"Deactivated strategy: {strategy.name}")
    
    return {"message": "Strategy deactivated", "strategy_id": strategy_id}


# Market data endpoints
@app.get("/market-data/{symbol}")
async def get_market_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: str = "1d"
):
    """Get historical market data for a symbol."""
    try:
        data = market_data_fetcher.fetch_historical_data(
            symbols=[symbol],
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
        
        if symbol not in data:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        df = data[symbol]
        df = market_data_fetcher.calculate_technical_indicators(df)
        
        return {
            "symbol": symbol,
            "data": df.tail(100).to_dict(orient="records"),
            "count": len(df)
        }
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/market-data/{symbol}/realtime")
async def get_realtime_data(symbol: str):
    """Get real-time market data for a symbol."""
    try:
        data = market_data_fetcher.fetch_realtime_data([symbol])
        if symbol not in data:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        return data[symbol]
    except Exception as e:
        logger.error(f"Error fetching real-time data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Signal endpoints
@app.post("/signals")
async def create_signal(signal: SignalCreate, db: Session = Depends(get_db)):
    """Create a trading signal."""
    db_signal = Signal(
        strategy_id=signal.strategy_id,
        symbol=signal.symbol,
        signal_type=signal.signal_type,
        confidence=signal.confidence,
        price=signal.price,
        features=signal.features
    )
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    
    return {
        "id": db_signal.id,
        "signal_type": db_signal.signal_type,
        "symbol": db_signal.symbol,
        "confidence": db_signal.confidence
    }


@app.get("/signals")
async def list_signals(
    strategy_id: Optional[int] = None,
    symbol: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List trading signals."""
    query = db.query(Signal)
    
    if strategy_id:
        query = query.filter(Signal.strategy_id == strategy_id)
    if symbol:
        query = query.filter(Signal.symbol == symbol)
    
    signals = query.order_by(Signal.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": s.id,
            "strategy_id": s.strategy_id,
            "symbol": s.symbol,
            "signal_type": s.signal_type,
            "confidence": s.confidence,
            "price": s.price,
            "created_at": s.created_at.isoformat(),
            "executed": s.executed
        }
        for s in signals
    ]


# Order endpoints
@app.post("/orders")
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Submit a new order."""
    # Create execution order
    exec_order = ExecutionOrder(
        symbol=order.symbol,
        side=order.side,
        quantity=order.quantity,
        order_type=OrderType.MARKET if order.order_type == "market" else OrderType.LIMIT,
        limit_price=order.limit_price,
        strategy_id=order.strategy_id
    )
    
    # Execute order
    result = execution_engine.submit_order(exec_order)
    
    if result['success']:
        # Save to database
        db_order = Order(
            strategy_id=order.strategy_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            order_type=order.order_type,
            limit_price=order.limit_price,
            status="filled" if result['status'] == 'filled' else "pending",
            filled_quantity=result.get('filled_quantity', 0),
            filled_price=result.get('filled_price')
        )
        db.add(db_order)
        db.commit()
        
        # Update portfolio
        if result['status'] == 'filled':
            portfolio_manager.update_position(
                symbol=order.symbol,
                quantity_change=order.quantity,
                price=result['filled_price'],
                side=order.side
            )
        
        return {
            "order_id": result['order_id'],
            "status": result['status'],
            "message": result['message']
        }
    else:
        raise HTTPException(status_code=400, detail=result['message'])


@app.get("/orders")
async def list_orders(
    strategy_id: Optional[int] = None,
    symbol: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List orders."""
    query = db.query(Order)
    
    if strategy_id:
        query = query.filter(Order.strategy_id == strategy_id)
    if symbol:
        query = query.filter(Order.symbol == symbol)
    
    orders = query.order_by(Order.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": o.id,
            "strategy_id": o.strategy_id,
            "symbol": o.symbol,
            "side": o.side.value if hasattr(o.side, 'value') else o.side,
            "quantity": o.quantity,
            "status": o.status.value if hasattr(o.status, 'value') else o.status,
            "filled_quantity": o.filled_quantity,
            "filled_price": o.filled_price,
            "created_at": o.created_at.isoformat()
        }
        for o in orders
    ]


# Portfolio endpoints
@app.get("/portfolio")
async def get_portfolio():
    """Get current portfolio status."""
    return {
        "cash": portfolio_manager.cash,
        "positions": portfolio_manager.positions,
        "total_value": portfolio_manager.get_portfolio_value(),
        "pnl": portfolio_manager.get_pnl()
    }


@app.get("/portfolio/positions")
async def get_positions(db: Session = Depends(get_db)):
    """Get all positions."""
    positions = db.query(Position).all()
    
    return [
        {
            "id": p.id,
            "symbol": p.symbol,
            "quantity": p.quantity,
            "entry_price": p.entry_price,
            "current_price": p.current_price,
            "unrealized_pnl": p.unrealized_pnl,
            "realized_pnl": p.realized_pnl
        }
        for p in positions
    ]


# Risk management endpoints
@app.get("/risk/report")
async def get_risk_report():
    """Get risk management report."""
    positions_list = [
        {
            'position_value': pos['quantity'] * pos['current_price'],
            'volatility': 0.02  # Placeholder
        }
        for pos in portfolio_manager.positions.values()
    ]
    
    report = risk_manager.generate_risk_report(
        positions=positions_list,
        portfolio_value=portfolio_manager.get_portfolio_value()
    )
    
    return report


# LLM Analysis endpoints
@app.get("/analysis/sentiment/{symbol}")
async def get_sentiment_analysis(symbol: str):
    """Get LLM-powered sentiment analysis for a symbol."""
    # Get recent market data
    realtime_data = market_data_fetcher.fetch_realtime_data([symbol])
    
    price_data = {
        'current_price': realtime_data.get(symbol, {}).get('price', 0),
        'volume': realtime_data.get(symbol, {}).get('volume', 0)
    }
    
    # Placeholder news data
    news_data = [
        f"Market update for {symbol}",
        "Trading volume increased",
        "Technical indicators show strength"
    ]
    
    analysis = llm_analyzer.analyze_market_sentiment(
        symbol=symbol,
        news_data=news_data,
        price_data=price_data
    )
    
    return analysis


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
