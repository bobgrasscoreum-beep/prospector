# Prospector — Target Profile System

## What Is a Target Profile?

A target profile is a configuration file that tells Prospector what kind of businesses to look for. It is the only thing you need to change to run a completely different search.

Profiles are saved as individual JSON files in `profiles/`. You can have as many as you want. You call one by name (without `.json`) when you run Prospector.

---

## Profile Parameters

### Required

| Parameter | Description | Example |
|-----------|-------------|---------|
| `name` | Profile identifier (should match filename) | `"maribor_wood"` |
| `keywords` | What to search for (each combined with each location) | `["woodworking", "carpenter", "lesarstvo"]` |
| `locations` | Where to search | `["Maribor", "Slovenija"]` |

### Optional Filters *(enforced in finder)*

| Parameter | Description | Example |
|-----------|-------------|---------|
| `require_website` | Only include businesses with a website URL | `true` |
| `require_phone` | Only include businesses with a phone number | `false` |
| `exclude_keywords` | Skip businesses with these words in name (case-insensitive) | `["hobi", "hobby"]` |
| `min_reviews` | Minimum Google Maps review count | `5` |
| `language` | Browser locale for Maps UI (`"sl"` → `sl-SI`, else `en-US`) | `"sl"` or `"en"` |
| `max_results` | Cap on total leads per run (across all keyword/location pairs) | `100` |

CLI override: `python pipeline.py --profile NAME --max 50` overrides `max_results` for that run only.

### AI Qualifier Parameters *(V2 — not used in V1)*

| Parameter | Description | Example |
|-----------|-------------|---------|
| `ideal_client_description` | Plain text description of ideal client | `"A small manufacturing company..."` |
| `qualification_model` | Which model to use | `"gemma"` or `"gpt-4o"` |
| `min_score` | Minimum score to include in output | `6` |

---

## Example Profile Files

### Quick test (included in repo)
```json
{
  "name": "test_run",
  "keywords": ["kavarna", "coffee"],
  "locations": ["Maribor"],
  "max_results": 10
}
```

### Broad — Any business with a website in Maribor
```json
{
  "name": "maribor_any_website",
  "keywords": ["podjetje", "storitve", "company", "services"],
  "locations": ["Maribor"],
  "require_website": true,
  "max_results": 200
}
```

### Niche — Wood companies Slovenia
```json
{
  "name": "slovenia_wood",
  "keywords": ["woodworking", "carpenter", "furniture", "lesarstvo", "mizar", "pohištvo"],
  "locations": ["Slovenija"],
  "require_website": false,
  "max_results": 150
}
```

### Teras AI ideal client — Small businesses needing AI
```json
{
  "name": "teras_ideal_client",
  "keywords": ["marketing agency", "consulting", "logistics", "manufacturing", "retail"],
  "locations": ["Maribor", "Ljubljana", "Celje"],
  "require_website": true,
  "min_reviews": 3,
  "max_results": 100
}
```

---

## How Profiles Are Used

1. Save `profiles/{name}.json`
2. Run: `python pipeline.py --profile {name}`
3. Finder reads keywords, locations, and filters; searches Google Maps
4. Enricher and output use `profile_used` from the profile `name` field
5. CSV and log files are named with profile name + timestamp

---

## Profile Design Philosophy

Profiles should be written by a human, in plain terms. The Finder turns `keywords` + `locations` into Google Maps search queries — the profile does not contain scraper selectors or URLs.

A non-technical user should be able to create a new profile by copying an existing one and changing keywords and locations.

---

## Country and City Inference

When `locations` is only a city (e.g. `"Maribor"`), the finder infers **country** from the address when it matches Slovenian postal format (e.g. `2000 Maribor` → `Slovenia`). For country-wide searches, include `"Slovenija"` or `"Slovenia"` in `locations` when possible.

---

## Future Profile Features

- Profile inheritance: base profile + overrides
- Profile templates: "local service business", "e-commerce", "manufacturer"
- Profile sharing: export/import profiles between Prospector instances
- UI for profile creation (V4)
