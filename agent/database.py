import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).parent.parent / "data" / "nexus.db"

def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            pair TEXT NOT NULL,
            regime TEXT NOT NULL,
            strategy TEXT NOT NULL,
            signal_score REAL NOT NULL,
            rsi REAL, macd REAL, vwap_signal REAL, bb_signal REAL, sentiment REAL,
            action TEXT NOT NULL,
            order_id TEXT, entry_price REAL, position_size REAL,
            stop_loss REAL, take_profit REAL, outcome TEXT
        );
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pair TEXT NOT NULL,
            direction TEXT NOT NULL,
            entry_price REAL NOT NULL,
            position_size REAL NOT NULL,
            stop_loss REAL NOT NULL,
            take_profit REAL NOT NULL,
            trailing_stop_high REAL,
            opened_at TEXT NOT NULL,
            order_id TEXT,
            outcome TEXT,
            is_open INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS pnl_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            equity REAL NOT NULL,
            daily_pnl REAL NOT NULL,
            total_pnl REAL NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def write_decision(d: dict) -> None:
    conn = get_connection()
    conn.execute("""
        INSERT INTO decisions
        (timestamp, pair, regime, strategy, signal_score, rsi, macd, vwap_signal,
         bb_signal, sentiment, action, order_id, entry_price, position_size, stop_loss, take_profit, outcome)
        VALUES (:timestamp, :pair, :regime, :strategy, :signal_score, :rsi, :macd, :vwap_signal,
                :bb_signal, :sentiment, :action, :order_id, :entry_price, :position_size, :stop_loss, :take_profit, :outcome)
    """, d)
    conn.commit()
    conn.close()

def write_position(p: dict) -> int:
    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO positions
        (pair, direction, entry_price, position_size, stop_loss, take_profit,
         trailing_stop_high, opened_at, order_id)
        VALUES (:pair, :direction, :entry_price, :position_size, :stop_loss, :take_profit,
                :trailing_stop_high, :opened_at, :order_id)
    """, p)
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid

def close_position(position_id: int, outcome: str) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE positions SET is_open=0, outcome=? WHERE id=?",
        (outcome, position_id)
    )
    conn.commit()
    conn.close()

def get_open_positions() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM positions WHERE is_open=1").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def write_pnl_snapshot(equity: float, daily_pnl: float, total_pnl: float) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO pnl_snapshots (timestamp, equity, daily_pnl, total_pnl) VALUES (?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), equity, daily_pnl, total_pnl)
    )
    conn.commit()
    conn.close()

def get_daily_pnl() -> float:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn = get_connection()
    row = conn.execute(
        "SELECT daily_pnl FROM pnl_snapshots WHERE timestamp LIKE ? ORDER BY id DESC LIMIT 1",
        (f"{today}%",)
    ).fetchone()
    conn.close()
    return float(row["daily_pnl"]) if row else 0.0
