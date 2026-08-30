# EP-L2 M0a + M1 Parallel Execution Plan

Status: **AUTHORIZED PARALLEL IMPLEMENTATION PREP**

## Why parallel

M0a modifies observation/parser/reporting around the frontend admission path. M1 modifies payload identity/storage plumbing while preserving behavior. Both derive independently from the same accepted D512 research baseline and neither depends scientifically on the other's output.

Running them in parallel reduces wall-clock time while keeping review boundaries clean.

## Ownership

```text
Window M0a
  hrl/ep-l2-m0a-observability-v0
  /workspace/worktrees/{accel-sim,gpgpu-sim}-ep-l2-m0a
  /workspace/results/ep_l2_m0a

Window M1
  hrl/ep-l2-m1-elastic-substrate-v0
  /workspace/worktrees/{accel-sim,gpgpu-sim}-ep-l2-m1
  /workspace/results/ep_l2_m1_equivalence
```

No shared simulator build directory or result root.

## Source parent

Both start from exact:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
```

Do not start M1 from M0a or M0a from M1.

## Expected overlap

Potential merge overlap is mainly:

```text
l2cache.h/.cc telemetry/config plumbing
parser/analyzer schema/config
```

M1's functional core changes should concentrate in `gpu-cache.h/.cc` plus minimal config plumbing. M0a must not touch payload allocation semantics.

Do not resolve cross-branch conflicts during either lane. Independent PASS comes first.

## Integration after independent review

Only after **both** ChatGPT reviews PASS:

1. create a fresh integration branch/worktree from the accepted M1 source;
2. port/cherry-pick the accepted M0a observation changes;
3. resolve only mechanical overlap;
4. re-run M1 static baseline equivalence and M0a ON/OFF timing-neutrality on a compact representative set;
5. publish one integration review pack;
6. use the integrated source as parent for M0b opportunity studies.

Do not begin M0b or any functional mechanism from either unintegrated branch.

## Scientific separation

M0a can characterize structural blocked-cycle/service behavior on the pre-M1 D512 parent because M1 is required to be behavior-equivalent. After integration, selected M0a results may be spot-revalidated rather than scientifically reinterpreted if exact behavior equivalence holds.

## STOP

Each lane stops at its own review-ready status. Integration requires a new ChatGPT handoff after both independent reviews.
