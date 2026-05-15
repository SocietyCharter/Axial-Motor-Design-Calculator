"""Backward-compatible import path for the axial motor physics model.

The implementation now lives in axial_motor_calculator.physics.axial_motor_model.
Existing code can continue using:

    from AxialMotorFixedParam import AxialMotorDesign
"""

from axial_motor_calculator.physics.axial_motor_model import AxialMotorDesign, MU0

__all__ = ["AxialMotorDesign", "MU0"]
