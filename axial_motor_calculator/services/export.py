"""Export helpers for calculator and optimization results."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from axial_motor_calculator.models import MotorResult


def export_candidates_csv(path: str | Path, candidates: Iterable[MotorResult]) -> None:
    """Export ranked optimization candidates to CSV."""
    path = Path(path)
    rows = []
    input_keys = set()
    output_keys = set()
    for rank, candidate in enumerate(candidates, start=1):
        input_keys.update(candidate.inputs.keys())
        output_keys.update(candidate.calculations.keys())
        rows.append((rank, candidate))

    input_cols = sorted(input_keys)
    output_cols = [
        "Total Torque (N-m)",
        "Required Current (A)",
        "Voltage Utilization (V_emf/V_avail)",
        "Estimated DC Current (A)",
        "Mechanical RPM",
        "Electrical Frequency (Hz)",
        "Number of Coil Turns",
        "Torque Constant Kt (N·m/A)",
        "Airgap Shear Stress (N/m^2)",
    ]
    output_cols.extend(sorted(key for key in output_keys if key not in output_cols))

    fieldnames = ["rank", "score", "valid", "violations"]
    fieldnames.extend(f"input:{key}" for key in input_cols)
    fieldnames.extend(f"output:{key}" for key in output_cols)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for rank, candidate in rows:
            row = {
                "rank": rank,
                "score": candidate.score,
                "valid": candidate.valid,
                "violations": "; ".join(candidate.violations),
            }
            for key in input_cols:
                row[f"input:{key}"] = candidate.inputs.get(key)
            for key in output_cols:
                row[f"output:{key}"] = candidate.calculations.get(key)
            writer.writerow(row)
