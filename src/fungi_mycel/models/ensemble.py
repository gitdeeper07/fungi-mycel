"""
AI Ensemble Model for MNIS Prediction

Combines CNN-1D (bioelectrical), XGBoost (tabular), and LSTM (temporal)
models into a unified ensemble with weighted voting.

Weights:
    - CNN: 0.38 (spike pattern classification)
    - XGBoost: 0.32 (parameter analysis)
    - LSTM: 0.30 (time series prediction)
"""

import numpy as np
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass
import json
import pickle
from pathlib import Path

# Try importing ML libraries - gracefully handle if not available
try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


@dataclass
class EnsembleConfig:
    """Configuration for the AI ensemble."""
    
    cnn_weight: float = 0.38
    xgb_weight: float = 0.32
    lstm_weight: float = 0.30
    
    cnn_model_path: Optional[str] = None
    xgb_model_path: Optional[str] = None
    lstm_model_path: Optional[str] = None
    
    use_gpu: bool = False
    batch_size: int = 32
    threshold: float = 0.5


@dataclass
class EnsembleResult:
    """Container for ensemble prediction results."""
    
    mnis_prediction: float
    cnn_prediction: float
    xgb_prediction: float
    lstm_prediction: float
    confidence: float
    feature_importance: Dict[str, float]
    warnings: List[str] = None


