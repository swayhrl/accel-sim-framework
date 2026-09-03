# M4 Completion-Accounting Recovery

Status: **AUTHORIZED HARD-FAIL RECOVERY — COMPLETE BEFORE RESUMING M4 BRING-UP**

This specification recovers the source-reachable `PAPER_IO` / `PAPER_OO` cacheable-load completion failure exposed by PolyBench 2DConv. It is a correctness recovery, not a performance-tuning task.

Current failure evidence:

- `docs/dtc_l1/implementation/M4_COMPUTE_BRINGUP_FAILURE.md`
- Core failure checkpoint: `56a9230e4a538b69a30673ebdf66c42526fb324a`
- Framework failure checkpoint: `5f674edccdf48dc768155fbd008723dc8a126b31`

M1, M2, and M3 remain closed PASS unless this recovery demonstrates a real regression in their previously validated semantics. M5 remains forbidden.

---

## 1. Observed HARD failure

The first provenance-controlled PolyBench 2DConv triplet produced:

- `PAPER_IO`: abort in `ldst_unit::dtc_l1_io_complete_instruction`, assertion `pending >= dependencies`;
- `PAPER_OO`: abort in `ldst_unit::dtc_l1_oo_complete_instruction`, same assertion;
- `PAPER_BASE`: wall-clock diagnostic timeout at 240 seconds, not yet classified as deadlock or correctness failure.

The IO/OO failure is source reachable and cannot be classified as `SOURCE_UNREACHABLE_NA`.

Current source registers cacheable DTC load dependencies in `ldst_unit::issue()` using the number of unique coalesced 128B line references. The DTC PIB later retains its own unique 128B line-reference vector and retirement currently subtracts `entry.references.size()` from the existing `m_pending_writes[warp][reg]` aggregate.

The failing condition means that, at retirement, the existing simulator aggregate contains fewer outstanding entries than the DTC retirement path believes it owns. This must be localized before any repair.

---

## 2. Recovery principle

Do **not** repair the assertion by clamping, forcing zero, skipping release, or changing performance/resource semantics.

Forbidden examples:

```text
pending = 0
pending -= min(pending, dependencies)
dependencies = min(pending, dependencies)
remove/disable the assertion
release the scoreboard register regardless of accounting
```

The recovery must establish one source-backed owner and one conserved dependency count for every DTC-owned cacheable load.

The desired conservation relation is:

```text
registered DTC dependencies at issue
        ==
PIB-owned 128B line dependencies
        ==
DTC dependencies closed at retirement
```

and each dependency must be closed exactly once.

`m_pending_writes` remains part of the existing GPGPU-Sim scoreboard/completion machinery. The recovery may add a DTC side ledger/checker to prove ownership and cardinality, but must not silently replace architectural scoreboard semantics with an unrelated new completion model.

---

# R4C.0 — Freeze/reproduce the pre-fix failure — HARD

Reproduce the first failure using the exact PolyBench 2DConv provenance already recorded in `M4_COMPUTE_BRINGUP_FAILURE.md`.

Before changing functional behavior, capture a bounded diagnostic record for the **first failing dynamic instruction** containing at least:

- cycle;
- SM;
- warp;
- dynamic instruction UID;
- PC;
- address-space/cache-op classification;
- destination register IDs;
- issue-time upstream `accessq_count()`;
- issue-time unique 128B line-reference count and addresses/masks;
- PIB-admission unique 128B line-reference count and addresses/masks;
- `m_pending_writes[warp][reg]` immediately after issue registration;
- the same pending value immediately before DTC retirement;
- DTC retirement dependency count;
- whether the UID has previously entered any completion/retirement path.

Acceptance: the first failure is deterministic enough to identify the exact UID/PC and the mismatch values. If the failure cannot be reproduced, do not guess; preserve evidence and STOP.

---

# R4C.1 — Add a per-instruction DTC dependency ledger — HARD

Add bounded/assertion-oriented bookkeeping for cacheable DTC loads, keyed by dynamic instruction UID (exact type/name may follow source conventions).

Conceptually record:

```text
uid -> {
    warp_id,
    pc,
    output_registers,
    registered_dependency_count,
    pib_dependency_count,
    closed_dependency_count,
    lifecycle_state
}
```

Required lifecycle states must distinguish at least:

```text
REGISTERED -> PIB_OWNED -> READY -> RETIRED
```

or an equivalent exactly-once state machine.

Rules:

