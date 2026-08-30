# EP-L2 Codex Target Goal — Lane E Line-MSHR Causality

## One-line goal

> Starting from the exact frozen Lane-B D512 candidate, safely generalize Line-MSHR telemetry to capacities above 128 if necessary, prove MSHR128 backward equivalence, run a minimal convolution Descriptor×MSHR 2x2 causal matrix plus one short spmv negative control, and determine whether the Line-MSHR-full pressure exposed by D512 is performance-causal or merely the next downstream admission symptom; publish review-ready evidence and STOP before any primary-baseline or RO/TVD/Unified implementation decision.

## Start location / read order

Start from the coordination worktree:

```text
/workspace/worktrees/accel-sim-ep-l2/
branch hrl/ep-l2-exp-v0
```

Fetch/pull latest, then read in order:

```text
docs/ep_l2/chatgpt_handoff/CURRENT_STATE.md
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
docs/ep_l2/chatgpt_handoff/PARALLEL_MASTER_PLAN.md
docs/ep_l2/chatgpt_handoff/SPECULATIVE_PARALLEL_EXECUTION_POLICY.md
docs/ep_l2/chatgpt_handoff/PARALLEL_NEW_WINDOW_BOOTSTRAP.md
docs/ep_l2/chatgpt_handoff/LANE_B_INTERIM_22OF26_CHATGPT_REVIEW.md
docs/ep_l2/chatgpt_handoff/LANE_E_LINE_MSHR_CAUSALITY_HANDOFF.md
docs/ep_l2/chatgpt_handoff/LANE_E_LINE_MSHR_CAUSALITY_ACCEPTANCE_CRITERIA.md
docs/ep_l2/chatgpt_handoff/LANE_E_WORKBOARD_ROWS.md
```

Treat the acceptance-criteria file as the mandatory self-gating contract. Before implementation, install the Lane-E rows from `LANE_E_WORKBOARD_ROWS.md` into the latest shared workboard if they are not already present, preserving all other lanes' fields.

## Frozen parents

Formal D256 semantic base:

```text
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
```

Frozen Lane-B D512 candidate:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
D512 config composite
          a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416
```

Use the Lane-B candidate as the Lane-E source parent. Do not recreate Descriptor-512 independently.

## Worktree isolation

Create new isolated Lane-E worktrees, preferably:

```text
Framework /workspace/worktrees/accel-sim-ep-l2-mshr-causality
Core      /workspace/worktrees/gpgpu-sim-ep-l2-mshr-causality
```

on lane-specific branches:

```text
hrl/ep-l2-mshr-causality-v0
```

Use result root:

```text
/workspace/results/ep_l2_line_mshr_causality/
```

All existing Lane A/B/C/D worktrees and result roots are read-only to Lane E.

## Execute autonomously

1. Audit Line-MSHR=256 allocator/config/telemetry support.
2. If needed, generalize observation-only `line_hist`/p95/delta state so >128 occupancy is represented exactly.
3. Add directed 127/128/129 and 255/256 boundary tests.
4. If source changes, prove exact MSHR128 equivalence to Lane B on D512 `vectorAdd_4M` and `convolutionSeparable`.
5. Launch the two new convolution B0-Banked rows:

```text
D256 + MSHR256
D512 + MSHR256
```

using existing D256/MSHR128 and D512/MSHR128 evidence as the other two cells of the 2x2 matrix.
6. Launch short negative control:

```text
D512 + spmv + MSHR256
```

7. Produce the causal interpretation required by the acceptance criteria.

Do not wait for Lane B's remaining D512 scan/3mm rows to launch the D512/MSHR256 work. Mark D512 descendants:

```text
SPECULATIVE_PENDING_GATE
promotion_dependency = D512_PREFLIGHT_PASS
```

If Lane B promotes the exact candidate, promote exact matching Lane-E descendants without rerun. If Lane B supersedes the candidate due a real source/config/producer/timing defect, invalidate and rerun only affected D512 descendants.

## Self-repair boundary

Allowed autonomous repairs:

```text
Line-MSHR capacity parameterization audit
observation-only line occupancy telemetry generalization
MSHR256 config overlays
runner/provenance/maturity plumbing
directed tests
Lane-E parser/analyzer/report tooling
```

Not allowed:

```text
MSHR lifetime/merge semantic redesign
Descriptor definition changes
per-address-cap changes
L1/WAD/payload/bank/lower/DRAM changes
trace/workload changes
another lane's runtime modification
RO/TVD/Unified implementation
```

## Required result

Continue until:

```text
LINE_MSHR_CAUSALITY_PROBE_COMPLETE
```

is supported by the acceptance criteria.

Publish:

```text
docs/ep_l2/codex_handoff/LANE_E_LATEST.md
docs/ep_l2/review_packs/LINE_MSHR_CAUSALITY_r1/
docs/ep_l2/coordination/PARALLEL_WORKBOARD.md
```

Then STOP and request ChatGPT review.
