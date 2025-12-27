"""Гидравлические формулы СНиП-85.

Каждая функция принимает и возвращает значения в фиксированных единицах, что
описано в docstring. Здесь нет привязки к конкретным сооружениям.
"""

from __future__ import annotations

from z85snip.core.validation import require_positive


def equalization_volume(Q_m3_per_day: float, averaging_hours: float, K: float) -> float:
    """Требуемый объем усреднителя.

    :param Q_m3_per_day: среднесуточный расход, м³/сут
    :param averaging_hours: время усреднения, ч
    :param K: коэффициент усреднения (безразмерный)
    :returns: объем, м³
    """

    Q = require_positive(Q_m3_per_day, "Q (м³/сут)")
    t = require_positive(averaging_hours, "t (ч)")
    k = require_positive(K, "K (коэффициент усреднения)")
    return Q * (t / 24.0) * k


def detention_time_hours(volume_m3: float, Q_m3_per_day: float) -> float:
    """Время пребывания в резервуаре (ч)."""

    V = require_positive(volume_m3, "Объем (м³)")
    Q = require_positive(Q_m3_per_day, "Расход (м³/сут)")
    return (V / Q) * 24.0


def surface_loading_area(Q_m3_per_day: float, q_surface_m3_per_m2_per_day: float) -> float:
    """Расчет требуемой площади по поверхностной нагрузке (м²)."""

    Q = require_positive(Q_m3_per_day, "Расход (м³/сут)")
    q_surface = require_positive(q_surface_m3_per_m2_per_day, "Поверхностная нагрузка (м³/(м²·сут))")
    return Q / q_surface


def detention_volume_from_seconds(Q_m3_per_day: float, detention_time_seconds: float) -> float:
    """Расчет требуемого объема W = Q * t/86400 (м³)."""

    Q = require_positive(Q_m3_per_day, "Расход (м³/сут)")
    t = require_positive(detention_time_seconds, "Время пребывания (с)")
    return Q * (t / 86400.0)


def primary_settler_area_qmax_hour(Q_max_m3_per_day: float, surface_loading_m3_per_m2_per_h: float) -> float:
    """Площадь отстойника по поверхностной нагрузке при Qmax (м²)."""

    q_max_hour = require_positive(Q_max_m3_per_day, "Qmax (м³/сут)") / 24.0
    q_surface = require_positive(surface_loading_m3_per_m2_per_h, "Поверхностная нагрузка (м³/(м²·ч))")
    return q_max_hour / q_surface


def volume_from_area_and_depth(area_m2: float, depth_m: float) -> float:
    """Объем резервуара как произведение площади и глубины (м³)."""

    a = require_positive(area_m2, "Площадь (м²)")
    h = require_positive(depth_m, "Глубина (м)")
    return a * h


def process_volume_from_time(Q_m3_per_day: float, time_hours: float) -> float:
    """Вспомогательная формула W = Q * t/24 для аэротенков/регенераторов."""

    Q = require_positive(Q_m3_per_day, "Расход (м³/сут)")
    t = require_positive(time_hours, "Время (ч)")
    return Q * (t / 24.0)
