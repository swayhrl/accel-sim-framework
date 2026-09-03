# CODEX_NEXT_STAGE

## Status

**PLANNING HOLD — M5 MATRIX DRAFTED; DO NOT EXECUTE FORMAL M5 YET**

M1-M4 are closed PASS and frozen as validated infrastructure.

M5 planning branches:

- Core: `swayhrl/gpgpu-sim:hrl/decoupled-l1-m5-v0`
- Framework: `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m5-v0`

The M5 experiment design is in:

1. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`
2. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
3. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
4. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`

Current user decisions frozen in the draft:

- mechanism/trend reproduction, not target-speedup fitting;
- recover all ten thesis compute workloads before compute formal closeout;
- graphics preparation proceeds in parallel and is nonblocking for compute;
- audit `gemv/gemver`, `gesu/gesummv`, `conv2d/2DConvolution` mappings;
- include thesis Figure 4.2;
- Figure 4.7 uses the common live-miss lifecycle from lower-request commit through final response, cycle-averaged;
- ordinary problems are resolve-in-goal tasks, not automatic STOPs.

Do not start workload recovery, simulator modifications, or formal runs from this file while status is PLANNING HOLD.

After user approval, this file will be replaced with an ACTIVE M5 execution contract. The intended continuous progression is:

`M5.0 Fidelity Lock -> M5.1 Fig4.2 -> M5.2 Fig4.5+4.7 -> M5.3 Fig4.8 -> M5.4 Fig4.9 -> M5.5 Fig4.10 -> M5.6 Causal -> M5_COMPUTE_READY_FOR_REVIEW`.

Graphics G0-G2 preparation may be authorized at the same time as a nonblocking side track.

The future Goal must use `M5_PROBLEM_RESOLUTION_POLICY.md`: missing workloads, build errors, assertions, counter gaps, timeouts-with-progress, poor speedup, workload mismatch, and unexpected resource bottlenecks are normally diagnosed and resolved inside the current stage rather than causing a STOP.

Pause only at a true researcher-decision boundary that cannot be resolved from thesis/source/canonical-workload evidence, or at final compute review.