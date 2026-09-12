# C15 cross-model findings — evidence bounded

Lane A's source-bound static library covers ten deployment configurations from
nine conceptual model lineages, including the Qwen2.5-7B raw/AWQ storage pair.
Three configurations have complete, range-verified Safetensors-header storage
catalogs; seven are configuration-only and intentionally have no inferred weight
byte count. Standard-KV formula curves are available for seven configurations.
DeepSeek-V2-Lite is explicitly tagged `MLA_OR_COMPRESSED` and is not passed to the
standard-KV adapter; two other configurations lack sufficient static facts for a
curve. These are static storage/layout facts only, never GPU virtual/physical
address, cache, TLB, timing, cycle, or speedup facts.

The hash-bound B publication reports a capability-limited capture lane: it has no
new native GPU run, no native timing, no SASS, and no capture trace. Its
trace-header catalog is retained only as an evidence-boundary result.

The hash-bound C publication validates historical C12/C13 evidence and reports
`SAMPLER_NOT_QUALIFIED`; its primary cheap-selector error remains outside the
pre-registered qualification expectation. C records no new simulator/GPU/trace
measurement, does not change thresholds, and classifies the cross-model dynamic
comparison as pending the missing committed native evidence.

Consequently, C15's static diversity is published and the absence of runtime
evidence is audited, but no cross-model dynamic behavior, translation pattern,
cache/TLB outcome, performance ranking, or upgrade authorization is concluded.

| Category | Statement | Sources | Coverage / object | Evidence tier and extrapolation boundary |
| --- | --- | --- | --- | --- |
| Static pattern | Storage and KV representation diversity is source-bound, not runtime-characterized. | A `MODEL_REGISTRY.tsv`, `TENSOR_STORAGE_CATALOG.tsv`, `KV_REPRESENTATION_AUDIT.tsv` | 10 deployment configurations; weights/KV formulas | `STATIC_DERIVED`; no phase, operator, cache, address, or timing extrapolation. |
| Static exception | The Qwen2.5-7B raw/AWQ pair has distinct verified physical storage encodings; the AWQ catalog separates packed I32 payload from F16 scale/zero metadata. | A `TENSOR_STORAGE_CATALOG.tsv`, `WEIGHT_STORAGE_BREAKDOWN.tsv` | 2 deployments of one conceptual lineage; weight storage | `STATIC_DERIVED`; not a dtype-causal or performance comparison. |
| Unknown dynamic class | No pair of comparable real deployments and no qualified sampler exists for a dynamic comparison. | B `CAPABILITY_MATRIX.tsv`, `KERNEL_CATALOG_TRACE_HEADER_ONLY.tsv`; C `METRIC_QUALIFICATION.tsv`, `FINAL_REPORT.md` | 0 new native deployments; no phase/operator/object dynamic metric admitted | B is header-only and C is retrospective calibration; no `KNOWN_CLASS_PROFILED` classification. |
