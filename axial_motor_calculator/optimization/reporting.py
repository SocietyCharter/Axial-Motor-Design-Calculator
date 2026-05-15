"""Reporting helpers for optimization runs."""

from __future__ import annotations

from axial_motor_calculator.models import MotorResult


SUMMARY_FIELDS = [
    "Total Torque (N-m)",
    "Required Current (A)",
    "Voltage Utilization (V_emf/V_avail)",
    "Mechanical RPM",
    "Electrical Frequency (Hz)",
    "Number of Coil Turns",
    "Torque Constant Kt (N·m/A)",
    "Airgap Shear Stress (N/m^2)",
]


def summarize_candidate(result: MotorResult) -> dict:
    """Return a compact dictionary for tables, export, or CLI output."""
    return {
        "score": result.score,
        "valid": result.valid,
        "violations": list(result.violations),
        "inputs": dict(result.inputs),
        "outputs": {key: result.calculations.get(key, "—") for key in SUMMARY_FIELDS},
    }


def format_candidate(result: MotorResult) -> str:
    """Return a human-readable one-candidate summary."""
    summary = summarize_candidate(result)
    lines = [f"Score: {summary['score']:.3f}" if summary["score"] is not None else "Score: —"]
    lines.append("Violations: " + ("; ".join(summary["violations"]) if summary["violations"] else "PASS"))
    lines.append("Inputs:")
    for key, value in summary["inputs"].items():
        if value is not None:
            lines.append(f"  {key}: {value}")
    lines.append("Key outputs:")
    for key, value in summary["outputs"].items():
        lines.append(f"  {key}: {value}")
    return "\n".join(lines)
