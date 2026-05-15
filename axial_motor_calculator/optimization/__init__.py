"""Optimization package."""

from axial_motor_calculator.optimization.optimizer import OptimizationRunResult, default_variable_specs, optimize_motor
from axial_motor_calculator.optimization.presets import practical_design_config

__all__ = ["OptimizationRunResult", "default_variable_specs", "optimize_motor", "practical_design_config"]
