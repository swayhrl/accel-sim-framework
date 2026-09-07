# Window A — C3 terminal -> C4 finalization handoff

Goal: `A_C3_TERMINAL_TO_C4_FINALIZE`

Status: `PREPARED / SELF-GATED / DO_NOT_RUN_BEFORE_C3_TERMINAL`.

This handoff is preparation only. It must not disturb the currently running C3 `prefill-paper` process. No new simulator workload is authorized by this document.

## Authoritative inputs

- A formal Framework branch: `hrl/vm-llm-m4b-v0`, frozen run-side Framework provenance as recorded per arm.
- A progress-review branch: `hrl/vm-llm-m4b-c3-progress-review-20260907`.
- Existing nonterminal checkpoint: `73d25ebbdd96833ee1ddb8ea42b9017cefbceb75`.
- Existing early-C4 checkpoint: `2e491abec2afb0c745ca26aae0d86f8f35ad096b`.
- Existing C3 run root: `/workspace/m4c-c3-formal-20260905-v1`.

The early-C4 pack already established schema/provenance preflight for seven terminal arms. `prefill-paper` must remain excluded until the strict terminal gate below passes.

## Gate 0 — do nothing while C3 is nonterminal

Do not execute finalization unless all eight arms satisfy all of:

1. `simulator_exit_status == 0`;
2. `Processing kernel` count equals immutable expected-kernel count;
3. `m4c_telemetry_schema` record count equals the same expected count;
4. generic/paper VM conservation checks required by `summarize_m4c_runs.py` pass;
5. no active C3 simulator remains for the just-completed arm and the supervisor has reached its normal terminal state.

For `prefill-paper`, expected count is 692.

Before terminal, only read-only liveness monitoring is allowed. Do not emit the attestation described below.

## Stage 1 — formal C3 8/8 closeout

Once Gate 0 passes naturally:

1. Run the existing formal summarizer on the complete C3 run root using a fresh output path. Do not overwrite prior evidence.
2. Verify eight rows are PASS and preserve each arm's original Framework/Core/binary/runtime/trace-list provenance exactly; do not silently normalize the known `7709376...` -> `a7c0759...` Framework split.
3. Verify no duplicate/missing telemetry or terminal marker anomalies.
4. Generate a final `C3_FINAL_ARM_MATRIX.tsv` and `C3_FINAL_PROVENANCE.tsv` in a new final closeout pack.
5. Mark `C3_FINAL_STATUS = TERMINAL_PASS` only after all checks pass.

If any arm fails the terminal/conservation/provenance gate, STOP before issuing any downstream attestation. Do not rerun automatically.

## Stage 2 — export the eighth arm and finalize C4 inputs

After C3 TERMINAL_PASS:

1. Export `prefill-paper` with the same `export_m4c_telemetry.py` schema used by the seven early arms.
2. Validate all 11 expected outputs plus `TELEMETRY_SCHEMA.md` against its manifest/provenance.
3. Reuse the seven already-exported terminal arms; do not regenerate them unless a provenance mismatch is found.
4. Build one immutable 8-arm C4 input manifest mapping every arm to its log, export directory, Framework/Core SHA, binary/runtime SHA, trace-list SHA, profile and ROI.

## Stage 3 — complete C4 analysis

The early pack `C4_EARLY_ANALYSIS_PREP` is the starting point, not a final result.

Complete:

- prefill disabled/ideal/generic/paper four-profile comparison;
- decode four-profile comparison, preserving the early observation that paper has lower TLB/MSHR-full counters yet higher cycles than generic;
- full existing structured-export aggregation across object VM, L1D, L2, replacement, queue, DRAM and cross-layer outcomes;
- exact offline immutable-trace locality/footprint/hotness/overlap analysis using `analyze_m4c_trace_locality.py`, only after C3 is terminal and resource gate is healthy;
- explicit separation of `OBSERVED_TERMINAL_FACT`, `SUPPORTED_MECHANISM_SIGNAL`, `C4_OBSERVABILITY_GAP`, and paper-reference comparison.

Do not invent object-specific DRAM channel/bank/row attribution where the telemetry does not contain it. Preserve every gap already listed in `C4_EARLY_ANALYSIS_PREP/OBSERVABILITY_GAPS.md` unless new existing evidence actually closes it.

No simulator replay is required for C4 finalization. If a missing conclusion would require new telemetry/replay, record the minimum follow-up experiment rather than modifying completed C3 evidence.

## Stage 4 — resource release and downstream attestation

Only after C3 8/8 terminal closeout succeeds:

1. Capture a host resource snapshot: `MemAvailable`, `SwapFree`, swap-in/out delta over a short window, CPU iowait, and whether the C3 simulator/supervisor has released its heavy resources.
2. Do not claim resources are healthy merely because C3 ended; B/C still apply their own independent resource gates.
3. Create a plain-text attestation file at:

`/workspace/m4c-c3-formal-20260905-v1/A_TERMINAL_ATTESTATION.txt`

Its first line must be exactly:

`A_TERMINAL_CONFIRMED`

Additional lines may record final A review commit, C3 final status, timestamp, eight-arm count and provenance hash, but the first exact line is required by Window B's prepared runner.

The attestation certifies only that A's simulator-heavy C3 workload is terminal and formal terminal gates passed. It does not certify that host memory/swap is healthy for new jobs.

## Stage 5 — final review pack / commit

Create a final pack such as:

`docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT/`

At minimum include:

- `C3_FINAL_ARM_MATRIX.tsv`
- `C3_FINAL_PROVENANCE.tsv`
- `PREFILL_FINAL_PROFILE_COMPARISON.tsv`
- `DECODE_FINAL_PROFILE_COMPARISON.tsv`
- `C4_CROSS_LAYER_SUMMARY.tsv`
- `C4_TRACE_LOCALITY_SUMMARY.tsv`
- `C4_OBSERVABILITY_GAPS.md`
- `RESOURCE_RELEASE_SNAPSHOT.tsv`
- `A_TERMINAL_ATTESTATION_RECORD.md`
- `FINAL_REPORT.md`

Commit/push only small review artifacts/scripts; never commit raw large logs, traces or simulator binaries.

## Downstream behavior

After the attestation exists:

- Window B may execute its already-prepared B9 E01-E10 runner only with its own resource gate.
- Window C may begin the separately prepared C10-B build/runtime validation only with its own resource gate.
- Window A may finish C4 final analysis offline, but must not start M4B/C5/M5 or a new simulator-heavy workload unless separately authorized.

## Failure policy

Ordinary parser/export/analysis issues: debug and repair analysis tooling without changing completed simulator evidence.

STOP and report if:

- any of the eight terminal gates fail;
- provenance cannot be closed;
- a completed run appears corrupt;
- fixing the issue would require rerunning or changing C3 simulator semantics.

Do not emit `A_TERMINAL_CONFIRMED` in any STOP case.