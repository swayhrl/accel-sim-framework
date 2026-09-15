# CODEX GOAL — C16 Next-Lineage Campaign Framework V11 (node109)

## Mission

Convert the successful but incrementally accumulated Qwen2.5-7B V5–V10 campaign into a reusable, resumable, fail-closed framework for future model lineages, especially Qwen3-8B.

This is NOT a new Qwen3 formal campaign. This is framework extraction + golden regression + Qwen3 plan-only readiness.

Base: `57ca798c851a3b9d4a2c787c01f4e2b3a16fcdea`

Suggested execution branch:

`hrl/c16-next-lineage-campaign-framework-109-v11`

Expected review pack:

`docs/vm_tlb/review_packs/C16_NEXT_LINEAGE_CAMPAIGN_FRAMEWORK_109_V11/`

---

## P0 — Mine the Qwen2.5 lessons into a machine-readable failure-mode catalog

Read the relevant Qwen2.5 V5–V10 handoffs, scripts and review packs. Do not merely summarize prose. Build:

`FAILURE_MODE_CATALOG.tsv`

with at least:

- failure_id
- stage
- symptom
- root_cause
- evidence_that_exposed_it
- incorrect_shortcut_to_forbid
- reusable_detection_gate
- bounded_fix_or_fallback
- stop_condition
- generalizable_to_next_lineage

At minimum encode the following learned classes where supported by existing evidence:

1. formal catalog/raw `.partial` concurrency race → serial admission only;
2. hash semantic ambiguity: raw file hash vs canonical token-sequence hash vs historical payload receipt;
3. source-text authority gap and prohibition on reverse-decoding tokens to invent source;
4. custom tokenizer implementation is not canonical tokenizer validation;
5. old AWQ function-level target could not be uniquely joined to a semantic WQLinear module;
6. launch-order inference is forbidden for semantic binding;
7. module replay output equivalence alone is insufficient without in-context vs replay kernel-signature equivalence;
8. old static SASS set cannot be reused when the actual replay kernel implementation changes;
9. LDGSTS GLOBAL_SOURCE must be audited separately from direct GLOBAL MREF; LDGDEPBAR is control-only;
10. `EXECUTED + ZERO_EXECUTION_PROVEN = complete static set` is required for set-level closure;
11. same-process ADDRESS_CONTEXT is required for object attribution; otherwise retain `UNKNOWN_RUNTIME`;
12. cross-process absolute VA, cross-shard chronology and reuse-distance claims are prohibited;
13. NCU display values must not be called bytes unless unit semantics are explicit;
14. application-context NCU is cache-counter evidence, not global full-model temporal history;
15. deployment-state divergence means matched semantic operator comparison is not a pure single-variable quantization causal experiment;
16. hard-coded PASS/test rows are forbidden; gates must be executable;
17. full-model loading may be unnecessary: selective layer streaming + exact state replay can be the correct capacity strategy;
18. Qwen2-specific class assumptions/hard-coded deployment enums in legacy `formal_runtime.py` must not become the next-lineage interface.

If an item above is not supported by repository evidence, mark it `NOT_CONFIRMED` rather than inventing details.

Also produce a short human-readable:

`QWEN25_CAMPAIGN_LESSONS.md`

organized by campaign stage, not by historical version number.

---

## P1 — Define a reusable campaign state machine

Implement a generic campaign state machine under a NEW reusable directory, for example:

`util/vm_tlb/c16/campaign/`

Do not delete or rewrite historical versioned scripts.

Required stages:

1. `ASSET_AUTHORITY`
2. `ENVIRONMENT_PREFLIGHT`
3. `INPUT_AUTHORITY`
4. `NATIVE_SMOKE`
5. `KERNEL_CENSUS`
6. `SEMANTIC_TARGET_SELECTION`
7. `SELECTIVE_STATE_CAPTURE`
8. `REPLAY_EQUIVALENCE`
9. `IN_CONTEXT_SIGNATURE_GATE`
10. `FRESH_STATIC_PATH_AUDIT`
11. `FORMAL_CAPTURE`
12. `FORMAL_ADMISSION_ACK`
13. `NCU_PROFILE`
14. `REVIEW_PACK_CLOSE`

For every stage, emit a deterministic JSON receipt containing at least:

- campaign_id
- model_id / revision
- scenario / phase
- stage
- status = PASS | BLOCKED | SKIPPED | FAIL
- inputs and SHA256s
- output artifact paths and SHA256s
- exact command/argv or normalized invocation descriptor
- environment identity if relevant
- dependency stage receipts
- timestamp only as metadata, never as semantic identity
- next_stage

