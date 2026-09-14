# C16 Recovery-V3 V12.1 — Route-B resume + GPU map closeout

Status: `AUTHORITATIVE_CHATGPT_REVIEW_2026-09-14_12XX+08`.

This is a coordination handoff only. The active scientific branch remains
`hrl/vm-c16-g-retry570-v0`; do not checkout/reset/merge this handoff branch into
the active worktree.

## Current reviewed heads

- Active GPU/science: `hrl/vm-c16-g-retry570-v0` at or beyond `5775690ff604b5f8e12a37379280b9c94708c28c`.
- Route-B CPU/dev: `hrl/vm-c16-g-routeb-producer-v0` at `c6b2bbb5b251059345beaf42438216db4a1987e8`.
- Route-B all-function V2 map batch: `be3aecfc5aa17bc334f9c63bb01596e92f313d78`.

## Review verdict

The Lane-C predicate/address correction is accepted: addresses are defined on
`executing_mask = active_mask & predicate_mask`; non-predicated instructions
set predicate mask equal to active mask. Multi-MREF is explicitly keyed by
`(static_index, mref_ordinal)` and bounded by `mref_count`.

`PRODUCER_Q0=PASS` means only the CPU/parser/binding contract is qualified. It
does **not** mean a device-side NVBit producer is ready. `GPU_Q1_READY=NO` is
therefore correct.

## Critical Lane-C fixes before final selection

1. `ROUTE_B_MAP_REQUESTS_V2` groups by exact full function and stores
   `phase_observations`. The current `route_b_selection.py` still expects the V1
   flat fields `phase/grid/block/shape_key/dtype_key`; it must be rewritten to
   consume V2 directly.
2. The current duration selection accidentally selects every mapped row. Freeze
   the actual smallest deterministic prefix reaching >=70% **per phase**.
3. Preserve per-geometry observations in V2. For each function/phase/geometry,
   retain at least `grid`, `block`, `shape_key`, `dtype_key`, `launch_count`,
   and `duration_ns`. Aggregate phase launch counts alone are insufficient to
   compute the requested memory proxy when one exact function appears with
   multiple geometries.
4. Compute memory proxy per phase as the sum over geometry observations:

   `launch_count_geometry * CTA_count(grid) * warps_per_CTA(block) * static_GLOBAL_MREF_count`.

5. Duration coverage denominator remains the whole frozen S0 phase census, not
   only successfully mapped rows. A `FAILED_CLOSED` map cannot silently increase
   the reported coverage fraction.
6. Memory-proxy >=80% cannot be claimed while an exact function remains
   unmapped/unknown. Resolve all V2 requests to `MAPPED_EXACT` or an explicit
   terminal failure; any unresolved failure remains a coverage gap.
7. Do not accept GPU VA/locality/cache/TLB/Route-B address results as selection
   inputs.

## Lane A — immediate GPU work

The V2 map batch now makes Route-B GPU work ready. Fetch the Lane-C branch
read-only and consume commit `be3aecfc5aa17bc334f9c63bb01596e92f313d78`.

Map every distinct exact Llama-S0 function requested by V2. Reuse an existing
map only after exact full/mangled function identity and actual owning code-object
identity match. Do not rerun already closed identical maps.

Publish a compact `ROUTE_B_MAP_RESULTS_V2.json` on the active scientific branch.
For every V2 request include:

- request id / exact full function / discovered full mangled function;
- owning code-object path + SHA256;
- static-map path + SHA256;
- static instruction count;
- GLOBAL+MREF instruction count;
- READ / WRITE / ATOMIC counts;
- MREF-count distribution, including any multi-MREF instruction;
- terminal status `MAPPED_EXACT` or `FAILED_CLOSED` with reason.

Do **not** fabricate code-object ownership. In particular, vendor/CUBLAS-looking
kernels must not automatically inherit `libtorch_cuda.so` merely because that
file was supplied to the runner. Resolve the actually loaded owning module/file
or mark code-object identity unresolved/failed closed.

When Route-B map work is temporarily blocked, immediately execute the global GPU
fallback queue (campaign-scoped Qwen0/Qwen7 G1, newly unlocked R4/R5/R6, then
Llama S1-S4). CPU-side selection/producer work is never a GPU-idle reason.

## Lane C — resume now

Resume the paused Goal. Do not wait for Lane-A map results before doing CPU/dev
work.

Priority order:

1. Fix V2 per-geometry observations and V2-aware final-selection code, including
   the real 70% duration prefix and 80% memory-proxy proof.
2. Keep the reviewed predicate/executing-lane and multi-MREF semantics.
3. Implement the actual versioned NVBit-1.7.5 append-only Route-B device producer
   (exact function, code-object SHA, static-map SHA, sorted `(static_index,
   mref_ordinal)` whitelist, CTA/warp, access kind, width, masks, executing-lane
   VAs, `OBSERVED_CALLBACK_ORDER`, terminal/overflow/drop, host cap).
4. Extend CPU Q0 fixtures as needed, but do not claim GPU Q1 ready until a buildable
   device producer and tiny-CUDA Q1 handoff exist.
5. Poll/fetch the active branch read-only for `ROUTE_B_MAP_RESULTS_V2.json`.
   Once all V2 requests are terminal, freeze the final selected-function manifest
   and immediately publish the Q1 GPU handoff for Lane A.

Required Lane-C checkpoint fields:

`ROUTEB_DEV_COMMIT`
`ROUTEB_MAP_REQUESTS_V2_COMMIT`
`V2_SCHEMA_FIXED`
`DURATION_PREFIX_70_FIXED`
`MEMORY_PROXY_80_PROOF_READY`
`PRODUCER_Q0`
`DEVICE_PRODUCER_BUILD_READY`
`ROUTEB_SELECTION_MANIFEST_COMMIT`
`GPU_Q1_READY`

## Lane B / Lane D

Continue their existing V12 goals. Lane B remains storage/safety first with
copyback deferred while free space is safe. Lane D continues producing frozen
GPU-ready bindings/authority rows. Neither lane may mutate the active GPU
worktree.
