# EP-L2 M0a + M1 Speculative Integration — Acceptance Criteria

## A. Immutable parent identity

PASS only if the integration source is derived from exact frozen candidates:

```text
M1 Core       955a50cbb5e8d928b6c7b0c78e1af062b835df44
M1 Framework  aae62b66685f15437cecf0193934f628e6fac6ae
M0a Core      666f0ba2d7b6a027f395346e274a934c19fdd3c1
M0a Framework 2da5dba0d0ca60dfa2ee5c12cb3b315c2c54120d
```

Record exact merge/cherry-pick audit and resulting SHAs.

## B. Isolation

Use fresh integration worktrees/build/result roots. No write to live M0a, historical D512, or M1 result roots.

## C. M1 semantics preserved

Integrated source must retain:

```text
single global 1152-slot payload namespace
static resident tag i -> payload_id i
bank = payload_id % 4
handle/owner/generation/tag-sidecar invariants
no production bypass consumer
all functional mechanisms OFF
```

All reviewed M1 directed lifecycle/mode-switch tests must pass.

## D. M0a observation-only semantics preserved

M0a OFF must not be read by architectural control paths. M0a ON may only produce/sample/parse observation state.

`any_blocked_cycles` is exact once-per-observed-cycle blocked accounting.

Reason counters must be documented as **production-visible / stage-primary** rather than an exhaustive independent all-resource bitset because production preview may short-circuit and MSHR `full_reason` is prioritized.

Do not sum reason counters into a total.

## E. Base resource contract

Both integration test modes use the exact accepted D512 research base resources. The only OFF/ON observability delta is the M0a statistics switch.

Functional EP-L2 features remain all OFF.

## F. Build / directed validation

Require:

```text
Release build
M1 payload-store/banked/WAD/descriptor/sidecar tests
M1 fail-closed mode-switch tests
M0a parser/cardinality tests
M0a once-per-cycle held-head test
M0a useful-admit/useful-response boundary test
config/manifest feature-vector test
git diff --check
clean frozen integration worktrees
```

## G. Short natural equivalence

At minimum use a compact set including:

```text
vectorAdd_4M
sad
cfd_097k
```

For `BASE_M1_STATIC`, compare against accepted D512 parent/M1 evidence.

For `M0A_ON_M1_STATIC`, require exact cycles/instructions and deterministic existing B0/L1/DRAM/terminal outputs versus `BASE_M1_STATIC`; M0a output is the only intended additive difference.

No mismatch may be dismissed as instrumentation noise.

## H. Provenance / mode switching

Every integration run/manifest records:

```text
semantic base
runtime Core SHA
runtime Framework SHA
base-resource config hash
experiment mode label
M0a switch
functional feature vector
trace identity
result root
maturity
promotion dependencies
```

Results must be in collision-free mode-specific roots.

## I. Maturity

All integration outputs remain:

```text
SPECULATIVE_PENDING_GATE
promotion_dependencies = [M0A_FINAL_PASS, M1_FINAL_PASS]
```

until both parent gates pass.

## J. M0b prep boundary

After A-I local integration self-gates pass, observation-only M0b scaffolding may be prepared. It may not be promoted or used for mechanism claims before integrated-parent promotion.

No functional Unified/RO/TVD behavior is allowed.

## K. Completion

Interim completion status is:

```text
M0A_M1_INTEGRATION_INTERIM_REVIEW_READY
```

This is not integrated-parent final acceptance and not M0b evidence promotion.
