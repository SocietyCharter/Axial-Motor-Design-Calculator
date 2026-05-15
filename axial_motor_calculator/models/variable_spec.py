"""Search-space variable definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Sequence


@dataclass(frozen=True)
class VariableSpec:
    name: str
    kind: str  # float, int, bool, categorical
    default: Any
    optimize: bool = False
    low: Optional[float] = None
    high: Optional[float] = None
    choices: Optional[Sequence[Any]] = None
    step: Optional[float] = None
    log: bool = False

    def validate(self) -> None:
        if self.kind not in {"float", "int", "bool", "categorical"}:
            raise ValueError(f"Unsupported variable kind for {self.name}: {self.kind}")
        if self.kind in {"float", "int"} and self.optimize:
            if self.low is None or self.high is None:
                raise ValueError(f"Optimized numeric variable {self.name} requires low/high bounds")
            if self.high < self.low:
                raise ValueError(f"Variable {self.name} has high < low")
        if self.kind == "categorical" and self.optimize and not self.choices:
            raise ValueError(f"Categorical variable {self.name} requires choices")
