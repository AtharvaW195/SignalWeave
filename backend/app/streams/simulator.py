"""
Simple simulated market tick generator.
Design decisions:
- Deterministic seed for reproducibility in tests and model training.
- Provides price, volume, bid_ask_spread and timestamp, matching the required tick schema.
- Includes occasional synthetic anomalies (spikes) to bootstrap detector development.
- Keeps generator simple; later adapters can swap in a real market API.
"""
import asyncio
import random
import time
from typing import AsyncGenerator, List, Dict
from ..core.config import SIM_SEED, SYMBOLS

random.seed(SIM_SEED)

async def stream_ticks(symbols: List[str] = SYMBOLS, interval: float = 0.9) -> AsyncGenerator[Dict, None]:
    baselines = {s: 100.0 + random.random() * 200.0 for s in symbols}
    while True:
        for s in symbols:
            # small random walk around baseline
            noise = random.normalvariate(0, 0.002)  # 0.2% typical noise
            price = max(0.01, baselines[s] * (1 + noise))
            # occasional synthetic spike to help model training and demos
            if random.random() < 0.002:
                # spike either up or down
                direction = 1 if random.random() < 0.6 else -1
                multiplier = 1 + direction * random.uniform(0.05, 0.2)
                price *= multiplier
            volume = max(1, int(random.expovariate(1/200) + random.randint(1, 800)))
            bid_ask_spread = round(abs(random.normalvariate(0.02, 0.01)), 4)
            tick = {
                "timestamp": int(time.time()),
                "symbol": s,
                "price": round(price, 4),
                "volume": volume,
                "bid_ask_spread": bid_ask_spread,
                "source": "simulated"
            }
            yield tick
            # Pause after every emitted tick so the dashboard can visibly follow the tape.
            await asyncio.sleep(interval)

# utility to run standalone for quick checks
if __name__ == "__main__":
    import asyncio
    async def main():
        async for t in stream_ticks(["AAPL", "MSFT"], 0.1):
            print(t)
            await asyncio.sleep(0.05)
    asyncio.run(main())
