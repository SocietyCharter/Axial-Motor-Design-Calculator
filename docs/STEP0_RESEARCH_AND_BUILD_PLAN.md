# Step 0 Research and Build Plan — Axial Motor Calculator ML Refactor

## Working Copy

Authoritative project path:

`/mnt/shared_projects/Telemanus/Axial-Motor-Design-Calculator`

The local clone under `/home/jbclaw/projects` is not the working target.

## Current Project Structure

Current repo is compact but monolithic:

- `AxialMotorFixedParam.py` — deterministic axial motor physics calculator.
- `AxialMotorFiixedParamGUI.py` — PyQt5 GUI, input parsing, calculation wiring, result display, and visualization in one file.
- `KVCalc.py` — auxiliary PyQt calculator.
- `README.md` — current usage and project vision.

Current line count snapshot:

- `AxialMotorFixedParam.py`: 327 lines
- `AxialMotorFiixedParamGUI.py`: 262 lines
- `KVCalc.py`: 54 lines
- `README.md`: 129 lines

Current available dependencies verified in the active Python environment:

- `PyQt5`: available
- `numpy`: available, 2.4.4
- `scipy`: available, 1.17.1
- `sklearn`: available, 1.8.0
- `optuna`: available, 4.8.0
- `matplotlib`: available, 3.10.8

Not currently available and should not be assumed without adding dependency management:

- `scikit-optimize`
- `nevergrad`
- `pymoo`
- `deap`
- `pandas`

## Current Physics Preservation Requirements

The existing calculator already supports useful first-order axial motor design behavior. The refactor must preserve all current options before adding optimization.

Inputs to preserve:

- number of coils
- input voltage
- outer radius
- desired torque
- ESC/electrical frequency
- fixed or auto-selected turns
- magnetic flux density
- explicit poles or legacy pole heuristic
- winding factor
- mechanical RPM
- modulation index
- DC bus vs line RMS input mode
- dual plate torque multiplier
- phase current limit
- DC current limit
- ESC frequency max

Outputs to preserve:

- number of poles
- number of magnets
- inner radius
- outer radius
- rotor area
- airgap shear stress
- RPM/frequency values
- peak flux density
- number of coil turns
- total torque
- required current
- flux per pole
- torque constant
- voltage utilization
- max RPM at voltage limit
- mechanical power
- estimated DC current
- shear stress heuristic limit
- pass/fail summaries

Core design rule: the physics model remains deterministic. ML/optimization chooses candidate inputs; physics evaluates them.

## External Research Findings

Comparable open-source references found during quick repository research:

1. `Eomys/pyleecan`
   - Large open-source electric machine simulation framework.
   - Useful as an architecture reference for separating machine definition, simulation, and results.
   - Too heavy to adopt directly for this calculator right now.

2. `occupycars/BORGI-WheelHubMotor`
   - Open axial-flux wheel hub motor project.
   - Useful real-world reference for axial motor constraints and open hardware positioning.

3. `pwspen/autocoil`
   - Python axial-flux BLDC/PCB stator generator.
   - Useful geometry/process reference, especially for future stator layout generation.

4. `wgbowley/OpenLSM`
   - Python design/optimization project for linear synchronous motors.
   - Useful precedent for Python-based motor optimization structure.

5. PMSM/SynRM optimization repos
   - Most available examples are MATLAB-heavy or academic single-objective studies.
   - Useful conceptually, but not a direct fit for this PyQt/Python calculator.

Conclusion: keep this project lightweight and practical. Do not try to become Pyleecan. Use a deterministic physics core plus Optuna optimization around it.

## Recommended ML Optimization Approach

Use `Optuna` as the first optimization engine.

Reasons:

- Already installed.
- Supports mixed variable types: float, int, categorical, boolean.
- TPE sampler is ML-guided/sequential model-based optimization.
- Handles constrained search spaces better than a simple grid search.
- Gives study history, best trials, ranked candidates, and parameter importances.
- Avoids adding fragile dependency setup before the refactor has value.

Initial optimizer structure:

1. User marks variables as fixed or optimizable.
2. Optimizable variables receive min/max bounds or categorical choices.
3. Optuna proposes candidate motor inputs.
4. Physics model evaluates the candidate.
5. Constraint system applies hard failures or penalties.
6. Scoring function returns one scalar objective value.
7. Optimizer stores all trials and returns ranked candidates.

Later enhancement:

- Add sklearn surrogate/sensitivity model for explainability after Optuna has generated trial data.
- Possible features: parameter importance, predicted tradeoff curves, design-space heatmaps.

## Clean Program Structure

Recommended contained MVC/service structure:

```text
axial_motor_calculator/
  __init__.py
  main.py

  models/
    __init__.py
    motor_inputs.py
    motor_result.py
    optimization_config.py
    variable_spec.py

  physics/
    __init__.py
    axial_motor_model.py
    constraints.py
    scoring.py

  optimization/
    __init__.py
    optimizer.py
    optuna_optimizer.py
    search_space.py

  ui/
    __init__.py
    main_window.py
    theme.py
    input_panel.py
    optimization_panel.py
    results_panel.py
    visualization_widget.py

  services/
    __init__.py
    validation.py
    export.py
```

Legacy compatibility during migration:

- Keep `AxialMotorFixedParam.py` initially as a wrapper/import compatibility layer.
- Keep `AxialMotorFiixedParamGUI.py` initially as a launcher shim or legacy fallback.
- Move real implementation into package modules.
- Prove parity before deleting or renaming legacy files.

## Variable Model

Each calculator input should become a variable spec with:

