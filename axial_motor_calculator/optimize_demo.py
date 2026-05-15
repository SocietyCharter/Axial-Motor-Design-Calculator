"""Command-line optimization smoke/demo runner."""

from __future__ import annotations

import argparse

from axial_motor_calculator.optimization import optimize_motor, practical_design_config
from axial_motor_calculator.optimization.reporting import format_candidate


def main() -> None:
    parser = argparse.ArgumentParser(description="Run practical Optuna/TPE motor optimization.")
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--radius-min", type=float, default=0.08, help="Minimum outer radius in meters")
    parser.add_argument("--radius-max", type=float, default=0.24, help="Maximum outer radius in meters")
    parser.add_argument("--voltage-min", type=float, default=24.0, help="Minimum input voltage")
    parser.add_argument("--voltage-max", type=float, default=120.0, help="Maximum input voltage")
    args = parser.parse_args()

    run = optimize_motor(
        practical_design_config(
            n_trials=args.trials,
            seed=args.seed,
            variable_ranges={
                "outer_radius": (args.radius_min, args.radius_max),
                "input_voltage": (args.voltage_min, args.voltage_max),
            },
        )
    )
    if run.best is None:
        raise SystemExit("No candidate produced")
    print(format_candidate(run.best))


if __name__ == "__main__":
    main()
