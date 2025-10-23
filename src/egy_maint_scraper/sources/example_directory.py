from __future__ import annotations
from typing import List, AsyncGenerator
from selectolax.parser import HTMLParser
from ..utils import Technician
from .base import Source

class ExampleDirectory(Source):
    """Example public directory with predictable HTML card layout.
    Replace BASE with a real, allowed domain before running in production.
    Always check the site's robots.txt and Terms first.
    """

    BASE = "https://example-eg-directory.test/maintenance"

    @property
    def name(self) -> str:
        return "example_directory"

    async def seed_urls(self) -> List[str]:
        # Pretend there are 5 paginated category pages
        return [f"{self.BASE}?page={i}" for i in range(1, 6)]

    async def parse(self, html: str, url: str) -> AsyncGenerator[Technician, None]:
        tree = HTMLParser(html)
        for card in tree.css("div.listing-card"):
            name = (card.css_first(".name").text() if card.css_first(".name") else None)
            phone = (card.css_first(".phone").text() if card.css_first(".phone") else None)
            city = (card.css_first(".city").text() if card.css_first(".city") else None)
            address = (card.css_first(".address").text() if card.css_first(".address") else None)
            category = (card.css_first(".category").text() if card.css_first(".category") else "Maintenance")
            detail_link = card.css_first("a.details")
            item_url = detail_link.attributes.get("href") if detail_link else url
            yield Technician(
                source=self.name,
                url=item_url,
                name=name,
                category=category,
                phone=phone,
                city=city,
                address=address,
            )
