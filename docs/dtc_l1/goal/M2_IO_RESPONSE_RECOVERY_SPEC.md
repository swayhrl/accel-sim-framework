# DTC-L1 M2 IO Response/Retirement Recovery Specification

Status: **AUTHORIZED RECOVERY TASK**

Scope: recover from the first real `PAPER_IO` integration failure, complete all M2 HARD gates, and resume M3 -> M4 only after M2 fully passes. M5 remains forbidden.

## 1. Observed HARD failure

The first real `PAPER_IO` VecAdd integration correctly attempted to issue an IO-owned lower read without allocating a conventional L1D MSHR entry. On return, however, `ldst_unit::cycle()` routed the response through the conventional cached-read branch and called `m_L1D->fill(mf, ...)`.

`baseline_cache::fill()` requires the request to exist in the conventional cache's `m_extra_mf_fields`; a true DTC IO-owned request deliberately has no such record. The run therefore aborted on the `m_extra_mf_fields` lookup assertion.

The failed experimental integration was discarded. The committed Core branch is clean at the reported stop SHA. This failure is expected evidence that the DTC data path must own both request and response lifecycles; it must not be repaired by fabricating conventional MSHR/`m_extra_mf_fields` state.

## 2. Architecture rule for the recovery

For `PAPER_IO` cacheable **read** traffic:

- logical Tag lookup, physical allocation, Pending/Valid state, and PIB lifetime are DTC-owned;
- DTC reads do not use the traditional L1D MSHR as a capacity/merge structure;
- a DTC new miss creates a DTC-owned lower request;
- the returning DTC-owned response must be recognized before the conventional `baseline_cache::fill()` branch;
- the response completes the recorded `{phys_id, generation}` allocation identity directly in the IO-DTC state;
- conventional `baseline_cache::fill()` remains untouched for conventional/LEGACY/Paper-Base traffic and for later non-read paths until M4 specifies them;
- DTC instruction retirement/writeback must be driven by the DTC PIB and readiness state, not by a fake conventional MSHR completion.

Do **not** insert a dummy `m_extra_mf_fields` entry or a hidden conventional MSHR entry merely to satisfy `baseline_cache::fill()`. That would invalidate the M2 no-MSHR proof.

## 3. Required recovery sequence

### R2.0 Confirm request identity round trip — HARD

Before functional recovery, establish with bounded diagnostics/source evidence how a shader-originated read `mem_fetch` is returned after the current L2/NoC path.

For at least one controlled read miss, record at issue and response:

- `mem_fetch::get_request_uid()`;
- original shader instruction UID;
- address/access type;
- whether the returned object/UID is the original request or a reconstructed child/original object after sector handling.

Preferred routing key is the existing immutable request UID if it survives the complete round trip. If it does not, use a source-backed immutable ownership marker/identity that survives the current split/recombine path. Do not guess.

Acceptance: one deterministic rule can identify a returned IO-owned request without consulting the current logical Tag or the conventional L1D `m_extra_mf_fields`.

### R2.1 Dedicated DTC IO request ownership — HARD

Add an IO-owned inflight record, conceptually:

```text
request identity -> {
    physical_id,
    generation,
    line_address,
    owning instruction UID / provenance
}
```

Exact container/field names may follow source conventions.

On `NEW_MISS`:

1. the IO frontend commits the logical Tag -> physical allocation;
2. acquire one configured global lower-request credit;
3. create exactly one DTC-owned whole-line lower read for the 128B paper line;
4. record the immutable request -> `{phys_id,generation}` association;
5. queue it in a DTC-owned bounded lower-request queue/path;
6. issue at no more than the configured **1 request/cycle/SM** and subject to current interconnect backpressure.

The DTC read path must not call conventional L1D MSHR allocation/merge for this request.

At response:

1. identify IO ownership before the conventional L1D fill branch;
2. assert the recorded physical generation still matches;
3. transition the intended physical allocation to ready/Valid through the IO frontend;
4. release the lower-request credit exactly once;
5. remove the inflight ownership record exactly once;
6. consume/delete the lower-response object according to normal ownership rules;
7. **do not call `m_L1D->fill()` for this response**.

