# CODEX GOAL — C16 Qwen3-8B Unattended Campaign V12 (node109) — DRAFT

Status: `DRAFT_PENDING_174NEW_V12_AUTHORITY`.

Do not execute this draft yet. The final version will bind exact 174-new V12 hashes and then be run as one multi-hour GOAL MODE task.

Suggested execution branch:
`hrl/c16-qwen3-8b-unattended-campaign-109-v12`

Expected review pack:
`docs/vm_tlb/review_packs/C16_QWEN3_8B_UNATTENDED_CAMPAIGN_109_V12/`

Base:
- V11 branch `hrl/c16-next-lineage-campaign-framework-109-v11`
- V11 HEAD `d7f5ad2c06831193113401b688711be80058cd00`
- Qwen3 exact revision `b968826d9c46dd6066d109eabc6255188de91218`

Read first:
- `CURRENT_SCOPE_AND_GATES.md`
- `QWEN3_UNATTENDED_STAGE_CONTRACT_DRAFT.json`
- final 174-new V12 authorization files after this handoff is finalized.

## Goal

Upgrade the V11 plan/resume scaffold into a real scientific executor and, in the same Goal, run the authorized Qwen3-8B campaign through S2 census, semantic target binding, exact state capture, replay/signature equivalence, fresh path audit, formal capture, serial admission/ACK, NCU and review-pack closure.

Do not stop after framework implementation. Continue automatically while all gates PASS. Stop only on campaign completion or a defined fail-closed condition.

## P0 — Final authority binding

The final handoff will replace:
- `PENDING_174NEW_V12_HEAD`
- `PENDING_AUTHORIZATION_SHA256`
- `PENDING_V2_VALIDATION_SHA256`
- `PENDING_QWEN3_S2_SEQUENCE_SHA256`
- `PENDING_QWEN3_S2_PAYLOAD_SHA256`
- `PENDING_EXECUTION_MODE_POLICY`
- `PENDING_TARGET_POLICY`
- `PENDING_S3_POLICY`

Before Qwen3 execution, verify the final 174-new decision is PASS and hash-bind the exact authorization/input authority into `AUTHORITY_BINDING.json`. Missing or mismatched authority -> BLOCKED before GPU work.

## P1 — Make V11 a real executor

The current V11 driver may emit `FRAMEWORK_ONLY` PASS. Remove that ambiguity.

Required executor changes:
1. Scientific PASS requires a real stage executor plus executable validators. `FRAMEWORK_ONLY`, `PLAN_ONLY`, `DRY_RUN`, mock/synthetic evidence cannot PASS.
2. Replace overwrite-style stage receipts with immutable attempt namespaces. A retry creates a new attempt; previous terminal evidence is preserved.
3. Resume only across a contiguous hash-valid dependency chain. Revalidate artifact hashes, dependency hashes and semantic input digests for every completed stage.
4. Any upstream semantic change invalidates downstream reuse. Do not silently continue from a stale higher-numbered PASS.
5. Treat SKIPPED as complete only when the bound authorization explicitly makes that stage not applicable.
6. SIGINT/SIGTERM/process interruption may leave RUNNING/PARTIAL evidence but never a false PASS.
7. Keep a per-campaign process lock and add a separate global formal-admission lock.
8. Make formal capture shard-resumable: deterministic shard IDs, immutable shard receipts, completed valid shards are not repeated.
9. Every fallback has a finite budget. Exhaustion emits BLOCKED with attempted methods/evidence/unblock condition.

## P2 — Executor self-test before Qwen3

Use accepted Qwen2.5 V10 evidence read-only. No new Qwen2 formal admission.

Required positive/negative regression:
- accepted matched semantic pair -> ACCEPT;
- token mutation -> REJECT;
- semantic/shape mutation -> REJECT;
- missing/invalid ACK -> REJECT.

Add executor-integrity tests:
- changed upstream semantic digest invalidates downstream resume;
- fake `FRAMEWORK_ONLY PASS` is rejected;
- non-contiguous stage chain is rejected;
- changed static-set SHA invalidates downstream formal/NCU evidence;
- second admission while ACK unresolved is rejected;
- `.partial` interrupted shard is not complete.

