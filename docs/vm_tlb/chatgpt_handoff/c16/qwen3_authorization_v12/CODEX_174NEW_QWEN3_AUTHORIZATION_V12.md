# C16 174-new V12 — Qwen3-8B Scientific Authorization Closure

## Goal
Close the remaining CPU-side **scientific authority** gates for Qwen3-8B and emit one hash-bound authorization that the node109 real campaign must consume. This is the final authorization round before the multi-hour GPU Goal, not a repair-only round.

## Accepted inputs
- V11 unified consumer HEAD: `a28b70cdc17a3efb3380b8d2d178a55d077dc194`
- V10 formal pair producer: `57ca798c851a3b9d4a2c787c01f4e2b3a16fcdea`
- node109 next-lineage framework base HEAD: `d7f5ad2c06831193113401b688711be80058cd00`
- Qwen3-8B exact revision: `b968826d9c46dd6066d109eabc6255188de91218`
- V2 prospective namespace: `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/prospective_inputs/C16_PROSPECTIVE_COMMON_INPUT_V2`
- canonical `tokenizers==0.20.3` wheel already durable on node164, exact SHA from V10/V11.

CPU-only. No GPU/model execution. No accepted formal raw/catalog mutation. No network. Qwen3-30B out of scope.

## P0 — Independently revalidate V2
Do not trust V2 merely because it was created by the same process that detected V1 mismatch.

For all 6 models × 7 scenarios = 42 V2 bindings:
- re-open exact source bytes;
- re-open exact canonical local `tokenizer.json` with real `tokenizers.Tokenizer.from_file()`;
- apply the declared V2 no-special-token/no-chat-template policy exactly;
- recompute first exact N token IDs;
- verify payload IDs token-for-token, canonical sequence SHA, payload SHA, revision, scenario, batch and decode metadata;
- fail closed on any mismatch.

Output a full 42-row machine-readable validation table.

Only if all 42 pass, emit `C16_PROSPECTIVE_COMMON_INPUT_V2_CANONICAL_VALIDATED` and freeze V2 as the prospective authority. Never modify V1 or historical bindings.

## P1 — Resolve stale V11 / producer gates
Independently confirm from V11 evidence that V10 full-binary consumer verification is already satisfied. Do not require it again if proven.

Consume node109 V11 framework evidence and classify remaining gates by ownership:
- scientific/input authority gates → must close here;
- producer runtime class/API availability → `PRODUCER_PREFLIGHT_REQUIRED`, **not** a reason to deny scientific authorization;
- GPU execution evidence → future node109 campaign.

Produce a resolved gate table with PASS / BLOCKED / PRODUCER_PREFLIGHT_REQUIRED / NOT_APPLICABLE.

## P2 — Qwen3 execution-mode policy; capacity is NOT an authorization blocker
Use archived Qwen3-8B config/index/header/residency authority from V7 and record exact revision, 36 layers, static checkpoint bytes and per-layer residency.

Capacity determines execution mode; it does not by itself determine whether Qwen3 can be studied.

Authorize the following ordered mode policy:

1. `NATIVE_FULL_RESIDENT` only if node109 later proves the exact BF16 deployment fits and runs without precision/offload/backend substitution.
2. Otherwise automatically use `EXACT_SEMANTIC_LAYER_STREAMING_REPLAY`.

Failure to prove full residency is **not BLOCKED** and must not stop the campaign. In streaming mode require exact model implementation, exact BF16 layer weights, true propagated hidden state, position/attention state and layer-local KV state; require replay equivalence and kernel-signature equivalence before formal capture.

Do not call layer streaming a simultaneous-resident native full-model deployment. Do not substitute FP16/INT8/offload/synthetic hidden state merely to fit memory.

## P3 — Hash-bound scientific campaign authorization
If V2 canonical validation and all scientific/input authority gates pass, emit:

`QWEN3_EXECUTION_AUTHORIZATION.json`

The authorization must bind at least:
- exact model ID/revision;
- V2 authority identity and Qwen3 scenario payload SHAs;
- accepted scientific scenarios/target-selection policy;
- allowed execution-mode policy above;
- accepted framework base HEAD `d7f5ad2c06831193113401b688711be80058cd00` or a verified descendant;
- `FORMAL_ADMISSION_CONCURRENCY=1`;
- forbidden substitutions and claim boundaries.

Authorize this staged logic for the future node109 unattended Goal:
1. asset/environment/runtime preflight;
2. exact V2 `S2_TEXT` baseline authority;
3. select native-full-resident if proven, otherwise exact semantic layer streaming;
4. bounded kernel census / implementation identification;
5. choose representative targets from observed implementation classes, never launch order;
6. prefer one decode MLP-linear lineage anchor plus one attention/KV target only if materially distinct;
7. exact incoming state freeze;
8. replay output equivalence;
9. in-context ↔ replay kernel-signature equivalence;
10. fresh SASS global-address-path audit; never reuse Qwen2.5 static sets;
11. formal capture only after complete executed/zero closure;
12. serial admission and ACK before any second admission;
13. NCU with explicit unit-preserving durable export;
14. bounded review-pack closure.

Explicit STOP conditions:
- exact assets/input/revision mismatch;
- producer runtime/API cannot execute the exact model implementation locally;
- exact state reconstruction fails;
- replay equivalence fails;
- signature isolation fails after bounded methods;
- new special address path is detected but not instrumented;
- overflow/drop nonzero;
- Pipeline ACK failure;
- continuing would require precision/offload/backend/synthetic-state substitution.

On STOP preserve receipts and emit scoped outcome; do not improvise a substitute deployment.

## P4 — Scenario / sampling policy
Do not authorize exhaustive formal capture of all seven scenarios.

- `S2_TEXT`: first baseline and required.
- `S3_TEXT`: only after S2, if long-context execution is feasible under the authorized mode and census indicates materially informative behavior.
- other scenarios: census-only initially; promote only if implementation/shape/behavior class is materially new.

This is stratified sampling, not exhaustive tracing.

## P5 — Outputs
Create:
`docs/vm_tlb/review_packs/C16_QWEN3_AUTHORIZATION_174NEW_V12/`

Include at least:
- `FINAL_DECISION.json`
- `V2_CANONICAL_42_VALIDATION.tsv`
- `QWEN3_GATE_RESOLUTION.tsv`
- `QWEN3_CAPACITY_AND_SCOPE.json`
- `QWEN3_EXECUTION_AUTHORIZATION.json` only if scientific authority gates pass
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Expected decision:
- `C16_QWEN3_AUTHORIZATION_174NEW_V12_PASS`, or
- `C16_QWEN3_AUTHORIZATION_174NEW_V12_BLOCKED_<specific scientific/input reason>`.

Commit/push and STOP. Do not execute Qwen3 on GPU.