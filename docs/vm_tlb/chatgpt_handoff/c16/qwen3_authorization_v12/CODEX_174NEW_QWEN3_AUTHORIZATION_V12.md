# C16 174-new V12 — Qwen3-8B Scientific Authorization Closure

## Goal
Close all remaining CPU-side scientific gates required before node109 may begin the Qwen3-8B campaign. This is one consolidated authorization task, not a repair-only round.

## Accepted inputs
- V11 unified consumer HEAD: `a28b70cdc17a3efb3380b8d2d178a55d077dc194`
- V10 formal pair producer: `57ca798c851a3b9d4a2c787c01f4e2b3a16fcdea`
- Qwen3-8B exact revision: `b968826d9c46dd6066d109eabc6255188de91218`
- V2 prospective namespace: `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/prospective_inputs/C16_PROSPECTIVE_COMMON_INPUT_V2`
- canonical tokenizers wheel already durable on node164, exact SHA from V10/V11.

CPU-only. No GPU/model execution. No accepted formal raw/catalog mutation. No network. Qwen3-30B out of scope.

## P0 — Revalidate V2 independently
Do not trust V2 merely because it was created by the same process that detected V1 mismatch.

For all 6 models x 7 scenarios = 42 V2 bindings:
- re-open exact source bytes;
- re-open exact canonical local `tokenizer.json` using real `tokenizers.Tokenizer.from_file()`;
- apply the declared V2 no-special-token/no-chat-template policy exactly;
- recompute the first exact N token IDs;
- verify payload IDs token-for-token, canonical sequence SHA, payload SHA, revision, scenario, batch and decode metadata;
- fail closed on any mismatch.

Output a full 42-row machine-readable validation table.

If all 42 pass, emit `C16_PROSPECTIVE_COMMON_INPUT_V2_CANONICAL_VALIDATED` and freeze V2 as the prospective authority. Never modify V1 or historical bindings.

## P1 — Resolve V11 stale/remaining gates
Independently confirm that V10 full-binary consumer verification is already satisfied by V11 evidence (catalog/manifest/static executed-zero partition/raw C16WARP1 shard fingerprints). Do not require it again if proven.

Produce a resolved gate table with each item exactly one of PASS / BLOCKED / NOT_APPLICABLE.

The only acceptable Qwen3 authorization blockers after this task are concrete unresolved evidence gaps, not stale status strings.

## P2 — Qwen3 execution scope and capacity classification
Use the already archived Qwen3-8B config/index/header/residency authority from V7.

Explicitly record:
- exact revision;
- 36 layers;
- checkpoint/static parameter size and per-layer residency;
- RTX4080 full-resident BF16 feasibility classification based on exact known bytes and GPU capacity evidence available in the repository/receipts;
- if full-resident native execution is not proven feasible, authorize only exact semantic layer streaming/replay and label it accordingly.

Do NOT silently call layer streaming a native full-model deployment.

## P3 — Scientific campaign contract for Qwen3-8B
If V2 canonical validation and all required gates pass, emit a hash-bound:

`QWEN3_EXECUTION_AUTHORIZATION.json`

It must authorize a resumable node109 campaign but constrain it to the following staged logic:

1. environment / asset preflight;
2. exact V2 S2_TEXT authority as the first baseline scenario;
3. exact semantic layer streaming to reconstruct state if full-resident BF16 is not feasible;
4. bounded kernel census / implementation identification before any formal target choice;
5. choose representative targets from observed implementation classes, not guessed launch order;
6. prefer one decode MLP linear anchor for lineage continuity with Qwen2.5 and one attention/KV target only if materially distinct and scientifically useful;
7. exact incoming hidden state + position/attention/KV state;
8. replay output equivalence;
9. in-context vs replay kernel-signature equivalence;
10. fresh SASS global-address-path audit; never reuse Qwen2.5 static sets;
11. formal capture only after complete static executed/zero closure;
12. `FORMAL_ADMISSION_CONCURRENCY=1`, wait for ACK before any second formal admission;
13. application-context NCU with explicit unit-preserving durable export;
14. no full-model/cache/TLB claim from a layer replay unless independently proven.

The authorization must include explicit STOP conditions so the node109 framework can run unattended for hours without improvising:
- exact state reconstruction fails;
- replay equivalence fails;
- signature isolation fails after bounded methods;
- new special address path is detected but not instrumented;
- overflow/drop nonzero;
- source/input/revision mismatch;
- Pipeline ACK failure;
- capacity/runtime requires precision/offload/backend substitution.

On STOP, preserve receipts, emit scoped outcome, and do not substitute configuration.

## P4 — Scenario policy
Do not try all seven scenarios formally on first pass.

Authorize:
- S2_TEXT as first baseline;
- S3_TEXT only after S2 baseline if long-context behavior is feasible and materially informative;
- other scenarios census-only unless implementation/shape classification is materially new.

This remains stratified sampling, not exhaustive capture.

## P5 — Output
Create:
`docs/vm_tlb/review_packs/C16_QWEN3_AUTHORIZATION_174NEW_V12/`

Include at least:
- `FINAL_DECISION.json`
- `V2_CANONICAL_42_VALIDATION.tsv`
- `QWEN3_GATE_RESOLUTION.tsv`
- `QWEN3_CAPACITY_AND_SCOPE.json`
- `QWEN3_EXECUTION_AUTHORIZATION.json` only if all authorization gates pass
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Expected decision:
- `C16_QWEN3_AUTHORIZATION_174NEW_V12_PASS`, or
- `..._BLOCKED_<specific reason>`.

Commit/push and STOP. Do not execute Qwen3 on GPU.