from __future__ import annotations

import pytest

from z85snip.snip85 import aeration, hydraulics, mechanical, oxygen, recirculation


def test_hydraulics_equalization_volume():
    assert hydraulics.equalization_volume(480, 6, 1.1) == pytest.approx(132.0)


def test_hydraulics_detention_time_hours():
    assert hydraulics.detention_time_hours(300, 720) == pytest.approx(10.0)


def test_hydraulics_surface_loading_area():
    assert hydraulics.surface_loading_area(960, 24) == pytest.approx(40.0)


def test_hydraulics_primary_and_process_volumes():
    assert hydraulics.detention_volume_from_seconds(800, 60) == pytest.approx(0.5555555, rel=1e-5)
    assert hydraulics.primary_settler_area_qmax_hour(1600, 1.2) == pytest.approx(55.5555, rel=1e-4)
    assert hydraulics.volume_from_area_and_depth(55.6, 3.5) == pytest.approx(194.6, rel=0.01)
    assert hydraulics.process_volume_from_time(1200, 6) == pytest.approx(300)


def test_recirculation_flow_and_ratio():
    q_recirc = recirculation.recirculation_flow(1200, 0.3)
    assert q_recirc == pytest.approx(360.0)
    assert recirculation.recirculation_ratio_from_flow(1200, q_recirc) == pytest.approx(0.3)


def test_mixed_flow_and_concentration():
    q_mix = recirculation.mixed_flow(900, 300)
    assert q_mix == pytest.approx(1200.0)
    l_mix = recirculation.mix_concentration(200, 100, 900, 300)
    assert l_mix == pytest.approx(175.0)


def test_aeration_times():
    t_total = aeration.total_aeration_time(2.5, 5.5)
    assert t_total == pytest.approx(8.0)
    t_reg = aeration.regeneration_time(t_total, 0.25)
    assert t_reg == pytest.approx(2.0)
    t_ox = aeration.oxidation_time(t_total, t_reg)
    assert t_ox == pytest.approx(6.0)


def test_mechanical_screen_velocity_and_head_loss():
    v = mechanical.screen_velocity(8640, 0.5)
    assert v == pytest.approx(0.2)
    head = mechanical.head_loss(v, 2.5)
    assert head == pytest.approx(0.0050968399)


def test_oxygen_calculations():
    demand = oxygen.oxygen_demand(120, 2400)
    assert demand == pytest.approx(120 * 2400 * 1000.0)
    uptake = oxygen.oxygen_uptake_rate(0.8, 3500)
    assert uptake == pytest.approx(2800.0)


def test_probability_validation():
    with pytest.raises(Exception):
        recirculation.recirculation_flow(1000, 1.5)
