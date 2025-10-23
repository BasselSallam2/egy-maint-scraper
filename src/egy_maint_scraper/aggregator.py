from __future__ import annotations
import asyncio, logging
from typing import Dict, List, Set, Iterable
from .http_client import HttpClient
from .utils import Technician, write_csv, stable_id
from .config import settings

LOGGER = logging.getLogger("egy-maint-scraper")

class Aggregator:
    def __init__(self, sources: Iterable):
        self.sources = list(sources)
        self.http = HttpClient()
        self.results: Dict[str, Technician] = {}

    async def fetch_and_parse(self, source) -> None:
        seed_urls = await source.seed_urls()
        for url in seed_urls:
            html = await self.http.get(url)
            if not html:
                continue
            async for tech in source.parse(html, url):
                sid = stable_id(tech)
                self.results[sid] = tech  # dedupe by (source,url,name,phone)

    async def run(self) -> List[Technician]:
        tasks = [self.fetch_and_parse(src) for src in self.sources]
        # Limit concurrency politely
        sem = asyncio.Semaphore(settings.concurrency)

        async def guarded(coro):
            async with sem:
                return await coro

        await asyncio.gather(*(guarded(t) for t in tasks))
        await self.http.close()
        return list(self.results.values())

    def export_csv(self, path: str) -> int:
        rows = [t.to_row() for t in self.results.values()]
        count = write_csv(rows, path)
        LOGGER.info(f"Wrote {count} rows -> {path}")
        return count
