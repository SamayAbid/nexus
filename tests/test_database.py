import sqlite3
import pytest
from pathlib import Path
from unittest.mock import patch
from agent.database import init_db, get_connection, write_decision, write_position, close_position, write_pnl_snapshot, get_open_positions, get_daily_pnl

TEST_DB = Path("data/test_nexus.db")

@pytest.fixture(autouse=True)
def clean_db():
    with patch("agent.database.DB_PATH", TEST_DB):
        init_db()
        yield
        TEST_DB.unlink(missing_ok=True)

def test_init_creates_tables():
    with patch("agent.database.DB_PATH", TEST_DB):
        conn = get_connection()
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        names = {row[0] for row in tables}
        conn.close()
    assert "decisions" in names
    assert "positions" in names
    assert "pnl_snapshots" in names

def test_wal_mode_enabled():
    with patch("agent.database.DB_PATH", TEST_DB):
        conn = get_connection()
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        conn.close()
    assert mode == "wal"

def test_write_and_read_decision():
    with patch("agent.database.DB_PATH", TEST_DB):
        write_decision({
            "timestamp": "2026-04-21T10:00:00Z",
            "pair": "BTC/USD",
            "regime": "trending",
            "strategy": "trend_following",
            "signal_score": 0.72,
            "rsi": 0.44,
            "macd": 0.30,
            "vwap_signal": 0.10,
            "bb_signal": -0.05,
            "sentiment": 0.20,
            "action": "long",
            "order_id": "ORD001",
            "entry_price": 50000.0,
            "position_size": 100.0,
            "stop_loss": 49250.0,
            "take_profit": 51500.0,
            "outcome": "open",
        })
        conn = get_connection()
        row = conn.execute("SELECT * FROM decisions WHERE order_id='ORD001'").fetchone()
        conn.close()
    assert row is not None
    assert row["pair"] == "BTC/USD"
    assert row["signal_score"] == pytest.approx(0.72)

def test_write_position_returns_id():
    with patch("agent.database.DB_PATH", TEST_DB):
        pid = write_position({
            "pair": "BTC/USD",
            "direction": "long",
            "entry_price": 50000.0,
            "position_size": 100.0,
            "stop_loss": 49250.0,
            "take_profit": 51500.0,
            "trailing_stop_high": None,
            "opened_at": "2026-04-21T10:00:00Z",
            "order_id": "ORD001",
        })
    assert isinstance(pid, int)
    assert pid > 0

def test_close_position_sets_outcome():
    with patch("agent.database.DB_PATH", TEST_DB):
        pid = write_position({
            "pair": "ETH/USD", "direction": "short", "entry_price": 3000.0,
            "position_size": 50.0, "stop_loss": 3045.0, "take_profit": 2940.0,
            "trailing_stop_high": None, "opened_at": "2026-04-21T10:00:00Z", "order_id": "ORD002",
        })
        close_position(pid, "win")
        conn = get_connection()
        row = conn.execute("SELECT is_open, outcome FROM positions WHERE id=?", (pid,)).fetchone()
        conn.close()
    assert row["is_open"] == 0
    assert row["outcome"] == "win"

def test_get_open_positions_returns_only_open():
    with patch("agent.database.DB_PATH", TEST_DB):
        pid = write_position({
            "pair": "BTC/USD", "direction": "long", "entry_price": 50000.0,
            "position_size": 100.0, "stop_loss": 49250.0, "take_profit": 51500.0,
            "trailing_stop_high": None, "opened_at": "2026-04-21T10:00:00Z", "order_id": "ORD003",
        })
        open_pos = get_open_positions()
        close_position(pid, "loss")
        open_pos_after = get_open_positions()
    assert any(p["order_id"] == "ORD003" for p in open_pos)
    assert not any(p["order_id"] == "ORD003" for p in open_pos_after)

def test_write_pnl_snapshot():
    with patch("agent.database.DB_PATH", TEST_DB):
        write_pnl_snapshot(equity=10500.0, daily_pnl=250.0, total_pnl=500.0)
        conn = get_connection()
        row = conn.execute("SELECT * FROM pnl_snapshots ORDER BY id DESC LIMIT 1").fetchone()
        conn.close()
    assert row["equity"] == pytest.approx(10500.0)

def test_get_daily_pnl_sums_today():
    with patch("agent.database.DB_PATH", TEST_DB):
        write_pnl_snapshot(equity=10100.0, daily_pnl=100.0, total_pnl=100.0)
        write_pnl_snapshot(equity=10200.0, daily_pnl=200.0, total_pnl=200.0)
        pnl = get_daily_pnl()
    assert pnl == pytest.approx(200.0)
