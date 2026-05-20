# API Reference

## GET /api/health

Returns platform health and current mode metrics.

## GET /api/modes

Returns the supported simulation modes.

## GET /api/history/{mode}

Returns recent decisions for a given mode.

## POST /api/analyze

Submits a single tick event for analysis.

## WS /ws/stream/{mode}

Streams live anomaly decisions for the selected mode.
