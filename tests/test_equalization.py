from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from z85snip.core.types import Flow
from z85snip.domain.facilities.equalization import EqualizationParameters, EqualizationTank
from z85snip.snip85.hydraulics import equalization_volume


def test_equalization_formula_matches_snip():
    result = equalization_volume(480, 6, 1.1)
    assert pytest.approx(result, rel=1e-6) == 132.0


def test_facility_produces_report():
    flow = Flow(q_avg_m3_per_day=720, q_min_m3_per_day=480, q_max_m3_per_day=960)
    facility = EqualizationTank(EqualizationParameters(averaging_hours=8, averaging_coefficient=1.25))
    result = facility.calculate(flow)
    assert result.report.outputs["averaging_volume_m3"] == pytest.approx(300.0)
    refs = result.report.snip_refs
    assert refs
    assert "4.2.3" in refs[0]


def test_pipeline_cli_exports_json(tmp_path: Path):
    output_file = tmp_path / "result.json"
    cmd = [
        sys.executable,
        "-m",
        "z85snip",
        "--flow-m3-per-day",
        "960",
        "--averaging-hours",
        "4",
        "--averaging-coefficient",
        "1.15",
        "--output",
        str(output_file),
    ]
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parent.parent / "src")}
    completed = subprocess.run(cmd, check=True, env=env)
    assert completed.returncode == 0

    content = json.loads(output_file.read_text(encoding="utf-8"))
    first_report = content["results"][0]["report"]
    assert first_report["outputs"]["averaging_volume_m3"] == pytest.approx(184.0)
    assert first_report["inputs"]["q_avg_m3_per_day"] == pytest.approx(960)
