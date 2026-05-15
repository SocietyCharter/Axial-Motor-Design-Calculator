"""Structured result model for physics and optimization outputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MotorResult:
    calculations: Dict[str, str] = field(default_factory=dict)
    valid: bool = True
    score: Optional[float] = None
    penalties: Dict[str, float] = field(default_factory=dict)
    violations: List[str] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def numeric(self, key: str, default: float = float("nan")) -> float:
        value = self.calculations.get(key)
        if value in (None, "", "—"):
            return default
        try:
            return float(str(value).replace(",", ""))
        except Exception:
            return default
