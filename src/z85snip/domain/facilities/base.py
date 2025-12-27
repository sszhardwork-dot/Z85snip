"""Контракты сооружений."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from z85snip.core.types import Flow


@dataclass(frozen=True)
class FacilityReport:
    inputs: dict
    outputs: dict
    checks: list[str]
    snip_refs: list[str]
    assumptions: list[str]


@dataclass(frozen=True)
class FacilityResult:
    flow: Flow
    report: FacilityReport
    facility_key: str


class Facility(Protocol):
    def calculate(self, inflow: Flow) -> FacilityResult:
        ...
