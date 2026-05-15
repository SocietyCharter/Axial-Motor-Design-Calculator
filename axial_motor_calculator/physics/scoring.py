"""Objective scoring for motor optimization."""

from __future__ import annotations

import math
from typing import Mapping

from axial_motor_calculator.models import MotorResult


def total_penalty(result: MotorResult) -> float:
    return sum(result.penalties.values()) if result.penalties else 0.0


def score_result(result: MotorResult, objective: str = "balanced", weights: Mapping[str, float] | None = None) -> float:
    """Return a scalar score to maximize."""
    if not result.valid:
        return -1_000_000_000.0

    weights = weights or {}
    penalty = total_penalty(result)
    torque = result.numeric("Total Torque (N-m)", 0.0)
    desired = float(result.inputs.get("desired_torque") or torque or 1.0)
    current = result.numeric("Required Current (A)", 1_000_000.0)
    rpm = result.numeric("Mechanical RPM", 0.0)
    radius = float(result.inputs.get("outer_radius") or 1.0)
    voltage_util = result.numeric("Voltage Utilization (V_emf/V_avail)", 10.0)
    shear = result.numeric("Airgap Shear Stress (N/m^2)", 0.0)
    shear_limit = result.numeric("Shear Stress Heuristic Limit (N/m^2)", max(shear, 1.0))

    if objective == "max_torque":
        return torque - penalty
    if objective == "min_current":
        return -current - penalty
    if objective == "max_rpm":
        return rpm - penalty
    if objective == "min_radius":
        return -radius * 1000.0 - penalty
    if objective == "min_stress":
        return -(shear / max(shear_limit, 1e-9)) * 100.0 - penalty

    torque_score = 100.0 * min(torque / max(desired, 1e-9), 1.0)
    current_score = 100.0 / (1.0 + max(current, 0.0) / 100.0)
    voltage_score = 100.0 - abs(0.85 - min(max(voltage_util, 0.0), 2.0)) * 100.0
    shear_score = 100.0 / (1.0 + max(shear / max(shear_limit, 1e-9), 0.0))
    size_score = 100.0 / (1.0 + max(radius, 0.0) / 0.15)

    score = (
        weights.get("torque", 1.2) * torque_score
        + weights.get("current", 1.0) * current_score
        + weights.get("voltage", 0.8) * voltage_score
        + weights.get("shear", 0.8) * shear_score
        + weights.get("size", 0.5) * size_score
    )
    if not math.isfinite(score):
        return -1_000_000_000.0
    return score - penalty
