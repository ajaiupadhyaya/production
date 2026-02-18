"""
Market data fetching and management.
Supports multiple data sources including yfinance and Alpaca.
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from loguru import logger
from backend.core.config import get_settings

settings = get_settings()


class MarketDataFetcher:
    """Fetch and manage market data from multiple sources."""
    
    def __init__(self, source: str = "yfinance"):
        """
        Initialize market data fetcher.
        
        Args:
            source: Data source ('yfinance' or 'alpaca')
        """
        self.source = source
        logger.info(f"Initialized MarketDataFetcher with source: {source}")
    
    def fetch_historical_data(
        self,
        symbols: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical market data.
        
        Args:
            symbols: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval (1m, 5m, 1h, 1d, etc.)
        
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Fetching historical data for {symbols} from {start_date} to {end_date}")
        
        data = {}
        for symbol in symbols:
            try:
                if self.source == "yfinance":
                    ticker = yf.Ticker(symbol)
                    df = ticker.history(start=start_date, end=end_date, interval=interval)
                    data[symbol] = df
                    logger.info(f"Fetched {len(df)} rows for {symbol}")
                else:
                    logger.warning(f"Source {self.source} not yet implemented")
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
        
        return data
    
    def fetch_realtime_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Fetch real-time market data.
        
        Args:
            symbols: List of ticker symbols
        
        Returns:
            Dictionary mapping symbols to current market data
        """
        logger.info(f"Fetching real-time data for {symbols}")
        
        data = {}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                data[symbol] = {
                    'price': info.get('currentPrice', info.get('regularMarketPrice')),
                    'volume': info.get('volume'),
                    'bid': info.get('bid'),
                    'ask': info.get('ask'),
                    'timestamp': datetime.now()
                }
            except Exception as e:
                logger.error(f"Error fetching real-time data for {symbol}: {e}")
        
        return data
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for the given DataFrame.
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with additional technical indicator columns
        """
        try:
            import pandas_ta as ta
            
            # Add technical indicators
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
            
            # RSI
            df['RSI'] = ta.rsi(df['Close'], length=14)
            
            # MACD
            macd = ta.macd(df['Close'])
            if macd is not None:
                df = pd.concat([df, macd], axis=1)
            
            # Bollinger Bands
            bbands = ta.bbands(df['Close'], length=20)
            if bbands is not None:
                df = pd.concat([df, bbands], axis=1)
            
            # ATR (Average True Range)
            df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
            
            # Volume indicators
            df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
            
            logger.info("Calculated technical indicators")
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
        
        return df


class FeatureEngine:
    """Create features for ML models from market data."""
    
    @staticmethod
    def create_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features from OHLCV data.
        
        Args:
            df: DataFrame with market data
        
        Returns:
            DataFrame with feature columns
        """
        features = df.copy()
        
        # Price-based features
        features['returns'] = df['Close'].pct_change()
        features['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
        features['high_low_spread'] = (df['High'] - df['Low']) / df['Close']
        features['close_open_spread'] = (df['Close'] - df['Open']) / df['Open']
        
        # Volatility features
        features['volatility_5'] = features['returns'].rolling(window=5).std()
        features['volatility_20'] = features['returns'].rolling(window=20).std()
        
        # Momentum features
        features['momentum_5'] = df['Close'] / df['Close'].shift(5) - 1
        features['momentum_10'] = df['Close'] / df['Close'].shift(10) - 1
        features['momentum_20'] = df['Close'] / df['Close'].shift(20) - 1
        
        # Volume features
        features['volume_change'] = df['Volume'].pct_change()
        features['volume_ratio'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
        
        # Trend features
        features['price_vs_sma20'] = df['Close'] / features['SMA_20'] - 1 if 'SMA_20' in features else 0
        features['price_vs_sma50'] = df['Close'] / features['SMA_50'] - 1 if 'SMA_50' in features else 0
        
        # Lagged features
        for lag in [1, 2, 3, 5]:
            features[f'return_lag_{lag}'] = features['returns'].shift(lag)
            features[f'volume_lag_{lag}'] = features['volume_change'].shift(lag)
        
        logger.info(f"Created {len(features.columns)} features")
        
        return features
