# M4 memory-operation semantics audit

Status: **SOURCE-LIMITED BOUNDARY — M4 RESUMED.** The source-backed audit
found that the required source-supported proxy-fence instruction is not
reachable from the current PTX input frontend. Under the authorized
`goal/M4_FENCE_REACHABILITY_RESOLUTION.md`, this is the source-limited
boundary for F01--F03 rather than an active M4 stop: F01--F03 are
`SOURCE_UNREACHABLE_NA` after F00A--F00D pass. Core source was initially
reviewed at M3 final `90cb35d5c4f9511a2eacb9e0e809a2d9c74ecb2c`; the
limitation is independent of the subsequent M4 sidecar implementation.

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

### HARD failure: the PTX frontend cannot construct the audited fence

The LD/ST code has a `FENCE_OP` path, but the actual PTX frontend used by this
build cannot produce it:

- `src/cuda-sim/ptx.l` recognizes `membar` as `MEMBAR_OP`, and its exhaustive
  opcode table has no `fence`/`fence.proxy` rule and no rule returning
  `FENCE_OP`.
- `src/cuda-sim/ptx.y` has no `FENCE_OP` token/production/mapping.
- A repository-wide source search finds `FENCE_OP` only in the dynamic
  instruction/LDST handling, not in the PTX lexer or parser.
- The second source audit confirms that this is not a one-line lexer omission:
  the static `ptx_instruction` opcode/decode path has no fence opcode case,
  and no source path calls `set_proxy_fence()` or
  `set_fence_proxy_kind()`. The existing dynamic fields therefore have no
  PTX-originating producer.

This is a reachability failure, not a missing test harness: no normal loaded
PTX can enter the only source-supported proxy-fence path. A regular PTX
`membar` is a different `MEMBAR_OP`; attempting to equate it with the proxy
fence would invent a semantic substitution, and regular `FENCE_OP` itself
asserts unsupported in `ldst_unit::cycle`.

Reproduce the evidence from the Core checkout:

```sh
rg -n "fence|FENCE_OP" src/cuda-sim/ptx.l src/cuda-sim/ptx.y
rg -n "FENCE_OP|set_proxy_fence|set_fence_proxy_kind" src/cuda-sim src/abstract_hardware_model.h
rg -n "membar|OPCODE" src/cuda-sim/ptx.l
rg -n "FENCE_OP|is_proxy_fence" src/abstract_hardware_model.h src/gpgpu-sim/shader.cc src/gpgpu-sim/shader.h
```

The first two commands show no static producer for a fence instruction while
the latter commands show the distinct `membar` and dynamically unreachable
`FENCE_OP` paths. Therefore
F01 (`LoadFenceLoad`), F02 (`StoreFenceLoad`), and F03
(`AtomicFenceLoad`) cannot be executed under the required current-source
semantics. Under the later authorized reachability resolution, F01--F03 are
`SOURCE_UNREACHABLE_NA` after F00A--F00D rather than active failures. Adding
parser/semantic support remains an architectural extension outside M4; M5 is
still forbidden.

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

## M4 implementation evidence under the source-limited boundary

The Core adds a sidecar external-dependency entry for Store, Atomic, bypass
Load, and proxy-fence lifecycle observation. It deliberately does not alter
their source request/cache/acknowledgement/side-effect routes and allocates no
DTC Tag/physical state for them. Whole-line IO, OO, and sector VecAdd
regressions passed with eight Stores admitted/completed/retired exactly once;
the available atomic-contention workload passed with one Atomic admitted,
completed, and retired exactly once. These checks do not implement or
substitute fence semantics. The authorized resolution instead requires
F00A--F00D plus the source-reachable Load/Store/Atomic/bypass validation
domain; see the M4 review pack for the acceptance evidence.
