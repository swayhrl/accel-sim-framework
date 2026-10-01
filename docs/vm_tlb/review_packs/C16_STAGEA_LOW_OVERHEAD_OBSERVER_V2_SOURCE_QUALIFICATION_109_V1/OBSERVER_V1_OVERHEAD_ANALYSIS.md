# Observer V1 overhead analysis

## Authority and preservation

This analysis is derived from runtime-qualification commit
`3f62f909a474e4c56695ffacf36ddcb5d7b5f147` (tree
`4b9a1c07ee6b16997957d804f26ab57d0ca3853e`). The frozen V1 neutrality
receipt is `INSTRUMENTATION_NEUTRALITY.tsv`, SHA256
`fd3f8ac88509d15f670f7bec8c3ad3d3cf1bef85ad40a6fb570cca8f35b20331`.
No V1 raw data, result, or decision is modified by this qualification.

## Frozen V1 result

| Target | Semantic occurrences | OFF median (ms) | ON median (ms) | Absolute delta (ms) | Gate (ms) | V1 result |
|---|---:|---:|---:|---:|---:|---|
| QWEN_BF16 | 576 | 67.814041 | 69.327521 | 1.513480 | 6.781404 | PASS |
| QWEN_AWQ | 576 | 55.088301 | 63.181815 | 8.093514 | 5.508830 | INSTRUMENTATION_NON_NEUTRAL |
| OLMOE | 1536 | 256.068688 | 304.745151 | 48.676463 | 25.606869 | INSTRUMENTATION_NON_NEUTRAL |

The unchanged gate is
`abs(median_on - median_off) <= max(5 ms, 0.10 * median_off)`.

## V1 source structure

Each semantic occurrence created and recorded two CUDA Events around the
module while also pushing and popping an NVTX range. Qwen therefore executed
1,152 per-occurrence CUDA Event records per observed request; OLMoE executed
3,072. These are in addition to the two request-level CUDA Events used for the
outer native wall.

Dividing the observed median delta by the occurrence count gives 2.628 us per
occurrence for BF16, 14.051 us for AWQ, and 31.690 us for OLMoE. This is only a
normalization diagnostic: it does not causally assign the full delta to Event
creation/recording, and it does not revise any frozen V1 conclusion.

## Design implication

The V1 source made an avoidable GPU-timestamp operation part of every observed
semantic occurrence. V2 removes only those per-occurrence CUDA Events. It
retains module-level NVTX ranges, ordinals, input/output shapes, and the outer
request CUDA Event pair. The neutrality standard is not relaxed.

QWEN_AWQ is the sole proposed GPU requalification target because its graph
correctness and backend identity already passed and its remaining MP05 blocker
is observer neutrality. OLMoE is excluded pending the separate Lane6 graph
correctness diagnosis. QWEN_BF16 is not needed for the first bounded canary.
