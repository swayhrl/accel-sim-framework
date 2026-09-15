# C16 Qwen3-8B Unattended Campaign V12 — Draft Scope

Status: `DRAFT_PENDING_174NEW_V12_AUTHORITY`.

This draft prepares the node109 multi-hour Goal before 174-new V12 finishes. It does not authorize Qwen3 execution. Every `PENDING_174NEW_V12` field must be replaced by exact hash-bound authority before the final handoff is released.

## Mission

Use node109 V11 as the base, upgrade its plan/resume scaffold into a real executor, self-test it on the accepted Qwen2.5 V10 golden fixture, then execute the first Qwen3-8B S2 campaign under the final 174-new V12 scientific authorization. The run must be resumable, fail closed, preserve partial evidence, serialize formal admissions, and produce a hash-complete review pack.

## Fixed authorities

- node109 V11 branch: `hrl/c16-next-lineage-campaign-framework-109-v11`
- node109 V11 HEAD: `d7f5ad2c06831193113401b688711be80058cd00`
- Qwen3 model: `Qwen/Qwen3-8B`
- exact revision: `b968826d9c46dd6066d109eabc6255188de91218`
- dtype: BF16 checkpoint
- architecture: `Qwen3ForCausalLM`
- 36 layers, hidden size 4096, 32 attention heads, 8 KV heads, head dim 128, intermediate size 12288
- exact checkpoint tensor bytes: 16,381,470,720
- static decoder-layer parameter bytes: 385,892,864 per layer

The existing replay contract requires exact layer weights, incoming hidden state, position/attention state, layer-local KV state, runtime deployment identity, output equivalence, kernel-signature equivalence, and a full-function global-address-path audit before formal capture.

V11 is not yet a real scientific executor: its current driver can emit `FRAMEWORK_ONLY` PASS receipts. V12 must make that impossible before any Qwen3 scientific stage can PASS.

## Pending final authority from 174-new V12

The final handoff must bind:

- `PENDING_174NEW_V12_HEAD`
- PASS decision
- exact `QWEN3_EXECUTION_AUTHORIZATION.json` path and SHA256
- validated V2 authority identifier and validation-table SHA256
- Qwen3 S2 canonical token-sequence SHA256 and payload SHA256
- execution-mode authorization/capacity classification
- target-selection policy and maximum target count
- S3 continuation policy
- any additional V12 STOP conditions

Missing or mismatched authority stops before Qwen3 GPU work.

## Immutable scientific guardrails

1. `FORMAL_ADMISSION_CONCURRENCY = 1`.
2. No launch-order semantic inference.
3. No Qwen2 static-set or semantic-binding reuse for Qwen3.
4. Direct GLOBAL MREF and LDGSTS GLOBAL_SOURCE close independently; LDGDEPBAR is control-only.
5. A newly observed address-bearing path not covered by instrumentation blocks formalization until audited.
6. `EXECUTED + ZERO_EXECUTION_PROVEN = complete static set` is required for set-level closure.
7. Nonzero drop/overflow rejects formal evidence.
8. Object attribution requires same-process address context; otherwise keep `UNKNOWN_RUNTIME`.
9. No cross-process absolute-VA comparison.
10. No cross-shard global chronology or cross-path reuse-distance reconstruction.
11. Application-context NCU is counter evidence, not a full-model temporal history.
12. Preserve explicit NCU metric/unit semantics; never infer byte units.
13. Streamed semantic-layer replay is not a full-resident native deployment.
14. No precision/model/backend substitution, synthetic hidden state, or standalone GEMM replacement.
15. Historical and prospective input axes remain distinct.
16. No Qwen3-30B or DeepSeek execution in this Goal.

## V11 lessons promoted to machine gates

- `FM01_ADMISSION_SERIALITY`: one formal admission in flight; ACK before another.
- `FM02_HASH_SEMANTICS`: payload/file hashes and canonical token-sequence hashes remain distinct typed fields.
- `FM03_SEMANTIC_BINDING`: semantic binding must use synchronized evidence, never launch order; at most two bounded methods, then BLOCKED.
- `FM04_REPLAY_SIGNATURE`: replay output equivalence is insufficient without in-context/replay kernel-signature equivalence.
- `FM05_FRESH_STATIC_SET`: implementation change invalidates stale static-path evidence and downstream formal artifacts.
- `FM06_LDGSTS_CLASSIFICATION`: audit LDGSTS global source independently; exclude LDGDEPBAR as control.
- `FM07_CONTEXT_ATTRIBUTION`: no same-process context means no promoted object attribution.
- `FM08_NCU_UNIT`: unresolved unit means preserve raw displayed value/unit and mark non-comparable.
- `FM09_CAPACITY_STRATEGY`: lack of full residency does not authorize precision/backend changes; use only the V12-authorized execution mode.
- `FM10_EXECUTABLE_VALIDATION`: no hard-coded PASS tables.

Executor-integrity gates added for the real unattended run:

- `EX01_NO_FRAMEWORK_ONLY_PASS`: scientific stages cannot PASS as FRAMEWORK_ONLY, PLAN_ONLY or DRY_RUN.
- `EX02_CONTIGUOUS_RECEIPT_CHAIN`: resume only from a contiguous hash-valid dependency chain.
- `EX03_IMMUTABLE_ATTEMPTS`: previous terminal attempts are never overwritten; retry creates a new attempt record.
- `EX04_AUTHORIZED_SKIP_ONLY`: SKIPPED is complete only when the bound contract explicitly makes the stage not applicable.
- `EX05_SIGNAL_SAFE`: interruption can leave RUNNING/PARTIAL evidence, never a false PASS.
- `EX06_STAGE_INPUT_DIGEST`: revision, input authority, authorization SHA, runtime identity, target identity, static-set SHA and upstream receipt SHAs act as invalidation keys where relevant.
- `EX07_NO_BLIND_RETRY`: every fallback has a bounded attempt budget; exhaustion emits BLOCKED and stops.

## Draft scenario and target policy

Subject to final V12 confirmation:

- S2_TEXT B1/T2048/D32 is the required first baseline.
- S3_TEXT B1/T8192/D16 is conditional after S2 closes and only if authorized/feasible/materially informative.
- other scenarios are not formal first-pass campaigns unless V12 explicitly requests them.
- prefer one decode MLP linear anchor for lineage continuity with Qwen2.5.
- allow at most one attention/KV target only if the observed implementation is materially distinct, useful, and losslessly bindable.
- never invent or substitute a target merely to satisfy the preference.

## Expected review pack

`docs/vm_tlb/review_packs/C16_QWEN3_8B_UNATTENDED_CAMPAIGN_109_V12/`

At minimum it must contain authority binding, executor self-test, environment/input/execution-mode receipts, census and implementation classes, semantic candidates and target decision, per-target state/equivalence/signature/static-path/capture/ACK evidence, unit-preserving NCU export, compact memory fingerprints, S3 continuation decision if applicable, final decision, open issues and SHA256SUMS.

Allowed final decisions:

- `C16_QWEN3_8B_UNATTENDED_CAMPAIGN_109_V12_PASS`
- `C16_QWEN3_8B_UNATTENDED_CAMPAIGN_109_V12_PASS_WITH_SCOPED_EVIDENCE`
- `C16_QWEN3_8B_UNATTENDED_CAMPAIGN_109_V12_BLOCKED_<specific_gate>`

A well-evidenced BLOCKED result is a valid unattended outcome. Do not turn it into PASS by changing model, input, backend, precision, or semantic target.