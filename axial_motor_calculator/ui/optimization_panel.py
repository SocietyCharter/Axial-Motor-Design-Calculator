"""Optimization controls."""

from __future__ import annotations

from PyQt5.QtWidgets import QComboBox, QGroupBox, QHBoxLayout, QLabel, QProgressBar, QPushButton, QSpinBox, QVBoxLayout


class OptimizationPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Machine Learning Optimization", parent)
        layout = QVBoxLayout(self)
        controls = QHBoxLayout()
        self.objective = QComboBox()
        self.objective.addItems(["balanced", "max_torque", "min_current", "max_rpm", "min_radius", "min_stress"])
        self.trials = QSpinBox()
        self.trials.setRange(1, 5000)
        self.trials.setValue(100)
        self.calculate_button = QPushButton("Calculate Fixed Design")
        self.optimize_button = QPushButton("Run ML Optimize")
        self.export_button = QPushButton("Export CSV")
        self.export_button.setEnabled(False)
        controls.addWidget(QLabel("Objective"))
        controls.addWidget(self.objective)
        controls.addWidget(QLabel("Trials"))
        controls.addWidget(self.trials)
        controls.addWidget(self.calculate_button)
        controls.addWidget(self.optimize_button)
        controls.addWidget(self.export_button)
        layout.addLayout(controls)
        self.status = QLabel("Ready. Edit Min/Max bounds, then optimize.")
        self.status.setWordWrap(True)
        self.progress = QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        layout.addWidget(self.status)
        layout.addWidget(self.progress)

    def set_running(self, running: bool) -> None:
        self.calculate_button.setEnabled(not running)
        self.optimize_button.setEnabled(not running)
        self.optimize_button.setText("Optimizing…" if running else "Run ML Optimize")
        if running:
            self.progress.setRange(0, 0)
            self.status.setText("Optimization running. UI remains responsive; results will update when complete.")
        else:
            self.progress.setRange(0, 1)
            self.progress.setValue(1)
