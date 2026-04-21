from pydantic import BaseModel
from typing import Optional


class StatusResponse(BaseModel):
    regime: Optional[str]
    strategy: Optional[str]
    pair: Optional[str]
    signal_score: Optional[float]
    last_heartbeat: Optional[str]
    is_running: bool
    is_paused: bool
    uptime_seconds: int


class PnLPoint(BaseModel):
    timestamp: str
    equity: float


class PnLResponse(BaseModel):
    equity_curve: list[PnLPoint]
    sharpe: float
    max_drawdown: float
    win_rate: float
    total_pnl: float


class PositionItem(BaseModel):
    id: int
    pair: str
    direction: str
    entry_price: float
    position_size: float
    stop_loss: float
    take_profit: float
    trailing_stop_high: Optional[float]
    opened_at: str
    order_id: Optional[str]
    outcome: Optional[str]
    is_open: int


class SignalItem(BaseModel):
    pair: str
    rsi: Optional[float]
    macd: Optional[float]
    vwap: Optional[float]
    bb: Optional[float]
    sentiment: Optional[float]
    composite: Optional[float]
    timestamp: Optional[str]


class TradeItem(BaseModel):
    id: int
    timestamp: str
    pair: str
    regime: str
    strategy: str
    action: str
    signal_score: float
    entry_price: Optional[float]
    position_size: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    outcome: Optional[str]


class TradesResponse(BaseModel):
    items: list[TradeItem]
    total: int
    page: int
    pages: int


class ControlRequest(BaseModel):
    action: str  # "pause" | "resume"


class ControlResponse(BaseModel):
    ok: bool
    is_paused: bool
