from __future__ import annotations
from typing import AsyncGenerator, List
from abc import ABC, abstractmethod
from ..utils import Technician

class Source(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def seed_urls(self) -> List[str]: ...

    @abstractmethod
    async def parse(self, html: str, url: str) -> AsyncGenerator[Technician, None]: ...
