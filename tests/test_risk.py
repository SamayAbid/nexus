import pytest
from datetime import datetime, timezone
from unittest.mock import patch
from agent.risk import (
    RiskState, OrderParameters,
    compute_position_size, compute_stop_loss, compute_take_profit,
    can_open_position, check_and_trigger_circuit_breaker,
    update_trailing_stop, build_order,
    MAX_POSITION_SIZE_PCT, CIRCUIT_BREAKER_PCT
)

def make_state(open_positions: int = 0, daily_pnl: float = 0.0,
               circuit_breaker_active: bool = False) -> RiskState:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return RiskState(
        open_positions=open_positions,
        daily_pnl=daily_pnl,
        starting_equity=10000.0,
        circuit_breaker_active=circuit_breaker_active,
        circuit_breaker_reset_date=today if circuit_breaker_active else "",
    )

def test_position_size_is_two_percent():
    size = compute_position_size(10000.0)
    assert size == pytest.approx(200.0)

def test_stop_loss_long_trend():
    sl = compute_stop_loss(entry=50000.0, direction="long", strategy="trend_following")
    assert sl == pytest.approx(50000.0 * 0.985)

def test_stop_loss_short_trend():
    sl = compute_stop_loss(entry=50000.0, direction="short", strategy="trend_following")
    assert sl == pytest.approx(50000.0 * 1.015)

def test_stop_loss_long_mean_reversion():
    sl = compute_stop_loss(entry=50000.0, direction="long", strategy="mean_reversion")
    assert sl == pytest.approx(50000.0 * 0.988)

def test_take_profit_long_trend():
    tp = compute_take_profit(entry=50000.0, direction="long", strategy="trend_following")
    assert tp == pytest.approx(50000.0 * 1.030)

def test_take_profit_short_mean_reversion():
    tp = compute_take_profit(entry=50000.0, direction="short", strategy="mean_reversion")
    assert tp == pytest.approx(50000.0 * 0.980)

def test_can_open_position_when_slots_available():
    state = make_state(open_positions=2)
    assert can_open_position(state) is True

def test_cannot_open_position_at_max_positions():
    state = make_state(open_positions=3)
    assert can_open_position(state) is False

def test_cannot_open_position_when_circuit_breaker_active():
    state = make_state(circuit_breaker_active=True)
    assert can_open_position(state) is False

def test_circuit_breaker_triggers_at_threshold():
    state = make_state(daily_pnl=-500.0)  # -5% of 10000
    new_state = check_and_trigger_circuit_breaker(state)
    assert new_state.circuit_breaker_active is True

def test_circuit_breaker_does_not_trigger_below_threshold():
    state = make_state(daily_pnl=-400.0)  # -4%, below -5% threshold
    new_state = check_and_trigger_circuit_breaker(state)
    assert new_state.circuit_breaker_active is False

def test_trailing_stop_long_raises_stop_with_price():
    high, new_sl = update_trailing_stop(
        current_price=51000.0, direction="long",
        trailing_high=50800.0, stop_loss=50000.0
    )
    assert high == pytest.approx(51000.0)
    assert new_sl > 50000.0

def test_trailing_stop_long_does_not_lower_stop():
    high, new_sl = update_trailing_stop(
        current_price=50500.0, direction="long",
        trailing_high=51000.0, stop_loss=50592.0
    )
    assert high == pytest.approx(51000.0)
    assert new_sl == pytest.approx(50592.0)

def test_build_order_returns_none_when_circuit_breaker():
    state = make_state(circuit_breaker_active=True)
    result = build_order("BTC/USD", "long", "trend_following", 50000.0, 10000.0, state)
    assert result is None

def test_build_order_returns_parameters_when_valid():
    state = make_state(open_positions=1)
    result = build_order("BTC/USD", "long", "trend_following", 50000.0, 10000.0, state)
    assert isinstance(result, OrderParameters)
    assert result.size == pytest.approx(200.0)
    assert result.stop_loss < 50000.0
    assert result.take_profit > 50000.0
