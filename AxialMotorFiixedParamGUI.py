"""Backward-compatible launcher for the modern axial motor calculator UI."""

import os
import sys

os.environ.setdefault("QT_OPENGL", "software")

from PyQt5.QtWidgets import QApplication

from axial_motor_calculator.ui.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
