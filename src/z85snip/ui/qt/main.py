from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel

def main() -> int:
    app = QApplication(sys.argv)
    w = QWidget()
    w.setWindowTitle(\"Z85snip\")
    layout = QVBoxLayout(w)
    layout.addWidget(QLabel(\"Z85snip: UI scaffold (PySide6)\"))

    w.resize(640, 360)
    w.show()
    return app.exec()

if __name__ == \"__main__\":
    raise SystemExit(main())