Generate `EXECUTOR_SELFTEST.tsv` from executed tests. Any failure -> `BLOCKED_EXECUTOR_SELFTEST`, commit/push and STOP.

## P3 — Asset/environment/input preflight

Verify exact Qwen3 model/revision/assets locally. No same-name different-revision fallback.

Record GPU, driver, CUDA, Python, torch, transformers/runtime source identity, NVBit/tool build, NSYS/NCU, compilers where relevant, staging paths and free-space evidence.

Resolve the V11 Qwen3 runtime class/API gap using approved/hash-closed local environment assets. Do not opportunistically install an arbitrary latest package from the network during scientific execution.

Follow the final V12 execution-mode policy exactly. Expected pattern:
- use full-resident BF16 only if proven feasible and authorized;
- otherwise use only explicitly authorized exact semantic layer streaming/replay;
- lack of full residency alone is not failure;
- precision, model, backend or synthetic-state substitution is forbidden.

Verify exact V2 S2 input token-for-token. Keep canonical token-sequence SHA and serialized payload SHA as distinct typed fields.

## P4 — S2 execution smoke and kernel census

S2 baseline is expected to be `S2_TEXT_B1_T2048_D32`, subject to final authorization.

If full-resident mode applies, run a bounded exact native smoke. If the authorization explicitly declares native full-resident not applicable, record an authorized SKIPPED native-smoke receipt and run a bounded exact streamed-execution smoke instead.

Then perform a bounded S2 kernel census with synchronized semantic module/range evidence and profiler support. Produce:
- `KERNEL_CENSUS.tsv`
- `IMPLEMENTATION_CLASSES.tsv`
- profiler artifact manifest.

Do not select a target before the census. Do not infer layer/module from launch order.

Semantic correlation gets at most two bounded methods. Still ambiguous -> BLOCKED.

## P5 — Semantic target selection

Generate `SEMANTIC_CANDIDATES.tsv` from observed Qwen3 implementation evidence, then apply the final 174-new authorization.

Draft preference, pending final V12:
- one decode MLP linear anchor for lineage continuity if losslessly bindable;
- at most one attention/KV target if materially distinct and scientifically useful.

Every selected target must bind exact scenario, phase, layer, semantic role, execution point, shape and observed implementation signature. Do not substitute another operator merely to keep the campaign moving.

Produce `TARGET_SELECTION.json` binding candidate-table SHA and authorization SHA.

## P6 — Exact state capture, replay and signature gates

For each selected target, preserve the existing Qwen3 replay contract:
- exact layer weights;
- exact incoming hidden state;
- exact position/attention state;
- exact layer-local KV state;
- exact runtime deployment identity.

In streamed mode, reconstruct state by executing exact model semantics; synthetic hidden states are forbidden.

Replay equivalence policy:
1. establish same-method repeatability first;
2. require bitwise equivalence if deterministic;
3. if genuine same-method nondeterminism exists, pre-freeze a tight tolerance from that control evidence before evaluating replay;
4. no post-hoc loose tolerance.

After output equivalence, prove in-context vs replay kernel-signature equivalence. Output match alone is insufficient. Signature isolation gets at most two bounded methods. Failure -> BLOCKED.

## P7 — Fresh static global-address-path audit

Audit the exact qualified Qwen3 target implementation. Never reuse Qwen2 static PCs/counts.

For each target:
- enumerate direct GLOBAL MREF;
- audit LDGSTS operand semantics and GLOBAL_SOURCE separately;
- treat LDGDEPBAR as control-only;
- detect any other address-bearing global path;
- prove `EXECUTED + ZERO_EXECUTION_PROVEN = complete static set` for each path class.

A newly observed address-bearing path not covered by the tracer blocks formalization until explicitly supported.

Hash-bind SASS, static sets and instrumentation build. Any later implementation change invalidates dependent formal/NCU evidence.

## P8 — Formal capture and serial admission

Only qualified targets may enter formal capture.

Requirements:
- exact authorized runtime/input/target;
- same-process address context;
- deterministic resumable shards;
- `.partial` while writing, verified final artifact on close;
- terminal/static-PC/path checks;
- drop=0, overflow=0;
- no unexpected static path/ID.

Promote object roles only from direct same-process storage/range identity; otherwise retain `UNKNOWN_RUNTIME`.

