"""Enricher stage — adds website and metadata fields to raw leads."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def run(leads: list[dict[str, Any]], profile: dict[str, Any], log: logging.Logger) -> list[dict[str, Any]]:
    """
    Enrich leads with website_live and related fields.

    V1 skeleton: sets website_live=false when no URL; true/false stub otherwise.
    Failed enrichment never drops a lead.
    """
    if not leads:
        log.info("Enricher: no leads to enrich")
        return leads

    enriched: list[dict[str, Any]] = []
    for lead in leads:
        row = dict(lead)
        website = (row.get("website") or "").strip()
        if not website:
            row["website_live"] = False
            log.debug("Enricher: no website for %s", row.get("name", "?"))
        else:
            # Real HTTP checks will replace this stub.
            row["website_live"] = False
        enriched.append(row)

    log.info("Enricher (stub): processed %d leads", len(enriched))
    return enriched
