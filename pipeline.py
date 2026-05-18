#!/usr/bin/env python3
"""Prospector V1 — main pipeline runner."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from config import LOG_DIR, PROFILES_DIR
from modules import run_enricher, run_finder, run_output, run_qualifier
from modules.finder import FinderNetworkError


@dataclass
class RunStats:
    finder_count: int = 0
    enricher_checked: int = 0
    enricher_skipped_no_url: int = 0
    enricher_live: int = 0
    enricher_unreachable: int = 0
    qualifier_skipped: bool = True
    output_count: int = 0
    warnings: int = 0
    errors: int = 0
    output_file: Path | None = None


class LogCounterHandler(logging.Handler):
    """Count WARNING and ERROR records for the run summary."""

    def __init__(self) -> None:
        super().__init__()
        self.warnings = 0
        self.errors = 0

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno >= logging.ERROR:
            self.errors += 1
        elif record.levelno >= logging.WARNING:
            self.warnings += 1


def _log_filename(profile_name: str, started: datetime) -> str:
    stamp = started.strftime("%Y-%m-%d_%H-%M")
    return f"prospector_{profile_name}_{stamp}.log"


def setup_logging(profile_name: str, started: datetime) -> tuple[logging.Logger, LogCounterHandler]:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / _log_filename(profile_name, started)

    counter = LogCounterHandler()
    counter.setLevel(logging.WARNING)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.DEBUG)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
    root.addHandler(counter)

    log = logging.getLogger("prospector")
    log.info("Log file: %s", log_path)
    return log, counter


def load_profile(profile_name: str) -> dict:
    path = PROFILES_DIR / f"{profile_name}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Profile not found: {path}")
    with path.open(encoding="utf-8") as handle:
        profile = json.load(handle)
    if profile.get("name") != profile_name:
        logging.getLogger("prospector").warning(
            "Profile file name (%s) does not match profile.name (%s)",
            profile_name,
            profile.get("name"),
        )
    return profile


def apply_max_override(profile: dict, max_results: int | None) -> dict:
    if max_results is None:
        return profile
    merged = dict(profile)
    merged["max_results"] = max_results
    return merged


def _count_enrichment(leads: list[dict]) -> tuple[int, int, int, int]:
    checked = 0
    skipped_no_url = 0
    live = 0
    unreachable = 0
    for lead in leads:
        website = (lead.get("website") or "").strip()
        if not website:
            skipped_no_url += 1
            continue
        checked += 1
        if lead.get("website_live") is True:
            live += 1
        else:
            unreachable += 1
    return checked, skipped_no_url, live, unreachable


def _format_duration(seconds: float) -> str:
    total = int(seconds)
    minutes, secs = divmod(total, 60)
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def print_run_summary(
    profile_name: str,
    started: datetime,
    finished: datetime,
    stats: RunStats,
    *,
    dry_run: bool,
) -> None:
    duration = _format_duration((finished - started).total_seconds())
    lines = [
        "",
        "--- Prospector Run Summary ---",
        f"Profile:        {profile_name}",
        f"Started:        {started.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Finished:       {finished.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Duration:       {duration}",
        "",
        f"Finder:         {stats.finder_count} businesses found",
        (
            f"Enricher:       {stats.enricher_checked} websites checked "
            f"({stats.enricher_skipped_no_url} skipped - no URL)"
        ),
        f"                {stats.enricher_live} websites live, {stats.enricher_unreachable} unreachable",
        "Qualifier:      Skipped (not enabled)",
    ]
    if dry_run:
        lines.append(f"Output:         Dry-run - {stats.output_count} leads (file not saved)")
        lines.append("")
        lines.append(f"Errors:         {stats.warnings} warnings, {stats.errors} errors")
        lines.append("Output file:    (dry-run - not written)")
    else:
        lines.append(f"Output:         {stats.output_count} leads written to CSV")
        lines.append("")
        lines.append(f"Errors:         {stats.warnings} warnings, {stats.errors} errors")
        if stats.output_file:
            lines.append(f"Output file:    {stats.output_file}")
        else:
            lines.append("Output file:    (none)")
    lines.append("------------------------------")
    summary = "\n".join(lines)
    print(summary)
    logging.getLogger("prospector").info("\n%s", summary)


def run_pipeline(profile_name: str, *, max_results: int | None = None, dry_run: bool = False) -> int:
    started = datetime.now()
    log, counter = setup_logging(profile_name, started)

    try:
        profile = load_profile(profile_name)
        profile = apply_max_override(profile, max_results)
        log.info("Starting pipeline for profile: %s", profile_name)
        if dry_run:
            log.info("Dry-run mode: output file will not be written")

        stats = RunStats()

        leads = run_finder(profile, log)
        stats.finder_count = len(leads)

        leads = run_enricher(leads, profile, log)
        checked, skipped, live, unreachable = _count_enrichment(leads)
        stats.enricher_checked = checked
        stats.enricher_skipped_no_url = skipped
        stats.enricher_live = live
        stats.enricher_unreachable = unreachable

        leads = run_qualifier(leads, profile, log)
        stats.qualifier_skipped = True

        output_path = run_output(
            leads,
            profile,
            log,
            dry_run=dry_run,
            run_started=started,
        )
        stats.output_count = len(leads)
        stats.output_file = output_path

        stats.warnings = counter.warnings
        stats.errors = counter.errors

        finished = datetime.now()
        print_run_summary(profile_name, started, finished, stats, dry_run=dry_run)
        return 0

    except FinderNetworkError as exc:
        log.critical("Pipeline stopped: %s", exc)
        return 1
    except FileNotFoundError as exc:
        log.critical("%s", exc)
        return 1
    except json.JSONDecodeError as exc:
        log.critical("Invalid profile JSON: %s", exc)
        return 1
    except Exception as exc:
        log.critical("Pipeline failed: %s", exc, exc_info=True)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Prospector — modular lead generation pipeline")
    parser.add_argument("--profile", required=True, help="Target profile name (without .json)")
    parser.add_argument("--max", type=int, dest="max_results", help="Override max_results from profile")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline without writing output CSV",
    )
    args = parser.parse_args()
    return run_pipeline(args.profile, max_results=args.max_results, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
