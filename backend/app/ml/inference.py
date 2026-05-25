"""
Real-time inference loader and predictor for IsolationForest and LSTM Autoencoder.
Design:
- Load serialized IsolationForest (joblib) and a Keras LSTM autoencoder.
- Provide `predict` method that accepts a window (list of ticks) and returns anomaly scores.
"""
import os
import json
import numpy as np
from typing import Dict, Any, Optional

try:
    import joblib
    from tensorflow import keras
except Exception:
    joblib = None
    keras = None

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts")
IF_MODEL_PATH = os.path.join(MODEL_DIR, "fintech_isolation_forest.joblib")
LSTM_MODEL_PATH = os.path.join(MODEL_DIR, "fintech_lstm_ae.h5")

if_model = None
lstm_model = None

# feature selection for ML: price, volume, spread, price_delta
FEATURE_KEYS = ['price', 'volume', 'bid_ask_spread']


def load_models():
    global if_model, lstm_model
    if joblib and os.path.exists(IF_MODEL_PATH):
        try:
            if_model = joblib.load(IF_MODEL_PATH)
        except Exception as e:
            print('Failed to load IF model:', e)
            if_model = None
    else:
        print('IF model not found at', IF_MODEL_PATH)
    if keras and os.path.exists(LSTM_MODEL_PATH):
        try:
            lstm_model = keras.models.load_model(LSTM_MODEL_PATH)
        except Exception as e:
            print('Failed to load LSTM model:', e)
            lstm_model = None
    else:
        print('LSTM model not found at', LSTM_MODEL_PATH)


def _window_to_feature_array(window: list) -> np.ndarray:
    # Convert ticks window to a 2D array (timesteps x features)
    arr = []
    for t in window:
        row = [t.get('price', 0.0), float(t.get('volume', 0.0)), float(t.get('bid_ask_spread', 0.0))]
        arr.append(row)
    return np.array(arr)


def predict(window: list) -> Dict[str, Any]:
    """Return combined anomaly scores and per-model outputs."""
    out = {'if_score': None, 'if_is_anomaly': False, 'lstm_score': None, 'lstm_is_anomaly': False, 'anomaly_score': 0.0}
    arr = _window_to_feature_array(window)
    # ML: IsolationForest uses flattened features (e.g., last row or aggregated features). We'll use simple aggregated features.
    try:
        if if_model is not None:
            # use last row aggregated
            feat = np.nanmean(arr, axis=0).reshape(1, -1)
            # score_samples: higher is less abnormal, so invert
            score = if_model.score_samples(feat)[0]
            # convert to positive anomaly score between 0-1
            if_score = float(-score)
            out['if_score'] = if_score
            out['if_is_anomaly'] = if_score > 0.5
    except Exception as e:
        print('IF predict error', e)
    try:
        if lstm_model is not None:
            # LSTM expects shape (1, timesteps, features)
            seq = arr.reshape(1, arr.shape[0], arr.shape[1])
            recon = lstm_model.predict(seq, verbose=0)
            # compute mse
            mse = float(((seq - recon) ** 2).mean())
            out['lstm_score'] = mse
            out['lstm_is_anomaly'] = mse > 1e-2
    except Exception as e:
        print('LSTM predict error', e)
    # combine scores heuristically
    scores = []
    if out['if_score'] is not None:
        scores.append(min(1.0, out['if_score']))
    if out['lstm_score'] is not None:
        # normalize mse (this is heuristic)
        lstm_norm = min(1.0, out['lstm_score']*100.0)
        scores.append(lstm_norm)
    if scores:
        out['anomaly_score'] = sum(scores)/len(scores)
    return out

# Auto-load when module imported
load_models()
