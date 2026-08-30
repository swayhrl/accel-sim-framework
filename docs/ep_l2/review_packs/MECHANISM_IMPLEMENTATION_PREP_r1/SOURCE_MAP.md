# Source Map

All paths/lines below refer to core C7e `ece1a3a77c5628763e0a4605bfd1c639ee6a1495`, unless noted.

## Payload state and static boundary

| concern | source anchor | observed implementation fact |
|---|---|---|
| storage/roles | `src/gpgpu-sim/gpu-cache.h:2052-2410`, `ep_l2_payload_store` | constructor creates `m_resident.resize(1024)` and `m_bypass.resize(128)`; APIs use role-local IDs and translate bypass to global `1024 + id` |
| static ID boundary | `gpu-cache.h:2111-14,2146-68,2198-2210,2236-70` | resident IDs must be `<1024`; bypass IDs `<128`; bank is `(resident ? id : 1024+id) % 4` |
| resident reserve/identity | `gpu-cache.cc:2416-2537`, `l2_cache::access` | tag probe's `cache_index` is assumed to be the resident payload ID; a MISS reserves that exact slot before the lower read is queued |
| payload identity carrier | `src/gpgpu-sim/mem_fetch.h:133-145`; init `mem_fetch.cc:73-74` | `mem_fetch` carries `{payload_id,generation}`; no role or owner is carried in the fetch |
| fill validation | `gpu-cache.cc:2561-73`, `l2_cache::fill`; `gpu-cache.h:2121-44,2170-88` | returned fill must match resident ID, owner block and generation and a pending sector; stale/reused landing asserts rather than silently accepts |
| hit/service request | `gpu-cache.cc:2429-37`; fill service `gpu-cache.h:2460-72`; cycle integration `l2cache.cc:1108-29` | hit/read/write and fill use the payload bank model; one operation/bank/cycle in Banked mode |
| bank arbitration | `gpu-cache.h:2236-2358` | four global-ID-modulo banks, immediate idle grant, retained oldest-ready retry grant; no role-specific bank behavior |
| release/rollback | `gpu-cache.cc:2465-81,2496-2527`; `gpu-cache.h:2113-14` | only a speculative new resident reservation is restored on WAD/admission failure; replacement retirement occurs inside `reserve_resident`; no general production bypass release exists |
| payload telemetry | `l2cache.cc:1785-2063` | B0 snapshots sample resident/bypass counts and expose terminal consistency, but current production bypass count remains zero |

### Static-partition enforcement points

1. `m_resident`/`m_bypass` are separate vectors with hard-coded sizes (`gpu-cache.h:2096`).
2. `l2_cache::access` asserts tag `cache_index < 1024` and directly calls `resident(cache_index)`/`reserve_resident(cache_index,...)` (`gpu-cache.cc:2429-55`). This is the largest M1 refactor point.
3. `ep_l2_payload_fill_request` rejects `id >= 1024` rather than routing a bypass fill (`gpu-cache.h:2465-72`).
4. `l2_cache::fill` asserts returned ID `<1024` (`gpu-cache.cc:2563-71`).
5. Bank mapping internally re-encodes role into the `1024` offset (`gpu-cache.h:2268-70,2334-46`).
6. The only bypass lifecycle callers found are `tests/ep_l2/test_payload_store.cc` and `tests/ep_l2/test_payload_banked.cc`; none exists in `src/gpgpu-sim`.

## Request, descriptor, and lower-path map

| stage | anchor | state acquired/released |
|---|---|---|
| exact preview/admission | `l2cache.cc:1168-1403`; `gpu-cache.cc:2576-2662` | non-mutating plan records tag, MSHR, MissQ, WAD, data/response needs; front-end head remains queued on denial |
| MSHR reason/alloc | `gpu-cache.cc:669-716`; issue `1681-1750` | `full_reason` selects per-address, line-MSHR, then descriptor-pool reason; `add` owns requester/descriptor and pending/issued masks |
| fill/readiness | `gpu-cache.cc:824-901`; `1525-1617` | fill updates tag, marks sectors ready, queues descriptors; descriptor and MSHR are released only by `commit_next_access` |
| response completion | `l2cache.cc:1065-1100` | response goes to L2→ICNT, then `commit_next_access`; descriptor lifetime includes enqueue backpressure |
| DRAM issue/return | `l2cache.cc:557-850` | no-return writebacks use special credit/progress path; demand fills return through DRAM→L2 FIFO |

## Dirty victim / WAD map

`l2_cache::access` checks and reserves WAD before destructive tag mutation (`gpu-cache.cc:2460-2507`). The base data-cache policy creates a `L2_WRBK_ACC` for dirty eviction (`gpu-cache.cc:1928-49`, plus write-policy variants). `memory_partition_unit::set_done` delegates to `memory_sub_partition::set_done`; only there is the WAD released (`l2cache.cc:821-37,2269-74`). Therefore a WAD reservation survives until no-return DRAM completion, not merely MissQ dequeue or DRAM issue.

## C7e vs D512 source comparison

Core diff `ece1a3a..878f808` changes only `ep_l2_b0_accum` descriptor histogram sizing/sampling/delta safety in `src/gpgpu-sim/l2cache.cc`. It carries no payload allocator, ownership, bank, WAD, MSHR, cache functional, or timing change. Framework D512 changes are configuration/telemetry-family material. This pack uses the C7e functional map and may reuse the D512 dynamic histogram pattern for M0 output sizing only.
