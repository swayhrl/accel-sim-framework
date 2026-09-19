# ChatGPT Scientific Review — 20h Pipeline Closure and Next-Stage Decision

Date: 2026-09-19

## Reviewed authorities

### 174-new repaired requalification

Execution branch:
`hrl/awma-repaired-vm-requalification-20h-174new-v1`

Final remote HEAD:
`a7110f789a2bc6761d8885a2ca5628b4acf50f69`

Scientific closure commit:
`79c2bf5a496f4a68eba6a015dac4f6209ed2cff9`

Repair authority:
`3f7bc0cd3cb3667b38fa0dd803ac034e19b493d6`

### 109 native/workload pipeline

Execution branch:
`hrl/awma-109-native-workload-pipeline-20h-v1`

Final remote HEAD:
`a271a0e57d3cb61ee878e686e6e517082a9f97df`

Parent:
`8a9d96ceb00e36ebdfa3d56cc277f965fffa649c`

## 1. 174 decision

Scientific result:

`REPAIRED_VM_PER_ACCESS_BASELINE_ACCEPTED_FOR_MODEL_RELATIVE_CHARACTERIZATION`

Hardware timing claim:

`NOT_HARDWARE_CALIBRATED`

Architecture mechanism:

`NOT_AUTHORIZED`

The repaired per-access semantics are now the accepted correctness baseline for further simulator characterization.
The configured 10-cycle L1 and 80-cycle L2 lookup latencies remain generic simulator assumptions, not RTX4080-calibrated facts.

## 2. Repaired Q05 requalification

Accepted target cycles:

- isolated R0 = 1,654,548
- isolated I0 = 674,179
- P34 R0 = 1,619,068
- P34 Q05-only I0 = 758,082
- P8 R0 = 1,675,884

All completed targets:

- downstream admissions = 3,090,304
- translated admissions = 3,090,304
- untranslated = 0
- unobserved = 0

Derived descriptive comparisons:

- isolated I0 reduces target cycles by ~59.25% versus repaired isolated R0;
- P34 Q05-only I0 reduces target cycles by ~53.18% versus repaired P34 R0;
- P34 repaired R0 is only ~2.14% faster than repaired isolated R0;
- P8 repaired R0 is ~1.29% slower than repaired isolated R0.

Therefore real predecessor history changes state/timing but does not remove the large modeled translation-path sensitivity.

## 3. Target-boundary telemetry interpretation

The target-boundary reconciliation is accepted.

For repaired P34 Q05 target delta:

- translation lookup requests = 3,090,412
- L1 hits = 3,087,016
- L1 misses = 3,396
- L2 hits = 3,288
- L2 misses = 108
- MSHR allocations = 15
- MSHR merges = 93
- walk starts = 15
- PWC accesses = 45
- PWC hits = 42
- PWC misses = 3
- PTE requests = 18
- PTE DRAM responses = 10

Requester-latency components:

- L1 lookup service = 30,904,120 requester-cycles
- L2 lookup service = 271,680 requester-cycles
- MSHR wait = 87,178 requester-cycles
- total requester latency = 31,263,812 requester-cycles

These requester-cycle quantities are not identical to exposed GPU stall cycles. However, they show that under the current repaired simulator model, most accumulated translation requester latency is associated with the configured per-access L1 lookup service rather than the 15 page walks.

This changes the immediate research question.

## 4. Mainline decision

The next mainline is:

`AWMA_REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V1`

Question:

> Under correct per-access VM coverage, how strongly does Q05 completion depend on the generic L1/L2 lookup-latency model, and what residual remains when lookup service is driven to zero?

This is a model-validity characterization stage, not an architecture mechanism stage.

The prior undercoverage-era lookup matrix is historical only and must not be reused as repaired quantitative evidence.

## 5. 174 provenance closeout requirement

The final 174 branch contains accepted scientific data, target-boundary deltas, hashes, and node164 run receipts, but two Git-packaging gaps remain:

1. the user-reported `REPAIRED_VM_REQUALIFICATION_20H_174NEW_V1_REPORT.md` is not present on the final remote branch;
2. `FINAL_CLOSURE_MANIFEST.md` references `REPAIRED_RUNTIME_AUTHORITY.json`, but that file is not present in the Git review pack/SHA256SUMS.

This does not invalidate the accepted scientific runs.

The next 174 Goal must first recover or reconstruct these provenance artifacts from durable/local authority without rerunning science.
Only if exact runtime authority cannot be proven may it rebuild the exact accepted repaired runtime and run one bounded P34 sanity.

