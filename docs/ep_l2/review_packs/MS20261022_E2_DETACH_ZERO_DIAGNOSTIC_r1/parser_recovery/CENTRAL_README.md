# Minimal original-central parser engineering revalidation candidate

**Not installed or activated.** Actual E051_c0185b56 is FAILED, actual_starts51. Its original run_status, raw, parser.log, input_spec, Q and durable native receipts remain byte-for-byte retained. The new native simulation does not need repeating for a terminal decoder engineering error.

## Existing API findings

- Original `Coordinator.resolve_scientific_hold` (production coordinator.py:565) only appends explicit evidence resolution history and removes the active matching qualification HOLD. Its own comment says this cannot accept old failed results.
- Original `finish_application` (:718) requires RUNNING and cannot safely finish this already FAILED endpoint again. Do not call it, rewrite state to RUNNING, or edit run_status.
- Original observer Authority only permits accepted_results from COMPLETE_VALID tail. That precise guard requires a narrow source-bound supplement, rather than a replacement application or broad qualification waiver.

## Patch

`MINIMAL_CENTRAL_PATCH.diff` contains:

1. New `detach_parser_recovery.py` with `FINAL_RECOVERY_REF=None` by default, so production refuses any attempt until root seals one exact actual supplemental review manifest in source. It has **no execution, reservation, controller, build, process or Q registration API**.
2. `detach_scope_core.Authority.active` adds only `parser_recovery.allowed_revalidated_results(item)` to allowed accepted IDs. This permits the one sealed E051 diagnostic result while preserving original FAILED attempt/canonical execution state and all existing original Authority constraints.
3. Original `Coordinator.append_observer_parser_revalidation()` invokes the supplemental checker under the existing `locked()` transaction. It appends supplemental history and an explicit diagnostic accepted_results pointer, with `acceptance_basis=PARSER_ENGINEERING_SUPPLEMENTAL_REVALIDATION` and `original_execution_status=FAILED`. The original raw/status/spec/Q/canonical run/actual-start history are untouched. It never produces a pair.

The module is a central **receipt-binding guard**, not a terminal decoder. Root must first actually rerun the repaired parser/independent validation against original raw and close full instructions, all64 slices, resources/hardware retirement, same source/config/input, actual durable wait0/exit0 and positive RO scope. Passing synthetic metadata controls is not scientific acceptance.

## Exact safe order

1. Preserve original failed artifacts and HOLD receipt. Implement repaired decoder/parser as **new distinct files**. Do not overwrite original decoder/parser/schema paths pinned by original Q/Authority. Otherwise original content_refs and Q.validation_scope change and the original run identity cannot close. New runtime core/main/archive/config/input are unnecessary and unauthorized.
2. Root independently validates the complete original raw with the fixed decoder and all original applicable terminal gates. Validate original durable four-document closure against the **original spec/Q IDs**, not a fabricated replacement Q. Reuse old original input provenance limits. Produce a new supplemental review/summary/audit at a new path, with exact source/schema/decoder/control/revalidation evidence refs. Keep all negative and original failed logs.
3. Fill `RECOVERY_MANIFEST_TEMPLATE_NOT_SEALED.json` with actual reviewed new evidence and the exact supplemental review; set status `E_SOURCE_BOUND_SUPPLEMENTAL_REVIEW_SEALED` only after full independent PASS. The template already has the real frozen51 attempt/Q/pair/workload/canonical and old accepted result fingerprints, but it has **no valid supplemental review** and cannot activate. It records old raw SHA from canonical evidence; this child did not read raw/trace. Root terminal audit must independently verify actual raw bytes.
4. Bind the actual manifest path/SHA into the one new helper source constant, publish/read back reviewed source and new evidence, update the complete original CLIENT source manifest at source-switch quiescence (including new helper). No second controller is created or needed. Keep all old source hashes/qualification files as historical evidence.
5. Use original `resolve_scientific_hold(original_qid, exact_resolution_review_path)` only after actual complete revalidation PASS. Match original hold_at_unix; resolution evidence pins the corrected parser/source controls and full audit. This preserves old HOLD in history; no attempts are refunded and consumed batch still cannot launch again.
6. `Coordinator().append_observer_parser_revalidation()` appends the exact supplemental result. It requires controller STOPPED, actual51, all old attempts/Q/pairs/workload frozen, unchanged canonical FAILED row, same original spec/native processes/raw/Q/receipt, no active matching HOLD and all full terminal closure flags. A repeated identical append is idempotent. Core/canonical regular checks still run under original lock. **Do not invoke controller.py, register a new Q, reserve or start anything.**
7. Deliver D the explicit supplemental diagnostic accepted result and its original FAILED provenance, corrected counter summary and source/schema identities. This is one point, never an S/F CURRENT_ACCEPTED_PAIR.

