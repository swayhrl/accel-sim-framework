# C16-P local postprocess report

Status: `C16_P_EVENT_DRIVEN_NATIVE_POSTPROCESS_ACTIVE`.

P consumed only G's frozen, hash-closed native-event publication at
`e3d49cea82a5730ccc4d796219acd6ff68aa65a0`. Its publication manifest SHA-256
is `ade888dab5aac6aa3090df7e7aec9395b6f5a1699ca56e02461f19d95d2d1ebc`.
All eight Llama/Qwen0.5 clean reports passed producer/event/receipt/transfer
closure, local Nsight export (2024.2.3), and the report-scoped physical launch
join audit.

P committed the materialized catalog as
`184f1480a9795d5aa12509f32c8f1e7f5fc42f69`. The C-facing immutable checkpoint
is [C16_P_NATIVE_CATALOG_READY_FOR_C_CONSUMPTION_CAPABILITY_LIMITED.json](../../../review_packs/C16_P_NATIVE_POSTPROCESS/C16_P_NATIVE_CATALOG_READY_FOR_C_CONSUMPTION_CAPABILITY_LIMITED.json).
It binds the exact P and G commits, raw/profile/catalog closure, semantic-map
and coverage hashes, and the frozen JOIN_KEY_CONTRACT SHA.

The retained physical population is 722,800 launches: 286,480 Llama and
436,320 Qwen0.5. The uncompressed catalog is 583,919,960 bytes; the
deterministic gzip is 22,689,209 bytes. Both are raw-outside-Git and hash
indexed. Required C join keys are complete, and the composite physical key has
zero duplicates. Report-local stream and correlation IDs collide across runs,
so bare stream/correlation IDs and cross-run timestamps remain forbidden.

Semantic coverage is `COVERAGE_LIMITED`: all 722,800 catalog launches are an
explicit `UNKNOWN` semantic stratum. The prior Llama S2 direct-semantic P2
event was verified and remains available as direct evidence inside its
diagnostic report, but its strict clean↔diagnostic structural mapping produced
no uniquely eligible clean launch; it does not change the clean catalog. P
used no kernel-name inference, timestamp matching, or bare local-ID join.

Capability boundary: Llama and Qwen0.5 are train-available. Qwen7 raw is
`SKIPPED_RESOURCE / RESOURCE_UNAVAILABLE_ON_RTX3090` and has no P native rows.
Qwen7 AWQ remains `HOLDOUT_PENDING_FREEZE`; P exposes no AWQ timing, launch,
heavy-tail, or semantic outcome to C.

P remains in local-CPU-only event-driven mode. It polls the G remote branch at
bounded intervals, performs no GPU work, makes no empty commits during quiet
intervals, and will consume only a subsequent exact commit plus closed
manifest/hash event.
