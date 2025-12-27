"""Экспорт результатов расчета."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

import sys


def _serialize(obj: Any) -> Any:
    if is_dataclass(obj):
        return {k: _serialize(v) for k, v in asdict(obj).items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    return obj


def export_run_json(result: Any, path: Path | str) -> None:
    payload = _serialize(result)
    data = json.dumps(payload, ensure_ascii=False, indent=2)
    if str(path) == "-":
        print(data)
        return
    Path(path).write_text(data, encoding="utf-8")
