import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.db import get_status_data, get_signals_data, get_trades_data

log = logging.getLogger("nexus.ws")
router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, event: dict) -> None:
        for ws in list(self.active):
            try:
                await ws.send_json(event)
            except Exception:
                self.disconnect(ws)


manager = ConnectionManager()


async def _start_broadcaster() -> None:
    state: dict = {
        "last_trade_id": 0,
        "regime": None,
        "circuit_breaker": False,
    }

    while True:
        await asyncio.sleep(5)
        if not manager.active:
            continue
        try:
            _check_new_trades(state)
            _check_regime_change(state)
            _check_circuit_breaker(state)
        except Exception as exc:
            log.warning(f"Broadcaster poll error: {exc}")


def _check_new_trades(state: dict) -> None:
    trades = get_trades_data(page=1)
    if not trades["items"]:
        return
    latest_id = trades["items"][0]["id"]
    if latest_id > state["last_trade_id"]:
        state["last_trade_id"] = latest_id
        asyncio.create_task(manager.broadcast({
            "type": "trade_executed",
            "data": trades["items"][0],
        }))


def _check_regime_change(state: dict) -> None:
    signals = get_signals_data()
    regime_now = get_status_data().get("regime")
    if regime_now and regime_now != state["regime"]:
        state["regime"] = regime_now
        asyncio.create_task(manager.broadcast({
            "type": "regime_changed",
            "data": {"regime": regime_now},
        }))
    if signals:
        asyncio.create_task(manager.broadcast({
            "type": "signal_changed",
            "data": signals,
        }))


def _check_circuit_breaker(state: dict) -> None:
    status = get_status_data()
    is_paused = status.get("is_paused", False)
    if is_paused and not state["circuit_breaker"]:
        state["circuit_breaker"] = True
        asyncio.create_task(manager.broadcast({
            "type": "circuit_breaker_triggered",
            "data": {"is_paused": True},
        }))
    elif not is_paused:
        state["circuit_breaker"] = False


@router.websocket("/stream")
async def stream(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
