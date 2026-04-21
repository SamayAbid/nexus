# NEXUS — AI Trading Agent

Autonomous paper-trading agent with adaptive dual-mode strategy, Claude-powered sentiment scoring, and a real-time Next.js analytics dashboard.

## Stack
- Python 3.11 + asyncio (agent core)
- FastAPI + uvicorn (API bridge)
- Next.js 14 + Recharts + Tailwind (dashboard)
- Kraken CLI — paper trading mode
- Claude API — sentiment scoring
- SQLite (WAL mode) — trade log

## Setup
```bash
pip install -r requirements.txt
```

## Run
```bash
./scripts/start.sh
```
