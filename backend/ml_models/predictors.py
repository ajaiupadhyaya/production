"""
Machine Learning based trading models.
Implements LSTM, Transformer, and ensemble methods for price prediction.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from loguru import logger


class LSTMPricePredictor(nn.Module):
    """LSTM model for price prediction."""
    
    def __init__(
        self,
        input_size: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.2
    ):
        """
        Initialize LSTM model.
        
        Args:
            input_size: Number of input features
            hidden_size: Hidden layer size
            num_layers: Number of LSTM layers
            dropout: Dropout rate
        """
        super(LSTMPricePredictor, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 3)  # 3 classes: up, down, neutral
        )
    
    def forward(self, x):
        """Forward pass."""
        # x shape: (batch, seq_len, features)
        lstm_out, _ = self.lstm(x)
        
        # Take the last output
        last_output = lstm_out[:, -1, :]
        
        # Pass through fully connected layers
        output = self.fc(last_output)
        
        return output


class TransformerPredictor(nn.Module):
    """Transformer model for time series prediction."""
    
    def __init__(
        self,
        input_size: int,
        d_model: int = 128,
        nhead: int = 8,
        num_layers: int = 4,
        dropout: float = 0.2
    ):
        """
        Initialize Transformer model.
        
        Args:
            input_size: Number of input features
            d_model: Model dimension
            nhead: Number of attention heads
            num_layers: Number of transformer layers
            dropout: Dropout rate
        """
        super(TransformerPredictor, self).__init__()
        
        self.d_model = d_model
        
        # Input projection
        self.input_projection = nn.Linear(input_size, d_model)
        
        # Positional encoding
        self.pos_encoder = nn.Parameter(torch.randn(1, 100, d_model))
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Output layer
        self.fc = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 3)  # 3 classes: up, down, neutral
        )
    
    def forward(self, x):
        """Forward pass."""
        # x shape: (batch, seq_len, features)
        batch_size, seq_len, _ = x.shape
        
        # Project input
        x = self.input_projection(x)
        
        # Add positional encoding
        x = x + self.pos_encoder[:, :seq_len, :]
        
        # Transformer
        x = self.transformer(x)
        
        # Take mean across sequence
        x = x.mean(dim=1)
        
        # Output
        output = self.fc(x)
        
        return output


class TimeSeriesDataset(Dataset):
    """Dataset for time series data."""
    
    def __init__(self, features: np.ndarray, labels: np.ndarray, sequence_length: int = 20):
        """
        Initialize dataset.
        
        Args:
            features: Feature array
            labels: Label array
            sequence_length: Sequence length for time series
        """
        self.features = features
        self.labels = labels
        self.sequence_length = sequence_length
    
    def __len__(self):
        return len(self.features) - self.sequence_length
    
    def __getitem__(self, idx):
        x = self.features[idx:idx + self.sequence_length]
        y = self.labels[idx + self.sequence_length]
        return torch.FloatTensor(x), torch.LongTensor([y])


class MLTradingModel:
    """Machine learning model manager for trading."""
    
    def __init__(
        self,
        model_type: str = "lstm",
        input_size: int = 20,
        device: str = "cpu"
    ):
        """
        Initialize ML trading model.
        
        Args:
            model_type: Model type ('lstm', 'transformer', 'ensemble')
            input_size: Number of input features
            device: Device to run model on
        """
        self.model_type = model_type
        self.input_size = input_size
        self.device = device
        self.scaler = StandardScaler()
        
        # Initialize model
        if model_type == "lstm":
            self.model = LSTMPricePredictor(input_size=input_size).to(device)
        elif model_type == "transformer":
            self.model = TransformerPredictor(input_size=input_size).to(device)
        elif model_type == "ensemble":
            self.model = self._create_ensemble()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        logger.info(f"Initialized {model_type} model")
    
    def _create_ensemble(self):
        """Create ensemble of classical ML models."""
        return {
            'rf': RandomForestClassifier(n_estimators=100, max_depth=10),
            'gb': GradientBoostingClassifier(n_estimators=100, max_depth=5)
        }
    
    def prepare_data(
        self,
        data: pd.DataFrame,
        target_col: str = 'returns'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for training.
        
        Args:
            data: Input DataFrame
            target_col: Target column name
        
        Returns:
            Features and labels as numpy arrays
        """
        # Create labels (1: up, 0: neutral, -1: down)
        labels = np.where(data[target_col] > 0.001, 1, np.where(data[target_col] < -0.001, 2, 0))
        
        # Select feature columns (exclude target and non-numeric)
        feature_cols = [col for col in data.columns if col != target_col and data[col].dtype in [np.float64, np.int64]]
        features = data[feature_cols].fillna(0).values
        
        # Scale features
        features = self.scaler.fit_transform(features)
        
        return features, labels
    
    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """
        Make prediction.
        
        Args:
            features: Input features
        
        Returns:
            Prediction dictionary with action and confidence
        """
        if self.model_type in ["lstm", "transformer"]:
            self.model.eval()
            with torch.no_grad():
                x = torch.FloatTensor(features).unsqueeze(0).to(self.device)
                output = self.model(x)
                probs = torch.softmax(output, dim=1).cpu().numpy()[0]
                pred_class = np.argmax(probs)
                confidence = probs[pred_class]
        else:
            # Ensemble prediction
            features_2d = features.reshape(1, -1) if len(features.shape) == 1 else features
            predictions = []
            for model in self.model.values():
                pred = model.predict_proba(features_2d)[0]
                predictions.append(pred)
            probs = np.mean(predictions, axis=0)
            pred_class = np.argmax(probs)
            confidence = probs[pred_class]
        
        # Map class to action
        action_map = {0: 'hold', 1: 'buy', 2: 'sell'}
        
        return {
            'action': action_map[pred_class],
            'confidence': float(confidence),
            'probabilities': {
                'hold': float(probs[0]),
                'buy': float(probs[1]),
                'sell': float(probs[2])
            }
        }
