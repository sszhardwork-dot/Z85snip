"""Централизованные пути и флаги."""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
SNIP85_LIBRARY_PATH = DATA_DIR / "snip85" / "snip85_library.json"

STRICT_SNIP = True
DEBUG = False
