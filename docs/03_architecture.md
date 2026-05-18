# Prospector — Architecture

## Pipeline Overview

Prospector is a linear pipeline. Data flows in one direction through independent stages. Each stage has a defined input and a defined output. Stages do not talk to each other directly — they pass data forward via `pipeline.py`.

```
[Target Profile]     profiles/{name}.json
      ↓
[Finder Module]      modules/finder.py      ← Google Maps (Playwright)
      ↓
[Enricher Module]    modules/enricher.py    ← stub: sets website_live=false
      ↓
[Qualifier Module]   modules/qualifier.py   ← stub (V2)
      ↓
[Output Module]      modules/output.py      ← CSV
      ↓
[CSV / Output File]  output/
```

---

## Stage Descriptions

### 1. Target Profile
**What it is:** A JSON file in `profiles/` that defines what to look for.
**Input:** User-defined parameters
**Output:** Dict passed to each module by the pipeline runner
**Details:** See Doc 04 — Target Profile System

---

### 2. Finder Module ✅ Implemented
**What it is:** The scraper. Finds businesses matching the profile on Google Maps.
**Implementation:** `modules/finder.py` — Playwright (Chromium), sync API
**Input:** Target profile (`keywords`, `locations`, filters, `max_results`)
**Output:** List of lead dicts (name, address, phone, website, rating, `google_maps_url`, `source`, `profile_used`, `found_at`, etc.)

**V1 sources:**
- Google Maps (primary) — live

**Future sources:**
- Local business directories
- Yellow Pages Slovenia
- Industry-specific sites

**Behaviour:**
- Builds queries as `{keyword} {location}` for each keyword × location pair
- Scrolls the Maps results feed; visits each place page for details
- Respects `REQUEST_DELAY` from `config.py` between navigations
- Deduplicates by name + address; applies profile filters before returning
- On block: logs CRITICAL, returns partial results. On network failure: raises `FinderNetworkError`, pipeline stops.

**Key principle:** The Finder just finds. It does not set `website_live` (enricher does).

---

### 3. Enricher Module ⏳ Stub
**What it is:** Takes raw leads and adds more information.
**Implementation:** `modules/enricher.py` — placeholder; sets `website_live = false` for all leads
**Input:** Raw lead list from Finder
**Output:** Enriched lead list

**V1 enrichment (planned):**
- Website live check (HTTP reachable?)
- Basic metadata from website (title tag, description tag)

**Key principle:** Enrichment is additive. If enrichment fails for a lead, the lead still passes through with empty or false enrichment fields.

---

### 4. Qualifier Module *(V2 — stub in V1)*
**What it is:** AI-powered scoring and filtering layer.
**Implementation:** `modules/qualifier.py` — pass-through; logs "skipped"
**Input:** Enriched lead list
**Output:** Same list (unscored in V1)

**Key principle:** AI-optional. If disabled, leads pass through unscored.

---

### 5. Output Module ✅ Implemented
**What it is:** Formats and saves the final lead list.
**Implementation:** `modules/output.py` — stdlib `csv`, UTF-8
**Input:** Processed lead list
**Output:** `output/prospector_{profile}_{timestamp}.csv`
**Details:** Doc 05 — Output Spec

---

## How Modules Connect

`pipeline.py` calls each module in sequence:

```python
leads = run_finder(profile, log)
leads = run_enricher(leads, profile, log)
leads = run_qualifier(leads, profile, log)
run_output(leads, profile, log, dry_run=..., run_started=...)
```

Imports are centralized in `modules/__init__.py`. No stage mutates another stage's internal state.

---

## Execution Model

**V1:** Command line — manual trigger only.

```bash
python pipeline.py --profile maribor_wood
python pipeline.py --profile maribor_wood --max 50
python pipeline.py --profile maribor_wood --dry-run
```

**Future:** Scheduled runs, web trigger, API endpoint.

---

## Folder Structure (Current)

```
/prospector
  pipeline.py          ← CLI entry point (only entry point)
  config.py            ← paths, HEADLESS, REQUEST_DELAY, etc.
  requirements.txt
  README.md
  .gitignore
  /profiles            ← target profile JSON files
  /modules
    __init__.py
    finder.py
    enricher.py
    qualifier.py
    output.py
  /output              ← generated CSV files
  /logs                ← run logs
  /docs                ← 11 documentation files
```

---

## Technology Choices (Confirmed)

| Area | Choice |
|------|--------|
| Language | Python **3.12+** |
| Maps scraping | **Playwright** (Chromium), headless via `HEADLESS` in config |
| Website fetching (enricher) | **requests** + **BeautifulSoup** (planned) |
| CSV | stdlib **csv** module (no pandas required) |
| Profiles | **JSON** in `profiles/` |
| Config | `config.py` + optional **`.env`** via python-dotenv |
| AI (V2) | Ollama local API or BYOK HTTP calls |

---

## Exceptions (Finder)

| Exception | Meaning | Pipeline behaviour |
|-----------|---------|-------------------|
| `FinderNetworkError` | Cannot reach Google Maps | CRITICAL log, exit code 1 |
| `FinderBlockedError` (internal) | CAPTCHA / unusual traffic | CRITICAL log, return partial leads |