class AIEnsemble:
    """
    AI Ensemble for MNIS prediction.
    
    Combines three models:
        1. CNN-1D: Processes raw bioelectrical spike trains
        2. XGBoost: Analyzes 8 tabular parameters
        3. LSTM: Predicts from time series history
    """
    
    def __init__(self, config: Optional[EnsembleConfig] = None):
        """
        Initialize the AI ensemble.
        
        Args:
            config: Ensemble configuration
        """
        self.config = config or EnsembleConfig()
        
        self.cnn_model = None
        self.xgb_model = None
        self.lstm_model = None
        
        self.is_loaded = False
    
    def load_models(self):
        """Load pre-trained models."""
        if self.is_loaded:
            return
        
        # Load CNN model
        if self.config.cnn_model_path and TENSORFLOW_AVAILABLE:
            try:
                self.cnn_model = keras.models.load_model(self.config.cnn_model_path)
            except Exception as e:
                print(f"Warning: Could not load CNN model: {e}")
        
        # Load XGBoost model
        if self.config.xgb_model_path and XGBOOST_AVAILABLE:
            try:
                self.xgb_model = xgb.Booster()
                self.xgb_model.load_model(self.config.xgb_model_path)
            except Exception as e:
                print(f"Warning: Could not load XGBoost model: {e}")
        
        # Load LSTM model
        if self.config.lstm_model_path and TENSORFLOW_AVAILABLE:
            try:
                self.lstm_model = keras.models.load_model(self.config.lstm_model_path)
            except Exception as e:
                print(f"Warning: Could not load LSTM model: {e}")
        
        self.is_loaded = True
    
    def predict_cnn(
        self,
        spike_data: np.ndarray  # [batch, time, electrodes]
    ) -> np.ndarray:
        """
        Predict using CNN-1D model.
        
        Args:
            spike_data: Raw bioelectrical spike data
            
        Returns:
            CNN predictions
        """
        if self.cnn_model is None:
            # Return dummy prediction if model not loaded
            return np.full(len(spike_data), 0.5)
        
        # Ensure correct shape
        if len(spike_data.shape) == 2:
            spike_data = spike_data.reshape(1, *spike_data.shape)
        
        return self.cnn_model.predict(spike_data, batch_size=self.config.batch_size)
    
    def predict_xgboost(
        self,
        parameters: np.ndarray  # [batch, 8] - 8 MNIS parameters
    ) -> np.ndarray:
        """
        Predict using XGBoost model.
        
        Args:
            parameters: Tabular parameter values
            
        Returns:
            XGBoost predictions
        """
        if self.xgb_model is None:
            return np.full(len(parameters), 0.5)
        
        if len(parameters.shape) == 1:
            parameters = parameters.reshape(1, -1)
        
        dmatrix = xgb.DMatrix(parameters)
        return self.xgb_model.predict(dmatrix)
    
    def predict_lstm(
        self,
        history: np.ndarray  # [batch, time_steps, features]
    ) -> np.ndarray:
        """
        Predict using LSTM model.
        
        Args:
            history: Time series history
            
        Returns:
            LSTM predictions
        """
        if self.lstm_model is None:
            return np.full(len(history), 0.5)
        
        if len(history.shape) == 2:
            history = history.reshape(1, *history.shape)
        
        return self.lstm_model.predict(history, batch_size=self.config.batch_size)
    
    def predict(
        self,
        spike_data: Optional[np.ndarray] = None,
        parameters: Optional[np.ndarray] = None,
        history: Optional[np.ndarray] = None
    ) -> EnsembleResult:
        """
        Make ensemble prediction.
        
        Args:
            spike_data: Raw bioelectrical data for CNN
            parameters: 8 parameter values for XGBoost
            history: Time series history for LSTM
        
        Returns:
            EnsembleResult with predictions
        """
        self.load_models()
        
        predictions = []
        weights = []
        
        # CNN prediction
        if spike_data is not None:
            cnn_pred = self.predict_cnn(spike_data)[0]
            predictions.append(cnn_pred)
            weights.append(self.config.cnn_weight)
        else:
            cnn_pred = 0.0
        
        # XGBoost prediction
        if parameters is not None:
            xgb_pred = self.predict_xgboost(parameters)[0]
            predictions.append(xgb_pred)
            weights.append(self.config.xgb_weight)
        else:
            xgb_pred = 0.0
        
        # LSTM prediction
        if history is not None:
            lstm_pred = self.predict_lstm(history)[0]
            predictions.append(lstm_pred)
            weights.append(self.config.lstm_weight)
        else:
            lstm_pred = 0.0
        
        # Weighted ensemble
        if predictions:
            total_weight = sum(weights)
            if total_weight > 0:
                ensemble_pred = sum(p * w for p, w in zip(predictions, weights)) / total_weight
            else:
                ensemble_pred = 0.5
            
            # Calculate confidence (agreement between models)
            if len(predictions) > 1:
                confidence = 1.0 - np.std(predictions)
            else:
                confidence = 0.7
        else:
            ensemble_pred = 0.5
            confidence = 0.0
        
        # Feature importance (simplified)
        feature_importance = {
            'cnn': self.config.cnn_weight,
            'xgboost': self.config.xgb_weight,
            'lstm': self.config.lstm_weight,
        }
        
        # Generate warnings
        warnings = []
        if confidence < 0.5:
            warnings.append("Low model agreement - prediction may be unreliable")
        
        if ensemble_pred < 0.25:
            warnings.append("Ensemble predicts EXCELLENT network state")
        elif ensemble_pred > 0.8:
            warnings.append("Ensemble predicts COLLAPSE risk")
        
        return EnsembleResult(
            mnis_prediction=float(ensemble_pred),
            cnn_prediction=float(cnn_pred),
            xgb_prediction=float(xgb_pred),
            lstm_prediction=float(lstm_pred),
            confidence=float(confidence),
            feature_importance=feature_importance,
            warnings=warnings
        )
    
    def save(self, path: Union[str, Path]):
        """Save ensemble configuration."""
        path = Path(path)
        path.mkdir(exist_ok=True)
        
        # Save config
        with open(path / 'config.json', 'w') as f:
            json.dump({
                'cnn_weight': self.config.cnn_weight,
                'xgb_weight': self.config.xgb_weight,
                'lstm_weight': self.config.lstm_weight,
                'batch_size': self.config.batch_size,
                'threshold': self.config.threshold,
            }, f, indent=2)
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> 'AIEnsemble':
        """Load ensemble configuration."""
        path = Path(path)
        
        with open(path / 'config.json', 'r') as f:
            config_dict = json.load(f)
        
        config = EnsembleConfig(
            cnn_weight=config_dict['cnn_weight'],
            xgb_weight=config_dict['xgb_weight'],
            lstm_weight=config_dict['lstm_weight'],
            batch_size=config_dict['batch_size'],
            threshold=config_dict['threshold'],
            cnn_model_path=str(path / 'cnn_model.h5'),
            xgb_model_path=str(path / 'xgb_model.json'),
            lstm_model_path=str(path / 'lstm_model.h5'),
        )
        
        ensemble = cls(config)
        ensemble.load_models()
        
        return ensemble
    
    @staticmethod
    def demo_prediction() -> EnsembleResult:
        """Generate a demo prediction for testing."""
        # Create dummy data
        spike_data = np.random.randn(1000, 16)  # 1000 time points, 16 electrodes
        parameters = np.random.uniform(0.3, 0.8, 8)  # 8 parameters
        history = np.random.randn(50, 8)  # 50 time steps, 8 features
        
        ensemble = AIEnsemble()
        return ensemble.predict(spike_data, parameters, history)
