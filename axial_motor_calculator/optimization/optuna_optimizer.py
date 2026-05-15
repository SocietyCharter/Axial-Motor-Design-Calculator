"""Optuna-backed machine-learning optimization for motor design."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import optuna

from axial_motor_calculator.models import MotorResult, OptimizationConfig, VariableSpec
from axial_motor_calculator.optimization.search_space import apply_motor_discrete_rules, specs_to_base_inputs
from axial_motor_calculator.physics.constraints import evaluate_constraints
from axial_motor_calculator.physics.scoring import score_result
from axial_motor_calculator.services.calculation_service import calculate_motor


@dataclass
class OptimizationRunResult:
    best: MotorResult | None
    candidates: List[MotorResult]
    study: optuna.Study


def _suggest(trial: optuna.Trial, spec: VariableSpec) -> Any:
    if not spec.optimize:
        return spec.default
    if spec.kind == "float":
        return trial.suggest_float(spec.name, float(spec.low), float(spec.high), step=spec.step, log=spec.log)
    if spec.kind == "int":
        step = int(spec.step or 1)
        return trial.suggest_int(spec.name, int(spec.low), int(spec.high), step=step, log=spec.log)
    if spec.kind == "bool":
        return trial.suggest_categorical(spec.name, [False, True])
    if spec.kind == "categorical":
        return trial.suggest_categorical(spec.name, list(spec.choices or []))
    raise ValueError(f"Unsupported variable kind: {spec.kind}")


def optimize_motor(config: OptimizationConfig) -> OptimizationRunResult:
    """Run ML-guided optimization and return ranked motor candidates."""
    config.validate()
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    sampler = optuna.samplers.TPESampler(seed=config.seed)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    candidates: List[MotorResult] = []
    base = specs_to_base_inputs(config.variables)

    def objective(trial: optuna.Trial) -> float:
        values: Dict[str, Any] = dict(base)
        for spec in config.variables:
            values[spec.name] = _suggest(trial, spec)
        values = apply_motor_discrete_rules(values)
        result = calculate_motor(values)
        violations, penalties = evaluate_constraints(result)
        result.violations = violations
        result.penalties = penalties
        result.score = score_result(result, config.objective, config.objective_weights)
        candidates.append(result)
        return float(result.score)

    study.optimize(objective, n_trials=config.n_trials, show_progress_bar=False)
    ranked = sorted(candidates, key=lambda item: item.score if item.score is not None else -1e18, reverse=True)
    return OptimizationRunResult(best=ranked[0] if ranked else None, candidates=ranked[: config.top_n], study=study)
