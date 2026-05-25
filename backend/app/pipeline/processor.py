"""
Feature engineering for streaming ticks.
Design choices:
- Implement lightweight, fast computations suitable for real-time use.
- Provide functions for rolling avg/std, z-score, EMA, RSI, momentum, volatility, price delta, and volume spike ratio.
- Keep pure functions to ease unit testing.
"""
import math
from typing import List, Dict

def rolling_mean(values: List[float]) -> float:
    return sum(values)/len(values) if values else 0.0

def rolling_std(values: List[float]) -> float:
    if not values:
        return 0.0
    m = rolling_mean(values)
    var = sum((v-m)**2 for v in values)/len(values)
    return math.sqrt(var)

def ema(values: List[float], period: int = 10) -> float:
    if not values:
        return 0.0
    alpha = 2/(period+1)
    s = values[0]
    for v in values[1:]:
        s = alpha*v + (1-alpha)*s
    return s

def rsi(values: List[float], period: int = 14) -> float:
    if len(values) < 2:
        return 50.0
    gains = 0.0
    losses = 0.0
    for i in range(1, len(values)):
        delta = values[i] - values[i-1]
        if delta > 0:
            gains += delta
        else:
            losses -= delta
    avg_gain = gains/period if period else gains
    avg_loss = losses/period if period else losses
    if avg_loss == 0:
        return 100.0
    rs = avg_gain/avg_loss
    return 100 - (100/(1+rs))

def features_from_window(ticks: List[Dict]) -> Dict:
    prices = [t['price'] for t in ticks]
    volumes = [t['volume'] for t in ticks]
    spreads = [t.get('bid_ask_spread', 0.0) for t in ticks]
    f = {}
    f['count'] = len(ticks)
    f['price_mean'] = rolling_mean(prices) if prices else 0.0
    f['price_std'] = rolling_std(prices)
    f['price_ema_10'] = ema(prices, period=10)
    f['rsi_14'] = rsi(prices, period=14)
    f['volatility'] = f['price_std']
    f['momentum'] = prices[-1]-prices[0] if len(prices) >= 2 else 0.0
    f['price_delta'] = (prices[-1]-prices[-2]) if len(prices) >= 2 else 0.0
    f['volume_mean'] = rolling_mean(volumes) if volumes else 0.0
    f['volume_spike_ratio'] = (volumes[-1]/(f['volume_mean']+1e-6)) if volumes else 1.0
    f['spread_mean'] = rolling_mean(spreads) if spreads else 0.0
    f['z_score'] = (prices[-1]-f['price_mean'])/(f['price_std']+1e-6) if f['price_std'] else 0.0
    return f
