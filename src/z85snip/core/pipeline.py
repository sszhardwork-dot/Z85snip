"""Последовательное выполнение цепочки сооружений."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from z85snip.core.errors import ValidationError
from z85snip.core.types import Flow
from z85snip.domain.facilities.base import Facility, FacilityResult


@dataclass
class PipelineRun:
    initial_flow: Flow
    results: List[FacilityResult] = field(default_factory=list)


class Pipeline:
    def __init__(self, initial_flow: Flow):
        self._initial_flow = initial_flow
        self._nodes: List[Facility] = []

    def add(self, facility: Facility) -> None:
        self._nodes.append(facility)

    def remove(self, facility: Facility) -> None:
        try:
            self._nodes.remove(facility)
        except ValueError as exc:
            raise ValidationError("Узел для удаления не найден в пайплайне") from exc

    def run(self) -> PipelineRun:
        flow = self._initial_flow
        results: List[FacilityResult] = []
        for node in self._nodes:
            result = node.calculate(flow)
            results.append(result)
            flow = result.flow
        return PipelineRun(initial_flow=self._initial_flow, results=results)
