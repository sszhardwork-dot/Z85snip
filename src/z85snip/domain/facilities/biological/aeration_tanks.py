"""Расчет аэротенка по укрупненным формулам СНиП-85."""

from __future__ import annotations

from dataclasses import dataclass

from z85snip.core.types import Flow, Pollutants
from z85snip.core.validation import require_positive
from z85snip.domain.facilities.base import Facility, FacilityReport, FacilityResult
from z85snip.snip85 import aeration, hydraulics, recirculation, refs


@dataclass(frozen=True)
class AerationParameters:
    recirculation_ratio: float
    t_atm_hours: float
    t_atx_hours: float
    rho_oxidation_mg_per_l_per_h: float
    subtype: str = "E3"
    h_avg_m: float | None = None
    corridors: int | None = None


class AerationTank(Facility):
    key = "biological.aeration_tank"

    def __init__(self, params: AerationParameters):
        self.params = params

    def _update_quality(self, inflow: Flow) -> Flow:
        pollutants = inflow.pollutants
        if pollutants is None:
            return inflow
        bod_in = getattr(pollutants, "bod_full_mg_per_l", None)
        removal_fraction = 0.85
        bod_out = None if bod_in is None else max(bod_in * (1 - removal_fraction), 0.0)
        new_pollutants = Pollutants(
            bod_full_mg_per_l=bod_out,
            suspended_solids_mg_per_l=getattr(pollutants, "suspended_solids_mg_per_l", None),
            ammonium_mg_per_l=getattr(pollutants, "ammonium_mg_per_l", None),
        )
        return Flow(
            q_min_m3_per_day=inflow.q_min_m3_per_day,
            q_avg_m3_per_day=inflow.q_avg_m3_per_day,
            q_max_m3_per_day=inflow.q_max_m3_per_day,
            pollutants=new_pollutants,
            meta=inflow.meta,
        )

    def calculate(self, inflow: Flow) -> FacilityResult:
        q_avg = require_positive(inflow.q_avg_m3_per_day or inflow.Q_m3_per_day, "Qavg (м³/сут) для аэротенка")
        q_mix = recirculation.mixed_flow(q_avg, recirculation.recirculation_flow(q_avg, self.params.recirculation_ratio))
        t_total = aeration.total_aeration_time(self.params.t_atm_hours, self.params.t_atx_hours)
        volume_req = hydraulics.process_volume_from_time(q_mix, t_total)
        oxygen_uptake = oxygen_supply = None
        if inflow.pollutants and inflow.pollutants.bod_full_mg_per_l is not None:
            oxygen_uptake = inflow.pollutants.bod_full_mg_per_l * q_mix * 1000
            oxygen_supply = self.params.rho_oxidation_mg_per_l_per_h * t_total

        flow_after = self._update_quality(inflow)

        report = FacilityReport(
            inputs={
                "q_avg_m3_per_day": q_avg,
                "recirculation_ratio": self.params.recirculation_ratio,
                "t_atm_hours": self.params.t_atm_hours,
                "t_atx_hours": self.params.t_atx_hours,
                "rho_oxidation_mg_per_l_per_h": self.params.rho_oxidation_mg_per_l_per_h,
                "subtype": self.params.subtype,
            },
            outputs={
                "q_mix_m3_per_day": q_mix,
                "t_at_hours": t_total,
                "volume_required_m3": volume_req,
                "oxygen_uptake_mg_per_day": oxygen_uptake,
                "oxygen_supply_mg_per_l": oxygen_supply,
            },
            checks=[
                "Требуемый объем рассчитан по суммарному расходу смеси",
                "Рециркуляция учтена как фиксированный коэффициент",
            ],
            snip_refs=[refs.SNIP_AERATION_E3_E4],
            assumptions=["Эффект по БПК принят укрупненно без итераций"],
        )
        return FacilityResult(flow=flow_after, report=report, facility_key=self.key)