- name
- label
- type
- default value
- fixed value
- optimize enabled flag
- min bound
- max bound
- allowed choices if categorical
- validation function
- transform/rounding function if needed

Recommended variable types:

### Continuous

- input voltage
- outer radius
- desired torque
- magnetic flux density
- winding factor
- mechanical RPM
- ESC frequency
- modulation index
- phase current limit
- DC current limit
- ESC frequency max

### Integer

- number of turns
- number of coils
- poles

### Boolean / categorical

- voltage is DC bus
- dual plate
- auto turns vs fixed turns
- speed input mode: mechanical RPM vs electrical frequency

Special constraints:

- coils must be divisible by 3.
- poles must be even and >= 4.
- one speed source must be active: RPM or electrical Hz.
- turns may be auto or fixed, but not ambiguous.
- voltage utilization should be <= 1.0 for pass.
- current and ESC limits only apply when provided.

## Constraint System

Invalid candidates should not crash. They should produce a failed result with a large penalty.

Hard invalid examples:

- negative radius
- zero or negative voltage
- invalid pole count
- coils not divisible by 3
- NaN or infinite physics output
- no valid speed input

Soft penalty examples:

- voltage utilization above 1.0
- required current above phase limit
- estimated DC current above DC limit
- ESC frequency above max
- shear stress above heuristic limit
- excessive size or current for selected objective

## Objective and Scoring Model

Initial objective modes:

1. Balanced design score
2. Max torque within limits
3. Min required current for target torque
4. Max RPM within voltage limit
5. Min outer radius for required torque
6. Min voltage/current stress

Recommended default: balanced design score.

Balanced score should reward:

- meeting target torque
- low required phase current
- voltage utilization close to but below 1.0
- passing current/DC/frequency limits
- lower shear stress ratio
- smaller radius where possible
- no invalid physics outputs

The scoring layer should be independent from the physics layer so objectives can be changed without touching equations.

## UI Plan

Use PyQt5 for continuity.

Main screen layout:

1. Input panel
   - current value
   - optimize checkbox
   - min bound
   - max bound

2. Optimization panel
   - objective selector
   - trial count
   - random seed
   - run/cancel controls
   - progress bar/status

3. Results panel
   - best design summary
   - top candidates table
   - pass/fail indicators
   - selected candidate detail view

4. Visualization panel
   - preserve current axial sketch
   - update colors and drawing style
   - later: visualize coils/poles/magnets more accurately

Theme:

- background black: `#05070D`
- panel blue: `#071A33`
- accent blue: `#0B2D5C`
- gold: `#D6A84F`
- muted gold: `#A8843A`
- text: `#E8E6DD`
- success: `#3FA66B`
- warning/error: `#C44`

Fonts:

- prefer `Segoe UI`, `Inter`, `Arial`, sans-serif fallback.

## Build Phases

### Phase 1 — Package scaffold and compatibility wrappers

- Create `axial_motor_calculator/` package.
- Move/refactor physics into pure model module.
- Keep old launcher/API compatibility.
- Add minimal import/compile checks.

Acceptance:

- existing GUI still launches or wrapper path remains intact.
- physics class can be imported from new package.

### Phase 2 — Dataclasses and parity tests

- Add `MotorInputs`, `MotorResult`, `OptimizationConfig`, and `VariableSpec`.
- Add tests comparing current known cases against refactored physics.

Acceptance:

- old and new calculations match within tolerance for selected fixtures.

### Phase 3 — Constraints and scoring

- Add constraint evaluator.
- Add objective scoring modes.
- Add invalid-candidate handling.

Acceptance:

- bad candidates fail gracefully.
- valid candidates produce score and result.

### Phase 4 — Optuna optimizer

- Add search-space builder.
- Add Optuna-backed optimizer.
- Return ranked candidate results.
- Add CLI or small smoke runner for non-UI testing.

Acceptance:

- optimizer runs with at least 3 selected variables.
- returns top N candidates.
- no crash on invalid sampled candidates.

### Phase 5 — UI refactor

- Split GUI into panels.
- Add optimize checkbox/bounds controls.
- Add objective/trial controls.
- Add results table.

Acceptance:

- manual calculate still works.
- optimizer can be launched from UI.

### Phase 6 — Society theme and UX polish

- Apply deep blue/gold/black theme.
- Improve labels, spacing, pass/fail badges.
- Improve visualization styling.

Acceptance:

- UI is visibly modernized.
- all existing options remain reachable.

### Phase 7 — Documentation and cleanup

- Update README.
- Add dependency notes.
- Add examples.
- Remove or deprecate duplicate legacy paths only after parity.

Acceptance:

- clean run instructions.
- clear optimization usage guide.

## Build Risk Notes

- The implementation is too large for one monolithic code-generation pass.
- It should be split into small, reviewable build tasks.
- Optuna makes the ML requirement practical without dependency churn.
- The current typo in `AxialMotorFiixedParamGUI.py` should be handled carefully to avoid breaking existing users/scripts.
- UI threading must stay safe if optimization runs in background; PyQt widgets should only be updated on the main thread.

## Open Questions for Jesse

1. Should optimization target be mostly builder/practical output, or should we expose advanced tuning weights immediately?
2. Should we optimize for real-world manufacturability constraints now, or defer until the physics engine is stable?
3. Is adding a formal `requirements.txt` acceptable in this repo?
4. Should the legacy filename typo stay as a compatibility shim long-term?

## Recommended Immediate Next Step

Start Phase 1 with a narrow scaffold/refactor task:

- create the package structure,
- extract the existing physics class into the package,
- leave legacy files as wrappers,
- add a tiny smoke test/import check.

Do not start with the UI rewrite. Protect physics parity first.
