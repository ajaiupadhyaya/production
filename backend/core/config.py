"""
Core configuration module for the trading platform.
Handles environment variables and system-wide settings.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "sqlite:///./trading.db"
    redis_url: str = "redis://localhost:6379/0"
    
    # API Keys
    openai_api_key: Optional[str] = None
    alpaca_api_key: Optional[str] = None
    alpaca_secret_key: Optional[str] = None
    alpaca_base_url: str = "https://paper-api.alpaca.markets"
    
    # Trading Configuration
    trading_mode: str = "paper"  # paper or live
    risk_limit_percent: float = 2.0
    max_positions: int = 10
    initial_capital: float = 100000.0
    
    # Server Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Monitoring
    enable_prometheus: bool = True
    log_level: str = "INFO"
    
    # Model Configuration
    model_checkpoint_dir: str = "./models/checkpoints"
    model_save_dir: str = "./models/saved"
    
    # Data Configuration
    data_dir: str = "./data"
    market_data_dir: str = "./data/market_data"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
