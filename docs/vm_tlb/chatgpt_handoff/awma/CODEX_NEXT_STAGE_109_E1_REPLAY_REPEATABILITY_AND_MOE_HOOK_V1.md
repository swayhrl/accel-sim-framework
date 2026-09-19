# CODEX NEXT STAGE — 109 E1 Replay Repeatability + MoE Control Hook V1

Date: 2026-09-19

Status: ACTIVE AFTER USER LAUNCH

Mode:
`GOAL MODE / solve-and-continue`

Node:
`109 / RTX4080`

Stage:
`AWMA_E1_REPLAY_REPEATABILITY_AND_MOE_CONTROL_HOOK_109_V1`

Coordination branch:
`hrl/awma-109-replay-determinism-routing-hook-handoff-v1`

Read:

1. `docs/vm_tlb/chatgpt_handoff/awma/REVIEW_109_E1_E3_2026-09-19.md`
2. the prior shared acceptance contract from `hrl/awma-hitpath-e1-authority-handoff-v1`
3. this Goal

Accepted prior execution:

`hrl/awma-e1-authority-moe-109-v1`

`10c1c19fd0314a187a772ea83034d71a64eb569a`

Suggested execution branch:

`hrl/awma-e1-repeatability-moe-hook-109-v1`

Create from `10c1c19f...`.

Do not rewrite the prior review pack.

## 0. Goal

Close two bounded qualification gaps:

A. determine whether AWQ live/reload differences are a stable numerical repeatability property of the exact runtime or a broken replay authority;

B. qualify a minimal Q30 direct-experts routing-control harness for N/P/U-active without modifying the model's architecture/backend.

If A qualifies, resume the E1 core M1/M256 native experiment.

If B qualifies, run the light E3 routing diagnostic.

The two tasks are scientifically independent and share only the GPU lock.

## 1. GPU / runtime

Use:

`/data/c16/locks/c16_gpu_campaign.lock`

Verify the accepted RTX4080 identity.

Do not upgrade:
- torch;
- CUDA;
- AutoAWQ;
- custom AWQ extensions;
- transformers/Q30 runtime.

Any runtime change is a scientific STOP for the affected task.

## 2. P0 — Provenance closeout for AWQ activation authority

Recover the already-produced node164 AWQ activation artifacts.

Add compact Git evidence:

- `E1_AUTHORITY_RAW_DATA_INDEX.tsv`
- `E1_AUTHORITY_RUN_RECEIPTS.json`
- node164 ACK/verification manifest
- hashes of large M256 input/output authority files

Do not recreate valid activation tensors just to make a receipt.

If the durable artifacts cannot be found/hash-verified:
freeze E1 authority and continue the E3 lane.

## 3. P1 — Freeze exact AWQ module state

For each:

- `model.layers.0.self_attn.q_proj`
- `model.layers.0.mlp.down_proj`

bind exact:

- module class;
- in/out features;
- group_size/w_bit;
- qweight SHA;
- qzeros SHA;
- scales SHA;
- bias SHA or NONE;
- extension/backend actually selected;
- input authority SHA.

For every fresh reload, hashes must equal the accepted reference.

Any quantized-buffer mismatch is:

`RELOAD_STATE_MISMATCH_STOP`

Do not form a tolerance around a state mismatch.

## 4. P2 — AWQ repeatability experiment

Use the accepted saved M256 input for each role.

Do not change tensor rank/dtype/stride intentionally.

### R0 — same-instance repeatability

Load one exact module instance.

After warmup, execute the identical saved M256 input at least 10 times.

Save every output hash and numerical comparison.

Report pairwise:

- bitwise equality;
- max_abs;
- max_rel excluding a clearly documented near-zero denominator rule;
- RMSE;
- exact-element fraction;
- elementwise absolute-error percentiles;
- ULP distance if it can be implemented without changing execution.

### R1 — fresh-live immediate replay

In a fresh exact full-model/live-module execution:

1. capture the live M256 input/output via hooks;
2. before unloading/changing the module, invoke that same module instance directly on the captured input;
3. compare live-hook output versus immediate replay.

