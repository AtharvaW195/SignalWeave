"""
Async Postgres helper using asyncpg.
Responsibilities:
- manage connection pool
- initialize DB schema on startup (idempotent)
- provide helpers to insert ticks and anomalies

Design notes:
- Keep SQL simple and idempotent (CREATE TABLE IF NOT EXISTS) for easy dev flow.
"""
import asyncio
import json
import asyncpg
from typing import Optional, Dict, Any
from ..core import config

pool: Optional[asyncpg.pool.Pool] = None

async def connect_pool():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(dsn=config.DB_DSN, min_size=1, max_size=4)
    return pool

async def close_pool():
    global pool
    if pool is not None:
        await pool.close()
        pool = None

async def init_db():
    """Create tables if they don't exist."""
    p = await connect_pool()
    async with p.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ticks (
                id SERIAL PRIMARY KEY,
                ts TIMESTAMP WITH TIME ZONE NOT NULL,
                symbol TEXT NOT NULL,
                price DOUBLE PRECISION NOT NULL,
                volume BIGINT NOT NULL,
                bid_ask_spread DOUBLE PRECISION,
                source TEXT,
                raw JSONB
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS anomalies (
                id SERIAL PRIMARY KEY,
                tick_id INTEGER REFERENCES ticks(id) ON DELETE SET NULL,
                detected_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                detector TEXT,
                score DOUBLE PRECISION,
                severity TEXT,
                reason TEXT,
                payload JSONB
            )
            """
        )

async def insert_tick(tick: Dict[str, Any]) -> int:
    p = await connect_pool()
    async with p.acquire() as conn:
        # convert epoch to timestamp using to_timestamp in SQL
        res = await conn.fetchrow(
            """
            INSERT INTO ticks (ts, symbol, price, volume, bid_ask_spread, source, raw)
            VALUES (to_timestamp($1), $2, $3, $4, $5, $6, $7)
            RETURNING id
            """,
            tick.get('timestamp', None),
            tick.get('symbol'),
            tick.get('price'),
            tick.get('volume'),
            tick.get('bid_ask_spread'),
            tick.get('source'),
            json.dumps(tick),
        )
        return int(res['id'])

async def insert_anomaly(tick_id: Optional[int], detector: str, score: Optional[float], severity: str, reason: str, payload: Dict[str, Any]):
    p = await connect_pool()
    async with p.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO anomalies (tick_id, detector, score, severity, reason, payload)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            tick_id,
            detector,
            score,
            severity,
            reason,
            json.dumps(payload),
        )

async def fetch_recent_ticks(limit: int = 100):
    p = await connect_pool()
    async with p.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, extract(epoch from ts) as ts_epoch, symbol, price, volume, bid_ask_spread, source, raw FROM ticks ORDER BY id DESC LIMIT $1",
            limit,
        )
        return [dict(r) for r in rows]

async def fetch_recent_anomalies(limit: int = 100):
    p = await connect_pool()
    async with p.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, tick_id, detected_at, detector, score, severity, reason, payload FROM anomalies ORDER BY id DESC LIMIT $1",
            limit,
        )
        return [dict(r) for r in rows]
