# Prospector — Error Handling & Logging

## Philosophy

Prospector runs unattended on a server. It must record what happened, fail gracefully without losing work, and make failures easy to diagnose from logs.

---

## Log Files

Every run writes to `logs/`.

**Naming convention:**
```
prospector_{profile_name}_{YYYY-MM-DD_HH-MM}.log
```

**Log levels (as implemented):**
- `INFO` — normal operation
- `WARNING` — recoverable issues (no Maps results, finder stub messages, etc.)
- `ERROR` — per-lead scrape failure; pipeline continues
- `CRITICAL` — network down, Maps blocked, missing profile, pipeline stop

Logs go to **file** (DEBUG+) and **console** (INFO+). Warnings and errors are counted for the run summary.

---

## Run Summary

Printed and logged at end of every run by `pipeline.py`:

```
--- Prospector Run Summary ---
Profile:        test_run
Started:        2025-05-18 20:16:18
Finished:       2025-05-18 20:16:36
Duration:       18s

Finder:         3 businesses found
Enricher:       2 websites checked (1 skipped - no URL)
                0 websites live, 2 unreachable
Qualifier:      Skipped (not enabled)
Output:         3 leads written to CSV

Errors:         0 warnings, 0 errors
Output file:    .../output/prospector_test_run_2025-05-18_20-16.csv
------------------------------
```

`--dry-run` omits CSV write; summary notes dry-run.

---

## Error Handling by Stage

### Finder ✅ Implemented

| Situation | Behaviour |
|-----------|-----------|
| No results for query | `WARNING`, continue other queries; empty list if none overall |
| No results at all | `WARNING`, pipeline continues; empty CSV with headers |
| Blocked mid-run (CAPTCHA / sorry page) | `CRITICAL`, return **partial** leads collected so far |
| Network unavailable (`net::`, timeout, etc.) | `CRITICAL`, raise `FinderNetworkError`, pipeline **exits 1** |
| Single place page fails | `ERROR`, skip that listing, continue |

### Enricher ⏳ Stub

| Situation | Planned behaviour |
|-----------|-------------------|
| Website unreachable | `INFO`, `website_live = false`, continue |
| HTTP 404/500 | `INFO`, mark false, continue |
| Timeout | `WARNING`, skip metadata for that lead, continue |

*Current stub:* sets `website_live = false` for all leads without HTTP checks.

### Qualifier (V2)

| Situation | Planned behaviour |
|-----------|-------------------|
| Model unavailable | `CRITICAL`, skip qualification, output unscored |
| Bad AI response | `WARNING`, empty score for that lead |

*Current stub:* pass-through, log "skipped".

### Output ✅ Implemented

| Situation | Behaviour |
|-----------|-----------|
| `output/` missing | Created automatically |
| File write fails | `CRITICAL` (planned fallback to `/tmp/` not yet implemented) |

---

## Partial Saves

If Maps blocks mid-run, the finder returns leads gathered before the block; enricher and output process that partial list.

If the process is killed externally (SIGKILL), no partial CSV is guaranteed — use smaller `--max` on risky runs.

---

## Log Retention

**Planned:** Delete logs older than 30 days automatically.

**Current:** Logs accumulate until manual cleanup. Output CSVs kept until manually deleted.

---

## Future: Run History

`run_history.json` (future) will track runs, profiles, lead counts, and success/failure for a simple health dashboard.
