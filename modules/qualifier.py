"""Qualifier stage — AI scoring (V2 only; stub passes leads through in V1)."""

from __future__ import annotations

import logging
from typing import Any


def run(leads: list[dict[str, Any]], profile: dict[str, Any], log: logging.Logger) -> list[dict[str, Any]]:
    """V1: qualification disabled; leads pass through unchanged."""
    log.info("Qualifier: skipped (not enabled in V1)")
    return leads
