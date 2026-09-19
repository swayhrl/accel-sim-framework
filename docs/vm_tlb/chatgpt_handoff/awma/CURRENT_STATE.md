# AWMA Current State

Date: 2026-09-19

## 1. Accepted repaired VM baseline

The legacy per-access coverage defect is closed.

Correctness repair authority:

`hrl/awma-vm-per-access-coverage-repair-174new-v1`

`3f7bc0cd3cb3667b38fa0dd803ac034e19b493d6`

Repaired requalification authority:

`hrl/awma-repaired-vm-requalification-20h-174new-v1`

`a7110f789a2bc6761d8885a2ca5628b4acf50f69`

Accepted status:

`REPAIRED_VM_PER_ACCESS_BASELINE_ACCEPTED_FOR_MODEL_RELATIVE_CHARACTERIZATION`

Hardware timing status:

`NOT_HARDWARE_CALIBRATED`

Architecture mechanism:

`NOT_AUTHORIZED`

## 2. Repaired Q05 core results

Frozen target:

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
scenario   = S2_TEXT
batch      = 1
prefill    = 2048
decode     = 32
dtype      = FP16
backend    = SDPA
target     = Q05_PREFILL_ATTN_FLASH
```

Accepted repaired cycles:

```text
formal isolated R0       = 1,654,548
formal isolated I0       =   674,179
P34 repaired R0          = 1,619,068
P34 Q05-only I0          =   758,082
P8 repaired R0           = 1,675,884
```

All completed targets:

```text
downstream admissions = 3,090,304
translated admissions = 3,090,304
untranslated          = 0
unobserved            = 0
```

The old translation-dependent quantitative baseline is retired as current evidence.

## 3. Context conclusion

Real predecessor history does not remove the large modeled translation sensitivity.

Descriptive comparisons:

- isolated R0 -> I0 target-cycle reduction: ~59.25%;
- P34 R0 -> Q05-only I0 reduction: ~53.18%;
- P34 R0 is ~2.14% faster than isolated R0;
- P8 R0 is ~1.29% slower than isolated R0.

Therefore the immediate question is no longer whether the old result was mostly isolated cold-start.

## 4. Repaired P34 target-delta translation structure

Accepted target-scoped delta:

```text
translation lookup requests = 3,090,412

L1 hits   = 3,087,016
L1 misses =     3,396

L2 hits   = 3,288
L2 misses =   108

MSHR allocations = 15
MSHR merges      = 93
walk starts      = 15

PWC accesses = 45
PWC hits     = 42
PWC misses   = 3

PTE requests       = 18
PTE DRAM responses = 10
```

Requester-cycle accumulation:

```text
L1 lookup service       = 30,904,120
L2 lookup service       =    271,680
MSHR wait               =     87,178
total requester latency = 31,263,812
```

Requester cycles are not identical to exposed GPU stall cycles.

However, under the current model, the dominant accumulated requester-latency component is the configured per-access L1 lookup service, not page walks.

## 5. Lookup-latency provenance

Current configuration:

```text
L1 lookup latency = 10 cycles
L2 lookup latency = 80 cycles
```

These remain generic simulator assumptions.

109 native reconnaissance did not calibrate them to RTX4080 hardware.

Therefore architecture mechanism design remains blocked until the repaired lookup/hit-path model sensitivity is characterized.

## 6. 174 packaging gap

The scientific runs/review data are accepted.

Two provenance artifacts are missing from the final Git branch:

- `REPAIRED_VM_REQUALIFICATION_20H_174NEW_V1_REPORT.md`
- `REPAIRED_RUNTIME_AUTHORITY.json`

The next 174 Goal first closes these from existing authority without rerunning science where possible.

## 7. 109 previous closure

Accepted branch:

`hrl/awma-109-native-workload-pipeline-20h-v1`

`a271a0e57d3cb61ee878e686e6e517082a9f97df`

Status:

`ACCEPTED_WITH_SCOPE`

E1:

`VALID_FAIL_CLOSED_STOP`

Reason:
no pre-existing hash-bound raw/AWQ activation/module-replay authority was found.

E3 was skipped only because the prior scheduling contract incorrectly made E1 closure a gate.

This dependency is removed in the new stage.

## 8. E1 historical authorities

Common raw/AWQ S2 token authority:

`e1d210d662ece6975648d04f628eb3f9e938117f`

```text
token_count = 2048
token SHA256 = 0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9
```

Raw revision:

`a09a35458c702b33eeacc393d103063234e8bc28`

AWQ revision:

`b25037543e9394b818fdfca67ab2a00ecc7dd641`

AWQ working runtime authority:

`2a05cadcbcc0e0b477b83d28aabe0c0aee270150`

Historical V8 proved raw replay and common token input but left AWQ module semantic binding unresolved.

The new E1 Goal solves this by binding directly to Python module objects and producing fresh activation authority.

## 9. Q30 E3 authority

Accepted S2/T2048 exact state/replay:

`ee67225edc8fc5868de585d38e0391cbeb755d9f`

This already records natural routing/state and exact layer replay.

E3 is scientifically independent of E1.

## 10. New coordinated stage

`AWMA_REPAIRED_HIT_PATH_AND_E1_AUTHORITY_V1`

Coordination branch:

`hrl/awma-hitpath-e1-authority-handoff-v1`

### 174-new

Stage:

`AWMA_REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V1`

Work:

1. provenance closeout;
2. repaired P34 lookup-latency envelope;
3. source/model hit-path semantics audit;
4. conditional Prefill GEMM non-Attention hit-path screen.

### 109

Stage:

`AWMA_E1_AUTHORITY_AND_MOE_DIAGNOSTICS_109_V1`

Work:

1. rebind exact model/token/runtime authority;
2. produce raw/AWQ live module activation authority;
3. fresh module replay equivalence;
4. E1 M1/M256 shape/implementation diagnostics;
5. independent Q30 N/P/U-active MoE routing diagnostic;
6. bounded profiling/decomposition only after local gates pass.

## 11. Frozen old stages

Do not redo or rewrite:

- producer qualification;
- Q05 identity;
- contiguous prefix capture;
- contextual replay;
- 109 V2.1 capture/native recon;
- generation-time global-access determinism;
- VM coverage defect proof;
- repaired Q05 requalification.

## 12. Forbidden

No architecture mechanism in this stage:

- no TLB capacity/port redesign;
- no PTW/PWC mechanism;
- no page-size/segmentation;
- no prefetch/speculation;
- no cache mechanism.

Lookup-latency changes on 174 are model-validity diagnostics only.
