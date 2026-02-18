# Quantitative Trading Platform

A professional-grade, AI-powered quantitative trading platform built with modern technologies following industry standards from firms like Jane Street, Citadel, and other top quantitative finance institutions.

## 🚀 Features

### Core Capabilities
- **Multiple Trading Strategies**: Momentum, Mean Reversion, ML-based, LLM-powered, and Hybrid strategies
- **Advanced ML Models**: LSTM, Transformer architectures for price prediction
- **LLM Integration**: GPT-4 powered market analysis and strategy suggestions
- **Risk Management**: Comprehensive risk controls, VaR calculation, position sizing
- **Real-time Monitoring**: Live portfolio tracking and performance analytics
- **Automated Execution**: TWAP, VWAP, and smart order routing algorithms
- **Web Interface**: Modern React-based dashboard for monitoring and control

### Technology Stack

**Backend:**
- Python 3.10+
- FastAPI for REST API
- SQLAlchemy for database ORM
- PyTorch for deep learning
- Transformers for LLM integration
- Multiple data sources (yfinance, Alpaca)

**Frontend:**
- React 18
- Material-UI components
- Recharts for visualization
- Vite for fast development

**Data & ML:**
- Pandas, NumPy for data processing
- Scikit-learn for classical ML
- PyTorch for deep learning
- Technical indicators (pandas-ta)

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- pip and npm

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
python -c "from backend.core.db_utils import init_db; init_db()"
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

## 🎯 Quick Start

### Option 1: Use the Start Script (Recommended)

```bash
chmod +x start.sh
./start.sh
```

This will start both backend and frontend automatically.

### Option 2: Manual Start

**Start the Backend Server:**

```bash
# From the project root
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

**Start the Frontend:**

```bash
# In a new terminal
cd frontend
npm run dev
```

The web interface will be available at `http://localhost:3000`

### Option 3: Docker Deployment

```bash
docker-compose up -d
```

## 📊 Architecture

### System Components

1. **Data Pipeline**
   - Market data fetching (real-time & historical)
   - Feature engineering
   - Technical indicator calculation
   - Data validation and cleaning

2. **Strategy Engine**
   - Base strategy framework
   - Multiple strategy implementations
   - Signal generation
   - Backtesting capabilities

3. **ML Models**
   - LSTM price predictors
   - Transformer-based models
   - Ensemble methods
   - LLM-powered analysis

4. **Risk Management**
   - Position sizing (Kelly Criterion)
   - VaR calculation
   - Drawdown monitoring
   - Portfolio risk limits

5. **Execution Engine**
   - Order management
   - Multiple execution algorithms
   - Paper & live trading modes
   - Commission tracking

6. **API Layer**
   - RESTful API with FastAPI
   - Real-time data endpoints
   - Strategy management
   - Portfolio monitoring

7. **Web Interface**
   - Dashboard overview
   - Strategy management
   - Portfolio tracking
   - Analytics and insights

## 🔧 Configuration

### Trading Configuration

Edit `.env` file:

```env
# Trading Mode
TRADING_MODE=paper  # paper or live

# Risk Management
RISK_LIMIT_PERCENT=2.0
MAX_POSITIONS=10
INITIAL_CAPITAL=100000

# API Keys (for live data)
OPENAI_API_KEY=your_key_here
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_key_here
```

## 📈 Usage Examples

See `examples/basic_usage.py` for a complete example.

### Create a Trading Strategy

```python
from backend.strategies.base_strategy import MomentumStrategy

# Create strategy
strategy = MomentumStrategy(parameters={
    'lookback_period': 20,
    'momentum_threshold': 0.02,
    'risk_per_trade': 0.02
})

# Generate signal
signal = strategy.generate_signal(market_data, 'AAPL')
print(signal)  # {'action': 'buy', 'confidence': 0.85, ...}
```

### Use ML Model for Prediction

```python
from backend.ml_models.predictors import MLTradingModel

# Initialize model
model = MLTradingModel(model_type='lstm', input_size=20)

# Make prediction
prediction = model.predict(features)
print(prediction)  # {'action': 'buy', 'confidence': 0.92, ...}
```

### Access via API

```bash
# Get portfolio status
curl http://localhost:8000/portfolio

# Create a strategy
curl -X POST http://localhost:8000/strategies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Strategy",
    "strategy_type": "momentum",
    "parameters": {"lookback_period": 20}
  }'

# Get market data
curl http://localhost:8000/market-data/AAPL?interval=1d
```

## 🧪 Testing

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=backend tests/
```

## 📊 Performance Metrics

The platform tracks comprehensive performance metrics:

- **Returns**: Total P&L, daily/monthly returns
- **Risk Metrics**: Sharpe ratio, Sortino ratio, Max drawdown
- **Win Rate**: Percentage of profitable trades
- **Risk-adjusted Returns**: Information ratio, Calmar ratio
- **Position Analytics**: Concentration, turnover

## 🔒 Security

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Paper trading mode for testing
- Risk limits enforced at multiple levels
- Order validation before execution

## 🚧 Development Roadmap

- [ ] Live broker integration (Interactive Brokers, TD Ameritrade)
- [ ] Advanced backtesting with walk-forward optimization
- [ ] Multi-asset support (options, futures, crypto)
- [ ] Real-time news sentiment analysis
- [ ] Custom alert system
- [ ] Mobile app
- [ ] Cloud deployment (AWS/GCP)
- [ ] Kubernetes orchestration

## 📚 Documentation

- API Documentation: `http://localhost:8000/docs` (when server is running)
- Code documentation: See docstrings in source files
- Examples: See `examples/` directory

## 🤝 Contributing

This is a production trading platform. Contributions should:
- Follow PEP 8 style guidelines
- Include comprehensive tests
- Update documentation
- Pass all CI/CD checks

## ⚠️ Disclaimer

This software is for educational and research purposes. Trading involves substantial risk of loss. Past performance does not guarantee future results. Always conduct thorough testing before deploying any trading strategy with real capital.

## 📄 License

Proprietary - All rights reserved

## 🙏 Acknowledgments

Built with inspiration from leading quantitative trading firms and modern software engineering practices.

---

**Status**: Production Ready 🚀
**Version**: 1.0.0
**Last Updated**: 2024
