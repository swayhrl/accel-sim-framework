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

P subsequently consumed the previously queued, hash-closed Qwen0.5 S2 P2
diagnostic at G commit `f7d1c2cb4d41b26472893a7d23466402c8e92e70` after the
clean P1 catalog became available. Local export qualification and direct-map
reproduction passed. Of 70,224 diagnostic kernels, 33,184 are direct within
that diagnostic report; clean reconciliation still has zero unique candidates:
173,901 are structurally ambiguous and 1,659 have no candidate. All 175,560
clean S2 launches remain explicit `UNKNOWN`. Its compact
[P2 receipt](../../../review_packs/C16_P_NATIVE_POSTPROCESS/P2_QWEN05_S2_SEMANTIC_RECEIPT.json)
binds the map, coverage, audit, raw, and contract hashes. This confirms rather
than changes the capability-limited C checkpoint's UNKNOWN-only semantics.

Capability boundary: Llama and Qwen0.5 are train-available. Qwen7 raw is
`SKIPPED_RESOURCE / RESOURCE_UNAVAILABLE_ON_RTX3090` and has no P native rows.
Qwen7 AWQ remains `HOLDOUT_PENDING_FREEZE`; P exposes no AWQ timing, launch,
heavy-tail, or semantic outcome to C.

P remains in local-CPU-only event-driven mode. It polls the G remote branch at
bounded intervals, performs no GPU work, makes no empty commits during quiet
intervals, and will consume only a subsequent exact commit plus closed
manifest/hash event.

## C selector-freeze post-freeze AWQ release

Status: `C16_P_AWQ_CHEAP_CATALOG_READY_POST_FREEZE`.

P verified the immutable C selector-freeze commit
`dd70d5faafb81ac2b921b49bb0606bcf2d9972a7` (`C16-C: freeze primary
Selector-R P train plan`) and its descendant C head
`941229c6eacef28e4e782e37f87c738458071d39` before opening any sealed AWQ
clean catalog. The frozen source is `SELECTOR_R` / `B48`; its selector source
SHA is `acb30e322de5f77a8fb33c5d63666e23c9c0c8097322e9736e1038510af8c301`
and its policy SHA is
`9f35e7b0809fdfb24352c46b7e43547238d9f0b1615dd39bbe3df934b2d2a3ad`.
C's frozen protocol explicitly declares `awq_outcomes_read=false` and that
candidate outcomes were not used before the freeze.

The exact P materializer commit is
`65ace4c138b77d6d5f8f1ab13b74b87f4875c6a3`. Its compact
[post-freeze receipt](../../../review_packs/C16_P_NATIVE_POSTPROCESS/P_AWQ_CHEAP_CATALOG_RECEIPT.json)
has SHA-256 `687da5a2c88de2d7328bc2da265ffa8248e896a763cf521eb8f9091250fa8627`.
It binds the four sealed P AWQ producer commits, raw report identities, source
catalog hashes, C freeze/train-input closure, and the unchanged P
`JOIN_KEY_CONTRACT` SHA. The immutable P receipt-release commit is
`5fa7e66e4afa0d3e6a976e69ce9e765139d6f2c2`.

The hash-closed Git-external apply view is
`artifacts/c16_p_native_postprocess/post_freeze_awq_cheap_catalog_dd70d5fa_v2`:
it retains all 841,120 report-scoped physical launches (423,674,371-byte TSV;
18,357,361-byte deterministic gzip). It provides only the frozen selector's
cheap structural fields and profile/report bridge. All rows are explicit
`UNKNOWN` semantics; no direct-semantic diagnostic was read. No NCU/NVBit,
counter, trace, candidate performance, or post-hoc ranking information was
read or exposed. S3 and S4 remain `SKIPPED_RESOURCE` without a shape, context,
batch, or offload substitution and create zero rows.

P now runs a separate bounded C selector-freeze observer alongside the G event
watcher. The observer is read-only and records only a new immutable C head and
candidate freeze closure; it cannot apply a selector or consume an AWQ payload.
