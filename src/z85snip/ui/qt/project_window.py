from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ProjectWindow(QMainWindow):
    """Главное окно проекта с каноническими экранами и карточками сооружений."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Z85snip — проект СНиП-85")
        self.resize(1280, 800)

        tabs = QTabWidget()
        tabs.addTab(self._build_scheme_tab(), "Схема")
        tabs.addTab(self._build_inflow_tab(), "Приток и состав")
        tabs.addTab(self._build_facilities_tab(), "Параметры сооружений")
        tabs.addTab(self._build_report_tab(), "Отчет")

        self.setCentralWidget(tabs)

    def _build_scheme_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)

        toolbar = QHBoxLayout()
        for label in [
            "Добавить",
            "Удалить",
            "Вверх",
            "Вниз",
            "Рециркуляция",
            "Дублировать",
            "Быстрые проверки",
        ]:
            toolbar.addWidget(QPushButton(label))
        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self._build_scheme_tree())
        splitter.addWidget(self._build_facility_card())
        splitter.addWidget(self._build_connection_panel())
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)
        layout.addWidget(splitter)
        return container

    def _build_scheme_tree(self) -> QWidget:
        tree = QTreeWidget()
        tree.setHeaderLabels(["Сооружения и связи"])
        mechanics = QTreeWidgetItem(["Механика"])
        screens = QTreeWidgetItem(["Решетки R1"])
        grit = QTreeWidgetItem(["Песколовка P1"])
        settlers = QTreeWidgetItem(["Первичный отстойник O1"])
        mechanics.addChildren([screens, grit, settlers])

        biology = QTreeWidgetItem(["Биология"])
        aeration = QTreeWidgetItem(["Аэротенк AT1"])
        regenerator = QTreeWidgetItem(["Регенератор RG1"])
        biology.addChildren([aeration, regenerator])

        sludge = QTreeWidgetItem(["Иловая линия"])
        thickener = QTreeWidgetItem(["Уплотнитель IL1"])
        sludge.addChild(thickener)

        recirculations = QTreeWidgetItem(["Рециркуляции"])
        recirculations.addChild(QTreeWidgetItem(["Возврат из AT1 в P1 (Ri=0.3)"]))

        for root in [mechanics, biology, sludge, recirculations]:
            tree.addTopLevelItem(root)
        tree.expandAll()
        return tree

    def _build_facility_card(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self._build_identification_section())
        layout.addWidget(self._build_flow_modes_section())
        layout.addWidget(self._build_snip_parameters_section())
        layout.addWidget(self._build_geometry_section())
        layout.addWidget(self._build_operation_section())
        layout.addWidget(self._build_results_section())
        layout.addStretch(1)
        return widget

    def _build_identification_section(self) -> QGroupBox:
        box = QGroupBox("Идентификация")
        form = QFormLayout(box)
        form.addRow("Имя", QLineEdit("AT1"))
        type_combo = QComboBox()
        type_combo.addItems(["MECH.SCREENS", "MECH.GRIT", "MECH.SETTLER", "BIO.AERATION", "BIO.REGEN"])
        form.addRow("Код/тип", type_combo)
        version = QLineEdit("v1.0")
        version.setReadOnly(True)
        form.addRow("Версия расчета", version)
        return box

    def _build_flow_modes_section(self) -> QGroupBox:
        box = QGroupBox("Режимы расхода")
        vbox = QVBoxLayout(box)

        form = QFormLayout()
        for label in ["Qmin (м³/сут)", "Qavg (м³/сут)", "Qmax (м³/сут)"]:
            spin = QDoubleSpinBox()
            spin.setRange(0, 1_000_000)
            spin.setValue(720.0 if "avg" in label else 480.0 if "min" in label else 1200.0)
            spin.setSuffix(" м³/сут")
            spin.setDecimals(2)
            form.addRow(label, spin)
        vbox.addLayout(form)

        table = QTableWidget(3, 2)
        table.setHorizontalHeaderLabels(["Расчет", "Используемый Q"])
        table.setVerticalHeaderLabels(["Пропуск/гидравлика", "Объем/время", "Проверки"])
        table.setItem(0, 0, QTableWidgetItem("Гидравлика"))
        table.setItem(0, 1, QTableWidgetItem("Qmax"))
        table.setItem(1, 0, QTableWidgetItem("Объем/время"))
        table.setItem(1, 1, QTableWidgetItem("Qavg"))
        table.setItem(2, 0, QTableWidgetItem("Проверки"))
        table.setItem(2, 1, QTableWidgetItem("Qmin / Qmax"))
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setStretchLastSection(False)
        vbox.addWidget(table)

        override = QCheckBox("Разрешить ручное переопределение Q для этого сооружения")
        vbox.addWidget(override)
        return box

    def _build_snip_parameters_section(self) -> QGroupBox:
        box = QGroupBox("Параметры СНиП")
        vbox = QVBoxLayout(box)
        table = QTableWidget(5, 4)
        table.setHorizontalHeaderLabels(["Параметр", "Значение", "Источник", "Ссылка"])
        params = [
            ("q_s", "24", "СНиП", "4.2.3"),
            ("phi", "0.65", "СНиП", "4.1.2"),
            ("R_i", "0.3", "Пользователь", "4.3.1"),
            ("rho", "0.8", "СНиП", "4.3.2"),
            ("t_at", "8", "Пользователь", "4.3.5"),
        ]
        for row, (name, value, source, ref) in enumerate(params):
            for col, text in enumerate([name, value, source, ref]):
                table.setItem(row, col, QTableWidgetItem(text))
        table.horizontalHeader().setStretchLastSection(True)
        vbox.addWidget(table)

        buttons = QHBoxLayout()
        buttons.addWidget(QPushButton("Сбросить к СНиП"))
        buttons.addWidget(QPushButton("Открыть пункт/таблицу"))
        buttons.addStretch(1)
        vbox.addLayout(buttons)
        return box

    def _build_geometry_section(self) -> QGroupBox:
        box = QGroupBox("Геометрия и уровни воды")
        form = QFormLayout(box)
        geom_type = QComboBox()
        geom_type.addItems(["Прямоугольный", "Цилиндрический", "Составной", "Профильное сечение"])
        form.addRow("Тип формы", geom_type)

        form.addRow("Длина (м)", self._spin(0, 500, 60.0))
        form.addRow("Ширина (м)", self._spin(0, 100, 8.0))
        form.addRow("Глубина (м)", self._spin(0, 50, 5.0))
        form.addRow("h_min (м)", self._spin(0, 20, 2.0))
        form.addRow("h_avg (м)", self._spin(0, 20, 3.5))
        form.addRow("h_max (м)", self._spin(0, 20, 5.0))

        summary = QTableWidget(3, 2)
        summary.setHorizontalHeaderLabels(["Уровень", "W(h) м³"])
        summary.setVerticalHeaderLabels(["h_min", "h_avg", "h_max"])
        for i, value in enumerate([1200, 1800, 2500]):
            summary.setItem(i, 0, QTableWidgetItem(summary.verticalHeaderItem(i).text()))
            summary.setItem(i, 1, QTableWidgetItem(str(value)))
        summary.horizontalHeader().setStretchLastSection(True)
        form.addRow(QLabel("Расчетные объемы"), summary)

        indicator = QLabel("W(h_max) ≥ W_req: ОК")
        indicator.setStyleSheet("color: green; font-weight: bold;")
        form.addRow("Статус", indicator)
        return box

    def _build_operation_section(self) -> QGroupBox:
        box = QGroupBox("Эксплуатация / Компоновка")
        form = QFormLayout(box)
        sections_spin = QSpinBox()
        sections_spin.setRange(1, 12)
        sections_spin.setValue(2)
        form.addRow("Число секций/линий", sections_spin)
        form.addRow("Резервирование", QCheckBox("Есть резервная линия"))
        form.addRow("Режим обслуживания", self._enum_combo(["ручная", "механическая"]))
        return box

    def _build_results_section(self) -> QGroupBox:
        box = QGroupBox("Результаты / Отчет")
        vbox = QVBoxLayout(box)
        vbox.addWidget(QLabel("Ключевые выходы: W_req, W_fact, t, v, n"))

        tabs = QTabWidget()
        for name in ["Входные", "Промежуточные", "Проверки", "Ссылки СНиП", "Допущения"]:
            tabs.addTab(QLabel(f"Раздел {name}"), name)
        vbox.addWidget(tabs)
        return box

    def _build_connection_panel(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Связи/рециркуляции"))

        water_link = QGroupBox("Поток воды")
        form_water = QFormLayout(water_link)
        form_water.addRow("Источник", QLineEdit("O1"))
        form_water.addRow("Приемник", QLineEdit("AT1"))
        form_water.addRow("Q режим", self._enum_combo(["Qmin", "Qavg", "Qmax"]))
        layout.addWidget(water_link)

        recirc = QGroupBox("Рециркуляция")
        form_recirc = QFormLayout(recirc)
        form_recirc.addRow("Источник", QLineEdit("AT1"))
        form_recirc.addRow("Приемник", QLineEdit("P1"))
        form_recirc.addRow("Тип", self._enum_combo(["возврат ила", "внутренняя", "внешняя"]))
        form_recirc.addRow("Метод", self._enum_combo(["R фикс.", "Qrecirc фикс.", "Итерация"]))
        form_recirc.addRow("R", self._spin(0, 5, 0.3, step=0.01))
        form_recirc.addRow("Qrecirc (м³/сут)", self._spin(0, 50000, 3600, step=10))
        form_recirc.addRow("Qmix (м³/сут)", self._spin(0, 50000, 9600, step=10))
        layout.addWidget(recirc)

        layout.addStretch(1)
        return widget

    def _build_inflow_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        mode_group = QGroupBox("Режим ввода")
        mode_layout = QHBoxLayout(mode_group)
        profile_radio = QRadioButton("Профиль Q(t)")
        summary_radio = QRadioButton("Только 3 точки")
        profile_radio.setChecked(True)
        group = QButtonGroup(mode_group)
        group.addButton(profile_radio)
        group.addButton(summary_radio)
        mode_layout.addWidget(profile_radio)
        mode_layout.addWidget(summary_radio)
        mode_layout.addStretch(1)
        layout.addWidget(mode_group)

        profile_table = QTableWidget(4, 2)
        profile_table.setHorizontalHeaderLabels(["t", "Q(t), м³/ч"])
        profile_table.setVerticalHeaderLabels(["00:00", "06:00", "12:00", "18:00"])
        for i, val in enumerate([150, 280, 320, 200]):
            profile_table.setItem(i, 0, QTableWidgetItem(profile_table.verticalHeaderItem(i).text()))
            profile_table.setItem(i, 1, QTableWidgetItem(str(val)))
        profile_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(profile_table)

        inflow_group = QGroupBox("Расчетные режимы")
        inflow_form = QFormLayout(inflow_group)
        inflow_form.addRow("Qmin (м³/сут)", self._spin(0, 200000, 480))
        inflow_form.addRow("Qavg (м³/сут)", self._spin(0, 200000, 720))
        inflow_form.addRow("Qmax (м³/сут)", self._spin(0, 200000, 1200))
        layout.addWidget(inflow_group)

        pollutants = QGroupBox("Состав притока")
        pol_form = QFormLayout(pollutants)
        pol_form.addRow("БПК полная (мг/л)", self._spin(0, 1000, 240))
        pol_form.addRow("Взвешенные (мг/л)", self._spin(0, 1000, 180))
        pol_form.addRow("Аммоний (мг/л)", self._spin(0, 200, 35))
        layout.addWidget(pollutants)

        layout.addStretch(1)
        return widget

    def _build_facilities_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addWidget(self._build_mechanical_screen_panel())
        layout.addWidget(self._build_mechanical_grit_panel())
        layout.addWidget(self._build_mechanical_settler_panel())
        layout.addWidget(self._build_aeration_panel())
        layout.addWidget(self._build_regenerator_panel())
        layout.addWidget(self._build_thickener_panel())

        layout.addStretch(1)
        scroll.setWidget(container)
        return scroll

    def _build_report_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        summary = QLabel("Общий отчет по схеме. Используйте вкладки справа для подробностей.")
        summary.setWordWrap(True)
        layout.addWidget(summary)

        report_tabs = QTabWidget()
        for name in ["Входные", "Промежуточные", "Проверки", "Ссылки СНиП", "Допущения"]:
            report_tabs.addTab(QLabel(f"Раздел {name}"), name)
        layout.addWidget(report_tabs)

        copy_button = QPushButton("Скопировать расчет")
        layout.addWidget(copy_button)
        return widget

    def _build_mechanical_screen_panel(self) -> QGroupBox:
        box = QGroupBox("МЕХАНИКА → Решетки")
        form = QFormLayout(box)
        form.addRow("Тип решетки", self._enum_combo(["грубая", "тонкая", "механизированная"]))
        form.addRow("Шаг прутьев s (мм)", self._spin(0, 100, 16, step=0.5))
        form.addRow("Толщина прутьев t (мм)", self._spin(0, 50, 8, step=0.5))
        form.addRow("Угол установки (°)", self._spin(0, 90, 60, step=1))
        form.addRow("Коэф. засорения φ", self._spin(0, 1, 0.65, step=0.01))
        form.addRow("Допустимая скорость v_allow (м/с)", self._spin(0, 5, 0.8, step=0.01))
        form.addRow("Режим обслуживания", self._enum_combo(["ручная", "механическая"]))
        form.addRow("Q для пропуска", self._enum_combo(["Qmax (по умолчанию)", "Qavg", "Qmin"]))
        form.addRow("A_eff (м²)", self._spin(0, 500, 4.5, step=0.01))
        form.addRow("v (м/с)", self._spin(0, 5, 0.2, step=0.01))
        form.addRow("ΔH (м)", self._spin(0, 2, 0.01, step=0.001))
        form.addRow("Число линий n", self._spin(1, 10, 2, step=1))
        form.addRow("Резервная линия", QCheckBox("Добавить резерв"))
        form.addRow("Ширина канала (м)", self._spin(0, 20, 1.2, step=0.01))
        form.addRow("Высота воды (м)", self._spin(0, 10, 2.0, step=0.01))
        return box

    def _build_mechanical_grit_panel(self) -> QGroupBox:
        box = QGroupBox("МЕХАНИКА → Песколовки")
        form = QFormLayout(box)
        form.addRow("Тип", self._enum_combo(["горизонтальная", "аэрируемая", "вихревая"]))
        form.addRow("Скорость v (м/с)", self._spin(0, 2, 0.3, step=0.01))
        form.addRow("Время пребывания t (ч)", self._spin(0, 10, 1.2, step=0.01))
        form.addRow("Глубина (м)", self._spin(0, 10, 3.0, step=0.01))
        form.addRow("Ширина (м)", self._spin(0, 20, 4.0, step=0.01))
        form.addRow("Длина (м)", self._spin(0, 200, 40.0, step=0.1))
        form.addRow("h_min/avg/max (м)", QLabel("2.0 / 3.0 / 3.5"))
        form.addRow("W (м³)", self._spin(0, 20000, 3600, step=1))
        form.addRow("t проверка", QLabel("t=W/Qavg"))
        form.addRow("Скорости при Qmin/Qmax", QLabel("в диапазоне"))
        return box

    def _build_mechanical_settler_panel(self) -> QGroupBox:
        box = QGroupBox("МЕХАНИКА → Первичные отстойники")
        form = QFormLayout(box)
        form.addRow("Тип", self._enum_combo(["радиальный", "горизонтальный"]))
        form.addRow("q_s (м³/(м²·сут))", self._spin(0, 100, 24, step=0.1))
        form.addRow("F (м²) = Q/q_s", self._spin(0, 5000, 40, step=0.1))
        form.addRow("H_work (м)", self._spin(0, 10, 3.0, step=0.01))
        form.addRow("W (м³)", self._spin(0, 50000, 1200, step=1))
        form.addRow("t=W/Q", QLabel("проверка"))
        form.addRow("Диаметр/длина", self._spin(0, 100, 24, step=0.1))
        form.addRow("Ширина", self._spin(0, 50, 8, step=0.1))
        form.addRow("Глубина", self._spin(0, 10, 3.5, step=0.01))
        form.addRow("Эффект SS (%)", self._spin(0, 100, 55, step=0.1))
        form.addRow("Эффект БПК (%)", self._spin(0, 100, 30, step=0.1))
        form.addRow("Число сооружений", self._spin(1, 10, 2, step=1))
        return box

    def _build_aeration_panel(self) -> QGroupBox:
        box = QGroupBox("БИОЛОГИЯ → Аэротенки")
        form = QFormLayout(box)
        form.addRow("Подтип", self._enum_combo(["E3", "E4"]))
        form.addRow("Q_in (м³/сут)", self._spin(0, 200000, 9600, step=10))
        form.addRow("R_i", self._spin(0, 5, 0.3, step=0.01))
        form.addRow("Q_recirc (м³/сут)", self._spin(0, 200000, 2880, step=10))
        form.addRow("Q_mix (м³/сут)", self._spin(0, 200000, 12480, step=10))
        form.addRow("L_mix (мг/л)", self._spin(0, 1000, 180, step=0.1))
        form.addRow("ρ (мг/(л·ч))", self._spin(0, 5, 0.8, step=0.01))
        form.addRow("t_atm (ч)", self._spin(0, 48, 2.5, step=0.1))
        form.addRow("t_atx (ч)", self._spin(0, 48, 5.5, step=0.1))
        form.addRow("t_at (ч)", QLabel("t_atm + t_atx"))
        form.addRow("t_r (ч)", self._spin(0, 48, 2.0, step=0.1))
        form.addRow("t_o (ч)", QLabel("t_at - t_r"))
        form.addRow("a_r (кг/м³)", self._spin(0, 10, 2.0, step=0.01))
        form.addRow("Геометрия", QLabel("Прямоугольный / коридорный"))
        form.addRow("Длина (м)", self._spin(0, 200, 80, step=0.1))
        form.addRow("Ширина (м)", self._spin(0, 50, 10, step=0.1))
        form.addRow("Глубина (м)", self._spin(0, 20, 6, step=0.01))
        form.addRow("Число коридоров", self._spin(1, 10, 2, step=1))
        form.addRow("W_req (м³)", QLabel("Q_mix * t_at"))
        form.addRow("W(h_avg/max)", QLabel("проверка"))
        form.addRow("Диапазоны", QLabel("ρ, a, R_i, t_at в норме"))
        return box

    def _build_regenerator_panel(self) -> QGroupBox:
        box = QGroupBox("БИОЛОГИЯ → Регенератор")
        form = QFormLayout(box)
        form.addRow("Привязан к аэротенку", self._enum_combo(["AT1", "AT2"]))
        form.addRow("Q_recirc (м³/сут)", self._spin(0, 200000, 2880, step=10))
        form.addRow("t_r (ч)", self._spin(0, 48, 2.0, step=0.1))
        form.addRow("a_r (кг/м³)", self._spin(0, 10, 2.0, step=0.01))
        form.addRow("Геометрия", QLabel("Тип/параметры/уровни"))
        form.addRow("W (м³)", self._spin(0, 20000, 4800, step=1))
        form.addRow("Проверки", QLabel("время, диапазоны"))
        return box

    def _build_thickener_panel(self) -> QGroupBox:
        box = QGroupBox("ИЛОВАЯ ЛИНИЯ → Уплотнители")
        form = QFormLayout(box)
        form.addRow("Тип", self._enum_combo(["гравитационный", "механический"]))
        form.addRow("Q_s (м³/сут)", self._spin(0, 50000, 1200, step=10))
        form.addRow("Концентрация (%)", self._spin(0, 100, 3.5, step=0.1))
        form.addRow("Нагрузка", QLabel("таблица/формула"))
        form.addRow("Площадь/объем", self._spin(0, 5000, 450, step=1))
        form.addRow("Время пребывания (ч)", self._spin(0, 72, 12, step=0.1))
        form.addRow("Геометрия", QLabel("Круглый/прямоугольный"))
        form.addRow("Статус", QLabel("по СНиП"))
        return box

    def _spin(self, min_value: float, max_value: float, value: float, *, step: float = 1.0) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(min_value, max_value)
        spin.setDecimals(3)
        spin.setSingleStep(step)
        spin.setValue(value)
        return spin

    def _enum_combo(self, options: Iterable[str]) -> QComboBox:
        combo = QComboBox()
        combo.addItems(list(options))
        return combo


__all__ = ["ProjectWindow"]
