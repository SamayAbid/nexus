import json
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from agent.pipeline import (
    KrakenCLIError, _parse_ndjson, _check_errors,
    fetch_ohlcv, fetch_ticker, cancel_after
)

SAMPLE_OHLCV_NDJSON = "\n".join([
    json.dumps({"timestamp": 1713700000 + i * 3600, "open": str(50000 + i * 10),
                "high": str(50100 + i * 10), "low": str(49900 + i * 10),
                "close": str(50050 + i * 10), "volume": "5.5"})
    for i in range(5)
])

SAMPLE_TICKER_NDJSON = json.dumps({
    "pair": "BTC/USD", "price": "50050.0", "bid": "50040.0",
    "ask": "50060.0", "volume": "12345.6"
})

AUTH_ERROR_NDJSON = json.dumps({
    "error": {"type": "auth", "message": "Invalid API key", "retryable": False}
})

RATE_LIMIT_NDJSON = json.dumps({
    "error": {"type": "rate_limit", "message": "Too many requests",
              "retryable": True, "suggestion": "Wait 1 second"}
})

def make_mock_result(stdout: str, returncode: int = 0) -> MagicMock:
    m = MagicMock()
    m.stdout = stdout
    m.returncode = returncode
    return m

def test_parse_ndjson_multiple_lines():
    rows = _parse_ndjson(SAMPLE_OHLCV_NDJSON)
    assert len(rows) == 5
    assert rows[0]["volume"] == "5.5"

def test_parse_ndjson_single_line():
    rows = _parse_ndjson(SAMPLE_TICKER_NDJSON)
    assert len(rows) == 1
    assert rows[0]["pair"] == "BTC/USD"

def test_check_errors_raises_on_auth_error():
    rows = _parse_ndjson(AUTH_ERROR_NDJSON)
    with pytest.raises(KrakenCLIError) as exc_info:
        _check_errors(rows)
    assert exc_info.value.error_type == "auth"
    assert exc_info.value.retryable is False

def test_check_errors_raises_on_rate_limit():
    rows = _parse_ndjson(RATE_LIMIT_NDJSON)
    with pytest.raises(KrakenCLIError) as exc_info:
        _check_errors(rows)
    assert exc_info.value.error_type == "rate_limit"
    assert exc_info.value.retryable is True

def test_fetch_ohlcv_returns_dataframe():
    with patch("agent.pipeline.subprocess.run", return_value=make_mock_result(SAMPLE_OHLCV_NDJSON)):
        df = fetch_ohlcv("BTC/USD", interval=60)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert len(df) == 5
    assert df["close"].dtype == float

def test_fetch_ohlcv_index_is_datetime():
    with patch("agent.pipeline.subprocess.run", return_value=make_mock_result(SAMPLE_OHLCV_NDJSON)):
        df = fetch_ohlcv("BTC/USD")
    assert pd.api.types.is_datetime64_any_dtype(df.index)

def test_fetch_ticker_returns_dict():
    with patch("agent.pipeline.subprocess.run", return_value=make_mock_result(SAMPLE_TICKER_NDJSON)):
        ticker = fetch_ticker("BTC/USD")
    assert ticker["pair"] == "BTC/USD"
    assert float(ticker["price"]) == pytest.approx(50050.0)

def test_fetch_ohlcv_raises_on_auth_error():
    with patch("agent.pipeline.subprocess.run", return_value=make_mock_result(AUTH_ERROR_NDJSON)):
        with pytest.raises(KrakenCLIError) as exc_info:
            fetch_ohlcv("BTC/USD")
    assert exc_info.value.error_type == "auth"

def test_cancel_after_calls_correct_command():
    with patch("agent.pipeline.subprocess.run", return_value=make_mock_result("{}")) as mock_run:
        cancel_after(120)
    call_args = mock_run.call_args[0][0]
    assert "cancel-after" in call_args
    assert "120" in call_args
