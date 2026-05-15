"""Optimization configuration model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from axial_motor_calculator.models.variable_spec import VariableSpec


@dataclass(frozen=True)
class OptimizationConfig:
    variables: List[VariableSpec] = field(default_factory=list)
    objective: str = "balanced"
    n_trials: int = 100
    seed: Optional[int] = 42
    top_n: int = 10
    objective_weights: Dict[str, float] = field(default_factory=dict)

    def validate(self) -> None:
        if self.n_trials <= 0:
            raise ValueError("n_trials must be positive")
        if self.top_n <= 0:
            raise ValueError("top_n must be positive")
        for variable in self.variables:
            variable.validate()
