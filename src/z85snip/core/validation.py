from __future__ import annotations

from .errors import ValidationError


def require_not_none(value, name: str):
    if value is None:
        raise ValidationError(f"{name}: значение не задано")
    return value


def _as_float(value, name: str) -> float:
    try:
        return float(value)
    except Exception as e:  # pragma: no cover - defensively narrow
        raise ValidationError(f"{name}: нельзя привести к числу: {value!r}") from e


def require_positive(value: float, name: str) -> float:
    require_not_none(value, name)
    v = _as_float(value, name)
    if v <= 0:
        raise ValidationError(f"{name}: должно быть > 0 (получено {v})")
    return v


def require_non_negative(value: float, name: str) -> float:
    require_not_none(value, name)
    v = _as_float(value, name)
    if v < 0:
        raise ValidationError(f"{name}: должно быть >= 0 (получено {v})")
    return v


def require_range(value: float, name: str, min_value: float, max_value: float) -> float:
    require_not_none(value, name)
    v = _as_float(value, name)
    if v < min_value or v > max_value:
        raise ValidationError(
            f"{name}: вне допустимого диапазона [{min_value}, {max_value}] (получено {v})"
        )
    return v


def require_probability(value: float, name: str) -> float:
    """Проверка для коэффициентов и вероятностей в диапазоне [0, 1]."""

    return require_range(value, name, 0.0, 1.0)


def require_nonempty_string(value: str, name: str) -> str:
    require_not_none(value, name)
    if not isinstance(value, str):  # pragma: no cover - defensive
        raise ValidationError(f"{name}: требуется строка, получено {type(value)}")
    trimmed = value.strip()
    if not trimmed:
        raise ValidationError(f"{name}: строка не должна быть пустой")
    return trimmed
