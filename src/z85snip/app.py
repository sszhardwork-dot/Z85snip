"""Точка входа CLI."""

from __future__ import annotations

import argparse
from pathlib import Path

from z85snip.application.pipeline import run_pipeline
from z85snip.core.pipeline import PipelineRun
from z85snip.core.types import Flow
from z85snip.domain.facilities.equalization import EqualizationParameters, EqualizationTank
from z85snip.io.exporters import export_run_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Расчет усреднителя по СНиП-85")
    parser.add_argument(
        "--flow-m3-per-day", type=float, required=False, help="Среднесуточный расход, м³/сут"
    )
    parser.add_argument("--flow-min-m3-per-day", type=float, help="Минимальный расход, м³/сут")
    parser.add_argument("--flow-max-m3-per-day", type=float, help="Максимальный расход, м³/сут")
    parser.add_argument("--averaging-hours", type=float, required=True, help="Время усреднения, ч")
    parser.add_argument(
        "--averaging-coefficient", type=float, required=True, help="Коэффициент усреднения"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Путь для записи результата в JSON. Если не задан — вывод в stdout",
    )
    return parser


def run_equalization_pipeline(
    flow_m3_per_day: float | None,
    averaging_hours: float,
    averaging_coefficient: float,
    *,
    flow_min_m3_per_day: float | None = None,
    flow_max_m3_per_day: float | None = None,
):
    params = EqualizationParameters(
        averaging_hours=averaging_hours, averaging_coefficient=averaging_coefficient
    )
    final_flow, results = run_pipeline(
        initial_flow=Flow(
            q_avg_m3_per_day=flow_m3_per_day,
            q_min_m3_per_day=flow_min_m3_per_day,
            q_max_m3_per_day=flow_max_m3_per_day,
        ),
        facilities=[EqualizationTank(params)],
    )
    return PipelineRun(initial_flow=final_flow, results=results)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    run = run_equalization_pipeline(
        flow_m3_per_day=args.flow_m3_per_day,
        averaging_hours=args.averaging_hours,
        averaging_coefficient=args.averaging_coefficient,
        flow_min_m3_per_day=args.flow_min_m3_per_day,
        flow_max_m3_per_day=args.flow_max_m3_per_day,
    )

    if args.output:
        export_run_json(run, args.output)
    else:
        export_run_json(run, Path("-"))

    return 0