## 6. 109 decision

109 closure:

`ACCEPTED_WITH_SCOPE`

E1 STOP:

`VALID_FAIL_CLOSED_STOP`

The STOP correctly refused to invent raw/AWQ activations.

However, the next-stage design changes:

> Absence of a pre-existing activation pool is no longer a terminal scientific condition.

The next 109 Goal explicitly authorizes production of a new exact activation/module-replay authority from accepted model assets and accepted token inputs.

## 7. Historical E1 authorities to reuse

### Common pair input authority

From:
`hrl/c16-qwen25-7b-raw-paired-replay-109-v8 @ e1d210d662ece6975648d04f628eb3f9e938117f`

Accepted S2 token sequence:

- token count = 2048
- token SHA256 = `0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9`
- raw/AWQ parsed token arrays were equal.

Raw model revision:
`a09a35458c702b33eeacc393d103063234e8bc28`

AWQ model revision:
`b25037543e9394b818fdfca67ab2a00ecc7dd641`

The old V8 raw replay proved a raw layer-0 replay path but explicitly left AWQ semantic target binding unresolved.
Do not promote that old unresolved pair.

### AWQ runtime authority

`hrl/c16-qwen25-7b-awq-characterization-109-v7 @ 2a05cadcbcc0e0b477b83d28aabe0c0aee270150`

This authority proves a working AWQ runtime and application-context NCU artifacts, but not a unique old kernel-to-WQLinear semantic binding.

The new E1 task should bind semantics directly at the Python module instance/path, not infer module identity from CUDA launch order.

## 8. E1 authority-production decision

Next E1 first produces exact module-level activation authority for:

- layer 0 `self_attn.q_proj`;
- layer 0 `mlp.down_proj`.

Use the accepted S2 2048-token sequence.

For each raw and AWQ deployment, save exact live module input/output authority with:

- model revision;
- module path/type;
- input tensor values;
- input/output SHA256;
- shape/rank/stride/dtype;
- runtime/backend identity;
- token authority;
- module weights/quantized-weight identity;
- fresh module-replay equivalence.

M-shape replay must preserve natural batch rank:

- M1 shape = `[1,1,K]`;
- M256 shape = `[1,256,K]`.

Do not flatten to `[M,K]`, because AWQ runtime heuristics may depend on tensor rank/dimensions.

M1 is a shape diagnostic, not natural Decode.

## 9. E1 comparison layers

Two evidence classes must be separated.

### Natural-deployment comparison

raw natural activation -> raw module

AWQ natural activation -> AWQ module

This compares deployed execution behavior and may include activation differences caused by quantization/scaling.

### Controlled semantic/input comparison

Attempt only where a provable input mapping or common semantic input can be constructed and validated against live module behavior.

If AWQ absorbed scaling/input transformation cannot be proved:

`IMPLEMENTATION_LEVEL_ONLY`

Do not force the same numeric tensor into both implementations and call it a semantic pair.

## 10. E3 dependency correction

E3 is scientifically independent of E1.

Next 109 scheduling is a DAG:

- E1 authority -> E1 core;
- E3 Q30 routing diagnostic;
- optional profiling/opportunity tasks.

They share the RTX4080 lock and therefore execute physically serially, but E1 STOP must not automatically skip E3.

Accepted Q30 state/replay authority:

`ee67225edc8fc5868de585d38e0391cbeb755d9f`

It already records S2/T2048 natural routing statistics and exact layer replay state.

## 11. NCU interpretation correction

The 109 M0 result:

`COUNTER_UNAVAILABLE_NO_KERNELS_PROFILED`

means the exact target-selector protocol matched zero kernels in those attempts.

It does not mean the RTX4080 lacks the requested counters.

Historical AWQ V7 contains successful application-context NCU evidence for:

- `l1tex__t_bytes`;
- `lts__t_bytes`;
- `dram__bytes`.

Next profiling should first prove a one-target selector canary or use isolated module replay/NVTX ranges so semantic-region profiling does not depend on fragile whole-application launch matching.

## 12. Next coordinated stage

`AWMA_REPAIRED_HIT_PATH_AND_E1_AUTHORITY_V1`

Two independent Goal lanes:

### 174-new

- provenance closeout with no scientific rerun if possible;
- repaired P34 lookup-latency sensitivity envelope;
- source/model semantics audit;
- optional one non-Attention hit-path screen.

### 109

- activation authority production;
- E1 core shape/implementation characterization;
- independent E3 N/P/U-active diagnostic;
- bounded profiling/implementation followups.

No architecture mechanism is authorized.
