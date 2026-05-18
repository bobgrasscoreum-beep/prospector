# Prospector — Security

*Lightweight version — to be expanded if/when Prospector becomes a multi-user or hosted product.*

---

## Current Threat Model

Prospector V1 is a local tool on a private server. Main risks:

1. API keys exposed in code or version control (V2+)
2. Output CSVs accessed by unintended parties on the network
3. Unauthorized server login
4. Compromised Playwright/browser fetching malicious pages (low risk for Maps + known URLs)

---

## API Key Handling

- Keys only in `.env`
- `.env` in `.gitignore` — never commit
- No keys in source files
- Verify `.env` excluded before sharing repo or screenshots

Example `.env` (V2):
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
```

V1 finder uses **no API keys** — Playwright only.

---

## Dependencies

- Keep `pip` packages updated (`playwright`, `requests`, etc.)
- Run `playwright install chromium` after Playwright upgrades
- Review `requirements.txt` periodically

---

## Output Data

- CSVs in `output/` on the server
- Local network access only in V1
- Do not upload CSVs to public cloud without review
- Delete when no longer needed

---

## Server Access

- Strong login password on server
- SSH: key-based auth preferred over password-only
- Do not expose Prospector or an open browser debug port to the public internet
- `HEADLESS=true` default reduces attack surface vs visible browser on shared machines

---

## Future Security Considerations

When productized:
- User authentication for web UI
- Rate limiting on API endpoints
- Audit log of runs
- Encryption at rest for stored leads
- Regular dependency patching in CI
