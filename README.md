# Prospector

Modular, self-hosted lead generation pipeline. V1 finds businesses on Google Maps, enriches them (website checks — in progress), and writes structured CSV output.

**Requirements:** Python **3.12+**, Ubuntu 24.04 (or any OS with Python 3.12).

## Quick start

```bash
cd /path/to/prospector

python3.12 -m venv venv
source venv/bin/activate   # Linux / macOS
# venv\Scripts\activate    # Windows

pip install -r requirements.txt
playwright install chromium

python pipeline.py --profile test_run --dry-run
```

## Usage

```bash
# Dry run — logs and summary only, no CSV written
python pipeline.py --profile test_run --dry-run

# Full run (writes CSV to output/)
python pipeline.py --profile test_run

# Override max results from profile
python pipeline.py --profile test_run --max 50
```

Entry point is always **`pipeline.py`** (not `prospector.py`).

## Project layout

```
prospector/
  pipeline.py       # CLI and pipeline runner
  config.py         # paths and global settings
  profiles/         # target profile JSON files
  modules/
    __init__.py
    finder.py       # Google Maps (Playwright) — implemented
    enricher.py     # website checks — stub
    qualifier.py    # AI scoring — stub (V2)
    output.py       # CSV writer — implemented
  output/           # generated CSV files
  logs/             # run logs
  docs/             # project documentation (11 files)
```

## Configuration

Optional `.env` in the project root (see `config.py` for defaults):

```
DEFAULT_MAX_RESULTS=100
HEADLESS=true
REQUEST_DELAY=2
```

API keys for V2 belong in `.env` only — never commit them.

## Documentation

See [`docs/`](docs/) for architecture, profiles, output spec, deployment, and policies.

## Implementation status (V1)

| Component | Status |
|-----------|--------|
| Pipeline runner (`pipeline.py`) | Done |
| Target profiles (`profiles/*.json`) | Done |
| Google Maps finder (Playwright) | Done |
| Website enricher (HTTP + metadata) | Not yet |
| Qualifier (AI) | V2 — stub only |
| CSV output | Done |
| Logging + run summary | Done |
