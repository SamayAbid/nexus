import httpx
import pandas as pd

KRAKEN_BASE = "https://api.kraken.com/0/public"

PAIR_MAP = {
    "BTC/USD": "XBTUSD",
    "ETH/USD": "XETHZUSD",
}


class KrakenCLIError(Exception):
    def __init__(self, error_type: str, message: str, retryable: bool = False):
        self.error_type = error_type
        self.retryable = retryable
        super().__init__(f"[{error_type}] {message}")


def _kraken_pair(pair: str) -> str:
    return PAIR_MAP.get(pair, pair.replace("/", ""))


def fetch_ohlcv(pair: str, interval: int = 60) -> pd.DataFrame:
    with httpx.Client(timeout=15) as client:
        r = client.get(f"{KRAKEN_BASE}/OHLC", params={"pair": _kraken_pair(pair), "interval": interval})
        r.raise_for_status()
        data = r.json()
    if data.get("error"):
        raise KrakenCLIError("api_error", str(data["error"]))
    candles = next(v for k, v in data["result"].items() if k != "last")
    df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "vwap", "volume", "count"])
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit="s", utc=True)
    return df.set_index("timestamp")[["open", "high", "low", "close", "volume"]]


def fetch_ticker(pair: str) -> dict:
    with httpx.Client(timeout=15) as client:
        r = client.get(f"{KRAKEN_BASE}/Ticker", params={"pair": _kraken_pair(pair)})
        r.raise_for_status()
        data = r.json()
    if data.get("error"):
        raise KrakenCLIError("api_error", str(data["error"]))
    ticker = next(iter(data["result"].values()))
    return {
        "pair": pair,
        "bid": float(ticker["b"][0]),
        "ask": float(ticker["a"][0]),
        "last": float(ticker["c"][0]),
        "volume": float(ticker["v"][1]),
    }


def cancel_after(seconds: int = 120) -> None:
    pass  # no-op; only relevant for live authenticated orders
