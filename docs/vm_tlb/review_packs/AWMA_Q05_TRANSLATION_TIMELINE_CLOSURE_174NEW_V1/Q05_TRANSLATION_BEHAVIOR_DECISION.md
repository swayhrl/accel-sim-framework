# Decision

Classification: `MIXED`, with `PREFILL_BURST_FANOUT` and `PERSISTENT_POST_FILL_REUSE` evidence.

The 10k zero-L2-hit aggregate is substantially pre-fill/outstanding behavior: 125 miss requesters collapse to 19 allocations plus106 merges. Fanout persists to 50k/full, while new keys grow from19 to104 to240. Post-fill REQUEST activity is substantial, but this minimal diagnostic schema does not separately emit L1-versus-L2 post-fill outcomes; that dimension remains unavailable rather than inferred.

No capacity pressure conclusion is supported: full key count is240 and no eviction/reuse causal evidence is added. No mechanism experiment is authorized.