# NEXUS — AI Trading Agent

Autonomous paper-trading AI agent with adaptive dual-mode strategy, Azure OpenAI GPT-5 sentiment scoring, and a real-time Next.js analytics dashboard.

## Architecture

```
Next.js Dashboard (localhost:3000 / Vercel)
         ↕  REST poll + WebSocket
FastAPI Bridge (localhost:8000 / ngrok tunnel)
         ↕  SQLite WAL
Python Agent Core (asyncio + supervisord)
    ↕ subprocess                ↕ HTTPS
Kraken CLI (paper mode)    Azure OpenAI (sentiment)
```

## Stack

| Layer | Technology |
|---|---|
| Dashboard | Next.js 15, Recharts, Tailwind CSS, TypeScript |
| API Bridge | FastAPI, uvicorn, Pydantic v2 |
| Agent Core | Python 3.12, asyncio, pandas-ta |
| Sentiment | Azure OpenAI GPT-5 (`gpt-5-chat` deployment) |
| Storage | SQLite (WAL mode) |
| Process mgmt | supervisord |
| Tunnel | ngrok static domain |

---

## Prerequisites

- Python 3.12+
- Node.js 18+
- An Azure OpenAI resource with the `gpt-5-chat` deployment

---

## Setup

### 1. Clone and install Python dependencies

```bash
git clone https://github.com/SamayAbid/nexus.git
cd nexus
pip install -r requirements.txt
```

### 2. Install dashboard dependencies

```bash
cd dashboard
npm install
cd ..
```

### 3. Configure environment variables

**Agent env — create `.env` in the repo root (already gitignored):**

```
AZURE_OPENAI_API_KEY=your_azure_openai_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com
TELEGRAM_BOT_TOKEN=your_bot_token   # optional — for trade alerts
TELEGRAM_CHAT_ID=your_chat_id       # optional — for trade alerts
```

> The Azure endpoint and deployment name (`gpt-5-chat`) are already configured in `agent/sentiment.py`. You only need to set the API key and optionally override the endpoint.

**Dashboard env — create `dashboard/.env.local`:**

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For Vercel deployment, set this to your ngrok static domain instead.

### 4. Initialize the database

Run once before starting the agent for the first time:

```bash
python -c "from agent.database import init_db; init_db(); print('DB ready')"
```

---

## Running Locally

Open **three separate terminals** from the repo root:

**Terminal 1 — FastAPI bridge:**

```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 — Trading agent:**

```bash
python -m agent.main
```

**Terminal 3 — Next.js dashboard:**

```bash
cd dashboard
npm run dev
```

Then open `http://localhost:3000` in your browser.

> Once the agent starts, the dashboard will show live regime, signals, positions, and trade history. Allow ~30 seconds for the first data cycle.

---

## Running with supervisord (Linux / WSL)

supervisord manages the API and agent as background processes with auto-restart:

```bash
./scripts/start.sh
```

This starts supervisord (agent + FastAPI) and an ngrok tunnel. Logs are written to `logs/`.

---

## Running Tests

```bash
pytest -v
```

Expected: **108 tests pass**.

---

## ngrok Tunnel (for remote dashboard access)

1. Create a free account at [ngrok.com](https://ngrok.com)
2. Claim your free static domain
3. Add to your shell environment:
   ```
   NGROK_AUTHTOKEN=your_token
   NGROK_DOMAIN=your-subdomain.ngrok-free.app
   ```
4. Update `dashboard/.env.local`:
   ```
   NEXT_PUBLIC_API_URL=https://your-subdomain.ngrok-free.app
   ```

---

## Deploy Dashboard to Vercel

1. Push this repo to GitHub
2. Import the repo on [vercel.com](https://vercel.com)
3. Set `NEXT_PUBLIC_API_URL` to your ngrok static domain in Vercel environment variables
4. Deploy

The `vercel.json` file configures Vercel to build from the `dashboard/` subdirectory.

---

## Project Structure

```
nexus/
├── agent/              # Python trading agent
│   ├── main.py         # Entry point, main loop
│   ├── pipeline.py     # Per-cycle orchestration
│   ├── signals.py      # Technical indicators
│   ├── regime.py       # Bull/bear regime detection
│   ├── strategy.py     # Trade decision logic
│   ├── risk.py         # Position sizing & circuit breakers
│   ├── execution.py    # Order execution (Kraken paper)
│   ├── sentiment.py    # Azure OpenAI news sentiment
│   ├── social.py       # Telegram alerts
│   └── database.py     # SQLite read/write
├── api/                # FastAPI bridge
│   ├── main.py         # App setup, CORS, WebSocket
│   ├── routes.py       # REST endpoints
│   └── db.py           # DB query helpers
├── dashboard/          # Next.js frontend
│   ├── app/            # App Router pages & layout
│   ├── components/     # Sidebar, TopBar, view components
│   └── lib/            # API client, hooks, types
├── tests/              # pytest test suite (108 tests)
├── scripts/            # supervisord, start.sh, ngrok tunnel
├── data/               # SQLite DB (gitignored)
├── .env                # Secrets — never commit (gitignored)
└── requirements.txt
```
