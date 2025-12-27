"""Базовые типы данных проекта.

В этом модуле нет расчетной логики: только структуры данных и соглашения
по единицам измерения. Все поля, связанные с расходами, задаются в м³/сут,
поскольку СНиП-85 оперирует суточными величинами для гидравлики и времени
пребывания. Для почасового профиля используйте :mod:`z85snip.domain.streams`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class Pollutants:
    """Состав сточной воды.

    Значения указываются в мг/л. Поля могут расширяться без нарушения API.
    """

    bod_full_mg_per_l: float | None = None
    suspended_solids_mg_per_l: float | None = None
    ammonium_mg_per_l: float | None = None


@dataclass(frozen=True)
class Flow:
    """Расход сточных вод с учетом режимов Qmin/Qavg/Qmax.

    По канонической схеме СНиП-85 каждый режим используется для своего
    участка расчета. Поле ``q_avg_m3_per_day`` используется как основное
    «рабочее» значение, если явно не указан другой режим.
    """

    q_min_m3_per_day: float | None = None
    q_avg_m3_per_day: float | None = None
    q_max_m3_per_day: float | None = None
    pollutants: Pollutants | Mapping[str, float] | None = None
    meta: Mapping[str, str] | None = None

    @property
    def Q_m3_per_day(self) -> float | None:
        """Совместимость со старыми вызовами.

        Возвращает ``q_avg_m3_per_day`` как основное расчетное значение,
        что соответствует методике СНиП при расчете объемов.
        """

        return self.q_avg_m3_per_day
