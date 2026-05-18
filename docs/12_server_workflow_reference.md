# Prospector — Server & Workflow Reference

*This document is the "pick it back up" guide. If you've been away from this project, start here.*

---

## The Setup in One Paragraph

Prospector runs on a local Ubuntu 24.04 server PC. You develop and trigger it from your main Windows PC using SSH over the local network. The server has Python 3.12, Playwright, Ollama with Gemma 4, and the Prospector codebase. You never need to sit at the server — everything is done remotely via SSH or by pushing code from Cursor via GitHub.

---

## Your Two Machines

| Machine | Role | OS |
|---------|------|----|
| Main PC (i9, RTX 3080, 32GB) | Development, Cursor, reviewing output | Windows |
| Server PC (i7, RTX 2070 Super, 16GB) | Runs Prospector, hosts Gemma 4 via Ollama | Ubuntu 24.04 |

---

## Server Connection

**Server local IP:** `192.168.1.13`
**Username:** `jernej`

**To SSH into the server from your main PC:**
```bash
ssh jernej@192.168.1.13
```

Enter your server password when prompted. You are now controlling the server remotely.

**To exit SSH:**
```bash
exit
```

---

## Code Workflow (Development → Server)

1. **Develop** in Cursor on main PC
2. **Push** to GitHub (`main` branch)
3. **SSH** into server
4. **Pull** latest code on server:
```bash
cd ~/prospector
git pull
```
5. **Run** Prospector on server

---

## First-Time Server Setup (already done — for reference)

```bash
# Connect to server
ssh jernej@192.168.1.13

# Clone repo (first time only)
git clone https://github.com/bobgrasscoreum-beep/prospector.git
cd prospector

# Set up Python environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

---

## Running Prospector on the Server

```bash
# SSH in
ssh jernej@192.168.1.13

# Navigate to project
cd ~/prospector

# Activate virtual environment
source venv/bin/activate

# Dry run (no CSV saved — just logs and summary)
python pipeline.py --profile test_run --dry-run

# Full run
python pipeline.py --profile test_run

# Full run with max results override
python pipeline.py --profile maribor_wood --max 50
```

---

## Getting Output Back to Main PC

CSV files are saved to `~/prospector/output/` on the server.

**Option 1 — Copy via SCP (from main PC terminal):**
```bash
scp jernej@192.168.1.13:~/prospector/output/*.csv D:\leads\
```

**Option 2 — View logs remotely:**
```bash
ssh jernej@192.168.1.13 "cat ~/prospector/logs/prospector_test_run_*.log"
```

---

## Ollama / Gemma 4 on the Server

Ollama runs as a background service and starts automatically on boot.

**Check if Ollama is running:**
```bash
ollama list
```

**Run Gemma 4 interactively (for testing):**
```bash
ollama run gemma4:e4b
```

**Note:** Only the official `gemma4:e4b` tag works on this server. HuggingFace GGUF imports fail due to a driver/architecture compatibility issue (NVIDIA driver 580 + Gemma 4 architecture). The official Ollama model runs correctly but uses RAM offloading (model is 9.6GB, VRAM is 8GB). This is acceptable for overnight batch runs.

---

## Current Build Status

| Component | Status |
|-----------|--------|
| Pipeline runner (`pipeline.py`) | ✅ Done |
| Target profiles (`profiles/*.json`) | ✅ Done |
| Google Maps finder (Playwright) | ✅ Done — v0.3.0 |
| Website enricher (HTTP + metadata) | ⏳ Next |
| Qualifier (AI) | V2 — stub only |
| CSV output | ✅ Done |
| Logging + run summary | ✅ Done |
| SSH access from main PC | ✅ Done |
| Ollama + Gemma 4 on server | ✅ Done |

---

## Daily Workflow (Once Fully Built)

1. Open Cursor on main PC
2. Make changes to profiles or code
3. Push to GitHub
4. SSH into server: `ssh jernej@192.168.1.13`
5. Pull latest: `git pull`
6. Run: `python pipeline.py --profile teras_ideal_client --max 100`
7. Wait for completion (can run overnight)
8. Copy CSV output to main PC
9. Import into Lynqd for outreach

---

## Profiles Location

Profiles are JSON files in `~/prospector/profiles/`.

To add a new profile, create a new `.json` file there or push one from your main PC via GitHub.

Example profiles:
- `test_run.json` — quick smoke test (kavarna/coffee, Maribor, 10 results)
- Add your own: `teras_ideal_client.json`, `maribor_wood.json`, etc.

---

## Troubleshooting Quick Reference

| Problem | Fix |
|---------|-----|
| SSH won't connect | Check server is on, ethernet cable connected, IP is still 192.168.1.13 |
| `python3: command not found` | Run `pyenv global system` first |
| Playwright error | Run `playwright install chromium` in activated venv |
| Ollama model won't load | Use `ollama run gemma4:e4b` not HuggingFace GGUF versions |
| Google Maps blocks run | Partial results saved, check logs, try smaller `--max` |
| No output CSV | Check logs in `~/prospector/logs/` for errors |

---

## GitHub Repository

**URL:** https://github.com/bobgrasscoreum-beep/prospector

- Push all changes from Cursor to `main` branch
- Never commit `.env` file (API keys)
- Cursor updates `docs/11_changelog.md` after every meaningful change