State transitions must be explicit and fail closed.

A failure must NOT result in repeated blind retries. Produce `BLOCKED.json` with:

- exact failing gate
- already-attempted bounded methods
- evidence paths
- what external/new fact would unblock it

Then stop.

---

## P2 — Make execution resumable and suitable for unattended multi-hour runs

Provide one top-level driver, for example:

`python util/vm_tlb/c16/campaign/driver.py --campaign <json> --resume`

or equivalent.

Requirements:

- resume from the last hash-valid PASS stage;
- do not re-run an expensive PASS stage merely because the process restarted;
- invalidate downstream stages when an upstream semantic input/hash changes;
- process lock to prevent two drivers operating on the same campaign;
- explicit global formal-admission lock honoring `FORMAL_ADMISSION_CONCURRENCY=1`;
- disk-space preflight for node109 before large captures;
- GPU identity/environment receipt;
- deterministic stage log paths;
- bounded ACK wait/poll policy; on unresolved ACK, write BLOCKED and stop rather than concurrently admitting another run;
- SIGTERM/interruption should leave resumable state, never a partially claimed PASS;
- raw output writes use `.partial` then atomic/final verified publish where applicable;
- no mutation of previously accepted raw/catalog.

Create a concise `UNATTENDED_OPERATION.md` explaining:

- how to start one long Goal;
- where to inspect current stage;
- how to resume after SSH/Codex/process interruption;
- which conditions intentionally stop the run;
- which conditions require human/scientific judgment rather than automatic continuation.

---

## P3 — Separate model-specific logic from general campaign logic

Do NOT extend the legacy hard-coded deployment enum pattern.

Define a model/deployment adapter interface driven by a machine-readable config. It must be able to express at least:

- model_id
- exact_revision
- canonical/local asset path
- architecture/model class identity
- dtype/deployment identity
- tokenizer/input authority
- layer count
- semantic module resolver
- selective layer loader/state loader
- cache/position-state requirements
- runtime backend identity
- candidate semantic roles
- object-role mapping policy

Qwen2.5 raw/AWQ can be implemented as golden fixture adapters.

Qwen3-8B gets a PLAN-ONLY adapter skeleton based only on exact already-recorded static authority:

- `Qwen/Qwen3-8B`
- revision `b968826d9c46dd6066d109eabc6255188de91218`
- 36 decoder layers
- hidden size 4096
- 32 attention heads
- 8 KV heads
- intermediate size 12288

Do not assume Qwen2 module structure beyond what exact Qwen3 local config/model implementation proves. If runtime class/API details are unavailable on node109, leave explicit unresolved gates.

Qwen3 existing planning contract remains authoritative: exact layer weights, exact incoming hidden state, position/attention state, layer-local KV state, runtime deployment identity, output equivalence, kernel-signature equivalence, and full-function global-address-path audit before formal capture.

---

## P4 — Golden regression on the already successful Qwen2.5 V10 evidence

The framework is not accepted merely because the code looks generic.

Use existing Qwen2.5 V10 artifacts as a golden regression fixture.

At minimum prove that the new framework can ingest/validate the known V10 matched pair and reproduce, without reinterpreting semantics:

- common historical token authority;
- decode token 23578;
- layer0 `mlp.down_proj` semantic identity;
- logical shape `[1,1,18944]`;
- in-context vs dedicated replay signature gate;
- AWQ static direct set size 43, LDGSTS 0;
- RAW static direct set size 243, LDGSTS 0;
- both formal ACKs;
- pair label `MATCHED_SEMANTIC_MODULE_REPLAY_DEPLOYMENT_COMPARISON`;
- forbidden cross-deployment VA/temporal/reuse claims remain forbidden.

Important: this is primarily a read-only golden regression. Do NOT create duplicate formal admissions just to test the framework.

Where a stage requires live execution for validation, prefer a bounded dry-run/smoke mode and clearly label it `REGRESSION_ONLY_NOT_NEW_FORMAL_EVIDENCE`.

Produce:

- `GOLDEN_REGRESSION_RESULTS.tsv`
- `GOLDEN_EXPECTED.json`
- executable negative tests that mutate semantic inputs and verify fail-closed rejection.

No hard-coded test result files.

---

## P5 — Encode target-selection policy without pretending scientific judgment is fully automatic

