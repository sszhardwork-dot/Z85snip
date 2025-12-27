# Z85snip

Инженерный калькулятор расчётов КОС по СНиП-85.

## Быстрый старт
- Создайте venv и установите зависимости: `pip install -e .`.
- Запустите расчёт усреднителя: `python -m z85snip --flow-m3-per-day 960 --flow-min-m3-per-day 720 --flow-max-m3-per-day 1200 --averaging-hours 4 --averaging-coefficient 1.15`.
- Если есть почасовой профиль, загрузите его через `io.importers.load_inflow_profile_csv` и передайте в пайплайн как `Flow`.
- Каркас UI с вкладками «Схема/Приток/Параметры/Отчет» можно открыть командой `python -m z85snip.ui.qt.main` (PySide6).

Документ по единицам и входным данным: [docs/inputs.md](docs/inputs.md).

## Слои и директории
- `src/z85snip/core` — базовые типы, валидация, пайплайн, реестр.
- `src/z85snip/snip85` — формулы, таблицы и ссылки на пункты СНиП.
- `src/z85snip/domain` — предметные модели: профиль притока, геометрия, сооружения.
- `src/z85snip/io` — импорт/экспорт входных и выходных данных.
- `src/z85snip/ui` — визуализация (каркас Qt, без расчётной логики).
- `data/` — библиотека СНиП и примеры входных данных (`data/snip85/snip85_library.json`, `data/examples/inflow_profile_example.csv`).
- `tests/` — автоматические проверки Pytest.

