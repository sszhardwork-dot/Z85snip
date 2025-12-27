"""Загрузка редактируемой библиотеки СНиП."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from z85snip.core.errors import SnipLibraryError


@dataclass(frozen=True)
class SnipLibrary:
    payload: Mapping[str, Any]
    strict: bool = True

    @classmethod
    def load(cls, path: Path, *, strict: bool = True) -> "SnipLibrary":
        if not path.exists():
            raise SnipLibraryError(f"Библиотека СНиП не найдена: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(payload=data, strict=strict)

    def get(self, key: str) -> Any:
        try:
            return self.payload[key]
        except KeyError as exc:
            if self.strict:
                raise SnipLibraryError(f"Ключ {key!r} не найден в библиотеке") from exc
            return None

    def get_table(self, name: str) -> Any:
        tables = self.get("tables") or {}
        try:
            return tables[name]
        except KeyError as exc:
            if self.strict:
                raise SnipLibraryError(f"Таблица {name!r} не найдена в библиотеке") from exc
            return None

    def get_ref(self, ref_id: str) -> Any:
        refs = self.get("refs") or {}
        try:
            return refs[ref_id]
        except KeyError as exc:
            if self.strict:
                raise SnipLibraryError(f"Ссылка {ref_id!r} не найдена в библиотеке") from exc
            return None
