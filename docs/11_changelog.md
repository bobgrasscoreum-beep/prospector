# Prospector — Changelog

*This file is updated by Cursor after every meaningful change. Each entry should include the version, date, and a plain-English description of what changed and why.*

---

## Format

```
## [version] — YYYY-MM-DD
### Added
- New features or files added

### Changed
- Modifications to existing functionality

### Fixed
- Bug fixes

### Removed
- Anything deleted or deprecated

### Notes
- Context, decisions made, things to remember
```

---

## [0.3.0] — 2025-05-18

### Added
- Google Maps finder using Playwright (`modules/finder.py`)
- Extracts name, address, phone, website, rating, review count, category, Maps URL
- Profile filters: `require_website`, `require_phone`, `min_reviews`, `exclude_keywords`
- Deduplication by name + address; `REQUEST_DELAY` between navigations
- Graceful handling: no results (warning), blocked mid-run (critical + partial results), network failure (critical + stop)

### Changed
- `pipeline.py` stops on `FinderNetworkError`
- All 11 docs + `README.md` updated to match implementation (entry point, Python 3.12+, module status, deployment)

---

## [0.2.0] — 2025-05-18

### Added
- Project folder structure per architecture doc (`profiles/`, `modules/`, `output/`, `logs/`)
- `pipeline.py` CLI entry point (`--profile`, `--max`, `--dry-run`)
- Stub modules: `finder`, `enricher`, `qualifier`, `output`
- `config.py` with paths and environment-based settings
- `requirements.txt`, `.gitignore`, `README.md`
- `profiles/test_run.json` for quick validation runs
- Run logging to `logs/` and end-of-run summary (per error-handling spec)
- CSV output writer with V1 field schema (stub finder returns no leads until implemented)

### Notes
- Entry point is `pipeline.py` everywhere (not `prospector.py`).
- Python 3.12+ required.
- Flat `modules/*.py` layout with `modules/__init__.py` for clean imports.

---

## [0.1.0] — 2025-05-18

### Added
- Initial project documentation (11 files)
- Project structure defined
- Architecture designed
- Target profile system designed
- Output CSV spec defined

### Notes
- Project initiated. Documentation-first approach before any code is written.
- Building will begin in Cursor using this documentation as full context.
- V1 goal: working pipeline that finds businesses via Google Maps and outputs clean CSV.
