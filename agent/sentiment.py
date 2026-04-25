import os
import numpy as np
import httpx
import xml.etree.ElementTree as ET
from openai import AzureOpenAI

openai_client = AzureOpenAI(
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://abdul-mk75p7ba-eastus2.cognitiveservices.azure.com"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY", "dummy"),
    api_version="2025-01-01-preview",
)

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
        response = openai_client.chat.completions.create(
            model="gpt-5-chat",
            max_tokens=10,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Score these headlines:\n{prompt}"},
            ],
        )
        raw = float(response.choices[0].message.content.strip())
        return float(np.clip(raw, -1.0, 1.0))
    except Exception:
        return None

async def fetch_and_score_sentiment() -> float | None:
    try:
        headlines = await fetch_headlines()
        return score_headlines(headlines)
    except Exception:
        return None
