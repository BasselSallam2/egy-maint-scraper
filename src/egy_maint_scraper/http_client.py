from __future__ import annotations
import asyncio, httpx, logging, random, time
from typing import Optional
from .config import settings

LOGGER = logging.getLogger("egy-maint-scraper")

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118 Safari/537.36",
]

def ua() -> str:
    return settings.user_agent or random.choice(UA_POOL)

class HttpClient:
    def __init__(self):
        self._client = httpx.AsyncClient(timeout=30.0, headers={"User-Agent": ua()}, follow_redirects=True)

    async def get(self, url: str) -> Optional[str]:
        proxy = settings.choose_proxy()
        if proxy:
            self._client._proxies = {"all://": proxy}  # type: ignore
        await asyncio.sleep(settings.delay_seconds)  # polite delay
        try:
            resp = await self._client.get(url)
            if resp.status_code == 200 and resp.text:
                return resp.text
            LOGGER.warning(f"Non-200 for {url}: {resp.status_code}")
            return None
        except Exception as e:
            LOGGER.error(f"GET failed for {url}: {e}")
            return None

    async def close(self):
        await self._client.aclose()
