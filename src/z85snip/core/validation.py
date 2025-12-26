from __future__ import annotations
from .errors import ValidationError

def require_positive(value: float, name: str) -> float:
    if value is None:
        raise ValidationError(f\"{name}: значение не задано\")
    try:
        v = float(value)
    except Exception as e:
        raise ValidationError(f\"{name}: нельзя привести к числу: {value!r}\") from e
    if v <= 0:
        raise ValidationError(f\"{name}: должно быть > 0 (получено {v})\")
    return v

def require_non_negative(value: float, name: str) -> float:
    if value is None:
        raise ValidationError(f\"{name}: значение не задано\")
    try:
        v = float(value)
    except Exception as e:
        raise ValidationError(f\"{name}: нельзя привести к числу: {value!r}\") from e
    if v < 0:
        raise ValidationError(f\"{name}: должно быть >= 0 (получено {v})\")
    return v
