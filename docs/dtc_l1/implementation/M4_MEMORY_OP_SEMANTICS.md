# M4 memory-operation semantics audit

Status: **SOURCE-BACKED — functional M4 work authorized only within these
observed semantics.** Core source reviewed at M3 final
`90cb35d5c4f9511a2eacb9e0e809a2d9c74ecb2c`.

## Common entrance and completion

- Global, local, and `param_space_local` memory instructions enter
  `ldst_unit::memory_cycle` in `src/gpgpu-sim/shader.cc`; the normal L1D path
  is `process_memory_access_queue_l1cache` then `L1_latency_queue_cycle`.
- `ldst_unit::issue` increments load register dependencies using the current
  coalesced access queue. `writeback_complete` releases scoreboard state and
  calls `warp_inst_complete` only when the final pending output dependency
  clears. Stores have no output-register pending-write counter.
- `PAPER_IO`, `PAPER_OO`, and sector mode currently divert **only cacheable
  loads**. Store/atomic/bypass therefore remain existing architectural paths
  until M4 adds a lifecycle wrapper; no DTC Tag/physical state is presently
  touched by those paths.

## Load

Cacheable global/local/param-local loads use L1D unless `CACHE_GLOBAL`, no
L1D, or global `gmem_skip_L1D` applies. In M2/M3, cacheable loads use the
dedicated DTC request/response/PIB path; bypass loads remain `m_next_global`
responses. A lower response eventually enters `writeback` and clears output
dependencies. This is the only operation class allowed to create DTC
Tag/physical/Ref state in M3.

## Store

- Stores use the normal L1D access path when not bypassed. The active smoke
  config string is `S:...:L:T:m:L:L,...`: sector cache, local-WB/global-WT
  write policy `L`, and `LAZY_FETCH_ON_READ` allocation policy `L`.
- `process_memory_access_queue_l1cache` increments store acknowledgements when
  a write event is sent. `L1_latency_queue_cycle` sends an immediate reply on
  write hit with no outgoing write, or on miss when the observed non-WT
  FETCH/LAZY policy did not send a write allocate; otherwise acknowledgement
  arrives through the normal response path and `store_ack`.
- The cache configuration parser is in `gpu-cache.h`; `data_cache` dispatches
  write-hit/miss behavior from the configured write and allocation policies.
  M4 must not change these policies or make Store allocate DTC physical lines.
- Store completion is acknowledgement/accounting based; it does not use the
  load scoreboard dependency mechanism.

## Atomic

- `cuda-sim.cc` maps `ATOM_OP` to `LOAD_OP`, but its default cache modifier is
  `CACHE_GLOBAL`; `memory_cycle` therefore takes the architectural L1 bypass.
- Atomic coalescing is handled by `memory_coalescing_arch_atomic`. Every
  generated `mem_fetch` retains `isatomic`; cache MSHR records mark atomic
  presence, and interconnect sizing treats atomics as data-carrying requests.
- The actual side effect is existing `warp_inst_t::do_atomic`, invoked at the
  source-backed memory-side return points (`ldst_unit` memory interface or
  global writeback). `decrement_atomic_count` occurs at writeback.
- M4 must never route atomic operations through DTC read Pending-hit merge.
  Each executed atomic remains on its existing bypass/lower path and must be
  counted independently.

## Fence and ordering

- `ldst_unit::cycle` recognizes fence instructions. Current code supports
  **only async proxy fences**: it sets `m_fence_async`, moves the instruction
  through the fence writeback client, and clears the flag when no later async
  proxy fence is in flight.
- The source explicitly asserts on a regular fence (`"Regular fence is not yet
  supported"`). M4 must not invent regular-fence semantics. Directed M4 fence
  tests are limited to source-supported proxy-fence ordering and record this
  limitation; unsupported regular fence is not a valid simulator workload.
- No fence allocates a DTC Tag or physical line in current source.

## Architectural bypass

`memory_cycle` sets `bypassL1D` for `CACHE_GLOBAL`, absent L1D, or global
`gmem_skip_L1D` unless explicitly `CACHE_L1`. It constructs normal `mem_fetch`
objects, pushes them to the interconnect, increments store requests for stores,
and sends returned reads to `m_next_global`; `cycle` deliberately skips L1D
fill for these replies. M4 must preserve this path and keep it distinct from
the out-of-scope thesis policy bypass.

## M4 implementation contract derived from the audit

1. DTC lifecycle tracking may wrap Store/Atomic/bypass for occupancy and
   retirement observability, but may not alter their request type, cache
   policy, side effect, acknowledgement, or architectural bypass route.
2. Only cacheable normal loads may use DTC Tag/physical/merge state.
3. Atomics are non-mergeable architectural operations; a counter/assertion
   must prove executed and completed atomic cardinality agree.
4. OO ready selection must not pass a source-supported unresolved async proxy
   fence in the same warp. No regular-fence behavior is synthesized.
