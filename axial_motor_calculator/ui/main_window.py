"""Modern PyQt main window for the axial motor calculator."""

from __future__ import annotations

import traceback

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QSplitter, QVBoxLayout, QWidget

from axial_motor_calculator.models import OptimizationConfig
from axial_motor_calculator.optimization import optimize_motor
from axial_motor_calculator.services.calculation_service import calculate_motor
from axial_motor_calculator.services.export import export_candidates_csv
from axial_motor_calculator.ui.input_panel import InputPanel
from axial_motor_calculator.ui.optimization_panel import OptimizationPanel
from axial_motor_calculator.ui.results_panel import ResultsPanel
from axial_motor_calculator.ui.theme import SOCIETY_QSS
from axial_motor_calculator.ui.visualization_widget import VisualizationWidget


class OptimizerWorker(QThread):
    finished_ok = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, config: OptimizationConfig):
        super().__init__()
        self.config = config

    def run(self):
        try:
            self.finished_ok.emit(optimize_motor(self.config))
        except Exception:
            self.failed.emit(traceback.format_exc())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.last_optimization = None
        self.setWindowTitle("Axial Flux Motor Calculator — ML Optimizer")
        self.resize(1350, 850)
        QApplication.instance().setStyleSheet(SOCIETY_QSS)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        title = QLabel("Axial Flux Motor Calculator")
        title.setObjectName("TitleLabel")
        root_layout.addWidget(title)

        self.input_panel = InputPanel()
        self.optimization_panel = OptimizationPanel()
        self.results_panel = ResultsPanel()
        self.visualization = VisualizationWidget(lambda: self.input_panel.value_widgets["coils"].text())

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(self.input_panel)
        left_layout.addWidget(self.optimization_panel)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(self.visualization)
        right_layout.addWidget(self.results_panel, 1)

        splitter = QSplitter()
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([560, 790])
        root_layout.addWidget(splitter, 1)
        self.setCentralWidget(root)

        self.optimization_panel.calculate_button.clicked.connect(self.calculate)
        self.optimization_panel.optimize_button.clicked.connect(self.optimize)
        self.optimization_panel.export_button.clicked.connect(self.export_results)
        self.calculate()

    def calculate(self) -> None:
        result = calculate_motor(self.input_panel.current_inputs())
        if result.valid:
            self.results_panel.show_calculations(result.calculations)
            self.optimization_panel.status.setText("Fixed design calculated successfully.")
        else:
            QMessageBox.warning(self, "Calculation failed", result.error or "Unknown error")
        self.visualization.update()

    def optimize(self) -> None:
        config = OptimizationConfig(
            variables=self.input_panel.variable_specs(),
            objective=self.optimization_panel.objective.currentText(),
            n_trials=self.optimization_panel.trials.value(),
            top_n=15,
            seed=42,
        )
        try:
            config.validate()
            if not any(variable.optimize for variable in config.variables):
                raise ValueError("Select at least one variable to optimize.")
        except Exception as exc:
            QMessageBox.warning(self, "Invalid optimization setup", str(exc))
            return
        self.optimization_panel.set_running(True)
        self.optimization_panel.export_button.setEnabled(False)
        self.worker = OptimizerWorker(config)
        self.worker.finished_ok.connect(self._optimization_done)
        self.worker.failed.connect(self._optimization_failed)
        self.worker.start()

    def _optimization_done(self, run_result) -> None:
        self.optimization_panel.set_running(False)
        self.last_optimization = run_result
        self.optimization_panel.export_button.setEnabled(bool(run_result.candidates))
        self.optimization_panel.status.setText(f"Optimization complete: {len(run_result.study.trials)} trials, {len(run_result.candidates)} displayed candidates.")
        self.results_panel.show_candidates(run_result.candidates)

    def _optimization_failed(self, trace: str) -> None:
        self.optimization_panel.set_running(False)
        self.optimization_panel.status.setText("Optimization failed.")
        QMessageBox.critical(self, "Optimization failed", trace)

    def export_results(self) -> None:
        if not self.last_optimization or not self.last_optimization.candidates:
            QMessageBox.information(self, "No results", "Run optimization before exporting.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Optimization Candidates", "optimization_candidates.csv", "CSV Files (*.csv)")
        if not path:
            return
        export_candidates_csv(path, self.last_optimization.candidates)
        self.optimization_panel.status.setText(f"Exported candidates to {path}")
