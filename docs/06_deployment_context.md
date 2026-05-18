# Prospector — Deployment Context

## Hardware

### Server PC (Primary Deployment Target)
- **CPU:** Intel i7
- **RAM:** 16GB (upgrading to 32GB)
- **GPU:** NVIDIA RTX 2070 Super
- **Role:** Runs Prospector, hosts local AI models (Gemma 4B via Ollama, V2), background processing
- **OS:** **Ubuntu 24.04** (primary)

### Main PC (Development)
- **CPU:** Intel i9
- **RAM:** 32GB (upgrading to 64GB)
- **GPU:** NVIDIA RTX 3080
- **Setup:** 3-monitor workstation
- **Role:** Development, Cursor, testing, review of output (Windows also used for dev)

---

## Deployment Model

Prospector runs locally on the server PC (Ubuntu 24.04). It is not deployed to any cloud service. It does not require an internet-facing server. It runs when triggered and stops when done.

**Source repository:** https://github.com/bobgrasscoreum-beep/prospector

Clone on the server:

```bash
cd ~
git clone https://github.com/bobgrasscoreum-beep/prospector.git prospector
cd ~/prospector
```

**V1 execution:** Manual trigger via `pipeline.py` on the command line  
**Future:** Scheduled execution, possible local web trigger

---

## How to Run (V1)

```bash
cd ~/prospector
source venv/bin/activate

python pipeline.py --profile test_run
python pipeline.py --profile maribor_wood --max 50
python pipeline.py --profile maribor_wood --dry-run
```

Entry point is **`pipeline.py`** only (not `prospector.py`).

---

## Environment Setup

### Python Environment
- **Python 3.12+** (minimum; tested on 3.12)
- Virtual environment recommended (`venv`)
- Dependencies in `requirements.txt`

### Required Installations
- Python 3.12+
- pip
- **Playwright** + Chromium (`playwright install chromium`) — required for Google Maps finder
- **Ollama** (V2 local AI only) — already on server for Gemma

### First-Time Setup (Ubuntu 24.04)

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv

cd ~/prospector
python3.12 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
playwright install chromium

python pipeline.py --profile test_run --dry-run
```

### First-Time Setup (Windows dev)

```powershell
cd D:\path\to\prospector
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python pipeline.py --profile test_run --dry-run
```

---

## Configuration

Global settings in `config.py`, overridable via `.env`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEFAULT_MAX_RESULTS` | `100` | Cap when profile omits `max_results` |
| `HEADLESS` | `true` | Playwright headless browser |
| `REQUEST_DELAY` | `2` | Seconds between Maps navigations |

Paths (`profiles/`, `output/`, `logs/`) are fixed relative to project root in `config.py`.

API keys (V2 BYOK) go in `.env` — never committed (see `.gitignore`).

---

## Network Considerations

- Outbound HTTPS to Google Maps and (when enricher is implemented) target websites
- No inbound connections required in V1
- Rate limiting: `REQUEST_DELAY` between finder page loads
- Residential IP may hit Google blocks on large runs — finder returns partial results and logs CRITICAL if blocked mid-run

---

## Accessing Output

CSV files: `~/prospector/output/`
Logs: `~/prospector/logs/`

From the main PC:
- SSH/SFTP
- Local network share
- Shared folder

---

## Future Deployment Considerations

- Simple local web UI to trigger runs and view output (V4)
- Docker containerization for client deployments
- Cloud option with authentication if productized
