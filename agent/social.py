import httpx
from datetime import datetime, timezone


def generate_daily_summary(stats: dict) -> str:
    trade_count = stats["trade_count"]
    win_count = stats["win_count"]
    loss_count = stats["loss_count"]
    total_pnl = stats["total_pnl"]
    best = stats["best_trade_pnl"]
    worst = stats["worst_trade_pnl"]
    starting_equity = stats["starting_equity"]
    win_rate = (win_count / trade_count * 100) if trade_count > 0 else 0.0
    pnl_pct = (total_pnl / starting_equity * 100) if starting_equity > 0 else 0.0

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sign = "+" if total_pnl >= 0 else ""

    return (
        f"📊 NEXUS Daily Report — {date_str}\n\n"
        f"Trades: {trade_count}  ({win_count}W / {loss_count}L)\n"
        f"Win Rate: {win_rate:.0f}%\n"
        f"Total P&L: {sign}${total_pnl:.2f} ({sign}{pnl_pct:.2f}%)\n"
        f"Best Trade: +${best:.2f}\n"
        f"Worst Trade: -${abs(worst):.2f}\n\n"
        f"#nexus #papertrading #algotrading"
    )


def format_trade_alert(trade: dict) -> str:
    action = trade["action"].upper()
    pair = trade["pair"]
    strategy = "TREND" if trade["strategy"] == "trend_following" else "MR"
    entry = trade["entry_price"]
    size = trade["position_size"]
    sl = trade["stop_loss"]
    tp = trade["take_profit"]
    score = trade["signal_score"]
    sign = "+" if score >= 0 else ""

    return (
        f"⚡ NEXUS Trade Alert\n"
        f"{action} {pair} [{strategy}]\n"
        f"Entry: ${entry:.2f}  Size: ${size:.2f}\n"
        f"SL: ${sl:.2f}  TP: ${tp:.2f}\n"
        f"Signal: {sign}{score:.2f}"
    )


def send_telegram_message(message: str, token: str, chat_id: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        response = httpx.post(
            url,
            json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
            timeout=10,
        )
        return response.status_code == 200
    except Exception:
        return False
