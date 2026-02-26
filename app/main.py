#!/usr/bin/env python3
"""Entry point for the DB Normalization Checker desktop app."""
import sys
from pathlib import Path

# Ensure app is on path when run as script
if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("DB Normalization Checker")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
