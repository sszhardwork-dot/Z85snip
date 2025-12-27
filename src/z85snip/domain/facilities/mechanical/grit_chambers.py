"""Простая модель горизонтальной/аэрируемой песколовки."""

from __future__ import annotations

from dataclasses import dataclass

from z85snip.core.types import Flow
from z85snip.core.units import to_m3_per_second
from z85snip.core.validation import require_positive
from z85snip.domain.facilities.base import Facility, FacilityReport, FacilityResult
from z85snip.snip85 import hydraulics, refs


@dataclass(frozen=True)
class GritChamberParameters:
    target_velocity_m_per_s: float
    detention_time_seconds: float
    sections: int
    chamber_type: str = "horizontal"


class GritChamber(Facility):
    key = "mechanical.grit_chamber"

    def __init__(self, params: GritChamberParameters):
        self.params = params

    def calculate(self, inflow: Flow) -> FacilityResult:  # type: ignore[override]
        q_avg = require_positive(inflow.q_avg_m3_per_day or inflow.Q_m3_per_day, "Qavg для песколовки (м³/сут)")
        volume_req = hydraulics.detention_volume_from_seconds(q_avg, self.params.detention_time_seconds)
        area = to_m3_per_second(q_avg) / require_positive(
            self.params.target_velocity_m_per_s, "Целевая скорость (м/с)"
        )
        velocities = {"q_avg_m_per_s": self.params.target_velocity_m_per_s}
        if inflow.q_min_m3_per_day:
            velocities["q_min_m_per_s"] = to_m3_per_second(inflow.q_min_m3_per_day) / area
        if inflow.q_max_m3_per_day:
            velocities["q_max_m_per_s"] = to_m3_per_second(inflow.q_max_m3_per_day) / area

        checks = ["Скорость при Qavg принята по целевому значению"]
        if "q_max_m_per_s" in velocities and velocities["q_max_m_per_s"] > self.params.target_velocity_m_per_s * 1.5:
            checks.append("Предупреждение: скорость при Qmax выше целевого диапазона")
        if "q_min_m_per_s" in velocities and velocities["q_min_m_per_s"] < self.params.target_velocity_m_per_s * 0.5:
            checks.append("Предупреждение: скорость при Qmin ниже целевого диапазона")

        report = FacilityReport(
            inputs={
                "q_avg_m3_per_day": q_avg,
                "target_velocity_m_per_s": self.params.target_velocity_m_per_s,
                "detention_time_seconds": self.params.detention_time_seconds,
                "sections": self.params.sections,
                "type": self.params.chamber_type,
            },
            outputs={
                "volume_required_m3": volume_req,
                "section_volume_m3": volume_req / self.params.sections,
                "flow_area_m2": area,
                "velocities_m_per_s": velocities,
            },
            checks=checks,
            snip_refs=[refs.SNIP_MECH_GRIT],
            assumptions=["Геометрия подобрана по целевой скорости и времени пребывания"],
        )
        return FacilityResult(flow=inflow, report=report, facility_key=self.key)

