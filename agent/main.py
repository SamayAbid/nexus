import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

_CONTROL_FILE = Path("data/control.json")

def _is_paused() -> bool:
    try:
        if _CONTROL_FILE.exists():
            return json.loads(_CONTROL_FILE.read_text()).get("paused", False)
    except Exception:
        pass
    return False
from agent.database import init_db, write_decision, write_position, get_open_positions, get_daily_pnl, write_pnl_snapshot
from agent.pipeline import fetch_ohlcv, fetch_ticker, cancel_after, KrakenCLIError
from agent.signals import compute_signals
from agent.regime import classify_regime
from agent.strategy import get_trade_signal
from agent.risk import RiskState, build_order, check_and_trigger_circuit_breaker, update_trailing_stop, TRAILING_TRIGGER_PCT
from agent.execution import place_paper_order, reconcile_positions

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("nexus")

PAIRS = ["BTC/USD", "ETH/USD"]
STARTING_EQUITY = 10000.0  # adjust to actual paper account balance

async def market_loop(shared: dict) -> None:
    while True:
        for pair in PAIRS:
            try:
                df = fetch_ohlcv(pair)
                signals = compute_signals(df, shared.get("sentiment"))
                regime = classify_regime(df)
                trade_signal = get_trade_signal(df, signals, regime, pair)

                open_pos = get_open_positions()
                daily_pnl = get_daily_pnl()
                state = RiskState(
                    open_positions=len(open_pos),
                    daily_pnl=daily_pnl,
                    starting_equity=STARTING_EQUITY,
                    circuit_breaker_active=shared.get("circuit_breaker", False),
                    circuit_breaker_reset_date=shared.get("cb_date", ""),
                )
                state = check_and_trigger_circuit_breaker(state)
                shared["circuit_breaker"] = state.circuit_breaker_active
                shared["cb_date"] = state.circuit_breaker_reset_date

                ticker = fetch_ticker(pair)
                current_price = float(ticker.get("price", 0))

                for pos in open_pos:
                    if pos["pair"] != pair:
                        continue
                    if pos["trailing_stop_high"] and current_price:
                        new_high, new_sl = update_trailing_stop(
                            current_price, pos["direction"],
                            pos["trailing_stop_high"], pos["stop_loss"]
                        )
                        shared.setdefault("trailing", {})[pos["id"]] = (new_high, new_sl)

                decision = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "pair": pair, "regime": regime, "strategy": trade_signal.strategy,
                    "signal_score": signals.composite, "rsi": signals.rsi,
                    "macd": signals.macd, "vwap_signal": signals.vwap,
                    "bb_signal": signals.bb, "sentiment": signals.sentiment,
                    "action": trade_signal.action, "order_id": None,
                    "entry_price": None, "position_size": None,
                    "stop_loss": None, "take_profit": None, "outcome": None,
                }

                if trade_signal.action != "hold" and not _is_paused():
                    order = build_order(pair, trade_signal.action, trade_signal.strategy,
                                        current_price, STARTING_EQUITY, state)
                    if order:
                        fill = place_paper_order(order)
                        if fill:
                            pos_id = write_position({
                                "pair": pair, "direction": fill.direction,
                                "entry_price": fill.fill_price,
                                "position_size": fill.fill_size,
                                "stop_loss": order.stop_loss,
                                "take_profit": order.take_profit,
                                "trailing_stop_high": None,
                                "opened_at": fill.timestamp,
                                "order_id": fill.order_id,
                            })
                            decision.update({
                                "order_id": fill.order_id,
                                "entry_price": fill.fill_price,
                                "position_size": fill.fill_size,
                                "stop_loss": order.stop_loss,
                                "take_profit": order.take_profit,
                                "outcome": "open",
                            })
                            log.info(f"[{pair}] {trade_signal.action.upper()} @ {fill.fill_price:.2f} | S={signals.composite:.3f} | {regime}")

                write_decision(decision)
                write_pnl_snapshot(equity=STARTING_EQUITY + daily_pnl, daily_pnl=daily_pnl, total_pnl=daily_pnl)

            except KrakenCLIError as e:
                log.error(f"[{pair}] Kraken CLI error ({e.error_type}): {e}")
            except Exception as e:
                log.exception(f"[{pair}] Unexpected error: {e}")

        await asyncio.sleep(60)

async def sentiment_loop(shared: dict) -> None:
    from agent.sentiment import fetch_and_score_sentiment
    while True:
        try:
            score = await fetch_and_score_sentiment()
            shared["sentiment"] = score
            log.info(f"Sentiment updated: {score}")
        except Exception as e:
            log.warning(f"Sentiment fetch failed: {e} — using cached value")
        await asyncio.sleep(900)  # 15 minutes

async def main() -> None:
    init_db()
    try:
        cancel_after(120)
        log.info("cancel-after 120 set on startup")
    except Exception:
        log.warning("cancel-after failed — Kraken CLI may not be installed yet")

    shared: dict = {"sentiment": None, "circuit_breaker": False, "cb_date": "", "trailing": {}}
    log.info("NEXUS agent starting — paper trading mode")
    await asyncio.gather(
        market_loop(shared),
        sentiment_loop(shared),
    )

if __name__ == "__main__":
    asyncio.run(main())
