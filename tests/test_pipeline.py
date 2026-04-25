import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from agent.pipeline import KrakenCLIError, fetch_ohlcv, fetch_ticker, cancel_after

BASE_TS = 1713700000

def _make_candles(n=5):
    return [
        [BASE_TS + i * 3600, str(50000 + i * 10), str(50100 + i * 10),
         str(49900 + i * 10), str(50050 + i * 10), "50025.0", "5.5", 42]
        for i in range(n)
    ]

OHLC_RESPONSE = {
    "error": [],
    "result": {"XXBTZUSD": _make_candles(), "last": BASE_TS + 5 * 3600},
}

TICKER_RESPONSE = {
    "error": [],
    "result": {
        "XXBTZUSD": {
            "a": ["50060.0", 1, "1.000"],
            "b": ["50040.0", 1, "1.000"],
            "c": ["50050.0", "0.5"],
            "v": ["100.0", "12345.6"],
        }
    },
}

ERROR_RESPONSE = {"error": ["EGeneral:Invalid arguments"], "result": {}}


def _mock_httpx(response_json: dict) -> MagicMock:
    resp = MagicMock()
    resp.json.return_value = response_json
    resp.raise_for_status.return_value = None
    client = MagicMock()
    client.get.return_value = resp
    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=client)
    ctx.__exit__ = MagicMock(return_value=False)
    return ctx


def test_fetch_ohlcv_returns_dataframe():
    with patch("agent.pipeline.httpx.Client", return_value=_mock_httpx(OHLC_RESPONSE)):
        df = fetch_ohlcv("BTC/USD", interval=60)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert len(df) == 5
    assert df["close"].dtype == float


def test_fetch_ohlcv_index_is_datetime():
    with patch("agent.pipeline.httpx.Client", return_value=_mock_httpx(OHLC_RESPONSE)):
        df = fetch_ohlcv("BTC/USD")
    assert pd.api.types.is_datetime64_any_dtype(df.index)


def test_fetch_ohlcv_raises_on_api_error():
    with patch("agent.pipeline.httpx.Client", return_value=_mock_httpx(ERROR_RESPONSE)):
        with pytest.raises(KrakenCLIError) as exc_info:
            fetch_ohlcv("BTC/USD")
    assert exc_info.value.error_type == "api_error"


def test_fetch_ticker_returns_dict():
    with patch("agent.pipeline.httpx.Client", return_value=_mock_httpx(TICKER_RESPONSE)):
        ticker = fetch_ticker("BTC/USD")
    assert ticker["pair"] == "BTC/USD"
    assert ticker["ask"] == pytest.approx(50060.0)
    assert ticker["bid"] == pytest.approx(50040.0)
    assert ticker["last"] == pytest.approx(50050.0)


def test_fetch_ticker_raises_on_api_error():
    with patch("agent.pipeline.httpx.Client", return_value=_mock_httpx(ERROR_RESPONSE)):
        with pytest.raises(KrakenCLIError):
            fetch_ticker("BTC/USD")


def test_cancel_after_is_noop():
    cancel_after(120)  # should not raise
