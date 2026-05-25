import pytest
from backend.app.detectors import rules, statistical

def test_price_spike_rule():
    tick = {'price': 110}
    window = {'price_mean': 100}
    is_anom, reason = rules.price_spike_rule(tick, window)
    assert is_anom

def test_spread_and_volume_rules():
    tick = {'price':100, 'volume':1000, 'bid_ask_spread':0.5}
    window = {'volume_mean':100, 'spread_mean':0.1}
    r1 = rules.spread_widen_rule(tick, window)
    r2 = rules.volume_jump_rule(tick, window)
    assert r1[0]
    assert r2[0]

def test_statistical_detectors():
    tick = {'price':105}
    features = {'z_score': 4.0, 'volatility': 0.5, 'price_delta': 3.0}
    z = statistical.zscore_detector(tick, features, threshold=3.0)
    v = statistical.volatility_detector(tick, features, mult=2.0)
    assert z['is_anomaly']
    assert not v['is_anomaly'] or isinstance(v['reason'], str)
