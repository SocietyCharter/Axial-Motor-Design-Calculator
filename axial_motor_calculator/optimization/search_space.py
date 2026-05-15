"""Search-space helpers for Optuna-backed optimization."""

from __future__ import annotations

from typing import Any, Dict, Iterable

from axial_motor_calculator.models import MotorInputs, VariableSpec


def default_variable_specs() -> list[VariableSpec]:
    """Return sensible default specs preserving current calculator defaults."""
    defaults = MotorInputs()
    return [
        VariableSpec("coils", "int", defaults.coils, optimize=False, low=6, high=72, step=3),
        VariableSpec("turns", "int", defaults.turns, optimize=False, low=1, high=200),
        VariableSpec("input_voltage", "float", defaults.input_voltage, optimize=False, low=12.0, high=144.0),
        VariableSpec("outer_radius", "float", defaults.outer_radius, optimize=False, low=0.03, high=0.5),
        VariableSpec("desired_torque", "float", defaults.desired_torque, optimize=False, low=1.0, high=500.0),
        VariableSpec("esc_frequency", "float", defaults.esc_frequency, optimize=False, low=5.0, high=1000.0),
        VariableSpec("mechanical_rpm", "float", defaults.mechanical_rpm, optimize=False, low=50.0, high=12000.0),
        VariableSpec("poles", "int", defaults.poles, optimize=False, low=4, high=64, step=2),
        VariableSpec("winding_factor", "float", defaults.winding_factor, optimize=False, low=0.65, high=0.98),
        VariableSpec("magnetic_flux_density", "float", defaults.magnetic_flux_density, optimize=False, low=0.2, high=1.4),
        VariableSpec("modulation_index", "float", defaults.modulation_index, optimize=False, low=0.5, high=1.0),
        VariableSpec("input_is_vdc", "bool", defaults.input_is_vdc, optimize=False),
        VariableSpec("dual_plate", "bool", defaults.dual_plate, optimize=False),
        VariableSpec("phase_current_limit", "float", defaults.phase_current_limit, optimize=False, low=10.0, high=600.0),
        VariableSpec("dc_current_limit", "float", defaults.dc_current_limit, optimize=False, low=5.0, high=400.0),
        VariableSpec("esc_freq_max", "float", defaults.esc_freq_max, optimize=False, low=50.0, high=2000.0),
    ]


def specs_to_base_inputs(specs: Iterable[VariableSpec]) -> Dict[str, Any]:
    return {spec.name: spec.default for spec in specs}


def apply_motor_discrete_rules(values: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize sampled values to motor-valid discrete forms."""
    out = dict(values)
    if "coils" in out and out["coils"] is not None:
        coils = max(3, int(round(float(out["coils"]))))
        remainder = coils % 3
        if remainder:
            coils += 3 - remainder
        out["coils"] = coils
    if "poles" in out and out["poles"] is not None:
        poles = max(4, int(round(float(out["poles"]))))
        if poles % 2:
            poles += 1
        out["poles"] = poles
    if "turns" in out and out["turns"] is not None:
        out["turns"] = max(1, int(round(float(out["turns"]))))

    # Current physics constructor requires exactly one speed source. Prefer mechanical RPM when set.
    if out.get("mechanical_rpm") not in (None, ""):
        out["esc_frequency"] = None
    elif out.get("esc_frequency") in (None, ""):
        out["mechanical_rpm"] = 750.0
    return out
