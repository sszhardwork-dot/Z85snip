from __future__ import annotations

import pytest

from z85snip.application.pipeline import run_pipeline
from z85snip.application.scenarios import _chain_for_scenario, scenario_catalog


def _run_catalog_entry(key: str):
    flow, facilities = _chain_for_scenario(scenario_catalog()[key])
    return run_pipeline(flow, facilities)


def test_scenario_a_small_wtp():
    final_flow, results = _run_catalog_entry("A")

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
    assert final_flow.q_avg_m3_per_day == 800


def test_scenario_b_medium_wtp():
    _, results = _run_catalog_entry("B")

    result_map = {r.facility_key: r for r in results}
    settler_out = result_map["mechanical.primary_settler"].report.outputs
    assert settler_out["area_total_m2"] == pytest.approx(1875, rel=0.02)

    aeration_out = result_map["biological.aeration_tank"].report.outputs
    assert aeration_out["q_mix_m3_per_day"] == pytest.approx(34000)
    assert aeration_out["volume_required_m3"] == pytest.approx(11333, rel=0.02)

    regen_out = result_map["biological.regenerator"].report.outputs
    assert regen_out["volume_required_m3"] == pytest.approx(875, rel=0.05)


def test_scenario_c_large_wtp():
    _, results = _run_catalog_entry("C")

    result_map = {r.facility_key: r for r in results}
    settler_out = result_map["mechanical.primary_settler"].report.outputs
    assert settler_out["area_total_m2"] == pytest.approx(11574, rel=0.02)

    aeration_out = result_map["biological.aeration_tank"].report.outputs
    assert aeration_out["q_mix_m3_per_day"] == pytest.approx(228000)
    assert aeration_out["volume_required_m3"] == pytest.approx(90250, rel=0.02)

    regen_out = result_map["biological.regenerator"].report.outputs
    assert regen_out["volume_required_m3"] == pytest.approx(9000, rel=0.02)

