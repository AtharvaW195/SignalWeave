"""
Statistical detectors: z-score and volatility-based checks.
Design notes:
- Complement rules with probabilistic signals.
- Return scores and boolean flags.
"""
from typing import Dict, Tuple


def zscore_detector(tick: Dict, features: Dict, threshold: float = 3.0) -> Dict:
    z = features.get('z_score', 0.0)
    is_anom = abs(z) >= threshold
    return {'z_score': z, 'is_anomaly': is_anom, 'reason': f'z_score {z:.2f} against threshold {threshold}'}


def volatility_detector(tick: Dict, features: Dict, mult: float = 2.5) -> Dict:
    vol = features.get('volatility', 0.0)
    # compare last price delta magnitude to volatility
    delta = abs(features.get('price_delta', 0.0))
    is_anom = delta >= vol * mult if vol else False
    return {'volatility': vol, 'price_delta': delta, 'is_anomaly': is_anom, 'reason': f'delta {delta:.4f} vs vol*{mult}'}
