import os
import numpy as np
import httpx
import anthropic
import xml.etree.ElementTree as ET

anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

COINDESK_RSS = "https://www.coindesk.com/arc/outboundfeeds/rss/"

SYSTEM_PROMPT = (
    "You are a crypto market sentiment analyzer. "
    "When given a list of news headlines, respond with a single decimal number "
    "from -1.0 (extremely bearish) to +1.0 (extremely bullish). "
    "Reply with only the number, no explanation."
)

async def fetch_headlines() -> list[str]:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(COINDESK_RSS, headers={"User-Agent": "NEXUS/1.0"})
        root = ET.fromstring(r.text)
        items = root.findall(".//item/title")
        return [item.text for item in items[:10] if item.text]

def score_headlines(headlines: list[str]) -> float | None:
    if not headlines:
        return None
    prompt = "\n".join(f"- {h}" for h in headlines)
    try:
        message = anthropic_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            system=[{
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{"role": "user", "content": f"Score these headlines:\n{prompt}"}],
        )
        raw = float(message.content[0].text.strip())
        return float(np.clip(raw, -1.0, 1.0))
    except (ValueError, IndexError, anthropic.APIError):
        return None

async def fetch_and_score_sentiment() -> float | None:
    try:
        headlines = await fetch_headlines()
        return score_headlines(headlines)
    except Exception:
        return None
