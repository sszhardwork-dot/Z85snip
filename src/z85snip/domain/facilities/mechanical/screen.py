from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Screen:
    \"\"\"Решетка (заглушка модели).\"\"\"
    name: str = \"Screen\"
