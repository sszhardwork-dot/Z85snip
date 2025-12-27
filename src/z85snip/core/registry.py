"""Реестр доступных сооружений для UI и пайплайна."""

from __future__ import annotations

from typing import Dict, Type

from z85snip.domain.facilities.base import Facility

_REGISTRY: Dict[str, Type[Facility]] = {}


def register(key: str, cls: Type[Facility]) -> None:
    if key in _REGISTRY:
        raise ValueError(f"Узел {key!r} уже зарегистрирован")
    _REGISTRY[key] = cls


def get_registry() -> Dict[str, Type[Facility]]:
    return dict(_REGISTRY)
