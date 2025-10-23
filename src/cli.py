from __future__ import annotations
import asyncio, os, logging
import typer
from dotenv import load_dotenv
from typing import Optional
from egy_maint_scraper.aggregator import Aggregator
from egy_maint_scraper.sources.example_directory import ExampleDirectory
from egy_maint_scraper.config import settings

app = typer.Typer(help="Egypt Maintenance Technicians Harvester")

def setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

@app.command()
def scrape(output: str = typer.Option("data/technicians.csv", "--output", "-o", help="Output CSV path"),
           verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logs")):
    """Run all enabled sources and export a deduplicated CSV."""
    load_dotenv()
    setup_logging(verbose)
    sources = [
        ExampleDirectory(),
        # Add more Source implementations here
    ]
    aggr = Aggregator(sources)
    technicians = asyncio.run(aggr.run())
    typer.echo(f"Collected {len(technicians)} unique records") 
    count = aggr.export_csv(output)
    typer.echo(f"Exported {count} rows to {output}")

@app.command()
def validate(csv_path: str = typer.Argument("data/technicians.csv")):
    """Validate CSV columns and show a quick summary."""
    import pandas as pd
    req_cols = ["source","url","name","category","phone","city","address","lat","lng"]
    df = pd.read_csv(csv_path)
    missing = [c for c in req_cols if c not in df.columns]
    if missing:
        typer.echo(f"ERROR: Missing columns: {missing}")
        raise SystemExit(1)
    typer.echo(df.head().to_string())
    typer.echo(f"Rows: {len(df)} | Unique phones: {df['phone'].nunique(dropna=True)}") 

if __name__ == "__main__":
    app()
