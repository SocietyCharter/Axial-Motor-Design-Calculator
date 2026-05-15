"""Package CLI entry point."""

from axial_motor_calculator.models import MotorInputs
from axial_motor_calculator.services.calculation_service import calculate_motor


def main() -> None:
    result = calculate_motor(MotorInputs())
    if not result.valid:
        raise SystemExit(result.error or "Calculation failed")
    for key, value in result.calculations.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
