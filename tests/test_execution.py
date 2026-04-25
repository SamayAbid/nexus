import pytest
from unittest.mock import patch
from agent.risk import OrderParameters
from agent.execution import FillResult, place_paper_order

MOCK_TICKER = {"pair": "BTC/USD", "bid": 50040.0, "ask": 50060.0, "last": 50050.0, "volume": 12345.6}


def make_params(direction: str = "long") -> OrderParameters:
    return OrderParameters(
        pair="BTC/USD", direction=direction,
        size=0.004, stop_loss=49250.0, take_profit=51500.0,
    )


def test_place_paper_order_returns_fill_result():
    with patch("agent.execution.fetch_ticker", return_value=MOCK_TICKER):
        result = place_paper_order(make_params("long"))
    assert result is not None
    assert isinstance(result, FillResult)
    assert result.pair == "BTC/USD"


def test_place_paper_order_long_fills_at_ask():
    with patch("agent.execution.fetch_ticker", return_value=MOCK_TICKER):
        result = place_paper_order(make_params("long"))
    assert result is not None
    assert result.fill_price == pytest.approx(50060.0)
    assert result.direction == "long"


def test_place_paper_order_short_fills_at_bid():
    with patch("agent.execution.fetch_ticker", return_value=MOCK_TICKER):
        result = place_paper_order(make_params("short"))
    assert result is not None
    assert result.fill_price == pytest.approx(50040.0)
    assert result.direction == "short"


def test_place_paper_order_returns_none_on_error():
    with patch("agent.execution.fetch_ticker", side_effect=Exception("network error")):
        result = place_paper_order(make_params("long"))
    assert result is None


def test_fill_result_has_unique_order_id():
    with patch("agent.execution.fetch_ticker", return_value=MOCK_TICKER):
        r1 = place_paper_order(make_params("long"))
        r2 = place_paper_order(make_params("long"))
    assert r1 is not None and r2 is not None
    assert r1.order_id != r2.order_id


def test_fill_result_has_timestamp():
    with patch("agent.execution.fetch_ticker", return_value=MOCK_TICKER):
        result = place_paper_order(make_params("long"))
    assert result is not None
    assert result.timestamp
