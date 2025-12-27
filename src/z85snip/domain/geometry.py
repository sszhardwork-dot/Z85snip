"""Геометрические примитивы для расчета объемов."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class VolumeProvider(Protocol):
    def volume(self) -> float:
        ...


@dataclass(frozen=True)
class RectangularPrism(VolumeProvider):
    length_m: float
    width_m: float
    height_m: float

    def volume(self) -> float:
        return self.length_m * self.width_m * self.height_m
