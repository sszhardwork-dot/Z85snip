"""Формулы для аэротенков и связанных времен."""

from __future__ import annotations

from z85snip.core.validation import require_positive


def total_aeration_time(t_atm_hours: float, t_atx_hours: float) -> float:
    """Полное время аэрации (ч)."""

    t_atm = require_positive(t_atm_hours, "t_atm (ч)")
    t_atx = require_positive(t_atx_hours, "t_atx (ч)")
    return t_atm + t_atx


def regeneration_time(total_time_hours: float, regeneration_share: float) -> float:
    """Время регенерации ила (ч) по доле от общего времени."""

    t_total = require_positive(total_time_hours, "Общее время (ч)")
    share = require_positive(regeneration_share, "Доля регенерации")
    return t_total * share


def oxidation_time(total_time_hours: float, regeneration_hours: float) -> float:
    """Время окисления (ч) как разница между общим временем и регенерацией."""

    t_total = require_positive(total_time_hours, "Общее время (ч)")
    t_reg = require_positive(regeneration_hours, "Время регенерации (ч)")
    return t_total - t_reg
