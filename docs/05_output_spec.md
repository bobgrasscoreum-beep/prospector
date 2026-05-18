# Prospector — Output Specification

## Output Format: CSV

V1 output is a single CSV file per run. One row per business. Clean headers. UTF-8 encoding.

---

## V1 Fields

| Field | Description | Example | Required | Set by |
|-------|-------------|---------|----------|--------|
| `id` | Unique row identifier | `PRO-0001` | Yes | Output (auto) |
| `name` | Business name | `Mizar Kovač d.o.o.` | Yes | Finder |
| `category` | Business category from Maps | `Woodworking` | If available | Finder |
| `address` | Full address | `Ulica 14, 2000 Maribor` | If available | Finder |
| `city` | City | `Maribor` | If available | Finder |
| `country` | Country | `Slovenia` | Yes* | Finder |
| `phone` | Phone number | `+386 2 123 4567` | If available | Finder |
| `website` | Website URL | `https://kovac-mizar.si` | If available | Finder |
| `website_live` | Is website reachable? | `true` / `false` | Yes | Enricher |
| `google_maps_url` | Direct link to Maps listing | `https://www.google.com/maps/place/...` | If available | Finder |
| `rating` | Google Maps rating | `4.2` | If available | Finder |
| `review_count` | Number of reviews | `17` | If available | Finder† |
| `source` | Where this lead was found | `google_maps` | Yes | Finder |
| `profile_used` | Which profile generated this | `slovenia_wood` | Yes | Finder |
| `found_at` | ISO timestamp of discovery | `2025-05-18T14:32:00` | Yes | Finder |
| `notes` | Flags or manual notes | `` | No | — |

\*Country may be blank if it cannot be inferred; prefer profiles with explicit country in `locations`.

†`review_count` is often empty when Google does not expose it in the page DOM.

---

## V2 Additional Fields (AI Qualification)

| Field | Description | Example |
|-------|-------------|---------|
| `ai_score` | Qualification score 1-10 | `7` |
| `ai_tag` | Hot / Warm / Skip | `warm` |
| `ai_reasoning` | Why this score was given | `"Small local manufacturer..."` |
| `website_summary` | AI summary of what they do | `"Custom wooden furniture..."` |

---

## File Naming Convention

```
prospector_{profile_name}_{YYYY-MM-DD_HH-MM}.csv
```

Example:
```
prospector_slovenia_wood_2025-05-18_14-32.csv
```

---

## Output Location

All CSV files are saved to `output/` in the Prospector root directory. Created automatically if missing.

---

## Lynqd Compatibility

When Prospector connects to Lynqd (V3), CSV fields should map cleanly to Lynqd client input:

- `name` → Client name
- `website` → Client website
- `phone` → Contact phone
- `address` / `city` → Location context
- `category` → Business type (helps Lynqd select service presets)

Unused fields are ignored on import.

---

## Data Quality Rules

- Empty fields are left blank — never `"N/A"` or `"unknown"`
- Website URLs include protocol (`https://` or `http://`); Google redirect URLs are unwrapped
- Phone numbers kept as-is from Google Maps — no reformatting in V1
- Duplicates (same name + address) removed in finder before output
- `website_live` is always `true` or `false` in CSV (enricher responsibility)
- Encoding: UTF-8 always
