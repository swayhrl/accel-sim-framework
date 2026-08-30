# EP-L2 M0a + M1 Speculative Integration Handoff

Status: **AUTHORIZED SPECULATIVE INTEGRATION**.

## Objective

Construct the first unified post-calibration EP-L2 implementation parent by combining:

```text
M1 behavior-preserving elastic/global-ID substrate
+
M0a generic observation-only telemetry
```

without waiting for the final live M0a `scan` validation.

The integrated child is not yet accepted evidence. It must remain:

```text
SPECULATIVE_PENDING_GATE
promotion_dependencies = [M0A_FINAL_PASS, M1_FINAL_PASS]
```

## Exact parents

Accepted D512 semantic base:

```text
Core       878f80869ce212e779df20b6421e4dc7f987825d
Framework  aae62b66685f15437cecf0193934f628e6fac6ae
```

Frozen M1 candidate — integration base:

```text
Core       955a50cbb5e8d928b6c7b0c78e1af062b835df44
Framework  aae62b66685f15437cecf0193934f628e6fac6ae
```

Frozen M0a changes to port:

```text
Core       666f0ba2d7b6a027f395346e274a934c19fdd3c1
Framework  2da5dba0d0ca60dfa2ee5c12cb3b315c2c54120d
```

Do not merge moving branch tips. Use these immutable source objects/diffs.

## Isolation

Create fresh worktrees/branches, preferably:

```text
Framework: /workspace/worktrees/accel-sim-ep-l2-m0a-m1-int/
Core:      /workspace/worktrees/gpgpu-sim-ep-l2-m0a-m1-int/
branch:    hrl/ep-l2-m0a-m1-int-v0
results:   /workspace/results/ep_l2_m0a_m1_int/
```

The live M0a scan worktree/result root is read-only. Do not use, rebuild, clean, reset, or reuse it.

## Integration order

1. Start from exact M1 Core candidate `955a50c...` and exact accepted Framework `aae62b...`.
2. Port the exact M0a Core changes from `666f0ba...` and Framework changes from `2da5dba...`.
3. Resolve only mechanical overlap in configuration declarations / `l2cache` telemetry plumbing.
4. Preserve M1 behavior as the single payload substrate. Do not resurrect the pre-M1 payload representation.
5. Preserve M0a as observation-only and default OFF.

## Required integrated effective configuration

Base resource configuration remains the accepted D512 research baseline:

```text
descriptor pool = 512
Line MSHR = 128
per-address cap = 32
L1 BASE
WAD = 128
payload storage = 1152 x 128B
4 x 288 banks
L2->DRAM = 128
scheduler = 128/channel
ReturnQ = 192/channel
DRAM = 850 MHz
```

Functional mechanism vector remains all OFF:

```text
unified_payload = 0
ro_pending_state = 0
tvd = 0
adaptive_policy = 0
```

M1 is infrastructure, not a functional mechanism feature.

Required modes for integration testing:

```text
BASE_M1_STATIC      M0a OFF
M0A_ON_M1_STATIC    M0a ON
```

Both modes use the same integrated Core/Framework SHA family and same D512 base resources.

## M0a reason semantics in the integrated source/docs

Do not describe M0a reason counters as an exhaustive independent all-resource bitset.

The integrated parser/docs must state:

```text
any_blocked_cycles:
  exact once-per-observed-cycle total;

reason fields:
  production-visible / stage-primary reasons exposed by the exact preview path;
  some predicates evaluated together may overlap, but early preview returns and
  prioritized MSHR full_reason mean the set is not exhaustive multi-cause evidence.
```

No producer change is required merely to manufacture an exhaustive bitset.

## Allowed work

The integration lane may:

```text
merge the frozen parents
Release build
run all M1 directed lifecycle/mode tests
run all M0a parser/collector tests
add missing directed once-per-cycle/useful-count tests
add explicit integrated mode/feature-vector manifest fields
run short BASE_M1_STATIC parent-equivalence smoke
run short M0A_ON_M1_STATIC timing-neutrality smoke
prepare M0b observation-only scaffolding after all integration self-gates pass
```

## M0b preparation allowed, evidence not yet promoted

After the integrated source passes build + directed + short natural equivalence, Codex may prepare OFF-by-default M0b observation plumbing for:

```text
RO eligibility/exclusion classification and MSHR lifetime hooks
TVD dirty-victim/WAD/payload-lifetime hooks
non-resident-payload opportunity only after a real candidate consumer is defined
```

Do not run a promoted M0b campaign until the integrated parent is promoted after both parent gates.

Do not create synthetic production bypass traffic merely to justify Unified Payload.

## Hard stops

Do not:

```text
interrupt/restart/duplicate M0a scan
change D512 base resources
implement Unified allocation
release/avoid Line MSHR functionally
add TVD functional storage
run headroom experiments
make a mechanism performance claim
```

## Deliverables

Publish a speculative integration pack:

```text
docs/ep_l2/review_packs/M0A_M1_INTEGRATION_INTERIM_r1/
```

with at least:

```text
README.md
SOURCE_ANCHORS.md
MERGE_AUDIT.md
CHANGED_FILES.md
CONFIG_MODE_CONTRACT.md
DIRECTED_TESTS.md
PARENT_EQUIVALENCE.csv
M0A_ON_TIMING_NEUTRALITY.csv
M0A_REASON_SEMANTICS.md
M0B_PREP_STATUS.md
RAW_LOG_INDEX.tsv
VALIDATION_SUMMARY.md
SHA256SUMS
```

Update/create:

```text
docs/ep_l2/codex_handoff/LANE_INT_LATEST.md
```

Then stop for ChatGPT integration review unless final parent gates have already passed and a later explicit handoff authorizes promotion/M0b execution.
