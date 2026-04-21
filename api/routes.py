from fastapi import APIRouter, HTTPException, Query
from api.db import (
    get_status_data, get_pnl_data, get_positions_data,
    get_signals_data, get_trades_data, get_control_state, set_control_state,
)
from api.schemas import (
    StatusResponse, PnLResponse, PositionItem, SignalItem,
    TradesResponse, ControlRequest, ControlResponse,
)

router = APIRouter()


@router.get("/api/status", response_model=StatusResponse)
def status():
    return get_status_data()


@router.get("/api/pnl", response_model=PnLResponse)
def pnl():
    return get_pnl_data()


@router.get("/api/positions", response_model=list[PositionItem])
def positions():
    return get_positions_data()


@router.get("/api/signals", response_model=list[SignalItem])
def signals():
    return get_signals_data()


@router.get("/api/trades", response_model=TradesResponse)
def trades(page: int = Query(default=1, ge=1)):
    return get_trades_data(page=page)


@router.post("/api/control", response_model=ControlResponse)
def control(body: ControlRequest):
    if body.action not in ("pause", "resume"):
        raise HTTPException(status_code=422, detail="action must be 'pause' or 'resume'")
    set_control_state(paused=(body.action == "pause"))
    state = get_control_state()
    return ControlResponse(ok=True, is_paused=state["paused"])
