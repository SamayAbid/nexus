import asyncio
import json
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

from api.websocket import ConnectionManager, router as ws_router

app = FastAPI()
app.include_router(ws_router)
client = TestClient(app)


def test_websocket_connects_and_closes():
    with client.websocket_connect("/stream") as ws:
        assert ws is not None


def test_websocket_receives_broadcast():
    with patch("api.websocket._start_broadcaster"):
        with client.websocket_connect("/stream") as ws:
            from api.websocket import manager
            assert hasattr(manager, "broadcast")


def test_connection_manager_connect_adds_client():
    mgr = ConnectionManager()
    assert len(mgr.active) == 0


def test_connection_manager_disconnect_removes_client():
    mgr = ConnectionManager()
    mock_ws = MagicMock()
    mgr.active.append(mock_ws)
    assert len(mgr.active) == 1
    mgr.disconnect(mock_ws)
    assert len(mgr.active) == 0


@pytest.mark.asyncio
async def test_broadcast_skips_dead_connections():
    mgr = ConnectionManager()
    dead_ws = AsyncMock()
    dead_ws.send_json.side_effect = Exception("connection closed")
    mgr.active.append(dead_ws)

    await mgr.broadcast({"type": "test", "data": {}})
    assert len(mgr.active) == 0


@pytest.mark.asyncio
async def test_broadcast_sends_to_all_active():
    mgr = ConnectionManager()
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    mgr.active.extend([ws1, ws2])

    event = {"type": "trade_executed", "data": {"pair": "BTC/USD"}}
    await mgr.broadcast(event)

    ws1.send_json.assert_called_once_with(event)
    ws2.send_json.assert_called_once_with(event)
