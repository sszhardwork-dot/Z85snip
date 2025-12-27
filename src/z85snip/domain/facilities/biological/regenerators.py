"""Регенератор ила с расчетом требуемого объема."""

from __future__ import annotations

from dataclasses import dataclass

from z85snip.core.types import Flow
from z85snip.core.validation import require_positive
from z85snip.domain.facilities.base import Facility, FacilityReport, FacilityResult
from z85snip.snip85 import hydraulics, recirculation, refs


@dataclass(frozen=True)
class RegeneratorParameters:
    recirculation_ratio: float
    t_r_hours: float
    sludge_dose_mg_per_l: float
    h_avg_m: float | None = None
    units: int | None = None


class Regenerator(Facility):
    key = "biological.regenerator"

    def __init__(self, params: RegeneratorParameters):
        self.params = params

    def calculate(self, inflow: Flow) -> FacilityResult:
        q_avg = require_positive(inflow.q_avg_m3_per_day or inflow.Q_m3_per_day, "Qavg (м³/сут) для регенератора")
        q_recirc = recirculation.recirculation_flow(q_avg, self.params.recirculation_ratio)
        volume_req = hydraulics.process_volume_from_time(q_recirc, self.params.t_r_hours)

        report = FacilityReport(
            inputs={
                "q_avg_m3_per_day": q_avg,
                "recirculation_ratio": self.params.recirculation_ratio,
                "t_r_hours": self.params.t_r_hours,
                "sludge_dose_mg_per_l": self.params.sludge_dose_mg_per_l,
                "units": self.params.units,
            },
            outputs={
                "q_recirc_m3_per_day": q_recirc,
                "volume_required_m3": volume_req,
                "volume_per_unit_m3": volume_req / self.params.units if self.params.units else volume_req,
            },
            checks=["Расход рециркуляции посчитан по коэффициенту R"],
            snip_refs=[refs.SNIP_REGENERATOR],
            assumptions=["Смесь ила и воды не влияет на общий расход сточных вод в этой версии"],
        )
        return FacilityResult(flow=inflow, report=report, facility_key=self.key)