Required invariants:

- each DTC new miss has exactly one inflight ownership record;
- each record has exactly one response completion;
- request UID/identity is never reused while live;
- stale generation is fatal in debug/assert mode;
- lower credit acquire/release closes at drain;
- DTC inflight table/queue is empty at kernel drain.

### R2.2 Dedicated IO PIB payload and retirement/writeback — HARD

A true DTC response cannot rely on conventional MSHR `next_access()` to manufacture writeback events for every waiting instruction. Therefore the IO PIB/lifecycle must retain enough instruction state to retire the ready FIFO head itself.

Required model:

- one live dynamic memory instruction occupies one IO PIB entry;
- retain/capture the `warp_inst_t` (or equivalent completion payload) and the instruction's unique 128B line references before the dispatch/access queue is destroyed;
- IO readiness is determined from the DTC physical identities referenced by that PIB entry;
- only the FIFO head may retire;
- configured retire width remains **1 instruction/cycle**;
- retirement must contend with the existing operand-collector/writeback availability rather than bypassing writeback resources;
- `warp_inst_complete()` occurs exactly once at the DTC true retirement point;
- scoreboard/output-register state is released exactly once;
- old physical release dependencies are released at this retirement and are visible to allocation in the same simulator cycle, consistent with the frozen event ordering.

Preferred integration is a dedicated DTC writeback client/path in `ldst_unit` (or an equivalent source-native arbitration point), not routing DTC-ready instructions through `baseline_cache::next_access()`.

### R2.3 Completion-cardinality alignment — HARD

The existing `ldst_unit::issue()` increments `m_pending_writes` using the upstream `accessq_count()`, which may count current sector transactions. Paper IO, however, defines one dependency per unique coalesced **128B line reference**.

Before completing integration, prove and document the cardinality used by the selected Paper IO configuration.

For cacheable `PAPER_IO` loads:

- build unique 128B line references from the already-coalesced upstream accesses;
- do not run a second lane-coalescing algorithm;
- make the pending-write/completion accounting use the same number of DTC completion dependencies that the IO PIB will retire;
- one 128B line touched through multiple current 32B sector accesses must not require multiple DTC line completions in whole-line paper mode;
- an N-line divergent instruction must close exactly N DTC line dependencies while completing the dynamic instruction once.

If changing the normal `m_pending_writes` count for Paper IO is necessary, make it mode-specific; `LEGACY` and `PAPER_BASE` must remain bit/cycle neutral to their already-validated behavior.

Directed proof must include 1/2/4/32 unique 128B lines and at least one multi-sector-within-one-128B-line case.

### R2.4 IO transient allocation-block state audit — HARD

Source review found a latent issue in the current committed `io_frontend`: `entry::allocation_blocked` is set when an allocation cannot proceed, but a later retry that becomes a Valid/Pending Tag hit can return without clearing the sticky flag. That can make an otherwise ready entry permanently non-retirable.

Do not carry a sticky per-entry block bit as a lifetime dependency unless it is rigorously maintained for every retry outcome.

Preferred semantics:

- allocation/tag service blocking is a **transient current-line/current-cycle condition**;
- do not advance the instruction's line-processing cursor when the current line cannot be serviced;
- retry the same unresolved line later;
- once every line reference has been successfully classified/attached, PIB readiness depends only on the referenced physical data states (plus ordinary retirement/writeback availability), not on a stale historical block flag.

Add a regression where an initially allocation-blocked line later resolves as a hit/pending hit and the instruction still retires normally.

### R2.5 PAPER_IO access-path isolation — HARD

For cacheable Paper IO reads, prove that the functional path does not perform a conventional L1D `access()`/MSHR/fill lifecycle in parallel with the DTC model.

Required evidence for a controlled cold miss and pending hit:

- DTC `NEW_MISS`: exactly one physical allocation + one DTC lower request;
- traditional L1D MSHR occupancy/merge gate is not consulted as the DTC capacity condition;
- DTC `PENDING_HIT`: no additional lower read;
- DTC `VALID_HIT`: no lower read;
- no IO-owned response enters `baseline_cache::fill()`;
- no duplicated conventional cache side effect is created merely for timing bookkeeping.

