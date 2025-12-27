"""Прикладная оркестрация расчета технологической схемы."""

from __future__ import annotations

from typing import Iterable

from z85snip.core.pipeline import Pipeline
from z85snip.core.types import Flow
from z85snip.core.validation import require_positive, ValidationError
from z85snip.domain.facilities.base import Facility, FacilityResult


def _validate_flow_balance(flow: Flow) -> None:
    """Быстрая проверка согласованности Qmin/Qavg/Qmax."""

    if flow.q_min_m3_per_day is not None:
        require_positive(flow.q_min_m3_per_day, "Qmin (м³/сут)")
    if flow.q_avg_m3_per_day is not None:
        require_positive(flow.q_avg_m3_per_day, "Qavg (м³/сут)")
    if flow.q_max_m3_per_day is not None:
        require_positive(flow.q_max_m3_per_day, "Qmax (м³/сут)")
    if (
        flow.q_min_m3_per_day is not None
        and flow.q_avg_m3_per_day is not None
        and flow.q_max_m3_per_day is not None
    ):
        if not (flow.q_min_m3_per_day <= flow.q_avg_m3_per_day <= flow.q_max_m3_per_day):
            raise ValidationError("Несогласованный диапазон расходов: Qmin ≤ Qavg ≤ Qmax должно соблюдаться")


def run_pipeline(initial_flow: Flow, facilities: Iterable[Facility]) -> tuple[Flow, list[FacilityResult]]:
    """Построить и выполнить пайплайн, возвращая итоговый поток и отчеты по узлам."""

    _validate_flow_balance(initial_flow)
    pipeline = Pipeline(initial_flow)
    for facility in facilities:
        pipeline.add(facility)
    run = pipeline.run()
    results = run.results
    final_flow = results[-1].flow if results else initial_flow
    _validate_flow_balance(final_flow)
    return final_flow, results
