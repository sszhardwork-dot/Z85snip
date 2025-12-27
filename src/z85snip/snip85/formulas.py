"""Совместимость: re-export формул в новых модулях snip85.*."""

from __future__ import annotations

from z85snip.snip85.hydraulics import equalization_volume as calc_equalization_volume

__all__ = ["calc_equalization_volume"]
