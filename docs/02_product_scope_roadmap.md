# Prospector — Product Scope & Roadmap

## V1 — The Working Pipeline

### In Scope

| Feature | Status |
|---------|--------|
| Google Maps scraper (keyword + location) | **Done** — `modules/finder.py`, Playwright |
| Target Profile system (JSON in `profiles/`) | **Done** |
| Profile filters (`require_website`, `require_phone`, `min_reviews`, `exclude_keywords`) | **Done** — applied in finder |
| CSV output (doc 05 schema) | **Done** — `modules/output.py` |
| CLI via `pipeline.py` (`--profile`, `--max`, `--dry-run`) | **Done** |
| Basic logging + run summary | **Done** |
| Website live check + basic page metadata | **Not yet** — enricher is still a stub |
| Deduplication (name + address) | **Done** — in finder |

### Explicitly Out of Scope for V1

- AI qualification (V2)
- LinkedIn scraping
- Automated scheduling / cron jobs (manual trigger only)
- Direct Lynqd integration
- Web UI or dashboard
- Email verification
- Any cloud deployment

### Definition of V1 Done

You can run Prospector with a target profile (e.g. "wood companies, Maribor"), it finds businesses from Google Maps, checks whether websites are reachable, and outputs a clean CSV. No errors. No manual cleanup needed.

**Remaining for V1:** Implement the enricher (HTTP checks + optional title/description from HTML).

---

## V2 — AI Qualification Layer

- Plug in local Gemma model or BYOK external model
- Analyze each lead: does this business match the ideal client profile?
- Score or tag leads (hot / warm / skip)
- Deeper enrichment: pull basic info from their website (what they do, contact info, tech stack hints)
- Still outputs CSV, now with qualification columns added

---

## V3 — Expanded Sources & Automation

- Additional scrapers: Yellow Pages, local business directories, industry-specific sites
- Scheduled runs: define a profile, set a schedule, leads appear automatically
- Stronger duplicate detection across runs (finder already dedupes within a run)
- Direct Lynqd integration: output feeds directly into Lynqd client list

---

## V4 — Product Mode

- Simple web UI for non-technical users
- Profile management through interface (not just config files)
- Multi-user support
- Packaged for sale or white-label to other agencies

---

## Parked Ideas (No Version Assigned Yet)

- LinkedIn integration (requires careful approach — heavily protected)
- Email finding and verification
- Social signal detection (is this business active? when did they last post?)
- CRM sync (HubSpot, Notion, Airtable)
- Webhook output (trigger Lynqd automatically when new leads arrive)

---

## Scope Discipline

When building, if a feature isn't listed in the current version scope — park it. Add it to the parked list. Don't build it now. The goal of each version is a working, stable, useful thing — not a complete thing.
