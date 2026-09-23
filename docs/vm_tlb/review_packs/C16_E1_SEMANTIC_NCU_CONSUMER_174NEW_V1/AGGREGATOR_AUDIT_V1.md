# E1 Semantic NCU Consumer Aggregator Audit V1

## Scope

Reviewed:

- `util/vm_tlb/c16/e1_semantic_ncu_consumer/aggregator.py`
- `test_aggregator.py`
- `METRIC_AGGREGATION_CONTRACT.json`

from:

`hrl/c16-e1-semantic-ncu-consumer-prep-174new-v1@92fa940cc7ca6e3e8eb7ca628e4d28634e05ac35`

## Verdict on the original prep implementation

The original implementation had the correct high-level scientific semantics:

- semantic range is the aggregation unit;
- multi-kernel AWQ ranges are supported;
- additive byte metrics are summed;
- utilization is retained per-kernel;
- ambiguous range occurrence fails closed;
- exact unit mismatch fails closed.

However, it was not yet strong enough to treat as final authority without hardening.

### Gaps found

1. Non-finite metric values such as NaN/Inf were accepted by `float()`.
2. Duplicate CSV header names were not rejected.
3. One `kernel_id` could map to different kernel names without failure because the grouping key used `(kernel_id,kernel_name)`.
4. Normalization denominator columns could be partially blank and still pass.
5. Required normalization denominators were not explicitly enforced positive/present.
6. Duplicate metric rows were rejected, but adversarial coverage was not tested.
7. Missing additive metrics on one in-range kernel were handled correctly by code but not explicitly tested.
8. Cross-point comparison did not verify unit consistency.
9. Cross-point comparison could divide by zero.
10. Floating summation did not preserve exact decimal totals.
11. The preregistered metric policy hard-coded example NCU metric names before node109 runtime availability was known; this is unsafe, especially for L1/TEX.
12. Most importantly, the parser consumes a **normalized semantic CSV schema**, not raw NCU CLI CSV directly. End-to-end independence therefore additionally requires 174-new to independently normalize from, or verify against, producer-preserved raw NCU/range evidence. Producer-authored semantic labels alone are insufficient.

## Hardening applied

Branch:

`hrl/c16-e1-semantic-ncu-consumer-hardening-v1`

Changes:

- strict duplicate-header rejection;
- canonical range-occurrence parsing;
- exact kernel-id -> kernel-name consistency;
- Decimal-based additive sums with exact string preservation;
- NaN/Inf rejection;
- required positive normalization denominators;
- rejection of partially missing denominators;
- explicit non-additive coverage reporting;
- cross-point unit validation;
- zero-denominator ratio reported as undefined rather than inf/NaN;
- expanded adversarial tests;
- metric aggregation contract V2 requires runtime-resolved exact metric names/units and raw NCU provenance.

## Remaining gate before final scientific use

The hardened aggregation core can be accepted as the intended consumer logic.

But final end-to-end correctness must still be checked against the actual node109 producer artifacts:

1. raw NCU export format and SHA;
2. exact installed NCU metric names/units;
3. exact NVTX/range identity fields;
4. how `kernel_id` is derived and whether it uniquely denotes one logical kernel launch;
5. independent 174-new normalization/verification of every semantic CSV row against the raw export.

Until those producer artifacts exist, no claim is made that a specific raw NCU CLI CSV layout is already parsed correctly.

