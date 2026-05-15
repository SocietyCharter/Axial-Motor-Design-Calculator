# Optimization Guide

This project uses **Optuna TPE** optimization, not a neural network.

That is intentional. A neural network would require a training dataset and would obscure the physics. Here, the physics model remains deterministic and authoritative. Optuna proposes candidate inputs, the physics model evaluates them, and the scoring layer ranks them.

## What is optimized?

The optimizer maximizes a scalar score from `axial_motor_calculator/physics/scoring.py`.

Default objective: `balanced`.

Balanced score rewards:

- achieving the requested torque target
- lower required phase current
- voltage utilization near useful headroom, currently around 0.85
- lower shear-stress ratio
- smaller radius where possible
- passing electrical/mechanical constraints

Penalties apply for:

- voltage utilization over 1.0
- phase-current limit violation
- DC-current limit violation
- ESC frequency limit violation
- shear-stress heuristic violation
- invalid coils/poles/non-finite outputs

## Available objective modes

- `balanced`
- `max_torque`
- `min_current`
- `max_rpm`
- `min_radius`
- `min_stress`

## Optimizable variables

The system can optimize any variable represented by `VariableSpec`, including:

- turns
- coils
- poles
- outer radius
- input voltage
- magnetic flux density
- winding factor
- modulation index
- dual plate
- RPM / electrical frequency
- current and frequency limits

The modern UI defaults to optimizing a practical subset:

- turns
- input voltage
- outer radius
- magnetic flux density
- poles
- winding factor
- modulation index

Every optimized row has editable `Min` and `Max` boxes. The radius range is therefore user-adjustable directly in the UI. If the user is designing around a known package size, set the outer-radius min/max tightly. If the user is exploring architecture, widen the range.

If the user is designing around a known battery/controller, voltage should be fixed. If the user is exploring architecture options, voltage should be optimized or swept.

CLI radius and voltage ranges are also adjustable:

```bash
python3 -m axial_motor_calculator.optimize_demo --trials 100 --radius-min 0.05 --radius-max 0.35 --voltage-min 24 --voltage-max 144
```

Users can enable more variables directly in the UI.

## Command-line demo

```bash
python3 -m axial_motor_calculator.optimize_demo --trials 100
```

## Exporting Results

After running optimization in the UI, use **Export CSV** to save the ranked candidate table. The export includes score, validity, violations, input variables, and key physics outputs.
