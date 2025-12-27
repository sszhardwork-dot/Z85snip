"""Утилиты пересчета единиц без внешних зависимостей."""

from __future__ import annotations

from z85snip.core.validation import require_positive


def to_m3_per_hour(q_m3_per_day: float) -> float:
    """Перевести расход из м³/сут в м³/ч."""

    return require_positive(q_m3_per_day, "Расход (м³/сут)") / 24.0


def to_m3_per_day(q_m3_per_hour: float) -> float:
    """Перевести расход из м³/ч в м³/сут."""

    return require_positive(q_m3_per_hour, "Расход (м³/ч)") * 24.0


def to_m3_per_second(q_m3_per_day: float) -> float:
    """Перевести расход из м³/сут в м³/с."""

    return require_positive(q_m3_per_day, "Расход (м³/сут)") / 86400.0


def to_m3_per_day_from_second(q_m3_per_second: float) -> float:
    """Перевести расход из м³/с в м³/сут."""

    return require_positive(q_m3_per_second, "Расход (м³/с)") * 86400.0
