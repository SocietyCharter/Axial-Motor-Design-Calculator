"""Data models for the axial motor calculator."""

from axial_motor_calculator.models.motor_inputs import MotorInputs
from axial_motor_calculator.models.motor_result import MotorResult
from axial_motor_calculator.models.optimization_config import OptimizationConfig
from axial_motor_calculator.models.variable_spec import VariableSpec

__all__ = ["MotorInputs", "MotorResult", "OptimizationConfig", "VariableSpec"]
