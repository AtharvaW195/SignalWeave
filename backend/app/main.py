"""
FastAPI entrypoint wiring simulator, processing pipeline hooks, and WebSocket broadcast.
Design notes:
- For MVP we keep processing in-memory and synchronous with the tick stream; later move to background workers/Redis.
- WebSocket endpoint streams ticks plus attached feature/detector data as JSON messages.
"""
import asyncio
import json
import io
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import StreamingResponse, JSONResponse
from .core.config import SYMBOLS, TICK_INTERVAL, WINDOW_SIZE
from .streams import simulator
from .pipeline.window import StreamWindow
from .pipeline.processor import features_from_window
from .detectors import rules, statistical
from .db import pg as db_pg
from .ml import inference as ml_inference

app = FastAPI(title="SignalWeave (Simulated Fintech MVP)")

window_store = StreamWindow(size=WINDOW_SIZE)


@app.on_event("startup")
async def on_startup():
    # initialize DB pool and schema
    try:
        await db_pg.connect_pool()
        await db_pg.init_db()
    except Exception as e:
        # log and continue; DB may be optional in dev
        print("DB init error:", e)
    # load ML models (best-effort)
    try:
        ml_inference.load_models()
    except Exception as e:
        print('ML load error', e)


@app.on_event("shutdown")
async def on_shutdown():
    await db_pg.close_pool()

@app.get("/health")
async def health():
    return {"status": "ok", "mode": "simulated", "symbols": SYMBOLS}


@app.get("/api/health")
async def api_health():
    # Alias for browser/demo tooling that expects routes under /api.
    return {"status": "ok", "mode": "simulated", "symbols": SYMBOLS}

@app.websocket("/ws/ticks")
async def websocket_ticks(ws: WebSocket):
    await ws.accept()
    try:
        async for tick in simulator.stream_ticks(SYMBOLS, interval=TICK_INTERVAL):
            # update window
            window_store.append(tick)
            feats = features_from_window(window_store.get(tick['symbol']))
            rule_results = rules.run_rules(tick, feats)
            stat_z = statistical.zscore_detector(tick, feats)
            stat_vol = statistical.volatility_detector(tick, feats)
            payload = {
                'tick': tick,
                'features': feats,
                'rules': rule_results,
                'stat': {'zscore': stat_z, 'volatility': stat_vol}
            }
            # persist tick and any detected anomalies (best-effort)
            try:
                tick_id = await db_pg.insert_tick(tick)
            except Exception:
                tick_id = None

            # check rule-based anomalies
            try:
                # rules
                for name, r in rule_results.items():
                    if r.get('is_anomaly'):
                        severity = 'HIGH'
                        await db_pg.insert_anomaly(tick_id, f'rule:{name}', None, severity, r.get('reason',''), {'features': feats, 'rule': name})
                # statistical
                if stat_z.get('is_anomaly'):
                    sev = 'HIGH' if abs(stat_z.get('z_score', 0)) >= 4.0 else 'MEDIUM'
                    await db_pg.insert_anomaly(tick_id, 'stat:zscore', stat_z.get('z_score'), sev, stat_z.get('reason',''), {'features': feats})
                if stat_vol.get('is_anomaly'):
                    await db_pg.insert_anomaly(tick_id, 'stat:volatility', stat_vol.get('price_delta'), 'MEDIUM', stat_vol.get('reason',''), {'features': feats})
            except Exception as e:
                # don't fail streaming on DB errors
                print('DB insert anomaly error', e)

            # ML inference (best-effort)
            try:
                # get recent window for this symbol
                window = window_store.get(tick['symbol'])
                ml_out = ml_inference.predict(window)
                payload['ml'] = ml_out
                # persist ml anomaly if high
                if ml_out.get('anomaly_score', 0.0) >= 0.7:
                    await db_pg.insert_anomaly(tick_id, 'ml:ensemble', ml_out.get('anomaly_score'), 'HIGH', 'ml ensemble score high', {'ml': ml_out})
            except Exception as e:
                print('ML infer error', e)

            await ws.send_text(json.dumps(payload))
    except WebSocketDisconnect:
        return


@app.get('/api/recent_ticks')
async def recent_ticks(limit: int = Query(100, le=1000)):
    rows = await db_pg.fetch_recent_ticks(limit=limit)
    return JSONResponse(rows)


@app.get('/api/export/ticks.csv')
async def export_ticks_csv(limit: int = Query(1000, le=10000)):
    rows = await db_pg.fetch_recent_ticks(limit=limit)
    buf = io.StringIO()
    # header
    buf.write('id,ts_epoch,symbol,price,volume,bid_ask_spread,source\n')
    for r in rows:
        buf.write(f"{r.get('id')},{r.get('ts_epoch')},{r.get('symbol')},{r.get('price')},{r.get('volume')},{r.get('bid_ask_spread')},{r.get('source')}\n")
    buf.seek(0)
    return StreamingResponse(buf, media_type='text/csv', headers={"Content-Disposition": "attachment; filename=ticks.csv"})


@app.get('/api/recent_anomalies')
async def recent_anomalies(limit: int = Query(100, le=1000)):
    rows = await db_pg.fetch_recent_anomalies(limit=limit)
    return JSONResponse(rows)


@app.get('/api/export/anomalies.csv')
async def export_anomalies_csv(limit: int = Query(1000, le=10000)):
    rows = await db_pg.fetch_recent_anomalies(limit=limit)
    buf = io.StringIO()
    buf.write('id,tick_id,detected_at,detector,score,severity,reason\n')
    for r in rows:
        buf.write(f"{r.get('id')},{r.get('tick_id')},{r.get('detected_at')},{r.get('detector')},{r.get('score')},{r.get('severity')},{(r.get('reason') or '').replace(',', ' ')}\n")
    buf.seek(0)
    return StreamingResponse(buf, media_type='text/csv', headers={"Content-Disposition": "attachment; filename=anomalies.csv"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
