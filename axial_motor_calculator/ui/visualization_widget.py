"""Motor visualization widget."""

from __future__ import annotations

import math

from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget


class VisualizationWidget(QWidget):
    def __init__(self, get_num_coils_callable, parent=None):
        super().__init__(parent)
        self.get_num_coils = get_num_coils_callable
        self.setMinimumSize(360, 360)

    def paintEvent(self, event):  # noqa: N802 - Qt API
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.fillRect(self.rect(), QColor("#05070D"))

            try:
                num_coils = int(float(str(self.get_num_coils()).strip() or "12"))
            except Exception:
                num_coils = 12
            num_coils = max(1, min(num_coils, 720))

            cx = self.width() // 2
            cy = self.height() // 2
            radius_outer = max(40, min(cx, cy) - 25)
            radius_inner = int(radius_outer * 0.58)

            painter.setPen(QPen(QColor("#D6A84F"), 2))
            painter.setBrush(QColor("#071A33"))
            painter.drawEllipse(cx - radius_outer, cy - radius_outer, 2 * radius_outer, 2 * radius_outer)

            painter.setPen(QPen(QColor("#0B2D5C"), 2))
            painter.setBrush(QColor("#05070D"))
            painter.drawEllipse(cx - radius_inner, cy - radius_inner, 2 * radius_inner, 2 * radius_inner)

            angle_step = 360.0 / float(num_coils)
            for i in range(num_coils):
                angle = math.radians(i * angle_step)
                x = cx + radius_outer * 0.82 * math.cos(angle)
                y = cy + radius_outer * 0.82 * math.sin(angle)
                color = QColor("#D6A84F") if i % 3 == 0 else QColor("#A8843A")
                painter.setBrush(color)
                painter.setPen(QPen(QColor("#05070D"), 1))
                painter.drawEllipse(int(x - 5), int(y - 5), 10, 10)

            painter.setPen(QPen(QColor("#E8E6DD"), 1))
            painter.drawText(self.rect(), Qt.AlignBottom | Qt.AlignHCenter, f"{num_coils} coils")
        except Exception:
            pass
