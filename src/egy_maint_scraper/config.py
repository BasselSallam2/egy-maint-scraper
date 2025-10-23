from __future__ import annotations
import os, random
from pydantic import BaseModel
from typing import List, Optional

class Settings(BaseModel):
    output_dir: str = os.getenv("OUTPUT_DIR", "data")
    concurrency: int = int(os.getenv("CONCURRENCY", "8"))
    delay_seconds: float = float(os.getenv("DELAY_SECONDS", "1.0"))
    user_agent: Optional[str] = os.getenv("USER_AGENT") or None
    proxies: List[str] = [p.strip() for p in os.getenv("PROXIES", "").split(",") if p.strip()]

    def choose_proxy(self) -> Optional[str]:
        return random.choice(self.proxies) if self.proxies else None

settings = Settings()
