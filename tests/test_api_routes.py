import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

from api.routes import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

MOCK_STATUS = {
    "regime": "trending", "strategy": "trend_following", "pair": "BTC/USD",
    "signal_score": 0.72, "last_heartbeat": "2026-04-21T10:00:00Z",
    "is_running": True, "is_paused": False, "uptime_seconds": 3600,
}

MOCK_PNL = {
    "equity_curve": [{"timestamp": "2026-04-21T10:00:00Z", "equity": 10100.0}],
    "sharpe": 1.23, "max_drawdown": 0.02, "win_rate": 0.6, "total_pnl": 100.0,
}

MOCK_POSITIONS = [{
    "id": 1, "pair": "BTC/USD", "direction": "long", "entry_price": 50000.0,
    "position_size": 200.0, "stop_loss": 49250.0, "take_profit": 51500.0,
    "trailing_stop_high": None, "opened_at": "2026-04-21T10:00:00Z",
    "order_id": "ORD001", "outcome": None, "is_open": 1,
}]

MOCK_SIGNALS = [{
    "pair": "BTC/USD", "rsi": 0.44, "macd": 0.30, "vwap": 0.10,
    "bb": -0.05, "sentiment": 0.20, "composite": 0.72,
    "timestamp": "2026-04-21T10:00:00Z",
}]

MOCK_TRADES = {
    "items": [{
        "id": 1, "timestamp": "2026-04-21T10:00:00Z", "pair": "BTC/USD",
        "regime": "trending", "strategy": "trend_following", "action": "long",
        "signal_score": 0.72, "entry_price": 50000.0, "position_size": 200.0,
        "stop_loss": 49250.0, "take_profit": 51500.0, "outcome": "open",
    }],
    "total": 1, "page": 1, "pages": 1,
}

def test_get_status_ok():
    with patch("api.routes.get_status_data", return_value=MOCK_STATUS):
        response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["regime"] == "trending"
    assert data["is_running"] is True

def test_get_pnl_ok():
    with patch("api.routes.get_pnl_data", return_value=MOCK_PNL):
        response = client.get("/api/pnl")
    assert response.status_code == 200
    data = response.json()
    assert len(data["equity_curve"]) == 1
    assert data["sharpe"] == pytest.approx(1.23)

def test_get_positions_ok():
    with patch("api.routes.get_positions_data", return_value=MOCK_POSITIONS):
        response = client.get("/api/positions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["pair"] == "BTC/USD"

def test_get_signals_ok():
    with patch("api.routes.get_signals_data", return_value=MOCK_SIGNALS):
        response = client.get("/api/signals")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["composite"] == pytest.approx(0.72)

def test_get_trades_ok():
    with patch("api.routes.get_trades_data", return_value=MOCK_TRADES):
        response = client.get("/api/trades")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["page"] == 1

def test_get_trades_page_param():
    with patch("api.routes.get_trades_data", return_value=MOCK_TRADES) as mock_fn:
        client.get("/api/trades?page=3")
    mock_fn.assert_called_once_with(page=3)

def test_post_control_pause():
    with patch("api.routes.set_control_state") as mock_set, \
         patch("api.routes.get_control_state", return_value={"paused": True}):
        response = client.post("/api/control", json={"action": "pause"})
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["is_paused"] is True
    mock_set.assert_called_once_with(paused=True)

def test_post_control_resume():
    with patch("api.routes.set_control_state") as mock_set, \
         patch("api.routes.get_control_state", return_value={"paused": False}):
        response = client.post("/api/control", json={"action": "resume"})
    assert response.status_code == 200
    assert response.json()["is_paused"] is False
    mock_set.assert_called_once_with(paused=False)

def test_post_control_invalid_action():
    response = client.post("/api/control", json={"action": "destroy"})
    assert response.status_code == 422
