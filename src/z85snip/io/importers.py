"""Загрузка входных данных."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from z85snip.domain.streams import InflowProfile, InflowProfilePoint


def load_inflow_profile_csv(path: Path) -> InflowProfile:
    points: list[InflowProfilePoint] = []
    with path.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            points.append(
                InflowProfilePoint(
                    hour=int(row["hour"]), Q_m3_per_hour=float(row["Q_m3_per_hour"])
                )
            )
    return InflowProfile(points=points)
