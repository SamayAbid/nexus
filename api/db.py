import json
from pathlib import Path

from agent.database import get_connection

_PAGE_SIZE = 50
_PAIRS = ["BTC/USD", "ETH/USD"]
_DEFAULT_CONTROL = Path("data/control.json")


def get_status_data() -> dict:
    conn = get_connection()
    row = conn.execute(
        "SELECT timestamp, pair, regime, strategy, signal_score FROM decisions ORDER BY id DESC LIMIT 1"
    ).fetchone()
    first_row = conn.execute(
        "SELECT timestamp FROM decisions ORDER BY id ASC LIMIT 1"
    ).fetchone()
    conn.close()

    if row is None:
        return {
            "regime": None, "strategy": None, "pair": None, "signal_score": None,
            "last_heartbeat": None, "is_running": False, "is_paused": False,
            "uptime_seconds": 0,
        }

    from datetime import datetime, timezone
    last_ts = row["timestamp"]
    now = datetime.now(timezone.utc)
    try:
        last_dt = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
        seconds_since = (now - last_dt).total_seconds()
        is_running = seconds_since < 120
    except Exception:
        seconds_since = 0
        is_running = False

    uptime = 0
    if first_row:
        try:
            first_dt = datetime.fromisoformat(first_row["timestamp"].replace("Z", "+00:00"))
            uptime = int((now - first_dt).total_seconds())
        except Exception:
            pass

    return {
        "regime": row["regime"],
        "strategy": row["strategy"],
        "pair": row["pair"],
        "signal_score": row["signal_score"],
        "last_heartbeat": last_ts,
        "is_running": is_running,
        "is_paused": get_control_state()["paused"],
        "uptime_seconds": uptime,
    }


def _compute_sharpe(daily_pnls: list[float]) -> float:
    if len(daily_pnls) < 2:
        return 0.0
    mean = sum(daily_pnls) / len(daily_pnls)
    variance = sum((x - mean) ** 2 for x in daily_pnls) / (len(daily_pnls) - 1)
    std = variance ** 0.5
    return (mean / std * (252 ** 0.5)) if std > 0 else 0.0


def _compute_max_drawdown(equities: list[float]) -> float:
    if not equities:
        return 0.0
    peak = equities[0]
    max_dd = 0.0
    for eq in equities:
        if eq > peak:
            peak = eq
        dd = (peak - eq) / peak if peak > 0 else 0.0
        max_dd = max(max_dd, dd)
    return max_dd


def get_pnl_data() -> dict:
    conn = get_connection()
    snapshots = conn.execute(
        "SELECT timestamp, equity, daily_pnl, total_pnl FROM pnl_snapshots ORDER BY id"
    ).fetchall()
    wins = conn.execute("SELECT COUNT(*) FROM positions WHERE outcome='win'").fetchone()[0]
    losses = conn.execute("SELECT COUNT(*) FROM positions WHERE outcome='loss'").fetchone()[0]
    conn.close()

    win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0.0

    if not snapshots:
        return {"equity_curve": [], "sharpe": 0.0, "max_drawdown": 0.0,
                "win_rate": round(win_rate, 3), "total_pnl": 0.0}

    equity_curve = [{"timestamp": r["timestamp"], "equity": r["equity"]} for r in snapshots]
    equities = [r["equity"] for r in snapshots]
    daily_pnls = [r["daily_pnl"] for r in snapshots]
    total_pnl = snapshots[-1]["total_pnl"]

    return {
        "equity_curve": equity_curve,
        "sharpe": round(_compute_sharpe(daily_pnls), 3),
        "max_drawdown": round(_compute_max_drawdown(equities), 4),
        "win_rate": round(win_rate, 3),
        "total_pnl": round(total_pnl, 2),
    }


def get_positions_data() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM positions WHERE is_open=1").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_signals_data() -> list[dict]:
    conn = get_connection()
    result = []
    for pair in _PAIRS:
        row = conn.execute(
            "SELECT timestamp, pair, rsi, macd, vwap_signal, bb_signal, sentiment, signal_score "
            "FROM decisions WHERE pair=? ORDER BY id DESC LIMIT 1",
            (pair,)
        ).fetchone()
        if row:
            result.append({
                "pair": row["pair"],
                "rsi": row["rsi"],
                "macd": row["macd"],
                "vwap": row["vwap_signal"],
                "bb": row["bb_signal"],
                "sentiment": row["sentiment"],
                "composite": row["signal_score"],
                "timestamp": row["timestamp"],
            })
    conn.close()
    return result


def get_trades_data(page: int = 1) -> dict:
    conn = get_connection()
    offset = (page - 1) * _PAGE_SIZE
    total = conn.execute("SELECT COUNT(*) FROM decisions WHERE action != 'hold'").fetchone()[0]
    rows = conn.execute(
        "SELECT id, timestamp, pair, regime, strategy, action, signal_score, "
        "entry_price, position_size, stop_loss, take_profit, outcome "
        "FROM decisions WHERE action != 'hold' ORDER BY id DESC LIMIT ? OFFSET ?",
        (_PAGE_SIZE, offset)
    ).fetchall()
    conn.close()

    pages = max(1, -(-total // _PAGE_SIZE))  # ceiling division
    return {
        "items": [dict(r) for r in rows],
        "total": total,
        "page": page,
        "pages": pages,
    }


def get_control_state(control_file: Path = _DEFAULT_CONTROL) -> dict:
    if control_file.exists():
        try:
            return json.loads(control_file.read_text())
        except Exception:
            pass
    return {"paused": False}


def set_control_state(paused: bool, control_file: Path = _DEFAULT_CONTROL) -> None:
    control_file.parent.mkdir(exist_ok=True)
    control_file.write_text(json.dumps({"paused": paused}))
