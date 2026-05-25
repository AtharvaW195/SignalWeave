"""
Rule-based detectors: simple, explainable checks.
Design notes:
- Rules are deterministic and return both boolean and human-friendly reason strings.
- Keep thresholds in `core.config` so they can be tuned without code changes.
"""
from typing import Dict, Tuple
from ..core import config


def price_spike_rule(tick: Dict, window_features: Dict) -> Tuple[bool, str]:
    # Detect immediate spike vs recent mean
    if window_features.get('price_mean'):
        pct = abs(tick['price'] - window_features['price_mean'])/window_features['price_mean']
        if pct >= config.PRICE_SPIKE_PCT:
            reason = f"price spike: {pct:.3f} >= {config.PRICE_SPIKE_PCT}"
            return True, reason
    return False, ""


def spread_widen_rule(tick: Dict, window_features: Dict) -> Tuple[bool, str]:
    baseline = window_features.get('spread_mean', 0.0)
    curr = tick.get('bid_ask_spread', 0.0)
    if baseline > 0 and curr > baseline * (1 + config.SPREAD_WIDEN_PCT):
        reason = f"spread widened: {curr:.4f} > {baseline:.4f} * (1+{config.SPREAD_WIDEN_PCT})"
        return True, reason
    return False, ""


def volume_jump_rule(tick: Dict, window_features: Dict) -> Tuple[bool, str]:
    vol_mean = window_features.get('volume_mean', 0.0)
    if vol_mean > 0 and tick['volume'] >= vol_mean * config.VOLUME_SPIKE_MULTIPLIER:
        reason = f"volume jump: {tick['volume']} >= {vol_mean:.1f} * {config.VOLUME_SPIKE_MULTIPLIER}"
        return True, reason
    return False, ""


def run_rules(tick: Dict, window_features: Dict) -> Dict:
    results = {}
    r, reason = price_spike_rule(tick, window_features)
    results['price_spike'] = {'is_anomaly': r, 'reason': reason}
    r, reason = spread_widen_rule(tick, window_features)
    results['spread_widen'] = {'is_anomaly': r, 'reason': reason}
    r, reason = volume_jump_rule(tick, window_features)
    results['volume_jump'] = {'is_anomaly': r, 'reason': reason}
    return results
