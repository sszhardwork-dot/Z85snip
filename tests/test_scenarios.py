from __future__ import annotations

import pytest

from z85snip.application.pipeline import run_pipeline
from z85snip.core.types import Flow, Pollutants
from z85snip.domain.facilities.biological.aeration_tanks import AerationParameters, AerationTank
from z85snip.domain.facilities.biological.regenerators import Regenerator, RegeneratorParameters
from z85snip.domain.facilities.mechanical.grit_chambers import GritChamber, GritChamberParameters
from z85snip.domain.facilities.mechanical.primary_settlers import (
    PrimarySettler,
    PrimarySettlerParameters,
)
from z85snip.domain.facilities.mechanical.screens import ScreenFacility, ScreenParameters


def _build_common_chain(flow: Flow, *, grit: GritChamberParameters, settler: PrimarySettlerParameters, aeration_params: AerationParameters, regenerator_params: RegeneratorParameters):
    facilities = [
        ScreenFacility(
            ScreenParameters(
                bar_spacing_mm=grit.target_velocity_m_per_s * 100,  # surrogate geometry binding to keep data flowing
                bar_thickness_mm=grit.target_velocity_m_per_s * 30,
                clogging_factor=0.7,
                lines=grit.sections,
            )
        ),
        GritChamber(grit),
        PrimarySettler(settler),
        AerationTank(aeration_params),
        Regenerator(regenerator_params),
    ]
    return run_pipeline(flow, facilities)


def test_scenario_a_small_wtp():
    flow = Flow(
        q_min_m3_per_day=400,
        q_avg_m3_per_day=800,
        q_max_m3_per_day=1600,
        pollutants=Pollutants(bod_full_mg_per_l=250, suspended_solids_mg_per_l=280, ammonium_mg_per_l=30),
    )

    final_flow, results = _build_common_chain(
        flow,
        grit=GritChamberParameters(target_velocity_m_per_s=0.30, detention_time_seconds=60, sections=2, chamber_type="horizontal"),
        settler=PrimarySettlerParameters(surface_loading_m3_per_m2_per_h=1.2, working_depth_m=3.5, units=1, settler_type="radial"),
        aeration_params=AerationParameters(recirculation_ratio=0.5, t_atm_hours=4.0, t_atx_hours=2.0, rho_oxidation_mg_per_l_per_h=20, subtype="E3", h_avg_m=4.5),
        regenerator_params=RegeneratorParameters(recirculation_ratio=0.5, t_r_hours=1.0, sludge_dose_mg_per_l=2500, h_avg_m=4.0, units=1),
    )

    result_map = {r.facility_key: r for r in results}
    grit_out = result_map["mechanical.grit_chamber"].report.outputs
    assert grit_out["volume_required_m3"] == pytest.approx(0.56, rel=0.05)

    settler_out = result_map["mechanical.primary_settler"].report.outputs
    assert settler_out["area_total_m2"] == pytest.approx(55.6, rel=0.02)
    assert settler_out["volume_total_m3"] == pytest.approx(195, rel=0.05)

    aeration_out = result_map["biological.aeration_tank"].report.outputs
    assert aeration_out["q_mix_m3_per_day"] == pytest.approx(1200)
    assert aeration_out["volume_required_m3"] == pytest.approx(300, rel=0.02)

    regen_out = result_map["biological.regenerator"].report.outputs
    assert regen_out["volume_required_m3"] == pytest.approx(16.7, rel=0.05)
    assert final_flow.q_avg_m3_per_day == flow.q_avg_m3_per_day


def test_scenario_b_medium_wtp():
    flow = Flow(
        q_min_m3_per_day=10000,
        q_avg_m3_per_day=20000,
        q_max_m3_per_day=45000,
        pollutants=Pollutants(bod_full_mg_per_l=220, suspended_solids_mg_per_l=250, ammonium_mg_per_l=35),
    )

    _, results = _build_common_chain(
        flow,
        grit=GritChamberParameters(target_velocity_m_per_s=0.25, detention_time_seconds=90, sections=3, chamber_type="aerated"),
        settler=PrimarySettlerParameters(surface_loading_m3_per_m2_per_h=1.0, working_depth_m=3.8, units=2, settler_type="radial"),
        aeration_params=AerationParameters(recirculation_ratio=0.7, t_atm_hours=5.0, t_atx_hours=3.0, rho_oxidation_mg_per_l_per_h=18, subtype="E4", h_avg_m=5.0, corridors=4),
        regenerator_params=RegeneratorParameters(recirculation_ratio=0.7, t_r_hours=1.5, sludge_dose_mg_per_l=3000, h_avg_m=4.5, units=1),
    )

    result_map = {r.facility_key: r for r in results}
    settler_out = result_map["mechanical.primary_settler"].report.outputs
    assert settler_out["area_total_m2"] == pytest.approx(1875, rel=0.02)

    aeration_out = result_map["biological.aeration_tank"].report.outputs
    assert aeration_out["q_mix_m3_per_day"] == pytest.approx(34000)
    assert aeration_out["volume_required_m3"] == pytest.approx(11333, rel=0.02)

    regen_out = result_map["biological.regenerator"].report.outputs
    assert regen_out["volume_required_m3"] == pytest.approx(875, rel=0.05)


def test_scenario_c_large_wtp():
    flow = Flow(
        q_min_m3_per_day=60000,
        q_avg_m3_per_day=120000,
        q_max_m3_per_day=250000,
        pollutants=Pollutants(bod_full_mg_per_l=200, suspended_solids_mg_per_l=220, ammonium_mg_per_l=40),
    )

    _, results = _build_common_chain(
        flow,
        grit=GritChamberParameters(target_velocity_m_per_s=0.25, detention_time_seconds=120, sections=6, chamber_type="vortex"),
        settler=PrimarySettlerParameters(surface_loading_m3_per_m2_per_h=0.9, working_depth_m=4.0, units=6, settler_type="radial"),
        aeration_params=AerationParameters(recirculation_ratio=0.9, t_atm_hours=6.0, t_atx_hours=3.5, rho_oxidation_mg_per_l_per_h=16, subtype="E4", h_avg_m=5.5),
        regenerator_params=RegeneratorParameters(recirculation_ratio=0.9, t_r_hours=2.0, sludge_dose_mg_per_l=3500, h_avg_m=5.0, units=1),
    )

    result_map = {r.facility_key: r for r in results}
    settler_out = result_map["mechanical.primary_settler"].report.outputs
    assert settler_out["area_total_m2"] == pytest.approx(11574, rel=0.02)

    aeration_out = result_map["biological.aeration_tank"].report.outputs
    assert aeration_out["q_mix_m3_per_day"] == pytest.approx(228000)
    assert aeration_out["volume_required_m3"] == pytest.approx(90250, rel=0.02)

    regen_out = result_map["biological.regenerator"].report.outputs
    assert regen_out["volume_required_m3"] == pytest.approx(9000, rel=0.02)

