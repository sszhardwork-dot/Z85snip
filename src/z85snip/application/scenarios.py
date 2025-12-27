"""Готовые сценарии расчета и вспомогательные обертки для лаунчера."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

from z85snip.core.types import Flow, Pollutants
from z85snip.domain.facilities.biological.aeration_tanks import (
    AerationParameters,
    AerationTank,
)
from z85snip.domain.facilities.biological.regenerators import (
    Regenerator,
    RegeneratorParameters,
)
from z85snip.domain.facilities.mechanical.grit_chambers import (
    GritChamber,
    GritChamberParameters,
)
from z85snip.domain.facilities.mechanical.primary_settlers import (
    PrimarySettler,
    PrimarySettlerParameters,
)
from z85snip.domain.facilities.mechanical.screens import ScreenFacility, ScreenParameters


@dataclass(frozen=True)
class ScenarioDefinition:
    key: str
    description: str
    flow: Flow
    grit: GritChamberParameters
    settler: PrimarySettlerParameters
    aeration: AerationParameters
    regenerator: RegeneratorParameters


def _chain_for_scenario(defn: ScenarioDefinition) -> Tuple[Flow, Iterable]:
    facilities = [
        ScreenFacility(
            ScreenParameters(
                bar_spacing_mm=defn.grit.target_velocity_m_per_s * 100,
                bar_thickness_mm=defn.grit.target_velocity_m_per_s * 30,
                clogging_factor=0.7,
                lines=defn.grit.sections,
            )
        ),
        GritChamber(defn.grit),
        PrimarySettler(defn.settler),
        AerationTank(defn.aeration),
        Regenerator(defn.regenerator),
    ]
    return defn.flow, facilities


def scenario_catalog() -> Dict[str, ScenarioDefinition]:
    """Возвращает справочник сценариев A/B/C, используемый в лаунчере и тестах."""

    return {
        "A": ScenarioDefinition(
            key="A",
            description="Малые КОС (поселок)",
            flow=Flow(
                q_min_m3_per_day=400,
                q_avg_m3_per_day=800,
                q_max_m3_per_day=1600,
                pollutants=Pollutants(
                    bod_full_mg_per_l=250,
                    suspended_solids_mg_per_l=280,
                    ammonium_mg_per_l=30,
                ),
            ),
            grit=GritChamberParameters(
                target_velocity_m_per_s=0.30,
                detention_time_seconds=60,
                sections=2,
                chamber_type="horizontal",
            ),
            settler=PrimarySettlerParameters(
                surface_loading_m3_per_m2_per_h=1.2,
                working_depth_m=3.5,
                units=1,
                settler_type="radial",
            ),
            aeration=AerationParameters(
                recirculation_ratio=0.5,
                t_atm_hours=4.0,
                t_atx_hours=2.0,
                rho_oxidation_mg_per_l_per_h=20,
                subtype="E3",
                h_avg_m=4.5,
            ),
            regenerator=RegeneratorParameters(
                recirculation_ratio=0.5,
                t_r_hours=1.0,
                sludge_dose_mg_per_l=2500,
                h_avg_m=4.0,
                units=1,
            ),
        ),
        "B": ScenarioDefinition(
            key="B",
            description="Средние КОС (город)",
            flow=Flow(
                q_min_m3_per_day=10_000,
                q_avg_m3_per_day=20_000,
                q_max_m3_per_day=45_000,
                pollutants=Pollutants(
                    bod_full_mg_per_l=220,
                    suspended_solids_mg_per_l=250,
                    ammonium_mg_per_l=35,
                ),
            ),
            grit=GritChamberParameters(
                target_velocity_m_per_s=0.25,
                detention_time_seconds=90,
                sections=3,
                chamber_type="aerated",
            ),
            settler=PrimarySettlerParameters(
                surface_loading_m3_per_m2_per_h=1.0,
                working_depth_m=3.8,
                units=2,
                settler_type="radial",
            ),
            aeration=AerationParameters(
                recirculation_ratio=0.7,
                t_atm_hours=5.0,
                t_atx_hours=3.0,
                rho_oxidation_mg_per_l_per_h=18,
                subtype="E4",
                h_avg_m=5.0,
                corridors=4,
            ),
            regenerator=RegeneratorParameters(
                recirculation_ratio=0.7,
                t_r_hours=1.5,
                sludge_dose_mg_per_l=3000,
                h_avg_m=4.5,
                units=1,
            ),
        ),
        "C": ScenarioDefinition(
            key="C",
            description="Крупные КОС (агломерация)",
            flow=Flow(
                q_min_m3_per_day=60_000,
                q_avg_m3_per_day=120_000,
                q_max_m3_per_day=250_000,
                pollutants=Pollutants(
                    bod_full_mg_per_l=200,
                    suspended_solids_mg_per_l=220,
                    ammonium_mg_per_l=40,
                ),
            ),
            grit=GritChamberParameters(
                target_velocity_m_per_s=0.25,
                detention_time_seconds=120,
                sections=6,
                chamber_type="vortex",
            ),
            settler=PrimarySettlerParameters(
                surface_loading_m3_per_m2_per_h=0.9,
                working_depth_m=4.0,
                units=6,
                settler_type="radial",
            ),
            aeration=AerationParameters(
                recirculation_ratio=0.9,
                t_atm_hours=6.0,
                t_atx_hours=3.5,
                rho_oxidation_mg_per_l_per_h=16,
                subtype="E4",
                h_avg_m=5.5,
            ),
            regenerator=RegeneratorParameters(
                recirculation_ratio=0.9,
                t_r_hours=2.0,
                sludge_dose_mg_per_l=3500,
                h_avg_m=5.0,
                units=1,
            ),
        ),
    }


__all__ = ["ScenarioDefinition", "scenario_catalog", "_chain_for_scenario"]
