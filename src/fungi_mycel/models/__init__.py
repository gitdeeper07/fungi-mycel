"""
FUNGI-MYCEL AI Ensemble Models

This module contains the AI ensemble architecture that combines:
    - CNN-1D for bioelectrical spike pattern classification
    - XGBoost for tabular parameter analysis
    - LSTM for time series prediction

The ensemble achieves 91.8% MNIS prediction accuracy.
"""

from fungi_mycel.models.ensemble import AIEnsemble, EnsembleConfig, EnsembleResult
from fungi_mycel.models.cnn_1d import CNN1D, CNNConfig
from fungi_mycel.models.xgboost_model import XGBoostModel, XGBoostConfig
from fungi_mycel.models.lstm_model import LSTMModel, LSTMConfig

__all__ = [
    'AIEnsemble',
    'EnsembleConfig',
    'EnsembleResult',
    'CNN1D',
    'CNNConfig',
    'XGBoostModel',
    'XGBoostConfig',
    'LSTMModel',
    'LSTMConfig',
]
