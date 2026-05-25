"""
Simple ML trainer for IsolationForest using synthetic windows.
Design:
- Use features computed from `pipeline.processor.features_from_window`.
- Train on 'normal' simulated windows and persist a model for real-time inference.
- Keep this lightweight so it can run locally during development.
"""
import joblib
from sklearn.ensemble import IsolationForest
import numpy as np

MODEL_PATH = "backend/artifacts/fintech_isolation_forest.joblib"


def train_dummy(X: np.ndarray):
    model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
    model.fit(X)
    joblib.dump(model, MODEL_PATH)
    return MODEL_PATH

if __name__ == "__main__":
    # Placeholder: in practice, assemble X from many windows
    X = np.random.normal(size=(1000, 6))
    print("Training dummy model...")
    path = train_dummy(X)
    print("Saved model to", path)
