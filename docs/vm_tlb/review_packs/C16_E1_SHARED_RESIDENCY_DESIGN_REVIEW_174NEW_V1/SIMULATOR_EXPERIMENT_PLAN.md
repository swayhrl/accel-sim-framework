# Simulator experiment plan

## Objective

Test replacement-policy efficacy under an oracle qweight-region tag independently of classifier accuracy. No experiment begins in this design-review stage.

## Policies

1. Accepted baseline replacement policy, mechanism disabled.
2. `M0_STATIC_PROTECTED_PARTITION` capacity-stranding control.
3. `ORACLE_ELASTIC_QWEIGHT_RESIDENCY_V1` (M1).

All new behavior is opt-in. The baseline must first pass exact transparency checks.

## Quota sweep

Test requested budgets corresponding to 8, 16, 24, 32 MiB and 33,947,648 B. Convert each to an exact global line count using the configured cache-line size and distribute by quotient/remainder over L2 instances. These are tested points, not exact thresholds or inferred CUDA alignment.

## Workloads and controls

- Isolated M1 AWQ q_proj, up_proj, and down_proj controls.
- Single-target L0 up control.
- Shared L0 up + L14 up, L0 up + L0 down, and all-three target sets.
- A natural reuse sequence covering at least two consecutive stable decode iterations, with all intervening model traffic present.
- Ordinary/non-target capacity pressure and static-partition stranding controls.

## Required trace/sidecar identity

- instruction/kernel sequence sufficient for the natural inter-token reuse interval;
- every data request address needed by the L2 model;
- exact qweight allocation intervals and target class in a SHA-pinned sidecar, expressed in the same address namespace as the current L2 `mem_fetch::get_addr()` value;
- kernel/launch boundaries and stable occurrence mapping;
- PC only if a later static-PC identity experiment is authorized;
- no dynamic classifier in the first experiment.

## Measurements

- total and per-target simulated cycles;
- L2 accesses/hits/misses and protected-line hit rate;
- protected occupancy/quota-full time series or bounded summaries;
- protected and ordinary victim classes;
- downstream DRAM requests/bytes;
- target and whole-decode effects where trace boundaries support them;
- all existing translation/cache scientific counters and quiescence/conservation checks.

## Validation sequence

1. Compile and directed metadata/quota/victim tests.
2. Mechanism-disabled transparency against the accepted baseline.
3. Small oracle-tagged isolated points.
4. Static-partition control versus elastic quota.
5. Quota sweep.
6. Natural shared-target trace only after identity and conservation gates pass.

## Claim boundary

The experiment may support a bounded residency/replacement contribution under the tested oracle-tagged workloads. It cannot establish an autonomous detector, NVIDIA cache organization, target-specific traffic causality, universal capacity threshold, or model-wide speedup beyond the simulated trace.
