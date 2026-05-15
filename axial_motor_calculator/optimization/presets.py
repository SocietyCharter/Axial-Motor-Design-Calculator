"""Optimization presets for common motor-design goals."""

from __future__ import annotations

from axial_motor_calculator.models import OptimizationConfig, VariableSpec
from axial_motor_calculator.optimization.search_space import default_variable_specs


PRACTICAL_DEFAULT_VARIABLES = {
    "turns": (5, 120),
    "input_voltage": (24.0, 120.0),
    "outer_radius": (0.08, 0.24),
    "magnetic_flux_density": (0.35, 1.05),
    "poles": (4, 24),
    "winding_factor": (0.75, 0.98),
    "modulation_index": (0.75, 1.0),
}


def practical_design_config(
    n_trials: int = 100,
    seed: int | None = 42,
    variable_ranges: dict[str, tuple[float, float]] | None = None,
) -> OptimizationConfig:
    """Return a practical default optimization setup.

    Goal: meet target torque/RPM under electrical limits, then reduce current,
    stress, and size. This intentionally avoids neural networks; Optuna/TPE is
    used as a lightweight model-based optimizer around deterministic physics.

    Pass ``variable_ranges`` to override any default optimized bounds, e.g.:
    ``{"outer_radius": (0.05, 0.35), "input_voltage": (24.0, 144.0)}``.
    """
    ranges = dict(PRACTICAL_DEFAULT_VARIABLES)
    if variable_ranges:
        ranges.update(variable_ranges)

    specs: list[VariableSpec] = []
    for spec in default_variable_specs():
        if spec.name in ranges:
            low, high = ranges[spec.name]
            specs.append(
                VariableSpec(
                    name=spec.name,
                    kind=spec.kind,
                    default=spec.default if spec.default is not None else int((low + high) / 2),
                    optimize=True,
                    low=low,
                    high=high,
                    step=spec.step,
                    log=spec.log,
                )
            )
        elif spec.name == "phase_current_limit":
            specs.append(VariableSpec(spec.name, spec.kind, 250.0, False, spec.low, spec.high))
        else:
            specs.append(spec)
    return OptimizationConfig(variables=specs, objective="balanced", n_trials=n_trials, seed=seed, top_n=15)