## Validation

`python3 test_metadata_recovery.py`: **9/9 PASS**. Controls use a read-only deep copy of actual51 metadata and actual small old receipts, plus clearly marked SYNTHETIC supplemental metadata with the manifest resolver and new execution/engineering checks patched in memory to isolate the original nine metadata controls. Production default-unbound and synthetic-manifest rejection are tested. No raw/trace/main/archive is read; no native/application/build/process is run; no actual registry/CLIENT/runtime is changed.

Controls cover original unresolved HOLD, missing full64 closure, false count refund, changed old attempt, changed canonical FAILED state, wrong raw identity and success/idempotence preserving all original FAILED/51 evidence. These controls are central receipt-binding engineering checks, not a claim that actual E051 terminal revalidation has passed.


## Root-requested append hardening (implemented)

Only `append` now streams the actual original raw (exact path, **11,981,308** recorded bytes, max384MiB, exact prior failed receipt+manifest SHA), checks original native/guardian PID+start_ticks+boot identity is no longer alive, and loads all four original small durable refs. It invokes the exact original `detach_validation.validate_native_documents` (sourceSHA93466c…) against original spec/input_audit, covering REQUEST/READY/RELEASE/EXIT one-to-one closure. Normal active/snapshot checks do **not** rehash raw.

`engineering_bindings` must pin fixed decoder647510163053d30773176578cf35c10e0aea0a1256af366feba520820d0e11d4, the unchanged original legacy parser/schema, original durable validator, new complete normalized terminal summary and E independent validation report. The latter must have `synthetic_fixture:false`, `status:PASS`, `validation.status:PASS`, original `identity`, `qualification_id`, `raw_log_sha256`, and exact `terminal_summary_ref`, `fixed_decoder_ref`, `legacy_parser_ref`. The supplemental receipt additionally binds `terminal_summary_ref` and `independent_validation_ref`. An arbitrary closure bool cannot replace these source-bound artifacts and original execution truth checks.

The complete summary must contain exact1658916864 instructions, positive cycles, REAL_UNACCEPTED decoder scope, exact64 slice IDs, exact212 unchanged schema fields, nonnegative integer counters and per-field GLOBAL=sum64 rollup. Missing slices/counters, source/schema substitutions and synthetic validation proofs fail.

`test_append_truth.py`: **7/7 additional PASS**. Raw stream/cap/live-process negatives use tiny tmp fixture bytes only; real E051 raw was **not read** by this agent. Original four **small actual metadata** documents genuinely pass the existing original validator. Wrong durable ref, missing64 membership, missing per-slice counter and synthetic proof are rejected. Old9 remain PASS separately. This still makes no actual full terminal scientific acceptance claim; root is performing the repaired-parser raw revalidation.

The template now supplies actual raw path/stat size and the four small native refs plus actual source bindings; actual new summary and E validation refs remain null. It remains NOT_SEALED and production is unbound until root seals the actual independent result. No new launch, retry or replacement-Q entrance was added.