The framework should automate mechanics but must NOT silently choose scientific targets from arbitrary heuristics.

Implement a two-layer contract:

### Mechanical candidate table

Generated from kernel census / semantic inventory with fields such as:

- semantic role
- phase
- kernel signature
- launch count / duration mass
- input/output shape
- implementation family
- whether code path is materially new
- whether special global-address paths appear
- whether exact semantic binding is available
- whether replay is feasible

### Scientific authorization

Formal tracing requires an external machine-readable authorization file specifying the chosen target(s) and rationale category.

For Qwen3, name the required gate something like:

`QWEN3_EXECUTION_AUTHORIZATION.json`

The driver MUST refuse Qwen3 `FORMAL_CAPTURE` if this authorization is absent or does not hash-bind the candidate table/model revision/input authority.

This allows 174-new V11 to finish the scientific decision before node109 commits hours of GPU tracing.

---

## P6 — Qwen3-8B plan-only campaign generation

Generate a complete PLAN-ONLY campaign for Qwen3-8B that can later be activated by adding the 174-new authorization.

It should predefine the sequence of work, NOT the unproven scientific result:

1. exact asset/runtime authority check;
2. canonical input authority check;
3. bounded native smoke;
4. S0/S2/S3 (or authorization-selected scenarios) kernel census;
5. architecture/semantic inventory;
6. candidate table;
7. target authorization gate;
8. exact selective state capture;
9. replay equivalence;
10. exact in-context signature gate using Method A first, one bounded fallback only if needed;
11. fresh SASS/global-address-path audit;
12. formal capture;
13. serial admission + ACK;
14. matched/application-context NCU where scientifically useful;
15. hash-closed review pack.

Do not start steps that require a Qwen3 execution authorization.

Produce:

- `QWEN3_8B_PLAN_ONLY_CAMPAIGN.json`
- `QWEN3_8B_UNRESOLVED_GATES.tsv`
- `QWEN3_8B_EXPECTED_ASSET_MANIFEST.tsv`

No network download and no Qwen3-30B work.

---

## P7 — Consolidate the exact learned stop/continue policy

Create `CAMPAIGN_DECISION_POLICY.json` with machine-readable rules including at least:

- semantic binding unresolved after two bounded methods → STOP/BLOCKED;
- replay output mismatch → STOP;
- in-context/replay implementation mismatch → STOP or new target classification; never silently continue;
- static path class discovered after capture design → invalidate static set and re-audit before formalization;
- drop/overflow nonzero → reject formal evidence;
- same-process context absent when object attribution is required → keep UNKNOWN, never infer;
- Pipeline ACK absent → no next formal admission;
- NCU unit semantics unresolved → retain raw displayed value, no byte conversion;
- model/input revision mismatch → invalidate downstream receipts;
- prospective and historical input axes never silently merge;
- new lineage/model implementation may not inherit Qwen2 static-set counts or semantic bindings.

---

## P8 — Review pack and decision

Review pack must include at least:

- `FINAL_DECISION.json`
- `FAILURE_MODE_CATALOG.tsv`
- `QWEN25_CAMPAIGN_LESSONS.md`
- `CAMPAIGN_STAGE_SCHEMA.json`
- `CAMPAIGN_DECISION_POLICY.json`
- `GOLDEN_EXPECTED.json`
- `GOLDEN_REGRESSION_RESULTS.tsv`
- `QWEN3_8B_PLAN_ONLY_CAMPAIGN.json`
- `QWEN3_8B_UNRESOLVED_GATES.tsv`
- `UNATTENDED_OPERATION.md`
- `SHA256SUMS`

Expected decision:

`C16_NEXT_LINEAGE_CAMPAIGN_FRAMEWORK_109_V11_PASS`

A scoped result is acceptable if exact Qwen3 runtime-specific adapter details cannot be proven locally:

`C16_NEXT_LINEAGE_CAMPAIGN_FRAMEWORK_109_V11_PASS_WITH_QWEN3_RUNTIME_GAPS`

But Qwen2 golden regression and the generic state-machine/resume/fail-closed mechanics must PASS.

## Explicit non-goals

- no Qwen3 formal GPU capture/admission;
- no new Qwen2 formal admissions;
- no modification of accepted formal raw/catalog;
- no Qwen3-30B;
- no DeepSeek execution;
- no attempt to automate scientific conclusions from one representative target;
- no invented global chronology, cross-shard ordering, or cross-process address comparison.

Commit, push, report branch/HEAD/review pack/decision, then STOP.