1. At `ldst_unit::issue()`, when DTC cacheable-load accounting is selected, record the exact dependency count used to increment `m_pending_writes`.
2. On first IO/OO PIB creation, record/compare the PIB reference count against the registered count.
3. On retirement, consume the registered count exactly once; do not re-derive an unverified independent number and assume equality.
4. At kernel drain, no live DTC dependency-ledger entry may remain.
5. The ledger is diagnostic/correctness ownership state only; it must not change Tag/physical/NoC/L2/DRAM semantics.

Acceptance: the ledger classifies the first 2DConv failure before functional repair.

---

# R4C.2 — Mutation provenance and root-cause classification — HARD

Instrument all relevant mutation points that can change `m_pending_writes` for the first failing warp/register while the failing DTC UID is live. Keep logging bounded/filterable.

For each mutation record:

```text
cycle, sm, warp, reg, uid/inst if available,
reason/path, before, delta, after
```

At minimum inspect/trace:

- `ldst_unit::issue()` registration;
- conventional L1 hit completion decrements;
- conventional cache/memory writeback completion;
- DTC IO completion;
- DTC OO completion;
- bypass/global writeback paths where applicable;
- any other source path found to mutate the same aggregate.

Classify the root cause into one of these source-backed categories, or document another category with evidence:

### A — premature/non-DTC consumption
A conventional or unrelated completion path consumes part/all of the pending state belonging to a DTC-owned cacheable load before DTC retirement.

### B — cardinality divergence
The issue-time registered 128B dependency count differs from the PIB-owned reference count for the same UID.

### C — duplicate DTC completion
The same DTC UID closes dependencies or retires more than once.

### D — cross-instruction aggregate alias
The aggregate `(warp, register)` contains contributions/consumption from another live instruction in a way that invalidates the current instruction-level subtraction assumption.

### E — other
Must be established from source/trace, not inferred from the assertion alone.

Acceptance: one root cause is demonstrated by a compact causal trace. No functional repair is authorized before this classification.

---

# R4C.3 — Minimal source-backed repair — HARD

Apply the smallest repair that restores exactly-once dependency ownership without changing frozen DTC architecture.

Allowed repair classes depend on R4C.2 evidence:

- **A:** isolate the DTC-owned cacheable load from the unintended conventional decrement/completion path; preserve the conventional path for LEGACY/PAPER_BASE/non-DTC operations.
- **B:** establish one authoritative dependency-count generation point and require issue registration and PIB ownership to use/verify the same value. Preserve the frozen 128B coalesced-line dependency granularity.
- **C:** repair lifecycle ownership so a UID can reach DTC completion/retirement only once; retain a fatal duplicate-completion assertion.
- **D:** preserve the existing simulator scoreboard semantics while making DTC completion accounting correctly attribute its own dependency contribution; do not simply zero the aggregate. If this requires a broader source-semantic decision, STOP for review rather than guessing.
- **E:** repair only after documenting why the fix is source-correct and architecture-neutral.

Hard requirements after the fix:

```text
registered_dependency_count == pib_dependency_count
closed_dependency_count == registered_dependency_count
```

at successful retirement, and DTC completion must not close the same UID twice.

For every destination register, scoreboard release occurs exactly once at the correct final completion point.

---

# R4C.4 — Permanent regression tests — HARD

Add deterministic tests/checkers so this class of bug cannot silently return.

Required tests include:

1. `C01 CardinalityConservation`: issue registration == PIB reference count == retirement closure for 1/2/4/32 unique 128B lines.
2. `C02 MultiSectorOneLine`: multiple upstream sector accesses grouped into one 128B line still register/close one line dependency in paper whole-line modes.
3. `C03 ExactlyOnceCompletion`: injected duplicate completion/retirement attempt is detected.
4. `C04 NoConventionalConsumption`: a DTC-owned cacheable load cannot be completed/decremented by the conventional L1D completion route.
5. `C05 RegisterReuse/Alias`: if source scheduling can create a relevant same-warp/register overlap, verify attribution; otherwise record source proof that the overlap is forbidden and keep a checker for unexpected occurrence.

The exact harness may be CTest/request-level/runtime microbench, but it must exercise the real completion-accounting logic rather than only a disconnected helper.

---

# R4C.5 — PolyBench 2DConv recovery validation — HARD

Rerun the exact recorded PolyBench 2DConv IO/OO configurations first.

For both `PAPER_IO` and `PAPER_OO` require:

