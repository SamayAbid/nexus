import pytest
from unittest.mock import patch, MagicMock
from agent.social import (
    generate_daily_summary,
    format_trade_alert,
    send_telegram_message,
)

SAMPLE_STATS = {
    "trade_count": 12,
    "win_count": 7,
    "loss_count": 5,
    "total_pnl": 143.50,
    "best_trade_pnl": 62.30,
    "worst_trade_pnl": -28.10,
    "starting_equity": 10000.0,
}

SAMPLE_TRADE = {
    "pair": "BTC/USD",
    "action": "long",
    "strategy": "trend_following",
    "entry_price": 50000.0,
    "position_size": 200.0,
    "stop_loss": 49250.0,
    "take_profit": 51500.0,
    "signal_score": 0.72,
}

def test_generate_daily_summary_contains_key_fields():
    result = generate_daily_summary(SAMPLE_STATS)
    assert "NEXUS" in result
    assert "12" in result          # trade count
    assert "7" in result           # wins
    assert "143.50" in result or "143" in result  # total pnl
    assert "%" in result           # win rate

def test_generate_daily_summary_is_string():
    result = generate_daily_summary(SAMPLE_STATS)
    assert isinstance(result, str)
    assert len(result) > 50

def test_format_trade_alert_contains_key_fields():
    result = format_trade_alert(SAMPLE_TRADE)
    assert "BTC/USD" in result
    assert "LONG" in result or "long" in result
    assert "50000" in result
    assert "0.72" in result

def test_format_trade_alert_is_string():
    result = format_trade_alert(SAMPLE_TRADE)
    assert isinstance(result, str)

def test_send_telegram_message_calls_api():
    mock_response = MagicMock()
    mock_response.status_code = 200
    with patch("agent.social.httpx.post", return_value=mock_response) as mock_post:
        result = send_telegram_message("test message", token="TOKEN123", chat_id="CHAT456")
    assert result is True
    call_args = mock_post.call_args
    assert "TOKEN123" in call_args[0][0]
    assert call_args[1]["json"]["chat_id"] == "CHAT456"
    assert call_args[1]["json"]["text"] == "test message"

def test_send_telegram_message_returns_false_on_error():
    with patch("agent.social.httpx.post", side_effect=Exception("network error")):
        result = send_telegram_message("test", token="T", chat_id="C")
    assert result is False

def test_send_telegram_message_returns_false_on_non_200():
    mock_response = MagicMock()
    mock_response.status_code = 400
    with patch("agent.social.httpx.post", return_value=mock_response):
        result = send_telegram_message("test", token="T", chat_id="C")
    assert result is False
