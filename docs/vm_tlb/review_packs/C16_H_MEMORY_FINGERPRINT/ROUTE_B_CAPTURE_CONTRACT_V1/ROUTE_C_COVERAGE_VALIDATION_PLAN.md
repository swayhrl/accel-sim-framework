# Route C coverage-validation tier plan

Route C is a small validation tier, not the default all-model capture path. It
asks whether Route B's formally selected representative functions account for a
useful fraction of one whole phase's observed memory activity and structural
footprint. It does not promote Route B samples into whole-phase TLB/cache
claims.

The first candidate is Llama S0 because its model/runtime identity, recovery
path, two static maps, and Route A evidence are the most mature. Only after a
Route B producer passes its canary and an exact S0 native census freezes the
candidate list may an explicitly authorized Route C run proceed.

Minimum design: one frozen Llama S0 native run, one predeclared Prefill launch
window and three predeclared Decode2/3/4 windows, with launch inventory and
phase boundaries captured before address tracing. The bounded phase-wide
reference must use the same GPU-VA, active-mask, width, memory-space, and
terminal schema as Route B. It has independent 4GiB/20-minute caps and may use
deterministic launch/static-range partitions. If the full-tracer fallback
cannot meet them, Route C remains unrun rather than silently sampling by
outcome.

For each phase, report Route B / Route C ratios for explicit-GLOBAL event
count, requested-byte proxy, unique exact VA count, 128B line count, and
4KiB/64KiB/2MiB observed-VA buckets. State all denominator partitions,
uncovered kernel classes, and raw completeness. Compare structural ratios only:
no cross-process absolute-VA Jaccard, physical-address, TLB-miss, cache-miss,
or global-order inference is permitted.

Route C is required before claiming Route B represents a phase, when the
selected-prefix duration mass is below 70%, when a class is absent/unmapped,
when canary results differ materially from census assumptions, or before
generalizing the Llama procedure to Qwen/DeepSeek.
