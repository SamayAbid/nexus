import json
import sqlite3
import pytest
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch
from agent.database import init_db, write_decision, write_position, close_position, write_pnl_snapshot, get_connection
from api.db import (
    get_status_data, get_pnl_data, get_positions_data,
    get_signals_data, get_trades_data, get_control_state, set_control_state,
)

TEST_DB = Path("data/test_nexus_api.db")
CONTROL_FILE = Path("data/test_control.json")

SAMPLE_DECISION = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
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
}

@pytest.fixture(autouse=True)
def setup_db():
    with patch("agent.database.DB_PATH", TEST_DB):
        init_db()
        yield
        TEST_DB.unlink(missing_ok=True)
        for suffix in ["-wal", "-shm"]:
            TEST_DB.with_suffix(TEST_DB.suffix + suffix).unlink(missing_ok=True)
        CONTROL_FILE.unlink(missing_ok=True)

def test_get_status_data_empty_db():
    with patch("agent.database.DB_PATH", TEST_DB):
        result = get_status_data()
    assert result["regime"] is None
    assert result["is_running"] is False
    assert result["is_paused"] is False

def test_get_status_data_with_decision():
    with patch("agent.database.DB_PATH", TEST_DB):
        write_decision(SAMPLE_DECISION)
        result = get_status_data()
    assert result["regime"] == "trending"
    assert result["strategy"] == "trend_following"
    assert result["pair"] == "BTC/USD"
    assert result["signal_score"] == pytest.approx(0.72)
    assert isinstance(result["last_heartbeat"], str)

def test_get_pnl_data_empty():
    with patch("agent.database.DB_PATH", TEST_DB):
        result = get_pnl_data()
    assert result["equity_curve"] == []
    assert result["sharpe"] == 0.0
    assert result["max_drawdown"] == 0.0
    assert result["win_rate"] == 0.0

def test_get_pnl_data_with_snapshots():
    with patch("agent.database.DB_PATH", TEST_DB):
        write_pnl_snapshot(equity=10100.0, daily_pnl=100.0, total_pnl=100.0)
        write_pnl_snapshot(equity=10200.0, daily_pnl=200.0, total_pnl=200.0)
        result = get_pnl_data()
    assert len(result["equity_curve"]) == 2
    assert result["equity_curve"][0]["equity"] == pytest.approx(10100.0)
    assert result["total_pnl"] == pytest.approx(200.0)

def test_get_pnl_data_win_rate():
    with patch("agent.database.DB_PATH", TEST_DB):
        pid1 = write_position({
            "pair": "BTC/USD", "direction": "long", "entry_price": 50000.0,
            "position_size": 100.0, "stop_loss": 49250.0, "take_profit": 51500.0,
            "trailing_stop_high": None, "opened_at": SAMPLE_DECISION["timestamp"], "order_id": "ORD001",
        })
        pid2 = write_position({
            "pair": "ETH/USD", "direction": "short", "entry_price": 3000.0,
            "position_size": 50.0, "stop_loss": 3045.0, "take_profit": 2940.0,
            "trailing_stop_high": None, "opened_at": SAMPLE_DECISION["timestamp"], "order_id": "ORD002",
        })
        close_position(pid1, "win")
        close_position(pid2, "loss")
        result = get_pnl_data()
    assert result["win_rate"] == pytest.approx(0.5)

def test_get_positions_data_returns_open():
    with patch("agent.database.DB_PATH", TEST_DB):
        write_position({
            "pair": "BTC/USD", "direction": "long", "entry_price": 50000.0,
            "position_size": 100.0, "stop_loss": 49250.0, "take_profit": 51500.0,
            "trailing_stop_high": None, "opened_at": SAMPLE_DECISION["timestamp"], "order_id": "ORD001",
        })
        result = get_positions_data()
    assert len(result) == 1
    assert result[0]["pair"] == "BTC/USD"
    assert result[0]["direction"] == "long"

def test_get_signals_data_returns_per_pair():
    with patch("agent.database.DB_PATH", TEST_DB):
        btc = {**SAMPLE_DECISION, "pair": "BTC/USD"}
        eth = {**SAMPLE_DECISION, "pair": "ETH/USD", "order_id": "ORD002"}
        write_decision(btc)
        write_decision(eth)
        result = get_signals_data()
    pairs = {s["pair"] for s in result}
    assert "BTC/USD" in pairs
    assert "ETH/USD" in pairs

def test_get_signals_data_fields():
    with patch("agent.database.DB_PATH", TEST_DB):
        write_decision(SAMPLE_DECISION)
        result = get_signals_data()
    s = next(r for r in result if r["pair"] == "BTC/USD")
    assert s["rsi"] == pytest.approx(0.44)
    assert s["composite"] == pytest.approx(0.72)
    assert "timestamp" in s

def test_get_trades_data_pagination():
    with patch("agent.database.DB_PATH", TEST_DB):
        for i in range(55):
            d = {**SAMPLE_DECISION, "order_id": f"ORD{i:03d}"}
            write_decision(d)
        result = get_trades_data(page=1)
    assert result["total"] == 55
    assert result["page"] == 1
    assert len(result["items"]) == 50
    assert result["pages"] == 2

def test_get_trades_data_page_2():
    with patch("agent.database.DB_PATH", TEST_DB):
        for i in range(55):
            d = {**SAMPLE_DECISION, "order_id": f"ORD{i:03d}"}
            write_decision(d)
        result = get_trades_data(page=2)
    assert len(result["items"]) == 5

def test_get_control_state_default():
    result = get_control_state(control_file=CONTROL_FILE)
    assert result == {"paused": False}

def test_set_and_get_control_state():
    set_control_state(paused=True, control_file=CONTROL_FILE)
    result = get_control_state(control_file=CONTROL_FILE)
    assert result["paused"] is True