Existing L1D may remain instantiated for LEGACY/PAPER_BASE and later M4 non-read semantics, but it must not secretly act as the Paper IO read backend.

### R2.6 Real VecAdd smoke — HARD

After R2.0-R2.5 directed checks, rerun the same real VecAdd integration first.

Required:

- application self-check PASS;
- no `baseline_cache::fill()` ownership assertion;
- no stale-generation assertion;
- no unexpected deadlock watchdog;
- IO PIB admits/retires/drain closes;
- DTC inflight lower requests drain to zero;
- lower credits close;
- dynamic instruction count is consistent with the same input/program;
- request counters demonstrate that IO reads use the DTC request/response path.

This remains `DIAGNOSTIC`, not a paper speedup result.

### R2.7 Full M2 HARD revalidation — HARD

Only after VecAdd passes, execute the complete M2 matrix already defined in `VALIDATION_ACCEPTANCE_MATRIX.md`:

- I01 ColdMiss;
- I02 ValidHit;
- I03 PendingHit;
- I04/I05 allocation-width behavior;
- I06 partial allocation/no rollback;
- I07 exact LRU;
- I08 eviction while fill in flight with original physical identity;
- I09 duplicate-after-Tag-eviction accounting;
- I10 IO HOL;
- I11 same-cycle release visibility;
- I12 natural tiny-pool expected deadlock;
- I13 default-80KB progress;
- I14 outstanding cap;
- I15 per-SM issue width;
- explicit no-traditional-L1-MSHR proof;
- all IO fill/release/accounting invariants;
- counter/parser sanity;
- release build/CTest;
- `git diff --check`;
- clean worktrees.

Create `review_packs/M2_IO_READ/` only after every HARD item passes.

## 4. Additional required counters/evidence for this recovery

Add/retain compact counters sufficient to distinguish request routing bugs from mechanism stalls:

- `io_lower_created`;
- `io_lower_issued`;
- `io_lower_responses`;
- `io_inflight_current/peak`;
- `io_inflight_identity_mismatch` (must remain zero except injected-negative test);
- `io_responses_routed_dtc`;
- `io_responses_routed_conventional` (must be zero for IO-owned reads);
- `io_pib_head_ready_cycles` / `io_head_not_ready_cycles`;
- `io_retire_count`;
- `io_ready_but_writeback_blocked_cycles`;
- `io_completion_dependency_count` and closed completion count;
- lower-credit acquire/release/current/peak;
- conventional L1D MSHR entry/merge counters retained as an independent proof that DTC read correctness does not depend on them.

Do not default to unbounded event logging.

## 5. Recovery acceptance criteria

M2 recovery is not PASS merely because VecAdd runs. It is PASS only when:

1. IO request ownership survives the lower-memory round trip by a source-backed immutable identity;
2. no IO-owned read response calls conventional `baseline_cache::fill()`;
3. IO read misses do not allocate/use the traditional L1D MSHR as their capacity/merge mechanism;
4. the DTC PIB itself supplies the ready instruction to a finite writeback/retirement path;
5. pending-write/dependency cardinality matches unique 128B Paper IO line references;
6. physical `{id,generation}` fill identity is checked;
7. all request/credit/PIB/dependency tables drain exactly;
8. the sticky allocation-block issue is removed or proven impossible by stronger source-backed state transitions;
9. VecAdd passes through the real Paper IO path;
10. every existing M2 HARD gate I01-I15 and no-MSHR proof passes.

## 6. Progression rule

If all M2 HARD gates pass:

- mark `M2_IO_READ` PASS;
- create/push `review_packs/M2_IO_READ/`;
- update Codex-owned `LATEST_REPORT.md`;
- continue automatically into the already-authorized M3 -> M4 goal.

If any HARD item fails or a source-semantic ambiguity cannot be resolved without guessing, record evidence and STOP.

Do not begin M5.