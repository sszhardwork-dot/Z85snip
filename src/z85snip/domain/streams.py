"""Профиль притока сточных вод.

Обеспечивает расчет базовых режимов расхода, используемых в СНиП-85:
``q_min_m3_per_day``, ``q_avg_m3_per_day`` и ``q_max_m3_per_day``. Эти
значения затем переносятся в :class:`z85snip.core.types.Flow`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from z85snip.core.types import Flow


@dataclass(frozen=True)
class InflowProfilePoint:
    hour: int
    Q_m3_per_hour: float


@dataclass(frozen=True)
class InflowProfile:
    points: List[InflowProfilePoint]

    def q_min(self) -> float:
        return min(p.Q_m3_per_hour for p in self.points)

    def q_max(self) -> float:
        return max(p.Q_m3_per_hour for p in self.points)

    def q_avg(self) -> float:
        return sum(p.Q_m3_per_hour for p in self.points) / len(self.points)

    def as_flow(self) -> Flow:
        """Преобразовать в агрегированный :class:`Flow` (м³/сут)."""

        factor = 24.0
        return Flow(
            q_min_m3_per_day=self.q_min() * factor,
            q_avg_m3_per_day=self.q_avg() * factor,
            q_max_m3_per_day=self.q_max() * factor,
            meta={"source": "profile"},
        )
