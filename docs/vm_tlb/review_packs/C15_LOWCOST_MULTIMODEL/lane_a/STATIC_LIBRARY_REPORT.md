# C15 lane A static-library report

## Scope and coverage

The candidate plan was frozen before any candidate result was read. It requested
12 source roles. Ten immutable model revisions were resolved and entered in
`MODEL_REGISTRY.tsv`: nine model lineages plus two deployment configurations of
the Qwen2.5-7B lineage (raw and AWQ). The AWQ configuration is reported as a
configuration/storage pair, not as a second model.

`TENSOR_STORAGE_CATALOG.tsv` has exact Safetensors header-derived storage only
for Qwen2.5-0.5B-Instruct, Qwen2.5-7B-Instruct, and
Qwen2.5-7B-Instruct-AWQ. Their static payload interval unions are respectively
988,065,536 B, 15,231,233,024 B, and 5,570,747,392 B. The AWQ catalog keeps
packed `qweight` (I32) separate from scales/zeros (metadata); this is a
checkpoint-file storage observation, not a runtime-memory, GPU-physical-address,
or speed claim.

The other seven source-bound configurations remain `STATIC_CONFIG_ONLY`, because
their index/header operation timed out, hit a bounded transport failure, or did
not expose a usable Safetensors header. Qwen3-0.6B and Falcon-7B did not yield a
source-bound configuration in the final bounded attempt. These are coverage gaps,
not zero-sized models or negative architectural findings.

## KV and pages

Seven configurations have enough config evidence for a standard-KV static payload
curve at B={1,8} and T={128,2048,8192}; the dtype is explicitly an assumption
drawn from the config, with reserved blocks excluded. DeepSeek-V2-Lite has a
config-evidenced MLA/compressed representation and is marked
`UNSUPPORTED_REPRESENTATION`, not run through the ordinary formula.

The 4-KiB, 64-KiB and 2-MiB counts in `STATIC_FOOTPRINT.tsv` apply only to
header-known disk-offset ranges under an explicitly per-shard file-layout proxy.
Disk offsets are not virtual or physical GPU addresses; the values do not estimate
TLB working sets, TLB misses, cache misses, timing, or dynamic active experts.

## Acceptance boundary

The bounded reader, schema, offset, packed-storage, alias, KV, page, selection,
atomic-publish and operation guards passed their applicable fixture checks. The
scientific completeness of checkpoint-file static storage is `INCONCLUSIVE` (3/10
configuration headers), while source-bound configuration/KV metadata coverage is
10 configurations. No conclusion about cross-model dynamic behavior is made.

`intermediate_sizes` for the three MoE configurations is retained as the observed
config scalar only. It is not a complete routed/shared-expert width description
and is excluded from later MoE clustering; see `MOE_INTERMEDIATE_LIMITATIONS.md`.
