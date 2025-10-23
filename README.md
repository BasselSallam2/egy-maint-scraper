# 🇪🇬 Egypt Maintenance Technicians Harvester

A professional, extensible Python project to collect **public** listings for maintenance technicians in Egypt (e.g., appliance repair, AC, plumbing, electrical, etc.), **normalize** the records, and export them to a clean **CSV** ready for analytics or a CRM.

> ⚖️ **Legal & Ethical**: Only crawl/collect data you are legally allowed to access. Always review a website's Terms of Service and `robots.txt`. Be polite with rate limits and identify yourself if required. This code is provided **as-is** for educational and compliant use.

---

## ✨ Features

- 🧩 **Modular “sources”** system – add new sites by implementing a tiny class.
- 🔁 **Deduplication** across sources (by source+url+name+phone).
- 📞 **Phone normalization** to E.164 (+20…).
- 🏙️ **City normalization** via fuzzy matching to a standard Egypt city list.
- 🐢 **Politeness**: concurrency + per-request delay + optional proxies.
- 🧰 **CLI** (Typer): `scrape` and `validate`.
- 📦 **Dockerfile** for reproducible runs.
- 🧪 Works with plain `requests`-style scraping (httpx + selectolax/BS4).

---

## 📂 Repository Layout

```
egy-maintenance-scraper/
├─ src/
│  ├─ cli.py
│  └─ egy_maint_scraper/
│     ├─ __init__.py
│     ├─ config.py
│     ├─ http_client.py
│     ├─ utils.py
│     └─ sources/
│        ├─ base.py
│        └─ example_directory.py
├─ data/                # output CSVs land here (gitignored)
├─ tmp/                 # scratchspace (gitignored)
├─ logs/                # logs (gitignored)
├─ .env.example
├─ requirements.txt
├─ pyproject.toml
├─ Dockerfile
├─ .gitignore
├─ LICENSE (MIT)
└─ README.md
```

---

## 🚀 Quickstart

### 1) Setup a virtualenv

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -U pip
pip install -r requirements.txt
```

### 2) Configure

Copy the example env and adjust if needed:

```bash
cp .env.example .env
# edit .env to set OUTPUT_DIR, CONCURRENCY, DELAY_SECONDS, PROXIES, etc.
```

### 3) Run a scrape

```bash
python -m src.cli scrape -o data/technicians.csv -v
```

> The repository ships with an **example** source at `sources/example_directory.py` using common card-like HTML selectors. Replace `BASE` with a real, permitted domain and adjust selectors. Add more sources by extending `Source` (see below).

### 4) Validate the CSV

```bash
python -m src.cli validate data/technicians.csv
```

---

## 🧱 Data Schema (CSV)

| column   | type   | description                               |
|----------|--------|-------------------------------------------|
| source   | str    | short code of the source implementation   |
| url      | str    | original listing URL                      |
| name     | str    | technician or shop name                   |
| category | str    | type of service (AC, plumbing, etc.)      |
| phone    | str    | phone in E.164 (+20…)                     |
| city     | str    | normalized city if possible               |
| address  | str    | freeform address                          |
| lat      | float  | optional latitude                         |
| lng      | float  | optional longitude                        |

---

## ➕ Adding a New Source

1. Create a new file in `src/egy_maint_scraper/sources/` (e.g. `yellowpages_eg.py`).
2. Implement three small pieces:

```python
from selectolax.parser import HTMLParser
from ..utils import Technician
from .base import Source

class YellowPagesEg(Source):
    @property
    def name(self) -> str:
        return "yellowpages_eg"

    async def seed_urls(self) -> list[str]:
        return [f"https://…?page={i}" for i in range(1, 51)]

    async def parse(self, html: str, url: str):
        tree = HTMLParser(html)
        for card in tree.css("div.card"):
            name = card.css_first(".name").text() if card.css_first(".name") else None
            # …extract phone/city/address
            yield Technician(
                source=self.name, url=url, name=name,
                category="Maintenance", phone="0123…", city="Cairo", address="…",
            )
```

3. Import and register your source in `src/cli.py`:

```python
from egy_maint_scraper.sources.yellowpages_eg import YellowPagesEg
sources = [YellowPagesEg(), …]
```

4. Run `scrape` again.

> 💡 Scraping tips: Be gentle with concurrency/delays, rotate user agents, consider using a `sitemap.xml` or public JSON endpoints. Respect pagination limits and avoid login-only areas.

---

## 🧭 Compliance Checklist

- Check **Terms of Service** for each domain.
- Review **robots.txt** and avoid disallowed paths.
- Throttle requests with `DELAY_SECONDS` and `CONCURRENCY`.
- Avoid PII beyond what’s clearly public.
- Provide attribution if required by the site.

---

## 🐳 Docker (optional)

Build and run inside Docker:

```bash
docker build -t egy-maint-scraper .
docker run --rm -v "$PWD:/app" egy-maint-scraper python -m src.cli scrape -o data/technicians.csv -v
```

---

## 📊 Working with an Existing CSV

If you already have data (e.g., exported manually or from a previous run), drop it in `data/` and validate:

```bash
python -m src.cli validate data/technicians.csv
```

---

## ❓ FAQ

**Q: Can I use Selenium/Playwright?**  
A: Yes. For JS-heavy sites, add a new `Source` that uses Playwright to render pages, then feed the HTML into `parse()`. Keep delays and headless etiquette.

**Q: How do I dedupe across sources?**  
A: We compute a stable ID from `source|url|name|phone`. You can customize this in `utils.py`.

---

## 📝 License

MIT — see `LICENSE`.
