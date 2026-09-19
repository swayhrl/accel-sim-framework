# CODEX NEXT STAGE — 109 E1 Authority Producer + Independent E3 V1

Date: 2026-09-19

Status: ACTIVE AFTER USER LAUNCH

Mode:
`GOAL MODE / solve-and-continue`

Node:
`109 / RTX4080`

Stage:
`AWMA_E1_AUTHORITY_AND_MOE_DIAGNOSTICS_109_V1`

Coordination:
`hrl/awma-hitpath-e1-authority-handoff-v1`

Read first:

1. `CURRENT_STATE.md`
2. `DISCUSSION_REFERENCE.md`
3. `POST_PIPELINE_REVIEW_DECISION_2026-09-19.md`
4. `NEXT_STAGE_ACCEPTANCE_CONTRACT_V1.md`
5. this Goal

## 0. Why this Goal differs from the previous 20h pipeline

Previous E1 correctly stopped because no hash-bound activation/module-replay authority existed.

This Goal explicitly authorizes producing that authority from accepted model assets and an accepted common token sequence.

E3 is no longer gated on E1.

Scientific DAG:

```text
A0/A1 activation authority -> E1 core -> bounded E1 profiling/followup

Q30 authority verification -> E3 N/P/U-active
```

These tasks share one GPU and therefore execute serially under the lock, but a scientific STOP in E1 does not automatically skip E3.

## 1. Accepted upstream authorities

Previous 109 closure:

`a271a0e57d3cb61ee878e686e6e517082a9f97df`

Common raw/AWQ paired replay evidence:

`hrl/c16-qwen25-7b-raw-paired-replay-109-v8`

`e1d210d662ece6975648d04f628eb3f9e938117f`

AWQ runtime characterization:

`hrl/c16-qwen25-7b-awq-characterization-109-v7`

`2a05cadcbcc0e0b477b83d28aabe0c0aee270150`

Old CPU pair-prep:

`04448e24b716ef16e13573f7adf9bc291ac777a6`

Q30 S2 exact state/replay:

`ee67225edc8fc5868de585d38e0391cbeb755d9f`

Q30 later target/capture evidence may be used for implementation context:

`c9979aa47961f843db4b5b06cffa488e4ff1a132`

`28620a89d55fd9230103a31d31d14757b57e1e0f`

Suggested execution branch:

`hrl/awma-e1-authority-moe-109-v1`

Create from the latest accepted 109 AWMA branch.
Historical utilities may be copied/cherry-picked only with exact source attribution; do not mutate old review packs.

## 2. GPU ownership

Before CUDA/profiler work:

- inspect `nvidia-smi`;
- verify expected RTX4080 UUID;
- inspect `/data/c16/locks/c16_gpu_campaign.lock`;
- acquire normally;
- never kill/bypass another owner.

All GPU tasks in this Goal are physically serial.

## 3. A0 — Rebind model/input/runtime authorities

### Raw model

`Qwen/Qwen2.5-7B-Instruct`

revision:

`a09a35458c702b33eeacc393d103063234e8bc28`

### AWQ model

`Qwen/Qwen2.5-7B-Instruct-AWQ`

revision:

`b25037543e9394b818fdfca67ab2a00ecc7dd641`

### Common S2 token authority

Historical pair-input authority states:

- token_count = 2048
- SHA256 = `0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9`
- raw/AWQ parsed arrays equal.

Verify the actual files/receipts before use.

If the local path moved but exact hash/bytes are found under accepted storage, bind the new path.
Do not regenerate token IDs from text if the accepted token file still exists.

### Runtime

For AWQ prefer the exact working V7-compatible runtime/environment.
Do not upgrade AutoAWQ/torch/CUDA to make the experiment easier.

For raw reuse the accepted selective layer loader approach where practical.

Produce:

`E1_INPUT_MODEL_RUNTIME_AUTHORITY.json`

If exact model or token authority cannot be recovered, STOP E1 only and continue E3.

## 4. A1 — Produce live module activation authority

Target layer:

`layer 0`

Target roles:

```text
model.layers.0.self_attn.q_proj
model.layers.0.mlp.down_proj
```

Use direct Python module object/path binding.

Do NOT infer the module from:
- CUDA launch order;
- a generic fused GEMM name;
- static index alone.

### Raw live execution

Use the accepted S2 token sequence and the accepted raw selective layer/semantic replay path.

Capture exact module pre-hook input and post-hook output.