- application completes normally;
- no `pending >= dependencies` / dependency-ledger assertion;
- dynamic instruction/load/store/atomic/source-reachable-FENCE_OP counts are internally valid;
- DTC PIB drains;
- inflight lower requests drain;
- lower credits close;
- dependency ledgers drain;
- no stale fill, Ref/Shadow Ref, merge/wakeup, or generation invariant failure;
- application output/self-check is valid when the workload exposes one.

If IO passes but OO fails, or vice versa, treat the remaining failure as HARD and STOP after evidence.

---

# R4C.6 — Closed-stage regression suite — HARD

Because the repair touches shared load completion glue, rerun enough closed-stage validation to prove no regression:

- Core release build;
- all DTC CTests including bad-generation negative test;
- M2 IO VecAdd runtime smoke and strict drain/accounting;
- M3 PAPER_OO VecAdd runtime smoke;
- M3 MODERN_OO_SECTOR VecAdd runtime smoke;
- key IO/OO causal/HOL and Ref/Shadow Ref deterministic tests already in CTest;
- one LEGACY neutrality smoke/differential sufficient to prove DTC-mode repair did not leak into LEGACY behavior;
- `git diff --check` and clean/expected worktrees.

Do not reopen or regenerate M2/M3 review packs unless the repair actually changes their accepted semantics. Instead add a compact cross-reference in the M4 recovery evidence to the regression results.

---

# R4C.7 — PAPER_BASE timeout diagnosis — HARD before accepting this workload triplet

The previous 240-second PAPER_BASE result is only `TIMEOUT_DIAGNOSTIC`; it is not yet a deadlock classification.

After IO/OO correctness is recovered, diagnose PAPER_BASE separately using bounded progress evidence:

- committed/dynamic instruction progress over wall-clock intervals;
- PIB occupancy/full events;
- MSHR/outstanding/lower-request activity;
- last simulator progress cycle;
- native deadlock/watchdog status if any.

Classify as exactly one of:

- `SLOW_BUT_PROGRESSING`;
- `RESOURCE_STALL_WITH_PROGRESS`;
- `NO_PROGRESS_DEADLOCK`;
- `OTHER_HARD_FAILURE`.

If it is measurably progressing, a larger wall-clock diagnostic allowance is permitted; do not change architecture to make it faster. If it is no-progress/deadlocked unexpectedly, record evidence and STOP.

2DConv need not become one of the final five accepted M4 triplets solely because it was the first diagnostic workload, but its IO/OO correctness failure must be fixed and its PAPER_BASE status must be understood before the failure is considered closed.

---

# R4C.8 — Resume the remaining M4 Goal — AUTHORIZED AFTER HARD PASS

If and only if R4C.0-R4C.7 pass/close with no active HARD failure:

1. create/update `docs/dtc_l1/implementation/M4_COMPLETION_ACCOUNTING_RECOVERY_EVIDENCE.md` with root cause, pre/post SHAs, tests, workload hashes, and regression results;
2. make semantic commits with explicit-path staging and push both branches;
3. update Codex-owned `docs/dtc_l1/codex_handoff/LATEST_REPORT.md` from blocked to recovery PASS / M4 in progress;
4. resume the existing M4 source-reachability/fence disposition unchanged;
5. continue W/A/BP/MIX/workload-manifest/5-triplet/parser/CSV/hygiene closeout automatically;
6. create `review_packs/M4_COMPUTE_BRINGUP/` only after every active M4 HARD gate passes;
7. set `LATEST_REPORT.md` to `READY_FOR_M5_REVIEW`, push, and STOP.

No new human authorization is required after full R4C PASS.

---

## 3. Fence-resolution interaction

`M4_FENCE_REACHABILITY_RESOLUTION.md` remains valid and unchanged.

Do not use this recovery to:

- implement PTX `fence` lexer/parser/decode support;
- map `membar` to `FENCE_OP`;
- force proxy-fence metadata onto ordinary instructions.

F00/F01-F03 disposition resumes only after the active completion-accounting HARD failure is closed.

---

## 4. STOP conditions

STOP, preserve compact evidence, push safe state, and update `LATEST_REPORT.md` if:

- the first failing UID cannot be localized reproducibly;
- dependency cardinality cannot be reconciled without changing frozen M0 DTC semantics;
- the repair would require bypassing/weakening scoreboard correctness;
- a closed M1/M2/M3 invariant regresses;
- 2DConv IO or OO remains source-reachably incorrect after the minimal repair;
- PAPER_BASE is proven unexpectedly deadlocked/no-progress;
- another active M4 HARD gate fails;
- M4 reaches `READY_FOR_M5_REVIEW`.

Do not begin M5.
