"""Простые механические расчеты (решетки, гидравлика каналов)."""

from __future__ import annotations

from z85snip.core.errors import ValidationError
from z85snip.core.units import to_m3_per_second
from z85snip.core.validation import require_positive


def screen_velocity(Q_m3_per_day: float, open_area_m2: float) -> float:
    """Средняя скорость через решетку (м/с)."""

    q_m3_per_s = to_m3_per_second(Q_m3_per_day)
    area = require_positive(open_area_m2, "Живое сечение (м²)")
    return q_m3_per_s / area


def head_loss(velocity_m_per_s: float, loss_coefficient: float) -> float:
    """Потеря напора (м) по упрощенной формуле ζ * v² / 2g."""

    v = require_positive(velocity_m_per_s, "Скорость (м/с)")
    zeta = require_positive(loss_coefficient, "Коэффициент сопротивления")
    g = 9.81
    return zeta * (v**2) / (2 * g)


def required_open_area(Q_m3_per_day: float, velocity_m_per_s: float, clogging_factor: float, lines: int) -> float:
    """Расчет требуемой живой площади решеток с учетом засорения (м²)."""

    q_m3_per_s = to_m3_per_second(Q_m3_per_day)
    v = require_positive(velocity_m_per_s, "Допустимая скорость (м/с)")
    phi = require_positive(clogging_factor, "Коэффициент засорения")
    if lines <= 0:
        raise ValidationError("Число линий должно быть положительным")
    return (q_m3_per_s / (v * phi)) / lines
