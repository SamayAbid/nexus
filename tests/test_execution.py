import json
import pytest
from unittest.mock import patch, MagicMock
from agent.risk import OrderParameters
from agent.execution import FillResult, place_paper_order, parse_fill

FILL_RESPONSE = json.dumps({
    "order_id": "PAPER-001", "pair": "BTC/USD", "side": "buy",
    "price": "50050.0", "size": "0.003992", "status": "filled"
})

ERROR_RESPONSE = json.dumps({
    "error": {"type": "validation", "message": "Insufficient funds", "retryable": False}
})

def make_params(direction: str = "long") -> OrderParameters:
    return OrderParameters(
        pair="BTC/USD", direction=direction,
        size=200.0, stop_loss=49250.0, take_profit=51500.0
    )

def make_mock_result(stdout: str) -> MagicMock:
    m = MagicMock()
    m.stdout = stdout
    m.returncode = 0
    return m

def test_parse_fill_extracts_fields():
    row = json.loads(FILL_RESPONSE)
    result = parse_fill(row, pair="BTC/USD", direction="long")
    assert isinstance(result, FillResult)
    assert result.order_id == "PAPER-001"
    assert result.fill_price == pytest.approx(50050.0)
    assert result.direction == "long"

def test_place_paper_order_returns_fill_result():
    with patch("agent.execution.subprocess.run", return_value=make_mock_result(FILL_RESPONSE)):
        result = place_paper_order(make_params("long"))
    assert result is not None
    assert isinstance(result, FillResult)
    assert result.pair == "BTC/USD"

def test_place_paper_order_uses_buy_for_long():
    with patch("agent.execution.subprocess.run", return_value=make_mock_result(FILL_RESPONSE)) as mock_run:
        place_paper_order(make_params("long"))
    args = mock_run.call_args[0][0]
    assert "buy" in args

def test_place_paper_order_uses_sell_for_short():
    with patch("agent.execution.subprocess.run", return_value=make_mock_result(FILL_RESPONSE)) as mock_run:
        place_paper_order(make_params("short"))
    args = mock_run.call_args[0][0]
    assert "sell" in args

def test_place_paper_order_returns_none_on_cli_error():
    with patch("agent.execution.subprocess.run", return_value=make_mock_result(ERROR_RESPONSE)):
        result = place_paper_order(make_params("long"))
    assert result is None

def test_fill_result_has_timestamp():
    row = json.loads(FILL_RESPONSE)
    result = parse_fill(row, pair="BTC/USD", direction="long")
    assert result.timestamp  # non-empty string
