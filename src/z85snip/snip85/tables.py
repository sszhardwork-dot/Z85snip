"""Работа с табличными данными СНиП."""

from __future__ import annotations

from typing import Iterable, Sequence, Tuple

from z85snip.core.validation import require_range


def _validate_points(points: Sequence[Tuple[float, float]]) -> None:
    if len(points) < 2:
        raise ValueError("Для интерполяции нужно минимум две точки")
    xs = [p[0] for p in points]
    if xs != sorted(xs):
        raise ValueError("Точки должны быть отсортированы по оси X")


def linear_interp(points: Sequence[Tuple[float, float]], x: float) -> float:
    _validate_points(points)
    xs = [p[0] for p in points]
    require_range(x, "x", xs[0], xs[-1])
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= x <= x1:
            if x1 == x0:
                return y0
            k = (y1 - y0) / (x1 - x0)
            return y0 + k * (x - x0)
    # pragma: no cover - require_range выше гарантирует возврат
    raise ValueError("Не удалось интерполировать значение")
