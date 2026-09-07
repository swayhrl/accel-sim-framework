# Window C — speculative M4B development goal

Status: **AUTHORIZED SPECULATIVE GOAL**.

## Purpose

Develop the M4B paper paging/sub-entry candidate and Weight Segmentation ahead of the authoritative C4 review, in a fully isolated lineage. The user accepts that candidate runs may be rerun or revised later.

## Isolation

Recommended:

- Framework branch/worktree: `hrl/vm-m4b-speculative-v0` / `/workspace/worktrees/accel-sim-vm-m4b-speculative`
- Core branch/worktree: `hrl/vm-m4b-speculative-v0` / `/workspace/worktrees/gpgpu-sim-vm-m4b-speculative`
- Scratch: `/workspace/vm-m4b-speculative/`

Core starts exactly from `0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd`.

Framework may start from the current parallel coordination handoff head; record the exact docs-only delta from `a7c0759...`.

Never touch Window A worktrees, active C3/C4 scratch, supervisor, formal binary, or manifests. Never merge C into A automatically.

## C0 — admission and baseline reproduction

1. Create fresh branches/worktrees/build roots.
2. Read the existing M4B spec and authorized addendum.
3. Cold build the accepted standard VM baseline in the C worktree.
4. Run M1-M3 directed regressions plus M4C object/telemetry regression subset sufficient to prove the branch point is healthy.
5. Bind simulator binary/runtime SHA and a small accepted real-trace smoke.

Acceptance: standard mode matches expected baseline behavior before mechanism changes.

## C1 — targeted paper/reference audit

Before coding sub-entry behavior, inspect:

- tracked `SEGMENTATION_LLM_2026.md` and evidence ledgers;
- locally available target-paper/reference material;
- current GPGPU-Sim/Accel-Sim source;
- public author/reference artifacts when network is available;
- target/reference [4] identity/source when resolvable.

Freeze an evidence table for:

- subentries/group;
- alignment/coverage;
- tag/index/set semantics;
- fill behavior;
- partial-valid semantics;
- replacement granularity/LRU;
- latency/ports;
- 2MB interaction.

Do not search indefinitely. If stronger exact/reference-backed semantics remain unavailable after targeted evidence collection and no conflicting evidence exists, select the already authorized `REFERENCE_APPROX_SUBENTRY_16` and continue. This is an expected fallback, not a hard stop.

If stronger evidence materially conflicts with the fallback, use the stronger evidence and document the change. Stop only if the conflict makes the intended mechanism genuinely ambiguous and cannot be represented without inventing semantics.

## C2 — L2-TLB sub-entry candidate

Implement a separable mode:

- standard L2 TLB remains unchanged;
- candidate sub-entry mode follows the accepted evidence or `REFERENCE_APPROX_SUBENTRY_16`;
- L1 TLB remains conventional;
- existing VM/MSHR/PTW/PWC semantics remain unchanged outside L2 lookup/fill grouping.

Required candidate stats include full hit, base-tag/subentry miss, base-tag miss, existing-group fill, new-group fill, group eviction, valid-subentries evicted, group/subentry occupancy, object occupancy when available.

Pass every directed test in `WINDOW_C_VALIDATION_CONTRACT.md` and standard-mode regressions before C3.

## C3 — Weight Segmentation candidate

Implement the paper mechanism as an explicit parallel Segment + L1 lookup state machine using the frozen Weight descriptor source.

Required semantics:

- segment and L1 launch together;
- default segment service latency equals accepted L1 lookup latency unless stronger evidence is found;
- segment hit masks/discards the conventional L1 result;
- segment hit launches no L2/MSHR/PWQ/walker/PWC/PTE work;
- segment hit fills no conventional L1/L2 TLB Weight translation;
- segment miss reuses the already-completed L1 result and never re-probes L1;
- non-weight accesses remain on the chosen paging candidate;
- data side effects occur exactly once.

Keep mechanism stats compatible with the M4C memory-hierarchy telemetry or introduce an explicitly versioned backward-compatible extension.

Pass all directed tests in `WINDOW_C_VALIDATION_CONTRACT.md` before real-trace replay.

## C4 — bounded real-trace validation

Use immutable accepted prefill/decode1 traces, but keep evidence speculative.

Run a bounded matrix on representative early/mid/heavy kernels without breaking intra-run state when multiple sequential kernels are selected:

- standard paging baseline;
- sub-entry paging candidate;
- sub-entry + Weight Segmentation;
- ideal translation diagnostic where useful.

Prove on real traces:

- Weight segment coverage is as expected from the frozen descriptor;
- segment-hit Weight accesses create zero downstream conventional L2/MSHR/PTW/PTE work;
- KV/UNKNOWN continue paging;
- non-weight behavior remains equivalent apart from secondary capacity effects after Weight translations no longer occupy TLB state;
- PTE/waiter/object conservation PASS.

Automatically investigate/fix implementation errors and rerun bounded tests. Do not stop for ordinary bugs.

## C5 — optional full speculative candidate runs

After C4 passes and farm resources are healthy, run continuous full ROI candidate comparisons for both prefill and decode1:

1. selected sub-entry paging candidate;
2. sub-entry + Weight Segmentation;
3. ideal translation diagnostic when practical.

These are `SPECULATIVE_CANDIDATE`, not formal M4B results. Keep the same trace policy/page size/platform parameters within each comparison and change only the intended mechanism/config.

If full prefill is expensive, launch it in parallel with decode1 subject to resource policy; never split an ROI into independent kernel simulators and add results.

## C6 — speculative closeout

Create `docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/` containing at least:

- `PAPER_SUBENTRY_EVIDENCE_LEDGER.tsv`
- `SOURCE_ANCHORS.md`
- `CHANGED_FILES.md`
- `STANDARD_MODE_REGRESSION.md`
- `SUBENTRY_DIRECTED_TESTS.md`
- `SEGMENTATION_DIRECTED_TESTS.md`
- `BOUNDED_REAL_TRACE_VALIDATION.tsv`
- `FULL_SPECULATIVE_RUNS.tsv` if run
- `MECHANISM_STATS.tsv`
- `TELEMETRY_COMPATIBILITY.md`
- `SPECULATIVE_FINDINGS.md`
- `OPEN_ISSUES.md`
- raw-log index with paths/hashes

Push C Framework/Core branches and STOP before synthetic KV/M5. Do not merge into A.

## Problem-solving policy

Ordinary implementation/build/test/replay failures are expected engineering work. Diagnose the root cause, reduce to a directed test, fix, rerun regressions, and continue. Do not abandon the Goal because the first implementation is wrong. Stop only for a hard semantic/provenance conflict, cross-window contamination, or an unresolvable evidence ambiguity that would require inventing material mechanism semantics.
