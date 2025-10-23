from __future__ import annotations
import re, time, hashlib, csv, os, logging
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Iterable, List
import phonenumbers
from rapidfuzz import process, fuzz

LOGGER = logging.getLogger("egy-maint-scraper")

EG_CITIES = [
    "Cairo","Giza","Alexandria","Qalyubia","Sharqia","Dakahlia","Gharbia","Kafr El Sheikh",
    "Monufia","Beheira","Ismailia","Suez","Port Said","Damietta","Fayoum","Beni Suef","Minya",
    "Asyut","Sohag","Qena","Luxor","Aswan","Red Sea","New Valley","Matrouh","North Sinai","South Sinai"
]

def normalize_city(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    # Fuzzy match to our standard city list
    match, score, _ = process.extractOne(text, EG_CITIES, scorer=fuzz.WRatio)
    return match if score >= 80 else None

def normalize_phone(phone_raw: Optional[str]) -> Optional[str]:
    if not phone_raw:
        return None
    phone_raw = re.sub(r"[^+\d]", "", phone_raw)
    try:
        num = phonenumbers.parse(phone_raw, "EG")
        if phonenumbers.is_valid_number(num):
            return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return None
    return None

@dataclass
class Technician:
    source: str
    url: str
    name: Optional[str]
    category: Optional[str]
    phone: Optional[str]
    city: Optional[str]
    address: Optional[str]
    lat: Optional[float] = None
    lng: Optional[float] = None

    def to_row(self) -> Dict[str, str]:
        return {
            "source": self.source,
            "url": self.url,
            "name": (self.name or "").strip(),
            "category": (self.category or "").strip(),
            "phone": normalize_phone(self.phone) or "",
            "city": normalize_city(self.city) or (self.city or ""),
            "address": (self.address or "").strip(),
            "lat": "" if self.lat is None else str(self.lat),
            "lng": "" if self.lng is None else str(self.lng),
        }

def stable_id(t: Technician) -> str:
    base = "|".join([t.source, t.url, (t.name or ""), (t.phone or "")])
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def write_csv(rows: Iterable[Dict[str, str]], out_path: str) -> int:
    ensure_dir(os.path.dirname(out_path) or ".")
    rows = list(rows)
    if not rows:
        return 0
    fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return len(rows)
