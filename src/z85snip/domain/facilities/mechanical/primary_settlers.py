"""Расчет радиальных/прямоугольных первичных отстойников."""

from __future__ import annotations

from dataclasses import dataclass

from z85snip.core.types import Flow, Pollutants
from z85snip.core.validation import require_positive
from z85snip.domain.facilities.base import Facility, FacilityReport, FacilityResult
from z85snip.snip85 import hydraulics, refs


@dataclass(frozen=True)
class PrimarySettlerParameters:
    surface_loading_m3_per_m2_per_h: float
    working_depth_m: float
    units: int
    bod_removal_fraction: float = 0.3
    ss_removal_fraction: float = 0.55
    settler_type: str = "radial"


class PrimarySettler(Facility):
    key = "mechanical.primary_settler"

    def __init__(self, params: PrimarySettlerParameters):
        self.params = params

    def _remove_pollutants(self, inflow: Flow) -> Flow:
        pollutants = inflow.pollutants
        if pollutants is None:
            return inflow
        bod = getattr(pollutants, "bod_full_mg_per_l", None)
        ss = getattr(pollutants, "suspended_solids_mg_per_l", None)
        ammonium = getattr(pollutants, "ammonium_mg_per_l", None)
        new_pollutants = Pollutants(
            bod_full_mg_per_l=None if bod is None else bod * (1 - self.params.bod_removal_fraction),
            suspended_solids_mg_per_l=None if ss is None else ss * (1 - self.params.ss_removal_fraction),
            ammonium_mg_per_l=ammonium,
        )
        return Flow(
            q_min_m3_per_day=inflow.q_min_m3_per_day,
            q_avg_m3_per_day=inflow.q_avg_m3_per_day,
            q_max_m3_per_day=inflow.q_max_m3_per_day,
            pollutants=new_pollutants,
            meta=inflow.meta,
        )

    def calculate(self, inflow: Flow) -> FacilityResult:
        q_max = require_positive(
            inflow.q_max_m3_per_day or inflow.q_avg_m3_per_day or inflow.Q_m3_per_day,
            "Qmax для отстойника (м³/сут)",
        )
        area_total = hydraulics.primary_settler_area_qmax_hour(q_max, self.params.surface_loading_m3_per_m2_per_h)
        volume_total = hydraulics.volume_from_area_and_depth(area_total, self.params.working_depth_m)

        flow_after = self._remove_pollutants(inflow)

        report = FacilityReport(
            inputs={
                "q_max_m3_per_day": q_max,
                "surface_loading_m3_per_m2_per_h": self.params.surface_loading_m3_per_m2_per_h,
                "working_depth_m": self.params.working_depth_m,
                "units": self.params.units,
                "type": self.params.settler_type,
            },
            outputs={
                "area_total_m2": area_total,
                "area_per_unit_m2": area_total / self.params.units,
                "volume_total_m3": volume_total,
                "volume_per_unit_m3": volume_total / self.params.units,
            },
            checks=["Площадь рассчитана по Qmax и поверхностной нагрузке"],
            snip_refs=[refs.SNIP_PRIMARY_SETTLER],
            assumptions=["Эффект снижения БПК и взвесей принят как усредненный"]
            if inflow.pollutants
            else ["Состав не задан, расчет выполнен по расходу"],
        )
        return FacilityResult(flow=flow_after, report=report, facility_key=self.key)