### AWQ live execution

Use the same accepted S2 token sequence and the V7-compatible AWQ model with semantic modules unfused where required for direct binding.

Prefer the historical proven loader setting `fuse_layers=False` if that is still the exact accepted runtime path.

Capture exact module pre-hook input and post-hook output.

Do not require the raw and AWQ activation values to match.

## 5. A1 activation-pool contract

For each implementation/role, freeze before timing:

`POOL = first 256 consecutive token rows of the live module input`

Preserve natural batch rank.

Required:

### q_proj

```text
M256: [1,256,3584]
M1:   [1,1,3584]
```

unless exact model metadata proves a different K.

### down_proj

```text
M256: [1,256,18944]
M1:   [1,1,18944]
```

unless exact model metadata proves a different K.

Never flatten to `[256,K]` or `[1,K]`.

Record:

- tensor values;
- rank;
- shape;
- stride;
- dtype;
- contiguous status;
- byte SHA256;
- source live execution ID;
- token SHA;
- model revision;
- module path/type.

Also save the corresponding live output for the selected 256 rows.

Produce durable node164 authority bundles and small Git manifests.

## 6. A2 — Fresh module replay equivalence

Reload the exact target module implementation independently.

Replay M256 from the saved pool.

Compare with saved live M256 output.

Preferred gate:

`BITWISE_EQUAL`

If bitwise fails:
- report max_abs/max_rel;
- do not auto-relax tolerance;
- mark `REPLAY_EQUIVALENCE_FAIL`;
- freeze only that role/implementation unless a pre-existing accepted numerical tolerance contract exists.

M1 is a slice of the same accepted M256 pool and does not require a separately generated live execution.

Successful A2 creates:

`E1_MODULE_REPLAY_AUTHORITY_PASS`

per role/implementation.

## 7. E1 — Core shape/implementation experiment

Only run points whose A2 authority passes.

Core deployments:

```text
raw q_proj   M1
raw q_proj   M256
AWQ q_proj   M1
AWQ q_proj   M256

raw down_proj M1
raw down_proj M256
AWQ down_proj M1
AWQ down_proj M256
```

These are natural-deployment-derived activation replays.

They do NOT automatically constitute same-numeric-input raw/AWQ pairs.

## 8. E1 native timing

For every accepted point:

- 2 warmups;
- 5 measured runs;
- CUDA events around the complete semantic module call;
- synchronize correctly;
- retain every sample;
- report median + dispersion.

Do not include model loading in module timing.

Do include all runtime work inside the module call:
- input conversion;
- dequantization;
- GEMM;
- temporary kernels;
- postprocessing.

## 9. E1 implementation fingerprint

For each point record:

- module class/path;
- input rank/shape/dtype;
- kernel sequence;
- kernel names;
- grid/block;
- whether AWQ uses quantized GEMM or dequantize+matmul;
- temporary allocations where observable;
- output dtype/hash.

Rank-dependent implementation switching is a result, not an error.

## 10. E1 comparison classes

### Deployment-level

Always valid after replay authority:

- raw M1 vs raw M256;
- AWQ M1 vs AWQ M256;
- normalized shape trend across implementations;
- raw deployment versus AWQ deployment with explicit activation difference.

### Controlled semantic/input pair

Attempt only if source/weight scaling audit proves a valid mapping.

If a common semantic input or an exact algebraic raw<->AWQ input transform can be constructed:

- validate it against the live AWQ module output;
- then mark `SEMANTIC_PAIR_QUALIFIED`.

Otherwise:

`IMPLEMENTATION_LEVEL_ONLY`

Do not force a common tensor.

## 11. E1 dtype bridge

Record actual raw/AWQ input/output dtypes and implementation compute path.

If an explanatory comparison requires raw FP16 bridge:
- create a new named diagnostic identity;
- preserve the same accepted activation values cast under an explicit rule;
- do not overwrite raw BF16 measurements.

Bridge is conditional, not mandatory.

## 12. E1 profiling

Do not reuse the failed whole-application exact-selector protocol from the previous pipeline.

Preferred profiling setup:

1. standalone module replay process containing only the target semantic call;
2. NVTX range around the call if installed NCU supports reliable range selection;
3. selector canary first;
4. only after canary success collect metrics.

Metrics where supported:

- L1/TEX requested bytes;
- L2 requested bytes;
- DRAM bytes;
- tensor/math utilization;
- occupancy/warp activity;
- selected instruction/stall evidence.

