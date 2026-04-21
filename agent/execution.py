import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from agent.pipeline import _parse_ndjson, _check_errors, KrakenCLIError
from agent.risk import OrderParameters

@dataclass
class FillResult:
    order_id: str
    pair: str
    direction: str
    fill_price: float
    fill_size: float
    timestamp: str

def parse_fill(row: dict, pair: str, direction: str) -> FillResult:
    return FillResult(
        order_id=row.get("order_id", ""),
        pair=pair,
        direction=direction,
        fill_price=float(row.get("price", 0)),
        fill_size=float(row.get("size", 0)),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

def place_paper_order(params: OrderParameters) -> FillResult | None:
    side = "buy" if params.direction == "long" else "sell"
    size_str = f"{params.size:.8f}"
    result = subprocess.run(
        ["kraken", "-o", "json", "paper", "order", "market", params.pair, side, size_str],
        capture_output=True, text=True, timeout=15
    )
    try:
        rows = _parse_ndjson(result.stdout)
        _check_errors(rows)
        return parse_fill(rows[0], params.pair, params.direction)
    except (KrakenCLIError, IndexError, ValueError):
        return None

def reconcile_positions(pair: str) -> list[dict]:
    result = subprocess.run(
        ["kraken", "-o", "json", "paper", "positions", pair],
        capture_output=True, text=True, timeout=15
    )
    try:
        rows = _parse_ndjson(result.stdout)
        _check_errors(rows)
        return rows
    except KrakenCLIError:
        return []
