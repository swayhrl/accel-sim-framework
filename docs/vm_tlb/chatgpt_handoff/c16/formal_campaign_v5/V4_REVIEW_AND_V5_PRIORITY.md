# C16 V4 review and V5 priority

## Accepted V4 outcome

Producer authority: `7b3e99b5bc518353c15aa808d777b0f430d4bb20`.

Accepted decision: `C16_FORMAL_EXPANSION_V4_PASS_WITH_DEFERRED_AWQ`.

V4 established:

- Qwen0 `S3_TEXT` B1/T8192/D16 admitted and NSYS-censused;
- S3 Prefill Attention direct-GLOBAL-MREF complete-set formal run Pipeline-ACKed;
- S4_STRUCTURED admitted/censused and retained as a current-campaign control because it introduced no new attention/GEMM family;
- AWQ fused recovery is externally blocked by unavailable source; do not spend repeated GPU time retrying network acquisition in every campaign;
- raw Qwen2.5-7B S2 is confirmed not admissible on the 16GB RTX4080 under the exact-safe recovery policy; no further 109/16GB retries unless the hardware/resource condition changes.

## Critical V4 scientific finding

The direct tracer is not a complete global-memory tracer for several representative SM89 kernels.

Full-function static audit found:

- `Q05_PREFILL_GEMM`: direct=141, special=23, coverage unresolved;
- `Q05_PREFILL_ATTN`: direct=29, special=54, coverage unresolved;
- `Q05_DECODE_EARLY_HEAVY`: direct=16, special=0, `ALL_DETECTED_GLOBAL_PATHS_COVERED`;
- `Q05_DECODE_KV_ATTN`: direct=41, special=89, coverage unresolved.

The important address-bearing special path is `LDGSTS...` (`GLOBAL_TO_SHARED`). `LDGDEPBAR` is a memory-control/dependency instruction and must not be counted as an address-bearing traffic path. V5 must split these two categories explicitly.

Existing V2/V3/V4 formal evidence remains valid but is scoped to `DIRECT_GLOBAL_MREF_SCOPE_ONLY` for functions with live special paths.

## V5 priority

Before broad cross-model replication, qualify and capture the address-bearing `LDGSTS` global-source path.

Priority targets:

1. S2 Prefill GEMM special path;
2. S2 Prefill Attention special path;
3. S2 Decode KV/Attention early special path;
4. S2 Decode KV/Attention late special path;
5. S3 Prefill Attention special path if the same special family executes at long context.

Decode Early Heavy does not need a special-path recapture because its audited function has no special global path.

## Evidence boundary

A successful V5 special-path campaign may establish set-level global-path coverage for the selected exact function/occurrence, but separate replays still do not establish:

- cross-path hardware order;
- whole-kernel reuse distance;
- a single physical absolute-VA stream;
- cross-replay absolute-VA union.

Use per-shard/per-path evidence and same-process address context. Use object-relative normalization only when semantic object identity is independently closed.

## Deferred items

- AWQ: `EXTERNAL_DEPENDENCY_DEFERRED` until source becomes available; do not retry network acquisition as a blocking subgoal.
- raw7B on 109: `NOT_ADMITTED_MEMORY_CONFIRMED_16GB`; revisit only on a larger-memory capture node or changed hardware resource condition.
- S4 batch axis: `CONTROL_ONLY_CURRENT_CAMPAIGN`, not a proof that batch has no memory-behavior effect. Revisit after path coverage is complete if batch sensitivity is needed for the final characterization matrix.
