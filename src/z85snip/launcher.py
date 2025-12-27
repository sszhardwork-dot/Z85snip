"""CLI-лаунчер для сценариев, UI и быстрой проверки расчетов."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from z85snip.app import run_equalization_pipeline
from z85snip.application.pipeline import run_pipeline
from z85snip.application.scenarios import _chain_for_scenario, scenario_catalog
from z85snip.io.exporters import export_run_json
from z85snip.ui.qt.main import main as qt_main


def _run_scenario(name: str, *, export_path: Path | None = None) -> int:
    catalog = scenario_catalog()
    if name not in catalog:
        print(f"Неизвестный сценарий {name}. Доступные: {', '.join(sorted(catalog))}")
        return 1

    flow, facilities = _chain_for_scenario(catalog[name])
    final_flow, results = run_pipeline(flow, facilities)

    payload = {
        "scenario": catalog[name].description,
        "final_flow": {
            "q_min_m3_per_day": final_flow.q_min_m3_per_day,
            "q_avg_m3_per_day": final_flow.q_avg_m3_per_day,
            "q_max_m3_per_day": final_flow.q_max_m3_per_day,
            "pollutants": getattr(final_flow.pollutants, "__dict__", None)
            if final_flow.pollutants
            else None,
        },
        "results": [
            {
                "facility_key": r.facility_key,
                "inputs": r.report.inputs,
                "outputs": r.report.outputs,
                "checks": r.report.checks,
                "snip_refs": r.report.snip_refs,
                "assumptions": r.report.assumptions,
            }
            for r in results
        ],
    }

    if export_path is None:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        export_run_json(payload, export_path)
        print(f"JSON-отчет записан в {export_path}")
    return 0


def _run_pytest() -> int:
    try:
        return subprocess.call([sys.executable, "-m", "pytest", "-q"])
    except FileNotFoundError:
        print("Pytest недоступен в текущем окружении")
        return 1


def _add_equalization(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("equalization", help="Запуск расчета усреднителя")
    parser.add_argument("--flow-m3-per-day", type=float, required=True)
    parser.add_argument("--flow-min-m3-per-day", type=float, required=False)
    parser.add_argument("--flow-max-m3-per-day", type=float, required=False)
    parser.add_argument("--averaging-hours", type=float, required=True)
    parser.add_argument("--averaging-coefficient", type=float, required=True)
    parser.add_argument("--output", type=Path, default=None)

    def _handle(args: argparse.Namespace) -> int:
        run = run_equalization_pipeline(
            flow_m3_per_day=args.flow_m3_per_day,
            averaging_hours=args.averaging_hours,
            averaging_coefficient=args.averaging_coefficient,
            flow_min_m3_per_day=args.flow_min_m3_per_day,
            flow_max_m3_per_day=args.flow_max_m3_per_day,
        )
        payload = {
            "initial_flow": run.initial_flow,
            "results": run.results,
        }
        export_run_json(payload, args.output or Path("-"))
        return 0

    parser.set_defaults(func=_handle)


def _add_ui(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("ui", help="Запуск Qt-интерфейса")

    def _handle(_: argparse.Namespace) -> int:
        return qt_main()

    parser.set_defaults(func=_handle)


def _add_scenarios(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("scenario", help="Запуск встроенного сценария A/B/C")
    parser.add_argument("name", choices=sorted(scenario_catalog().keys()))
    parser.add_argument("--export-json", type=Path, default=None, help="Путь до JSON-отчета")

    def _handle(args: argparse.Namespace) -> int:
        return _run_scenario(args.name, export_path=args.export_json)

    parser.set_defaults(func=_handle)


def _add_tests(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("tests", help="Быстро запустить pytest")

    def _handle(_: argparse.Namespace) -> int:
        return _run_pytest()

    parser.set_defaults(func=_handle)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Лаунчер Z85snip")
    subparsers = parser.add_subparsers(dest="command", required=True)
    _add_scenarios(subparsers)
    _add_equalization(subparsers)
    _add_ui(subparsers)
    _add_tests(subparsers)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "func", None)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
