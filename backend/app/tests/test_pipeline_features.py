import pytest
from backend.app.pipeline.processor import rolling_mean, rolling_std, ema, rsi, features_from_window

def test_rolling_mean_std():
    vals = [1,2,3,4,5]
    assert abs(rolling_mean(vals) - 3.0) < 1e-6
    assert rolling_std(vals) > 0

def test_ema_rsi():
    vals = [1,2,3,4,5,6,7,8,9,10]
    assert ema(vals, period=5) != 0
    assert 0 <= rsi(vals, period=5) <= 100

def test_features_from_window():
    # build synthetic ticks
    ticks = [{'price':100+i, 'volume':100+i*10, 'bid_ask_spread':0.02} for i in range(10)]
    f = features_from_window(ticks)
    assert 'price_mean' in f
    assert 'z_score' in f
