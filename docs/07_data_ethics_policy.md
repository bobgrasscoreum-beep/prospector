# Prospector — Data & Ethics Policy

## Overview

Prospector collects publicly available business information. This document outlines what data is collected, how it is handled, and the legal and ethical boundaries the system operates within.

---

## What Data Is Collected

Prospector collects only **publicly visible business information** from Google Maps listings (and, when implemented, publicly accessible website pages):

- Business name
- Business address
- Phone number (if publicly listed on Maps)
- Website URL (if listed on Maps)
- Google Maps rating and review count (when shown)
- Business category

Prospector does **not** collect:

- Personal names of individuals (unless listed as the business name on Maps)
- Private email addresses
- Any data behind login walls
- Any data from private or restricted sources

---

## GDPR Considerations

Teras AI operates from Slovenia (EU). GDPR applies.

### Key Points

**Business data vs personal data**
GDPR primarily protects personal data. Data about a company entity is generally not personal data. Data about sole traders where a personal name and personal phone are the business contact **is personal data**.

### Our Approach

- Prospector targets businesses, not individuals
- Output used for legitimate B2B outreach only
- Do not contact individuals in a personal capacity using business listings
- Do not retain lead data longer than needed
- Delete CSVs and logs when no longer required

### Legitimate Interest Basis
B2B outreach to businesses may rely on legitimate interest when outreach is relevant, an opt-out exists, and data is not kept longer than necessary.

---

## Ethical Scraping Principles

**Rate limiting**
Implemented via `REQUEST_DELAY` in `config.py` (default 2 seconds between Maps page navigations). Do not lower aggressively on production runs.

**Respect robots.txt**
Website enrichment (planned in `enricher.py`) should respect `robots.txt` for target sites. Google Maps is accessed via browser automation for listing data only.

**No fake identity**
Prospector does not impersonate users or use deceptive CAPTCHA bypass. If Google blocks the session, the run stops or returns partial results.

**No private data**
Pages requiring login are not accessed.

---

## Data Storage

- All lead data stored locally (`output/`, `logs/`)
- V1 finder does not send lead data to third-party APIs
- V2 AI calls may send business descriptions to a chosen model — not raw contact dumps
- Output CSVs are business-sensitive; restrict filesystem access on the server
- API keys in `.env` only — never in git

---

## When Productized

If Prospector is offered to clients:
- Client data stays with the client
- Terms of use provided
- Clients responsible for their own GDPR compliance in how they use output

---

## Review Schedule

Review this policy when:
- A new data source is added
- The product is offered externally
- GDPR guidance changes materially
