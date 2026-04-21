# NEXUS — AI Trading Agent

Autonomous paper-trading AI agent with adaptive dual-mode strategy, Claude-powered sentiment scoring, and a real-time Next.js analytics dashboard.

## Architecture

```
Next.js Dashboard (Vercel) ←──── REST poll / WebSocket
         ↕
FastAPI Bridge (local + ngrok static domain)
         ↕ SQLite WAL
Python Agent Core (asyncio + supervisord)
    ↕ subprocess                ↕ HTTPS
Kraken CLI (paper mode)    Claude API (sentiment)
```

## Stack

| Layer | Technology |
|---|---|
| Dashboard | Next.js 14, Recharts, Tailwind, TypeScript |
| API Bridge | FastAPI, uvicorn, Pydantic v2 |
| Agent Core | Python 3.11, asyncio, pandas-ta, anthropic SDK |
| Storage | SQLite (WAL mode) |
| Process mgmt | supervisord |
| Tunnel | ngrok static domain (free) |

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install dashboard dependencies

```bash
cd dashboard && npm install
```

### 3. Set environment variables

Create `.env` in the repo root (gitignored):
```
ANTHROPIC_API_KEY=your_key_here
TELEGRAM_BOT_TOKEN=your_bot_token   # optional
TELEGRAM_CHAT_ID=your_chat_id       # optional
```

Create `dashboard/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For Vercel deployment, set `NEXT_PUBLIC_API_URL` to your ngrok static domain.

### 4. Set up ngrok static domain

1. Create a free ngrok account at ngrok.com
2. Claim your free static domain (one per account)
3. Add `NGROK_AUTHTOKEN` and `NGROK_DOMAIN` to your shell environment

### 5. Run everything locally

```bash
./scripts/start.sh
```

This starts supervisord (agent + FastAPI) and the ngrok tunnel.

### 6. Run tests

```bash
pytest -v
```

Expected: 108 tests pass.

## Dashboard

Run the dashboard locally against the FastAPI bridge:

```bash
cd dashboard && npm run dev
```

Visit `http://localhost:3000`.

## Deploy Dashboard to Vercel

1. Push this repo to GitHub
2. Import the repo on vercel.com
3. Set `NEXT_PUBLIC_API_URL` to your ngrok static domain in Vercel env vars
4. Deploy

The `vercel.json` file configures Vercel to build from the `dashboard/` subdirectory.
