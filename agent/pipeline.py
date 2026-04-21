import json
import subprocess
import pandas as pd
from typing import Any

class KrakenCLIError(Exception):
    def __init__(self, error_type: str, message: str, retryable: bool = False):
        self.error_type = error_type
        self.retryable = retryable
        super().__init__(f"[{error_type}] {message}")

def _parse_ndjson(stdout: str) -> list[dict]:
    lines = [l.strip() for l in stdout.strip().split("\n") if l.strip()]
    return [json.loads(l) for l in lines]

def _check_errors(rows: list[dict]) -> None:
    for row in rows:
        if "error" in row:
            err = row["error"]
            raise KrakenCLIError(
                error_type=err.get("type", "unknown"),
                message=err.get("message", "unknown error"),
                retryable=err.get("retryable", False),
            )

def _run(args: list[str]) -> list[dict]:
    result = subprocess.run(
        ["kraken", "-o", "json"] + args,
        capture_output=True, text=True, timeout=15
    )
    rows = _parse_ndjson(result.stdout)
    _check_errors(rows)
    return rows

def fetch_ohlcv(pair: str, interval: int = 60) -> pd.DataFrame:
    rows = _run(["market", "ohlcv", pair, "--interval", str(interval)])
    df = pd.DataFrame(rows)
    df[["open", "high", "low", "close", "volume"]] = (
        df[["open", "high", "low", "close", "volume"]].astype(float)
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit="s", utc=True)
    return df.set_index("timestamp")[["open", "high", "low", "close", "volume"]]

def fetch_ticker(pair: str) -> dict:
    rows = _run(["market", "ticker", pair])
    return rows[0] if rows else {}

def cancel_after(seconds: int = 120) -> None:
    _run(["order", "cancel-after", str(seconds)])
