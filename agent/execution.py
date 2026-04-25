import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from agent.pipeline import fetch_ticker
from agent.risk import OrderParameters


@dataclass
class FillResult:
    order_id: str
    pair: str
    direction: str
    fill_price: float
    fill_size: float
    timestamp: str


def place_paper_order(params: OrderParameters) -> FillResult | None:
    try:
        ticker = fetch_ticker(params.pair)
        # Buys fill at ask, sells fill at bid (realistic paper spread)
        fill_price = ticker["ask"] if params.direction == "long" else ticker["bid"]
        return FillResult(
            order_id=f"paper-{uuid.uuid4().hex[:12]}",
            pair=params.pair,
            direction=params.direction,
            fill_price=fill_price,
            fill_size=params.size,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    except Exception:
        return None


def reconcile_positions(pair: str) -> list[dict]:
    return []  # positions are tracked in DB; no external reconciliation needed
