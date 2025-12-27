"""Рециркуляции и смешение потоков по СНиП-85."""

from __future__ import annotations

from z85snip.core.validation import require_positive, require_probability


def recirculation_flow(Q_waste_m3_per_day: float, R: float) -> float:
    """Расчет расхода рециркуляции по коэффициенту R (м³/сут)."""

    Q_waste = require_positive(Q_waste_m3_per_day, "Q сточной (м³/сут)")
    r = require_probability(R, "R (коэффициент рециркуляции)")
    return Q_waste * r


def recirculation_ratio_from_flow(Q_waste_m3_per_day: float, Q_recirculation_m3_per_day: float) -> float:
    """Определить коэффициент рециркуляции R = Qrecirc / Qwaste."""

    Q_waste = require_positive(Q_waste_m3_per_day, "Q сточной (м³/сут)")
    Q_recirc = require_positive(Q_recirculation_m3_per_day, "Q рециркуляции (м³/сут)")
    return Q_recirc / Q_waste


def mixed_flow(Q_waste_m3_per_day: float, Q_recirculation_m3_per_day: float) -> float:
    """Суммарный расход смешанного потока (м³/сут)."""

    Q_waste = require_positive(Q_waste_m3_per_day, "Q сточной (м³/сут)")
    Q_recirc = require_positive(Q_recirculation_m3_per_day, "Q рециркуляции (м³/сут)")
    return Q_waste + Q_recirc


def mix_concentration(
    L_waste_mg_per_l: float,
    L_recirc_mg_per_l: float,
    Q_waste_m3_per_day: float,
    Q_recirc_m3_per_day: float,
) -> float:
    """Смешанная концентрация БПК (мг/л) с учетом рециркуляции."""

    L_waste = require_positive(L_waste_mg_per_l, "L сточной (мг/л)")
    L_recirc = require_positive(L_recirc_mg_per_l, "L рециркуляции (мг/л)")
    Q_waste = require_positive(Q_waste_m3_per_day, "Q сточной (м³/сут)")
    Q_recirc = require_positive(Q_recirc_m3_per_day, "Q рециркуляции (м³/сут)")
    return (L_waste * Q_waste + L_recirc * Q_recirc) / (Q_waste + Q_recirc)
