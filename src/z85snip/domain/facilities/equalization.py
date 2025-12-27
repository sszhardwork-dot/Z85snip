"""Усреднитель расхода."""

from __future__ import annotations

from dataclasses import dataclass

from z85snip.core.types import Flow
from z85snip.core.validation import require_positive
from z85snip.domain.facilities.base import Facility, FacilityReport, FacilityResult
from z85snip.snip85 import refs
from z85snip.snip85.hydraulics import equalization_volume


@dataclass(frozen=True)
class EqualizationParameters:
    averaging_hours: float
    averaging_coefficient: float


class EqualizationTank(Facility):
    key = "equalization_tank"

    def __init__(self, params: EqualizationParameters):
        self.params = params

    def calculate(self, inflow: Flow) -> FacilityResult:
        Q = require_positive(
            inflow.q_avg_m3_per_day or inflow.Q_m3_per_day,
            "Среднесуточный расход Qavg (м3/сут)",
        )
        t = require_positive(self.params.averaging_hours, "Время усреднения (ч)")
        k = require_positive(self.params.averaging_coefficient, "Коэффициент усреднения")

        volume = equalization_volume(Q, t, k)
        checks: list[str] = []
        if inflow.q_max_m3_per_day is not None:
            checks.append(
                f"Проверено, что Qmax={inflow.q_max_m3_per_day} м³/сут используется для гидравлики"
            )
        if inflow.q_min_m3_per_day is not None:
            checks.append(
                f"Проверено, что Qmin={inflow.q_min_m3_per_day} м³/сут не нарушает режим усреднения"
            )
        report = FacilityReport(
            inputs={
                "q_avg_m3_per_day": Q,
                "q_min_m3_per_day": inflow.q_min_m3_per_day,
                "q_max_m3_per_day": inflow.q_max_m3_per_day,
                "averaging_hours": t,
                "averaging_coefficient": k,
            },
            outputs={"averaging_volume_m3": volume},
            checks=checks,
            snip_refs=[refs.SNIP_EQUALIZATION_VOLUME],
            assumptions=["Объем рассчитывается без учета запаса по осадку"],
        )
        return FacilityResult(flow=inflow, report=report, facility_key=self.key)
