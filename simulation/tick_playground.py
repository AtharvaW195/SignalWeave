from __future__ import annotations

import argparse
import json
import sys

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.schemas import SourceType
from app.streams.simulator import TickStreamSimulator


async def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic SignalWeave ticks")
    parser.add_argument("--mode", choices=[mode.value for mode in SourceType], default="fintech")
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("ticks.jsonl"))
    args = parser.parse_args()

    simulator = TickStreamSimulator()
    mode = SourceType(args.mode)
    records = []
    async for tick in simulator.stream(mode):
        records.append(tick.model_dump())
        if len(records) >= args.count:
            break
    with args.output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
