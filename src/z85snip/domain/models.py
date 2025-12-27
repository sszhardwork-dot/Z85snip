"""Доменные контейнеры для потоков и качества воды."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from z85snip.core.types import Flow, Pollutants


@dataclass(frozen=True)
class Quality:
    """Качество воды (концентрации загрязнений, мг/л)."""

    bod_full_mg_per_l: float | None = None
    suspended_solids_mg_per_l: float | None = None
    ammonium_mg_per_l: float | None = None
    extra: Mapping[str, float] | None = None


@dataclass(frozen=True)
class Mixture:
    """Смесь потоков с указанием долей и итогового качества."""

    flow: Flow
    quality: Quality
    dilution_ratio: float | None = None


__all__ = ["Flow", "Pollutants", "Quality", "Mixture"]
