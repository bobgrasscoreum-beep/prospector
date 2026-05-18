"""Global Prospector settings."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent
PROFILES_DIR = ROOT_DIR / "profiles"
OUTPUT_DIR = ROOT_DIR / "output"
LOG_DIR = ROOT_DIR / "logs"
MODULES_DIR = ROOT_DIR / "modules"

DEFAULT_MAX_RESULTS = int(os.getenv("DEFAULT_MAX_RESULTS", "100"))
HEADLESS = os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes")
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "2"))

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
