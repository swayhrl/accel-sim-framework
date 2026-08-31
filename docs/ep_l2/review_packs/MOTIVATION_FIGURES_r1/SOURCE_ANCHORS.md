# Motivation telemetry source anchors

Frozen simulator provenance: Core `2a6a31591bc42023e5997cca969e4b672efe0405`;
Framework runtime `02f36816f60afcff55e910cdef2b60937e691cdc`.

| Concern | Anchor | Review point |
|---|---|---|
| Reference, epoch-local stack, post-eviction evidence | `src/gpgpu-sim/l2cache.cc:1857-1917` | 128-B normalized frontend demand references; primary state resets per epoch. |
| Demand-miss scope and exclusive source order | `src/gpgpu-sim/l2cache.cc:1919-1962` | Reads and writes are eligible; writebacks/fills are excluded; one blocker per attempted exact admission. |
| WB create and packet identity | `src/gpgpu-sim/l2cache.cc:1964-1977`; `src/gpgpu-sim/gpu-cache.h` | Active shadow state is keyed by the real WB `mem_fetch*`, not an address. |
| WB release boundary | `src/gpgpu-sim/l2cache.h:682-687`; `src/gpgpu-sim/l2cache.cc:1987-2002` | Release follows successful enqueue into the per-slice L2->DRAM queue, before DRAM issue and `set_done`. |
| Terminal active-at-snapshot evidence | `src/gpgpu-sim/l2cache.cc:2005-2019` | Each application record reports live packet-keyed WBUF occupancy. |
| Streaming parser and terminal fail-close | `util/ep_l2/parse_epl2_motivation.py` | One-pass last cumulative application record selection; exactly 64 slices; fail on an open terminal shadow lifecycle. |
| Stage-6 aggregation | `util/ep_l2/aggregate_epl2_motivation.py` | Revalidates every parser manifest and closure before copying any formal table or rendering a figure. |