Repeat in at least 3 fresh processes/loads.

This distinguishes hook/context effects from independent reload effects.

### R2 — independent reload repeatability

Perform at least 5 fresh exact module/model reloads.

Verify qweight/qzeros/scales/bias hashes every time.

For each reload, execute the same accepted M256 input at least 3 times.

Record:
- within-reload variability;
- between-reload variability;
- kernel path/fingerprint.

## 5. P3 — Freeze a repeatability envelope

Do NOT choose tolerance from the old two failed values alone.

Use only the first subset of P2 as calibration:

Suggested deterministic split:
- reloads 1-3 = calibration
- reloads 4-5 = holdout

Freeze a repeatability envelope separately per role before inspecting holdout acceptance.

The envelope must include at least:
- max_abs limit;
- relative-error rule;
- RMSE limit;
- exact/ULP characterization where meaningful.

The envelope should be derived from actual calibration repeatability and documented mathematically.

Do not round upward merely to make the old replay pass.

Then evaluate held-out reloads 4-5.

Accepted status only if holdout stays within the frozen envelope:

`NUMERICALLY_EQUIVALENT_UNDER_QUALIFIED_RUNTIME_REPEATABILITY`

Otherwise:

`REPLAY_EQUIVALENCE_FAIL`

If the runtime is bitwise deterministic, retain bitwise equality as the contract; do not create an unnecessary tolerance.

## 6. P4 — Re-evaluate the original saved live authority

Only after P3 freezes the contract.

Compare the original saved live M256 output from the prior stage against a fresh exact reload.

Classify it using the new held-out-qualified contract.

This prevents circularly choosing the contract from the original mismatch.

If original authority is outside the qualified envelope:
do not use it for E1 core; generate a new live authority under the qualified process and bind it separately.

## 7. P5 — Close raw module authority

Use:

raw model revision:
`a09a35458c702b33eeacc393d103063234e8bc28`

common S2 token SHA:
`0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9`

Target:
- layer0 q_proj
- layer0 down_proj

Produce exact live M256 input/output and fresh replay evidence using the same authority schema as AWQ.

Reuse historical raw selective-loader logic from:

`e1d210d662ece6975648d04f628eb3f9e938117f`

only with source attribution.

Do not claim the old layer-level replay alone closes the new exact module authority.

## 8. P6 — Resume E1 core only if authority qualifies

For every role/implementation with accepted replay authority:

```text
M256 = accepted [1,256,K]
M1   = first row [1,1,K]
```

Keep natural rank.

Run:

- raw q_proj M1/M256
- AWQ q_proj M1/M256
- raw down_proj M1/M256
- AWQ down_proj M1/M256

If one role fails authority, run the other accepted role and mark the matrix scoped.

Timing:
- 2 warmups
- 5 CUDA-event measurements
- retain samples
- median/dispersion
- complete semantic module call

Record implementation/kernel fingerprint.

Do not require raw and AWQ live activations to be equal.

Comparison status remains:
- deployment-level by default;
- `SEMANTIC_PAIR_QUALIFIED` only with separately proven input/scaling mapping;
- otherwise `IMPLEMENTATION_LEVEL_ONLY`.

## 9. E3-H0 — Qualify direct-experts natural canary

Authority:

`ee67225edc8fc5868de585d38e0391cbeb755d9f`

Use accepted S2 T2048 Prefill target-layer state.

Inspect the exact frozen local transformers/model source.

Do not assume upstream-main source if the installed source differs.

Identify the exact MoE block boundary:

```text
hidden_states
 -> gate
 -> routing_weights + selected_experts
 -> experts(hidden, selected_experts, routing_weights)
 -> expert output
```

If the exact runtime does not expose an equivalent experts-call boundary:
`STOP_SCIENTIFIC_HOOK_NOT_SUPPORTED`.

### Natural direct-call canary

Using the accepted hidden state:

1. execute the exact real gate;
2. capture natural routing_weights/selected_experts;
3. execute the exact experts function directly;
4. compare its output to the natural MoE block's expert-path output under an explicitly matched boundary.

Only if this closes may P/U proceed.

No monkeypatch of expert math/backend is allowed.

