"""Расчеты по кислородному режиму."""

from __future__ import annotations

from z85snip.core.validation import require_positive


def oxygen_demand(L_mix_mg_per_l: float, Q_m3_per_day: float) -> float:
    """Суточный расход кислорода (мг/сут) при заданной БПК смеси."""

    L_mix = require_positive(L_mix_mg_per_l, "L_mix (мг/л)")
    Q = require_positive(Q_m3_per_day, "Q (м³/сут)")
    return L_mix * Q * 1000.0


def oxygen_uptake_rate(oxidation_rate_mg_per_l_per_hour: float, biomass_concentration_mg_per_l: float) -> float:
    """Удельное поглощение кислорода (мг/(л·ч))."""

    rate = require_positive(oxidation_rate_mg_per_l_per_hour, "Скорость окисления (мг/(л·ч))")
    biomass = require_positive(biomass_concentration_mg_per_l, "Концентрация ила (мг/л)")
    return rate * biomass
