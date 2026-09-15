"""Runtime settings from environment (12-factor)."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOST = os.getenv("LENTSWE_HOST", "127.0.0.1")
PORT = int(os.getenv("PORT") or os.getenv("LENTSWE_PORT") or "7000")
DEBUG = os.getenv("FLASK_DEBUG", "0").strip() in {"1", "true", "True"}
LOG_LEVEL = (os.getenv("LOG_LEVEL") or "INFO").upper()


def data_dir() -> Path:
    override = (os.getenv("LENTSWE_DATA_DIR") or "").strip()
    return Path(override) if override else ROOT / "data"