## 10. E3-H1 — P histogram-preserving permutation

Create a deterministic permutation from the accepted state SHA, or use a fixed documented seed before looking at timing.

Jointly permute token rows of:

- hidden_states;
- selected_experts;
- routing_weights.

Call the exact experts function.

Inverse-permute output.

Acceptance:
- expert histogram exactly unchanged;
- routing weights associated with each token move with that token;
- output matches natural direct-experts output under the accepted numerical repeatability contract;
- backend/weights unchanged.

If P equivalence fails:
freeze P and U timing claims that depend on the same harness.

## 11. E3-H2 — U-active deterministic balanced assignment

Let natural active expert IDs be sorted set A.

Let M=2048 and k be the exact model top-k.

Require `|A| >= k`.

Construct:

`selected[t,j] = A[(t*k + j) mod |A|]`

unless this formula fails the distinct-expert-per-token constraint for the exact A/k; if so, use a deterministic cyclic construction that proves:

- k distinct experts for every token;
- only experts from natural active set A;
- total assignments = M*k;
- global counts max-min <= 1 where mathematically possible.

Keep each token's natural routing-weight vector in its original rank slots.

Do not renormalize if the natural vector is already normalized under the accepted model semantics.

Record construction receipt/hash.

Label:

`SYNTHETIC_ROUTING`.

## 12. E3-H3 — Timing boundary

After N/P/U hook qualification:

Measure the exact experts execution region that includes its native dispatch/grouping, expert compute, weighting and combine behavior.

Measure router/gate separately for N.

P/U do not claim model-quality equivalence.

Use:
- 2 warmups
- 5 measured runs
- all samples
- kernel sequence/shapes
- active expert count
- assignment histogram/CV
- timing

No detailed SASS/NVBit trace in this stage.

## 13. Solve-and-continue

Engineering:
solve and continue.

Task-local scientific STOP:
freeze only that task.

Examples:
- AWQ repeatability fails -> continue raw authority and E3.
- P fails inverse equivalence -> retain N authority; do not fabricate U claim.
- E3 exact source has no direct experts boundary -> finish E1 work.

Whole Goal STOP only for:
- GPU identity/lock safety;
- shared model/storage authority corruption.

## 14. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/E1_REPLAY_REPEATABILITY_AND_MOE_CONTROL_HOOK_109_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_E1_REPLAY_REPEATABILITY_AND_MOE_CONTROL_HOOK_109_V1/`

At minimum:

```text
README.md
SOURCE_ANCHORS.md
E1_AUTHORITY_RAW_DATA_INDEX.tsv
E1_AUTHORITY_RUN_RECEIPTS.json
AWQ_BUFFER_HASHES.tsv
AWQ_SAME_INSTANCE_REPEATABILITY.tsv
AWQ_LIVE_IMMEDIATE_REPLAY.tsv
AWQ_RELOAD_REPEATABILITY.tsv
AWQ_REPEATABILITY_CONTRACT.md
AWQ_HOLDOUT_VALIDATION.tsv
AWQ_ORIGINAL_AUTHORITY_REEVALUATION.tsv
RAW_ACTIVATION_AUTHORITY_INDEX.tsv
RAW_REPLAY_EQUIVALENCE.tsv
E1_CORE_MATRIX.tsv
E1_NATIVE_TIMING.tsv
E1_IMPLEMENTATION_FINGERPRINT.tsv
E3_EXACT_SOURCE_CONTRACT.md
E3_NATURAL_DIRECT_CALL_CANARY.tsv
E3_P_EQUIVALENCE.tsv
E3_U_ACTIVE_CONSTRUCTION.json
E3_ROUTING_CASES.tsv
E3_NATIVE_TIMING.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Skipped/non-applicable files may be replaced by explicit status receipts rather than fake data.

Success marker:

`AWMA_E1_REPLAY_REPEATABILITY_AND_MOE_CONTROL_HOOK_109_V1_COMPLETE_WITH_SCOPE`

Then:
node164 ACK -> report -> review pack -> hashes -> commit -> push -> remote verify -> clean -> release lock -> STOP.
