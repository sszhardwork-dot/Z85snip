"""Модель решеток с расчетом скорости и напора по СНиП-85."""

from __future__ import annotations

from dataclasses import dataclass

from z85snip.core.types import Flow
from z85snip.core.validation import require_positive
from z85snip.domain.facilities.base import Facility, FacilityReport, FacilityResult
from z85snip.snip85 import mechanical, refs


@dataclass(frozen=True)
class ScreenParameters:
    bar_spacing_mm: float
    bar_thickness_mm: float
    clogging_factor: float
    lines: int
    loss_coefficient: float = 2.5
    allowable_velocity_m_per_s: float = 0.8
    name: str = "Screen"


class ScreenFacility(Facility):
    key = "mechanical.screen"

    def __init__(self, params: ScreenParameters):
        self.params = params

    def calculate(self, inflow: Flow) -> FacilityResult:
        q_max = require_positive(
            inflow.q_max_m3_per_day or inflow.q_avg_m3_per_day or inflow.Q_m3_per_day,
            "Qmax для решеток (м³/сут)",
        )
        open_area_per_line = mechanical.required_open_area(
            q_max, self.params.allowable_velocity_m_per_s, self.params.clogging_factor, self.params.lines
        )
        effective_open_area = open_area_per_line * self.params.lines * self.params.clogging_factor
        velocity_max = mechanical.screen_velocity(q_max, effective_open_area)
        head_loss = mechanical.head_loss(velocity_max, self.params.loss_coefficient)

        velocities = {"q_max_m_per_s": velocity_max}
        for label, q in {"q_min_m3_per_day": inflow.q_min_m3_per_day, "q_avg_m3_per_day": inflow.q_avg_m3_per_day}.items():
            if q is None:
                continue
            velocities[label.replace("m3_per_day", "m_per_s")] = mechanical.screen_velocity(
                q, effective_open_area
            )

        checks = []
        if velocity_max <= self.params.allowable_velocity_m_per_s:
            checks.append("Скорость при Qmax в допустимых пределах")
        else:
            checks.append("Предупреждение: скорость при Qmax превышает рекомендуемую")
        checks.append(f"Потери напора рассчитаны по ζ={self.params.loss_coefficient}")

        report = FacilityReport(
            inputs={
                "q_max_m3_per_day": q_max,
                "bar_spacing_mm": self.params.bar_spacing_mm,
                "bar_thickness_mm": self.params.bar_thickness_mm,
                "clogging_factor": self.params.clogging_factor,
                "lines": self.params.lines,
            },
            outputs={
                "open_area_per_line_m2": open_area_per_line,
                "effective_open_area_m2": effective_open_area,
                "velocity_m_per_s": velocities,
                "head_loss_m": head_loss,
            },
            checks=checks,
            snip_refs=[refs.SNIP_MECH_SCREENS],
            assumptions=["Живое сечение подобрано по Qmax и допустимой скорости"],
        )
        return FacilityResult(flow=inflow, report=report, facility_key=self.key)

