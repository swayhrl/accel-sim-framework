# EP-L2 Lane C — L1 Causality Acceptance Criteria

This is the authoritative self-gating contract for Lane C.

Lane C is a **causality/calibration experiment**, not a redesign of L1. Codex may self-repair runner/config/instrumentation/tooling inside the authorized scope until all mandatory gates pass.

## C0. Source identity and isolation — mandatory

PASS only if:

```text
D256 cells derive from the exact C7e formal source/config semantics
Lane A worktrees/binaries/results remain untouched
Lane C has isolated worktrees/branches/result roots
all runs record source SHA/config hash/trace/L1 class/descriptor capacity
```

For D512 interaction cells, consume the exact Lane B `D512_READY` source/config. Lane C must not independently implement its own descriptor-512 semantics.

## C1. Frozen L1 geometry — mandatory

Across all first-stage cells keep:

```text
capacity = 64 KiB
sets = 4
ways = 128
line = 128 B
latency = 20 cycles
```

Do not change L1 capacity/associativity/line size to obtain headroom.

## C2. Authorized cells — mandatory

### D256 + META-HR

Only:

```text
MSHR 512 -> 1024
merge cap 8 -> 32
MissQ 16 -> 64
banks stays 4
```

### D256 + BANK-HR

Only:

```text
banks 4 -> 8
MSHR/merge/MissQ stay baseline
```

### D512 interaction cells

Only after Lane B `D512_READY`:

```text
D512 + META-HR
D512 + BANK-HR
```

No other modeled resource may change.

## C3. Base reproduction gate — mandatory

Before interpreting headroom results, prove the Lane C baseline configuration reproduces the existing exact C7e D256/B0-Banked result when no headroom delta is applied.

Use at least:

```text
vectorAdd_4M
spmv
one longer selected workload
```

Require exact simulated equality for cycles, instructions, selected L2/DRAM counts, and terminal invariants.

If Lane C requires source instrumentation changes, compare old exact C7e source vs new instrumentation-enabled source at the same baseline configuration and require timing neutrality.

## C4. Configuration-delta audit — mandatory

For every experiment generate a machine-readable effective-config diff.

PASS only if the diff proves:

```text
META-HR cell: only MSHR/merge/MissQ differ
BANK-HR cell: only bank count differs
D512 interaction: descriptor capacity plus the named L1 headroom class differ
```

If changing bank count also changes the simulator's bank-index mapping, document that this is part of the intended bank-throughput headroom experiment; do not describe it as a pure extra-port experiment unless the code actually models it that way.

## C5. L1 counter/instrumentation correctness — mandatory if code or counters change

Prefer exact existing C7e L1D counters. If new counters/hooks are needed, every field must have a source semantic map:

```text
field name
unique/retry/event semantics
exact production increment point
denominator if any
application/kernel scope
reset/delta behavior
```

Directed tests must cover the relevant path, including when practical:

```text
MSHR entry full
per-address merge full
MissQ full
line allocation fail
bank/latency queue conflict
no-failure control
```

Do not reinterpret retry/stall attempts as unique-request failures.

If instrumentation is observation-only, require exact baseline timing neutrality on natural workloads.

## C6. Build/regression — mandatory

Final Lane C experiment source/config infrastructure must have:

```text
Release build PASS
existing relevant C7e/L1 regressions PASS
new config-delta tests PASS
new counter tests PASS if counters changed
parser/analyzer tests PASS if output changed
git diff --check PASS
clean frozen experiment worktrees
```

## C7. Screening workload completion — mandatory

Initial set:

```text
vectorAdd_4M
scan
spmv
convolutionSeparable
btree
sad
FWT_7_21
```

First complete all 7 D256 META-HR and all 7 D256 BANK-HR runs unless a proven common producer defect invalidates the lane.

Each run requires:

```text
COMPLETE_VALID
normal exit
exact expected source/config hashes
terminal_clean = 1
payload consistency = 1
parser success
required L1/L2/lower telemetry present
```

## C8. Causality analysis — mandatory

For each workload/cell compare against the corresponding BASE cell:

```text
cycles/speedup
L1 blocker movement
L1 accesses/misses
L2 descriptor need/block/occupancy
Line-MSHR pressure
L2 request/lower traffic
L2->DRAM/scheduler/BW
5K temporal pressure
```

Classify each result into one of:

```text
L1_NOT_CAUSAL
L1_LOCAL_BOTTLENECK
L1_MASKS_L2
BOTTLENECK_MOVES_DOWNSTREAM
MIXED_OR_INSUFFICIENT
```

Use speedup **and downstream movement**, not blocker-count reduction alone.

Screening thresholds may use:

```text
<2% cycle improvement: weak
2-5%: moderate
>5%: strong enough to decompose
```

but these are heuristics, not conclusions by themselves.

## C9. One-at-a-time decomposition — mandatory for material META-HR responses

Because META-HR changes three resources together, any workload showing meaningful response (normally >5%, or a strong downstream-pressure shift) must be decomposed before `BASELINE-DECISION`.

Run only for sensitive workloads as needed:

```text
MSHR-only: 512 -> 1024
merge-only: 8 -> 32
MissQ-only: 16 -> 64
```

Keep every other variable at the relevant D256 or D512 base.

This is required to avoid claiming "L1 MSHR" when the actual cause was MissQ or merge capacity.

## C10. D512 interaction gate

Lane C may start D512 META/BANK cells only when workboard `D512-PREFLIGHT` is DONE/PASS and Lane B provides exact:

```text
source SHA
config overlay/hash
D512_READY result path
```

Then run the same selected workload set unless Lane B/ChatGPT has narrowed it based on evidence. Do not change the D512 definition locally.

## C11. Review pack / return path — mandatory

Create a browsable pack such as:

```text
docs/ep_l2/review_packs/L1_CAUSALITY_CALIBRATION_r1/
```

Include:

```text
source/config anchors
effective-config diffs
base reproduction/timing-neutrality evidence
run status table
D256 META/BANK comparison
D512 META/BANK interaction when available
one-at-a-time decomposition for sensitive cases
causality classification table
raw-log index
SHA256SUMS
open issues
```

Update:

```text
docs/ep_l2/codex_handoff/LANE_C_LATEST.md
PARALLEL_WORKBOARD.md
```

## Completion state

Lane C is complete for convergence only when all required D256 cells and all dependency-available D512 interaction/decomposition cells have valid evidence.

Final lane status:

```text
L1_CAUSALITY_SCREEN_COMPLETE
```

Lane C must not independently alter the primary L1 baseline.

## Hard stops

Stop and request review if completion would require:

```text
changing L1 capacity/assoc/line/latency outside authorized cells
changing L2/DRAM resources except consuming Lane B D512
accepting unexplained base-reproduction/timing mismatch
changing traces/workloads to improve outcomes
rewriting L1 event semantics to make counts look smaller/larger
modifying Lane A or Lane B active runtime worktrees
```
