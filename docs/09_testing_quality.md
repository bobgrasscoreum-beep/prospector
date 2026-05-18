# Prospector — Testing & Quality

*Lightweight version — to be expanded as the project matures.*

---

## What "Good Output" Looks Like

A successful Prospector run produces a CSV where:
- Every row has at minimum: `name`, `source`, `profile_used`, `found_at`
- No duplicate rows (same name + address) within the run
- Website URLs use `http://` or `https://` when present
- `website_live` is `true` or `false` — never empty *(once enricher is implemented)*
- UTF-8 displays correctly (š, č, ž, etc.)

---

## Quick Validation Commands

After code changes:

```bash
# Wiring only (no CSV)
python pipeline.py --profile test_run --dry-run

# Small live Maps run
python pipeline.py --profile test_run --max 5
```

Expect: exit code 0, log in `logs/`, CSV in `output/` (unless dry-run).

---

## Manual Spot Checks (V1)

After each run:
- [ ] Open CSV — loads cleanly in Excel/LibreOffice
- [ ] Sample 5 rows — businesses exist on Google Maps (`google_maps_url`)
- [ ] Sample 3 `website` values — URLs look correct (live check pending enricher)
- [ ] No obvious duplicates
- [ ] Lead count reasonable (not 0 unless search is empty; not absurdly high for `--max`)

---

## Test Profile

Included at `profiles/test_run.json`:

```json
{
  "name": "test_run",
  "keywords": ["kavarna", "coffee"],
  "locations": ["Maribor"],
  "max_results": 10
}
```

Use `--max 3` for faster smoke tests.

---

## Known Quality Risks

| Risk | Notes |
|------|-------|
| Google Maps DOM changes | May break selectors; monitor finder errors in logs |
| `review_count` often empty | Google does not always expose count in HTML |
| Country inference | City-only profiles rely on Slovenian postal codes in address |
| Maps blocks / CAPTCHA | More likely on large runs or datacenter IPs; partial results returned |
| `website_live` | Stub always `false` until enricher HTTP checks ship |
| Stale or incomplete listings | Maps data is user-maintained |

---

## Future Testing Plans

- Unit tests per module (finder parsing, filters, CSV schema)
- CSV schema validation on every output
- Regression suite before releases
- AI qualification quality review (V2)
