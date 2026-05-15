"""Physics-aware design constraints and penalty calculations."""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

from axial_motor_calculator.models import MotorResult


def _ratio_over(value: float, limit: float) -> float:
    if not math.isfinite(value) or limit <= 0:
        return 1_000_000.0
    return max(0.0, (value / limit) - 1.0)


def evaluate_constraints(result: MotorResult) -> Tuple[List[str], Dict[str, float]]:
    """Return constraint violations and scalar penalties for optimization."""
    violations: List[str] = []
    penalties: Dict[str, float] = {}

    if not result.valid:
        return result.violations or [result.error or "invalid result"], {"invalid": 1_000_000.0}

    inputs = result.inputs
    coils = int(round(float(inputs.get("coils", 0))))
    poles = inputs.get("poles")
    if coils <= 0 or coils % 3 != 0:
        violations.append("coils must be positive and divisible by 3")
        penalties["coils"] = 100_000.0
    if poles is not None:
        poles_int = int(round(float(poles)))
        if poles_int < 4 or poles_int % 2 != 0:
            violations.append("poles must be even and >= 4")
            penalties["poles"] = 100_000.0

    voltage_utilization = result.numeric("Voltage Utilization (V_emf/V_avail)")
    if voltage_utilization > 1.0:
        violations.append("voltage utilization exceeds available voltage")
        penalties["voltage"] = 1_000.0 * _ratio_over(voltage_utilization, 1.0)

    required_current = result.numeric("Required Current (A)")
    phase_limit = inputs.get("phase_current_limit")
    if phase_limit not in (None, "") and required_current > float(phase_limit):
        violations.append("required phase current exceeds phase current limit")
        penalties["phase_current"] = 800.0 * _ratio_over(required_current, float(phase_limit))

    dc_current = result.numeric("Estimated DC Current (A)")
    dc_limit = inputs.get("dc_current_limit")
    if dc_limit not in (None, "") and dc_current > float(dc_limit):
        violations.append("estimated DC current exceeds DC current limit")
        penalties["dc_current"] = 800.0 * _ratio_over(dc_current, float(dc_limit))

    esc_freq = result.numeric("Electrical Frequency (Hz)")
    esc_freq_max = inputs.get("esc_freq_max")
    if esc_freq_max not in (None, "") and esc_freq > float(esc_freq_max):
        violations.append("electrical frequency exceeds ESC max")
        penalties["esc_frequency"] = 500.0 * _ratio_over(esc_freq, float(esc_freq_max))

    shear = result.numeric("Airgap Shear Stress (N/m^2)")
    shear_limit = result.numeric("Shear Stress Heuristic Limit (N/m^2)")
    if math.isfinite(shear) and math.isfinite(shear_limit) and shear > shear_limit:
        violations.append("airgap shear stress exceeds heuristic limit")
        penalties["shear"] = 500.0 * _ratio_over(shear, shear_limit)

    for key in ("Required Current (A)", "Total Torque (N-m)", "Voltage Utilization (V_emf/V_avail)"):
        value = result.numeric(key)
        if not math.isfinite(value):
            violations.append(f"{key} is not finite")
            penalties[f"nonfinite:{key}"] = 100_000.0

    return violations, penalties
