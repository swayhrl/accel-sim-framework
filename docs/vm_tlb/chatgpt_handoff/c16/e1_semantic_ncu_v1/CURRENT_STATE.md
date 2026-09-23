# C16 E1 Semantic NCU Selector — Current State V1

## Accepted E1 closure

Producer:
`hrl/c16-e1-clean-baseline-109-v1@8988d6108ff8bdca180a14cec2fe769df45b09f1`

Independent consumer:
`hrl/c16-e1-clean-baseline-consumer-prep-174new-v1@59ddb8ba2a33ef12b73bfc859f3a994e0b4ef4ca`

Accepted conclusion:

> Under byte-identical FP16 activation inputs, Qwen2.5-7B RAW_FP16 vs AWQ shows a strong operator × M-shape × deployed-implementation interaction.

Independent clean ratios:

- q_proj: R_awq M1=0.9801257351, M256=1.3044559790, abs(I)=0.2858604939
- down_proj: R_awq M1=0.5010500375, M256=1.2758391297, abs(I)=0.9346534106
- up_proj: R_awq M1=0.4002389919, M256=1.8687647899, abs(I)=1.5409711030

CODE down_proj holdout reproduces the same qualitative direction.

AWQ down_proj path transition:
- M1023: GEMM_QUANTIZED
- M1024: DEQUANTIZE_PLUS_TORCH_MATMUL

RAW_FP16 remains dense Linear.

## Current blocker

The pre-registered NCU role is `up_proj`, but the first NCU attempt closed as:

`NCU_SELECTOR_UNRESOLVED`

No L1/L2/DRAM traffic values were claimed.

The next stage does not broaden the workload matrix. It resolves the semantic NCU selector at the exact module-call boundary and, only if qualified, collects bounded traffic metrics for:

- up_proj M1 RAW_FP16
- up_proj M1 AWQ_FP16_INPUT
- up_proj M256 RAW_FP16
- up_proj M256 AWQ_FP16_INPUT

The scientific unit is the **semantic module invocation**, not one arbitrarily selected GPU kernel.

For AWQ, one semantic module call may legitimately launch multiple kernels. If so, all kernels belonging to the uniquely qualified module-call range are part of the traffic sum.

## Claim boundary

This stage may establish:
- semantic-module kernel composition;
- L1/L2/DRAM traffic associated with the exact up_proj module invocation;
- how that traffic differs across M1/M256 and RAW_FP16/AWQ.

It still does not establish:
- cache/TLB causality;
- why a specific cache policy would help;
- pure quantization causality;
- end-to-end model speedup.

No NVBit/full-address trace/mechanism is authorized in this stage.


---

## 174-new consumer prep completed

Parallel consumer/prep is complete at:

`hrl/c16-e1-semantic-ncu-consumer-prep-174new-v1@92fa940cc7ca6e3e8eb7ca628e4d28634e05ac35`

Closed prep facts:

- semantic selector design audit PASS;
- scientific unit fixed as one complete `up_proj` semantic module invocation;
- AWQ multi-kernel module calls allowed;
- additive byte/event metrics may be summed only inside the uniquely qualified range;
- utilization/percentage metrics remain per-kernel;
- ambiguous/missing semantic range fails closed;
- parser/aggregator synthetic tests PASS;
- selected points remain frozen to up_proj M1/M256 × RAW_FP16/AWQ;
- no producer traffic/selector values were populated because producer branch was absent at the single fetch.

174-new is now stopped at:

`READY_FOR_E1_SEMANTIC_NCU_109`

When node109 producer closes, resume the same 174-new consumer branch rather than rebuilding prep.


---

## Consumer aggregator audit/hardening

The original 174-new prep implementation at:

`hrl/c16-e1-semantic-ncu-consumer-prep-174new-v1@92fa940cc7ca6e3e8eb7ca628e4d28634e05ac35`

had correct high-level semantic aggregation intent but was reviewed and hardened before final producer consumption.

Use the hardened consumer authority:

`hrl/c16-e1-semantic-ncu-consumer-hardening-v1@396233ca250c20be834aa0c50d2504e6017953bc`

Audit:

`docs/vm_tlb/review_packs/C16_E1_SEMANTIC_NCU_CONSUMER_174NEW_V1/AGGREGATOR_AUDIT_V1.md`

Important final-consumption rule:

- the aggregator's normalized semantic CSV is not, by itself, sufficient provenance;
- 174-new must independently normalize from, or verify every normalized row against, producer-preserved raw NCU export/range evidence;
- exact metric names/units must be resolved from the installed node109 NCU evidence, not from preregistered aliases;
- the hardened V2 aggregation contract supersedes the original hard-coded metric-name policy.

