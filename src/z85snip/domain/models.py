from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Flow:
    Q_m3_per_day: float

@dataclass(frozen=True)
class Concentrations:
    # Пример: БПКполн, взвешенные и т.п. Заполнить по вашим полям.
    bod_full_mg_per_l: float | None = None
