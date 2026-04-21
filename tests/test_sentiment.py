import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from agent.sentiment import fetch_headlines, score_headlines, fetch_and_score_sentiment

SAMPLE_HEADLINES = [
    "Bitcoin surges past $60,000 as institutional demand rises",
    "Ethereum upgrade boosts developer activity",
    "Crypto markets rally amid ETF approval news",
]

def make_openai_response(text: str) -> MagicMock:
    message = MagicMock()
    message.content = text
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response

def test_score_headlines_returns_float_in_range():
    mock_response = make_openai_response("0.65")
    with patch("agent.sentiment.openai_client.chat.completions.create", return_value=mock_response):
        result = score_headlines(SAMPLE_HEADLINES)
    assert result is not None
    assert -1.0 <= result <= 1.0

def test_score_headlines_clips_out_of_range():
    mock_response = make_openai_response("1.8")  # out of range
    with patch("agent.sentiment.openai_client.chat.completions.create", return_value=mock_response):
        result = score_headlines(SAMPLE_HEADLINES)
    assert result == pytest.approx(1.0)

def test_score_headlines_returns_none_on_invalid_response():
    mock_response = make_openai_response("very bullish!")  # not a number
    with patch("agent.sentiment.openai_client.chat.completions.create", return_value=mock_response):
        result = score_headlines(SAMPLE_HEADLINES)
    assert result is None

def test_score_headlines_returns_none_on_empty_list():
    result = score_headlines([])
    assert result is None

@pytest.mark.asyncio
async def test_fetch_and_score_returns_float_or_none():
    mock_response = make_openai_response("0.42")
    with patch("agent.sentiment.fetch_headlines", new=AsyncMock(return_value=SAMPLE_HEADLINES)), \
         patch("agent.sentiment.openai_client.chat.completions.create", return_value=mock_response):
        result = await fetch_and_score_sentiment()
    assert result is None or isinstance(result, float)

@pytest.mark.asyncio
async def test_fetch_and_score_returns_none_on_network_error():
    with patch("agent.sentiment.fetch_headlines", new=AsyncMock(side_effect=Exception("network error"))):
        result = await fetch_and_score_sentiment()
    assert result is None
