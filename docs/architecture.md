# SignalWeave Architecture

SignalWeave is organized as a streaming observability platform with a domain-agnostic tick event schema.

## Backend flow

1. Synthetic or external tick data enters the ingestion layer.
2. Events are validated and normalized into the unified JSON schema.
3. Sliding windows maintain rolling feature state.
4. Rule-based, statistical, and ML detectors score the event.
5. Aggregation converts detector output into a final anomaly decision.
6. WebSocket consumers receive the live decision stream.

## Frontend flow

1. The dashboard connects to the WebSocket stream.
2. Metrics are refreshed from REST health endpoints.
3. The live feed, anomaly alert list, and trend chart update in place.
