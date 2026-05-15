"""Stable calculation service wrapping the deterministic physics model."""

from __future__ import annotations

from typing import Mapping, Union

from axial_motor_calculator.models import MotorInputs, MotorResult
from axial_motor_calculator.physics import AxialMotorDesign


def calculate_motor(inputs: Union[MotorInputs, Mapping]) -> MotorResult:
    """Run the physics model and return a structured result instead of raising."""
    if isinstance(inputs, MotorInputs):
        kwargs = inputs.to_kwargs()
    else:
        kwargs = dict(inputs)

    try:
        motor = AxialMotorDesign(**kwargs)
        return MotorResult(calculations=motor.get_calculations(), valid=True, inputs=kwargs)
    except Exception as exc:
        return MotorResult(valid=False, inputs=kwargs, error=str(exc), violations=[str(exc)])
