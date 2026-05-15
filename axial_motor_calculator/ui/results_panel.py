"""Results display widgets."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QHeaderView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout


class ResultsPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Results", parent)
        layout = QVBoxLayout(self)
        self.summary = QLabel("Ready")
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        self.table = QTableWidget(0, 2)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

    def show_calculations(self, calculations: dict) -> None:
        self.summary.setText("Manual calculation complete.")
        self.table.setSortingEnabled(False)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.table.setRowCount(len(calculations))
        for row, (key, value) in enumerate(calculations.items()):
            self.table.setItem(row, 0, QTableWidgetItem(str(key)))
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 1, item)
        self.table.setSortingEnabled(True)

    def show_candidates(self, candidates) -> None:
        if not candidates:
            self.summary.setText("Optimization produced no candidates.")
            self.table.setRowCount(0)
            return
        best = candidates[0]
        pass_text = "PASS" if not best.violations else "CHECK: " + "; ".join(best.violations)
        self.summary.setText(
            f"Best score {best.score:.3f} — {pass_text}. "
            f"Voltage {best.inputs.get('input_voltage')} V, radius {best.inputs.get('outer_radius')} m, "
            f"turns {best.inputs.get('turns')}."
        )
        headers = ["Rank", "Score", "Status", "Voltage", "Turns", "Radius", "Poles", "B", "Dual", "Phase A", "Est DC A", "V Util", "Torque"]
        self.table.setSortingEnabled(False)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(candidates))
        for idx, result in enumerate(candidates, start=1):
            values = [
                idx,
                f"{result.score:.3f}" if result.score is not None else "—",
                "PASS" if not result.violations else "CHECK",
                result.inputs.get("input_voltage"),
                result.inputs.get("turns"),
                result.inputs.get("outer_radius"),
                result.inputs.get("poles"),
                result.inputs.get("magnetic_flux_density"),
                result.inputs.get("dual_plate"),
                result.calculations.get("Required Current (A)", "—"),
                result.calculations.get("Estimated DC Current (A)", "—"),
                result.calculations.get("Voltage Utilization (V_emf/V_avail)", "—"),
                result.calculations.get("Total Torque (N-m)", "—"),
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if col not in (2,):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(idx - 1, col, item)
        self.table.setSortingEnabled(True)
