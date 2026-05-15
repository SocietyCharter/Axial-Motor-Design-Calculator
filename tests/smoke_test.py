"""Smoke tests for the refactored axial motor calculator package.

Run from repo root:
    python3 tests/smoke_test.py
"""

from __future__ import annotations

import math
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from AxialMotorFixedParam import AxialMotorDesign as LegacyDesign
from axial_motor_calculator.models import MotorInputs, OptimizationConfig, VariableSpec
from axial_motor_calculator.optimization import default_variable_specs, optimize_motor, practical_design_config
from axial_motor_calculator.services.export import export_candidates_csv
from axial_motor_calculator.physics.axial_motor_model import AxialMotorDesign as PackageDesign
from axial_motor_calculator.services.calculation_service import calculate_motor


def parse_float(value: str) -> float:
    return float(str(value).replace(",", ""))


def test_legacy_import_points_to_working_model() -> None:
    assert LegacyDesign.__name__ == PackageDesign.__name__
    motor = LegacyDesign(coils=12, input_voltage=36, outer_radius=0.127, desired_torque=50, mechanical_rpm=750, poles=8)
    results = motor.get_calculations()
    required_keys = [
        "Number of Poles",
        "Required Current (A)",
        "Voltage Utilization (V_emf/V_avail)",
        "Mechanical RPM",
        "Total Torque (N-m)",
    ]
    for key in required_keys:
        assert key in results, key
        assert results[key] != "—", key
    assert math.isfinite(parse_float(results["Required Current (A)"]))


def test_calculation_service() -> None:
    result = calculate_motor(MotorInputs())
    assert result.valid, result.error
    assert result.numeric("Mechanical RPM") == 750.0
    assert math.isfinite(result.numeric("Torque Constant Kt (N·m/A)"))


def test_practical_preset_smoke() -> None:
    run = optimize_motor(practical_design_config(n_trials=8, seed=11))
    assert run.best is not None
    assert run.best.valid, run.best.error
    assert run.best.score is not None


def test_export_smoke() -> None:
    run = optimize_motor(practical_design_config(n_trials=5, seed=13))
    with tempfile.NamedTemporaryFile(suffix=".csv") as handle:
        export_candidates_csv(handle.name, run.candidates)
        text = pathlib.Path(handle.name).read_text()
    assert "rank,score,valid" in text
    assert "input:outer_radius" in text


def test_optimizer_smoke() -> None:
    specs = default_variable_specs()
    selected = []
    for spec in specs:
        if spec.name == "outer_radius":
            selected.append(VariableSpec(spec.name, spec.kind, spec.default, True, 0.08, 0.20))
        elif spec.name == "magnetic_flux_density":
            selected.append(VariableSpec(spec.name, spec.kind, spec.default, True, 0.4, 0.9))
        elif spec.name == "turns":
            selected.append(VariableSpec(spec.name, spec.kind, 20, True, 5, 80))
        elif spec.name == "phase_current_limit":
            selected.append(VariableSpec(spec.name, spec.kind, 250.0, False, spec.low, spec.high))
        else:
            selected.append(spec)
    run = optimize_motor(OptimizationConfig(variables=selected, n_trials=8, top_n=3, seed=7))
    assert run.best is not None
    assert len(run.candidates) >= 1
    assert run.best.score is not None
    assert run.best.valid, run.best.error


if __name__ == "__main__":
    test_legacy_import_points_to_working_model()
    test_calculation_service()
    test_practical_preset_smoke()
    test_export_smoke()
    test_optimizer_smoke()
    print("smoke tests passed")