Formal admission is strictly serial: acquire the global lock, admit one completed target, wait for accepted hash-bound ACK, then and only then allow another admission. ACK failure/timeout -> BLOCKED; never admit concurrently.

No accepted historical raw/catalog mutation.

## P9 — NCU and compact memory fingerprint

Collect application-context NCU for the exact qualified target implementation. Preserve numeric values together with metric names, explicit units, NCU version, replay/application mode, cache-control mode and report hashes.

At minimum retain the accepted traffic family when available:
- `l1tex__t_bytes`
- `lts__t_bytes`
- `dram__bytes`

Do not infer units or whole-model temporal history.

Produce a compact per-target memory fingerprint including only supported fields: semantic identity, execution mode, kernel signature, static path-set sizes, executed/zero partition, active-lane event counts by path, supported page/line footprint metrics, same-process object composition with explicit UNKNOWN, NCU metrics/units, run/catalog/ACK identities.

Do not invent cross-path chronology, global reuse distance or full-model cache/TLB behavior.

## P10 — Conditional S3

Evaluate S3 only after S2 closes and according to final V12 policy.

Expected candidate scenario: `S3_TEXT_B1_T8192_D16`.

Run only if authorized, feasible under the same scientific execution constraints and materially informative. If run, give S3 its own input authority and hash-valid stage chain; do not reuse S2 dynamic receipts/static sets unless exact implementation identity is re-proven.

If not run, record an explicit reason such as `SKIPPED_BY_AUTHORIZATION`, `NOT_MATERIALLY_INFORMATIVE`, `INFEASIBLE_UNDER_AUTHORIZED_MODE`, or `BLOCKED_<gate>`.

## P11 — Review-pack closure

Create `docs/vm_tlb/review_packs/C16_QWEN3_8B_UNATTENDED_CAMPAIGN_109_V12/` with at least:
- `FINAL_DECISION.json`
- `AUTHORITY_BINDING.json`
- `EXECUTOR_SELFTEST.tsv`
- execution stage/decision policy actually used
- environment/execution-mode/input receipts
- census/implementation/candidate/target-selection artifacts
- per-target state/equivalence/signature/static-audit/capture/ACK/NCU evidence
- per-target compact memory fingerprint
- `S3_CONTINUATION_DECISION.json`
- receipt index with hashes
- `OPEN_ISSUES.md`
- `SHA256SUMS`.

Run executable review-pack validation. No handwritten PASS rows.

Allowed decisions:
- `C16_QWEN3_8B_UNATTENDED_CAMPAIGN_109_V12_PASS`
- `C16_QWEN3_8B_UNATTENDED_CAMPAIGN_109_V12_PASS_WITH_SCOPED_EVIDENCE`
- `C16_QWEN3_8B_UNATTENDED_CAMPAIGN_109_V12_BLOCKED_<specific_gate>`

A BLOCKED outcome with complete preserved evidence is valid. Never change model, input, precision, backend or semantic target just to obtain PASS.

## Immutable STOP conditions

Stop safely if any required authority/hash mismatches; executor self-test fails; exact runtime cannot execute under the authorized environment; exact state reconstruction fails; replay equivalence fails; signature isolation fails after bounded methods; new address-bearing path lacks coverage; static closure fails; drop/overflow is nonzero; runtime/input/implementation identity drifts after qualification; ACK fails/remains unresolved; required NCU semantics cannot be established; storage failure risks evidence integrity; or continuing requires semantic/configuration substitution.

On STOP: preserve valid and partial evidence separately, emit an exact BLOCKED receipt, build the valid portion of the review pack, hash-close it, commit/push and STOP. Do not improvise a new experiment.

## Forbidden claims/non-goals

No Qwen3-30B, no DeepSeek execution, no Qwen2 formal recapture, no launch-order semantic inference, no cross-process absolute-VA comparison, no cross-shard/global direct+LDGSTS chronology, no global reuse-distance claim from independent shards, no claim that shard order is L2 arrival order, no full-model cache/TLB claim from one streamed semantic target, and no description of streamed execution as full-resident native deployment.

After finalization, run this as one continuous/resumable Goal: do not stop after framework preparation; continue through Qwen3 until PASS/scoped completion or an explicit fail-closed STOP.