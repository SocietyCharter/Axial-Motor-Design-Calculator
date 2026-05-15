"""Structured input model for axial motor calculations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass(frozen=True)
class MotorInputs:
    coils: int = 12
    input_voltage: float = 36.0
    outer_radius: float = 0.127
    desired_torque: float = 50.0
    esc_frequency: Optional[float] = None
    turns: Optional[float] = None
    magnetic_flux_density: float = 0.6
    poles: Optional[int] = 8
    winding_factor: float = 0.92
    mechanical_rpm: Optional[float] = 750.0
    modulation_index: float = 0.95
    input_is_vdc: bool = False
    dual_plate: bool = False
    phase_current_limit: Optional[float] = None
    dc_current_limit: Optional[float] = None
    esc_freq_max: Optional[float] = None

    def to_kwargs(self) -> dict:
        """Return kwargs accepted by AxialMotorDesign."""
        return asdict(self)