If canary matches zero kernels:

`SELECTOR_UNRESOLVED`

Do not call counters unavailable.

## 13. E1 optional implementation decomposition

Only after core E1 closes.

For one preselected role, preferably down_proj, if the exact frozen AWQ runtime exposes trustworthy paths:

A. deployed AWQ module

B. one-time dequantized weight + FP16 matmul

C. per-call dequantization + FP16 matmul

No new backend implementation.

This is diagnostic only.

## 14. E3 — Independent Q30 MoE routing diagnostic

E3 may run even if E1 stops.

Verify:

`Q30_S2_T2048_STATE_REPLAY_PASS`

authority:

`ee67225edc8fc5868de585d38e0391cbeb755d9f`

Use the accepted S2 Prefill exact layer replay/state.

Do not rerun the 48-layer semantic stream unless the state authority is corrupted.

### E3 target scope

Use one preselected MoE FFN region/layer supported by the exact replay state.

Freeze:
- layer;
- input hidden state SHA;
- router logits/routes/gate weights;
- E;
- top-k;
- expert backend;
- weight residency/loading policy;
- timing boundary.

### N — natural

Execute exact natural routing.

Save:
- active experts;
- token histogram;
- CV/dispersion;
- kernel sequence;
- dispatch/expert/combine timing.

### P — histogram-preserving permutation

Jointly permute token hidden states and their route/gate metadata.

Preserve per-expert token count exactly.

Inverse-permute output.

Require equivalence to natural output under the corresponding permutation.

If equivalence fails:
freeze P; N remains valid.

### U-active — active-set-preserving balance

Keep the natural active expert set.

Redistribute assignments as evenly as possible within that set while preserving:

- M;
- top-k;
- total assignments.

Each token still selects distinct expert IDs.

Label:

`SYNTHETIC_ROUTING`

Do not claim natural model quality or natural speed.

## 15. E3 measurements

Measure full:

`dispatch -> expert compute -> combine`

Router cost separately.

Use:
- 2 warmups;
- 5 measured repetitions where replay semantics allow;
- all sample values;
- route histogram;
- kernel shapes/counts;
- native timing;
- lightweight NCU only if selector/range canary is reliable.

No detailed NVBit/SASS trace is required.

## 16. Scheduling rule

After A0:

- if E1 authority work is progressing, continue A1/A2/E1;
- if E1 hits a scientific STOP, switch to E3 rather than ending the Goal;
- E3 may also run first if its accepted state is already locally ready while E1 data are being transferred/verified.

Do not run E1 and E3 concurrently on the GPU.

## 17. Forbidden

No:

- new model download;
- model revision substitution;
- random/synthetic activation substituted for E1 authority;
- AWQ semantic binding inferred from launch order;
- new quantization backend;
- OLMoE/DeepSeek bring-up;
- architecture mechanism;
- broad detailed trace campaign.

## 18. Durable output

Large authority/state artifacts:

`/root/share/mnt164/huangrulin/awma_e1_authority_moe_109_v1/`

Report:

`docs/vm_tlb/codex_handoff/awma/E1_AUTHORITY_AND_MOE_DIAGNOSTICS_109_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_E1_AUTHORITY_AND_MOE_DIAGNOSTICS_109_V1/`

At minimum:

```text
README.md
SOURCE_ANCHORS.md
PIPELINE_STATE.json
E1_INPUT_MODEL_RUNTIME_AUTHORITY.json
E1_ACTIVATION_AUTHORITY_INDEX.tsv
E1_REPLAY_EQUIVALENCE.tsv
E1_CORE_MATRIX.tsv
E1_NATIVE_TIMING.tsv
E1_IMPLEMENTATION_FINGERPRINT.tsv
E1_SEMANTIC_CLASSIFICATION.tsv
E1_RESOURCE_DIAGNOSIS.tsv
E3_AUTHORITY.json
E3_ROUTING_CASES.tsv
E3_NATIVE_TIMING.tsv
E3_EQUIVALENCE.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Files for skipped/blocked tasks must record explicit status rather than be fabricated empty results.

Success marker:

`AWMA_E1_AUTHORITY_AND_MOE_DIAGNOSTICS_109_V1_COMPLETE_WITH_SCOPE`

Then:
report -> review pack -> hashes -> node164 ACK -> commit -> push -> remote verify -> clean -> release GPU lock -> STOP.

Do not automatically start detailed capture or a new model.
