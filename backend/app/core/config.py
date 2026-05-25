"""
Configuration and constants for SignalWeave backend.
Design notes:
- Keep configuration in one module so both simulator and processing pipeline use the same symbols and timings.
- Values read from environment variables to make the project ready for Docker/production.
"""
import os

SYMBOLS = os.getenv("SYMBOLS", "AAPL,TSLA,NVDA,MSFT,SPY").split(",")
# Slightly slower default so the dashboard is readable in demos.
TICK_INTERVAL = float(os.getenv("TICK_INTERVAL", "0.9"))  # seconds between emitted ticks
SIM_SEED = int(os.getenv("SIM_SEED", "42"))
WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", "64"))

# Rule thresholds (adjustable): chosen conservatively for simulated data
PRICE_SPIKE_PCT = float(os.getenv("PRICE_SPIKE_PCT", "0.05"))  # 5% price jump
VOLUME_SPIKE_MULTIPLIER = float(os.getenv("VOLUME_SPIKE_MULTIPLIER", "3.0"))
SPREAD_WIDEN_PCT = float(os.getenv("SPREAD_WIDEN_PCT", "0.5"))  # 50% wider than baseline

DB_DSN = os.getenv("DATABASE_DSN", "postgresql://postgres:password@db:5432/signalweave")
