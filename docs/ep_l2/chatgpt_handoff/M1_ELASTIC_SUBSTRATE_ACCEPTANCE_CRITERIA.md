# EP-L2 M1 Elastic Substrate — Acceptance Criteria

Status: mandatory self-gating contract.

## A. Exact parent / authorized delta

M1 derives from the accepted D512 research parent:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
```

Authorized semantic goal: **representation/lifecycle plumbing only**. No architectural behavior/capacity/timing change is allowed in the default static path.

## B. Single post-M1 substrate

PASS requires a coherent global-ID/handle implementation that becomes the post-M1 infrastructure.

Do not leave two independently evolving payload state machines as a permanent baseline/mechanism toggle. A temporary bring-up selector is allowed only if it is removed or proven non-semantic before closeout.

## C. Exact static mapping

Under all functional features OFF + static policy:

```text
resident tag_index i -> payload_id i       for 0..1023
bypass-model id j     -> payload_id 1024+j for 0..127
bank                  -> payload_id % 4
```

Current production request paths must continue to use resident only; M1 may not introduce a production bypass consumer.

## D. Tag/payload sidecar integrity

Required invariants:

```text
valid resident tag needing payload -> exactly one live sidecar handle
sidecar handle -> live slot with matching role/owner/generation
no two live tag owners claim the same slot incarnation
invalid/replaced tag -> no stale live sidecar claim after lifecycle completion
```

Rollback must atomically restore prior slot + sidecar state when admission fails after speculative reservation.

## E. Handle/generation safety

For every live allocation:

```text
0 <= payload_id < 1152
one live owner per {payload_id,generation}
old handle becomes invalid before ID reuse
pending fill cannot land after incarnation reuse
no release while pending sector ownership requires the slot
no double free
```

Late/stale fill must be rejected before tag/data corruption.

## F. Tag/cache policy neutrality

M1 must not alter:

```text
tag lookup/replacement choice
tag state semantics
sector validity/dirty semantics
MSHR allocation/merge/full reasons
descriptor allocation/lifetime
per-address cap
MissQ
WAD allocation/release
lower request creation/routing
response retirement
```

Any source refactor touching these areas must be mechanically necessary for handle plumbing and must preserve behavior.

## G. Bank-service neutrality

Static mode must preserve the exact payload ID and therefore exact bank for resident accesses.

Required:

```text
bank = payload_id % 4
4 banks
one arbitrary op/bank/cycle
same immediate idle grant
same oldest-ready pending priority
```

Directed same-bank replay and natural bank counters must show no unexplained drift.

## H. Dormant bypass discipline

Existing directed bypass APIs may be migrated to the global slot representation and must remain correct.

However:

```text
no production bypass caller
no synthetic bypass workload
no bypass opportunity claim
```

are required M1 boundaries.

## I. Storage accounting

Physical payload budget remains exactly:

```text
1152 x 128 B / slice
4 x 288 bank organization
1024 resident tags
```

Any sidecar/role/generation metadata additions must be quantified separately as metadata bits/bytes. Do not hide extra 128-B data storage in helper objects.

## J. Mode/config contract

Post-M1 baseline is:

```text
all functional EP-L2 feature bits OFF
payload policy = static
accepted D512 base resource config
```

Omitted feature options must resolve to OFF. Unsupported future feature combinations fail closed.

Every run manifest/effective config records mode/feature vector and exact runtime config hash.

## K. Build / directed correctness

Required:

```text
Release build
existing payload-store/banked tests
existing C3-C7/EP-L2 regressions
new sidecar/handle lifecycle tests
rollback tests
late-fill/generation tests
same-bank arbitration replay
dormant bypass unit lifecycle
terminal drain/no-leak tests
parser/config tests
git diff --check
clean frozen worktrees
```

## L. Parent equivalence

At minimum run parent D512 baseline vs post-M1 static baseline on:

```text
vectorAdd_4M
convolutionSeparable
cfd_097k
sad
FWT_7_21
```

PASS requires exact simulated cycles/instructions and no unexplained functional/native counter differences.

Where parsed schemas are unchanged, compare the seven existing parsed artifact families byte-for-byte:

```text
target_summary
target_slice
target_kernel
target_bank
target_window
target_l1
target_dram
```

If M1 adds only new additive output fields, compare a canonical old-field projection byte-for-byte and separately validate new fields. Do not accept a timing mismatch as instrumentation noise.

## M. No functional performance claim

M1 success is **equivalence/correctness**, not speedup.

No Unified/RO/TVD/shared policy result may appear in the M1 evidence set.

## N. Packaging

Required:

```text
docs/ep_l2/review_packs/M1_ELASTIC_SUBSTRATE_r1/
docs/ep_l2/codex_handoff/LANE_M1_LATEST.md
```

Review pack must contain source diff/map, metadata/storage accounting, directed-test matrix, exact parent-equivalence evidence, raw-log index, SHA256SUMS, validation outputs and final source/config SHAs.

## O. STOP

Only declare:

```text
M1_ELASTIC_SUBSTRATE_REVIEW_READY
```

STOP before any shared/unified allocation, RO pending-state, TVD, adaptive policy or headroom campaign.
