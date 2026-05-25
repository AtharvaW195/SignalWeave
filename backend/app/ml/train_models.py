"""
Train IsolationForest and LSTM Autoencoder on synthetic windows collected from simulator.
Design notes:
- Collect windows by running the simulator for a short period and assembling feature windows using pipeline.processor features.
- Train IsolationForest on aggregated features; train LSTM AE on raw sequences of [price, volume, spread].
- Save models to backend/artifacts/.
"""
import os
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

try:
    from tensorflow import keras
    from tensorflow.keras import layers
except Exception:
    keras = None

from ..streams.simulator import stream_ticks
from ..pipeline.window import StreamWindow
from ..pipeline.processor import features_from_window

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'artifacts')
os.makedirs(ARTIFACTS_DIR, exist_ok=True)
IF_PATH = os.path.join(ARTIFACTS_DIR, 'fintech_isolation_forest.joblib')
LSTM_PATH = os.path.join(ARTIFACTS_DIR, 'fintech_lstm_ae.h5')

async def collect_windows(symbols, duration_seconds=10, interval=0.1, window_size=32):
    import asyncio, time
    sw = StreamWindow(size=window_size)
    start = time.time()
    windows = []
    async for tick in stream_ticks(symbols, interval=interval):
        sw.append(tick)
        w = sw.get(tick['symbol'])
        if len(w) >= 8:
            windows.append(list(w))
        if time.time()-start > duration_seconds:
            break
    return windows

def aggregate_feature_vector(windows):
    # For IF, compute aggregated features: mean price, std price, mean vol, mean spread, momentum
    X = []
    for w in windows:
        feats = features_from_window(w)
        vec = [feats.get('price_mean',0.0), feats.get('price_std',0.0), feats.get('volume_mean',0.0), feats.get('volume_spike_ratio',0.0), feats.get('momentum',0.0)]
        X.append(vec)
    return np.array(X)

async def train_all(symbols=['AAPL','TSLA','NVDA','MSFT','SPY']):
    import asyncio
    print('Collecting windows...')
    windows = await collect_windows(symbols, duration_seconds=12, interval=0.05, window_size=32)
    print('Collected', len(windows), 'windows')
    X = aggregate_feature_vector(windows)
    # Train IF
    print('Training IsolationForest...')
    if_model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
    if_model.fit(X)
    joblib.dump(if_model, IF_PATH)
    print('Saved IF model to', IF_PATH)
    # Train LSTM AE
    if keras is None:
        print('Keras not available; skipping LSTM train')
        return
    print('Preparing LSTM data...')
    # Prepare sequences: pad/truncate to fixed timesteps
    timesteps = 32
    feat_seqs = []
    for w in windows:
        arr = np.array([[t['price'], float(t['volume']), float(t.get('bid_ask_spread',0.0))] for t in w])
        if arr.shape[0] >= timesteps:
            seq = arr[-timesteps:]
        else:
            # pad with first row
            pad = np.repeat(arr[0:1], timesteps - arr.shape[0], axis=0)
            seq = np.vstack([pad, arr])
        feat_seqs.append(seq)
    X_seq = np.stack(feat_seqs)
    X_seq = X_seq.astype('float32')
    # normalize per feature
    mean = X_seq.mean(axis=(0,1), keepdims=True)
    std = X_seq.std(axis=(0,1), keepdims=True) + 1e-6
    Xn = (X_seq - mean)/std
    print('Training LSTM autoencoder...')
    # small LSTM AE
    inputs = keras.Input(shape=(timesteps, 3))
    encoded = layers.LSTM(64, return_sequences=False)(inputs)
    repeated = layers.RepeatVector(timesteps)(encoded)
    decoded = layers.LSTM(64, return_sequences=True)(repeated)
    outputs = layers.TimeDistributed(layers.Dense(3))(decoded)
    model = keras.Model(inputs, outputs)
    model.compile(optimizer='adam', loss='mse')
    model.fit(Xn, Xn, epochs=10, batch_size=32, validation_split=0.1, verbose=1)
    # Save model and normalization stats
    model.save(LSTM_PATH)
    np.save(os.path.join(ARTIFACTS_DIR, 'lstm_mean.npy'), mean)
    np.save(os.path.join(ARTIFACTS_DIR, 'lstm_std.npy'), std)
    print('Saved LSTM model to', LSTM_PATH)

if __name__ == '__main__':
    import asyncio
    asyncio.run(train_all())
