# Shared-Residency Producer / Consumer Resume Audit V3

## Producer reviewed

Producer:
`hrl/c16-e1-shared-residency-feasibility-109-v1@1e701f013fc174b5b4df9febb5c33500f9ea586e`

Preliminary remote audit supports the reported producer closure:

- stage label: `SHARED_RESIDENCY_LOCAL_ONLY`;
- rotating A->B->A qualification passes against a Normal/Normal matched API-switch control;
- shared fixed-budget conditions retain material local timing benefit for >=2 selected targets;
- stable D1-D3 whole-decode benefit remains <0.5% for the best shared conditions, below the preregistered 2% gate;
- critical-path changes are concentrated in quantized GEMM for up_proj; reduction is nearly unchanged;
- aggregate DRAM is not a reliable standalone critical-path proxy;
- prior producer/strict-consumer divergence remains frozen.

No node109 rerun is requested.

## Important consumer-packaging hardening before raw closure

The original 174-new prep contract was intentionally pre-data, but the real producer uses a richer full-model update harness than the synthetic prep assumed.

### Actual full-model policy schedule

For every non-SETASIDE_ONLY condition, producer performs 15 policy updates:

- PREFILL: L0_UP, L0_DOWN, L14_UP
- D0: L0_UP, L0_DOWN, L14_UP
- D1: L0_UP, L0_DOWN, L14_UP
- D2: L0_UP, L0_DOWN, L14_UP
- D3: L0_UP, L0_DOWN, L14_UP

Selected targets are PERSISTING.
Unselected targets are explicit NORMAL/NORMAL updates.

Examples:

- SINGLE_L0_UP:
  - L0_UP persists with hitRatio=1
  - L0_DOWN and L14_UP receive matched NORMAL/NORMAL updates with the same hitRatio field

- SHARE2_UP:
  - L0_UP and L14_UP persist with hitRatio=0.5
  - L0_DOWN is NORMAL/NORMAL

- SHARE2_L0:
  - L0_UP and L0_DOWN persist with hitRatio=0.5
  - L14_UP is NORMAL/NORMAL

- SHARE3:
  - all three persist with hitRatio=1/3

- ROTATE_CONTROL_3:
  - all 15 updates are NORMAL/NORMAL
  - hitRatio field remains 1/3
  - no target is persisting

Therefore the consumer must validate the exact 15-update schedule, including PREFILL and explicit non-selected NORMAL controls.

### Fixed runtime query-back

For every fixed-full-budget rotating/shared condition:

- requested set-aside = 33,947,648 B
- accepted runtime query-back = 37,748,736 B

A different query-back is fail-closed.

### hitRatio interpretation boundary

CUDA hitRatio is a runtime policy hint.

It must not be interpreted as:
- an exact deterministic fraction of qweight lines or bytes retained;
- an exact simulator quota split.

### Producer raw schema normalization

Real native run files expose:

- `policy_receipt`: condition-level set-aside/reset receipt
- `policy_transitions`: ordered full-model policy updates
- `policy_transition_count`
- `qweight_regions`
- semantic/timing evidence

Rotating qualification exposes:
- `policy_receipt`
- `window_transitions`
- A/B qweight regions

The consumer may deterministically normalize these raw fields into its internal ordered-policy schema.

Normalization must retain raw file SHA and may not invent missing scientific state.

NCU PROFILE application replay can emit multiple PASS receipts when runtime metric collection requires multiple application replay passes. The consumer must require:
- each replay receipt has the same semantic/token/policy identity;
- BASE `profiler__replayer_passes` matches the receipt count;
rather than requiring exactly one PASS receipt for every multi-pass profile.

## Consumer hardening authority

Before raw consumption use:

`hrl/c16-e1-shared-residency-consumer-hardening-v2`

This branch already hardens:
- fixed runtime query-back;
- 15-update full-model schedule;
- selected-vs-normal policy semantics;
- hitRatio interpretation boundary.

Any remaining adapter/parser work for the producer split schema is ordinary consumer packaging and should be solved inside the resumed Goal, not a separate repair round.

## Scientific boundary

The producer result is local-only.

Do not authorize simulator implementation merely because local target modules accelerate.

After independent closure, project review should decide whether to:
1. run a broader fixed-budget fan-out scaling experiment on real hardware; or
2. proceed to bounded trace + oracle mechanism simulation.

The whole-decode result is the deciding evidence.
