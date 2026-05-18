"""Output stage — writes the final lead list to CSV."""

from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from config import OUTPUT_DIR

CSV_FIELDS = [
    "id",
    "name",
    "category",
    "address",
    "city",
    "country",
    "phone",
    "website",
    "website_live",
    "google_maps_url",
    "rating",
    "review_count",
    "source",
    "profile_used",
    "found_at",
    "notes",
]


def _output_filename(profile_name: str, run_started: datetime) -> str:
    stamp = run_started.strftime("%Y-%m-%d_%H-%M")
    return f"prospector_{profile_name}_{stamp}.csv"


def _format_website_live(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return ""


def _row_for_csv(lead: dict[str, Any], index: int) -> dict[str, str]:
    row: dict[str, str] = {}
    for field in CSV_FIELDS:
        if field == "id":
            row[field] = str(lead.get("id") or f"PRO-{index:04d}")
        elif field == "website_live":
            row[field] = _format_website_live(lead.get("website_live"))
        else:
            value = lead.get(field)
            row[field] = "" if value is None else str(value)
    return row


def run(
    leads: list[dict[str, Any]],
    profile: dict[str, Any],
    log: logging.Logger,
    *,
    dry_run: bool = False,
    run_started: datetime | None = None,
) -> Path | None:
    """Write leads to CSV, or skip file write in dry-run mode."""
    profile_name = profile.get("name", "unknown")
    started = run_started or datetime.now()

    if dry_run:
        log.info("Output (dry-run): would write %d leads - file not saved", len(leads))
        return None

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = _output_filename(profile_name, started)
    path = OUTPUT_DIR / filename

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for index, lead in enumerate(leads, start=1):
            writer.writerow(_row_for_csv(lead, index))

    log.info("Output: wrote %d leads to %s", len(leads), path)
    return path
