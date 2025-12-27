from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .project_window import ProjectWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = ProjectWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
