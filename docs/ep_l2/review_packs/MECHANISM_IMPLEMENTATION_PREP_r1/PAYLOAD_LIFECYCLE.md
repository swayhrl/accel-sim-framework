# Payload Lifecycle

Source: C7e core `ece1a3a77c5628763e0a4605bfd1c639ee6a1495`.

## Current resident lifecycle

```text
ICNT head -> preview_access (no mutation)
  -> l2_cache::access probe MISS
  -> reserve_resident(tag/cache_index, block, mf)
       [slot: FREE/old incarnation -> RESIDENT_FILL_PENDING; generation++]
  -> send_read_request -> MSHR + descriptor + MissQ + lower request
  -> DRAM-to-L2 head -> payload fill bank request
  -> complete_resident_fill(id, block, generation, returned sectors)
       [pending mask clears; state VALID or DIRTY]
  -> baseline_cache::fill -> tag/sector valid + MSHR mark_ready
  -> response ICNT enqueue -> descriptor/line-MSHR retirement
```

The tag array remains authoritative for tag and sector validity. Payload state is line-owned, while `pending_sector_mask` is sector scoped (`gpu-cache.h:2077-82,2136-44`). A request merged to a reserved line attaches the resident identity instead of reserving a second slot (`gpu-cache.cc:2444-55`).

### Failure and replacement paths

| path | source | required result |
|---|---|---|
| payload bank denial on hit | `gpu-cache.cc:2429-37` | `RESERVATION_FAIL`, no tag/MSHR mutation by this request |
| WAD hazard/full after speculative reserve | `gpu-cache.cc:2465-81` | restore saved resident slot before returning failure |
| base cache admission failure | `gpu-cache.cc:2496-2527` | restore saved resident slot |
| locally absorbed full-sector write | `gpu-cache.cc:2523-27` | reservation becomes valid/dirty without lower fill |
| stale old owner on a new static landing | `gpu-cache.h:2146-64` | prior non-pending identity for same owner is retired; pending one asserts |
| stale fill/reused ID | `gpu-cache.cc:2561-73` | owner+generation+pending-sector validation asserts before tag fill |

## Current bypass model lifecycle

The store exposes `FREE -> BYPASS_FILL_PENDING -> BYPASS_READY -> FREE` through `reserve_bypass`, `complete_bypass`, and `release_bypass` (`gpu-cache.h:2198-2210`). The global ID is 1024–1151. **This is not connected to a production L2 request path.** It has no source caller in `src/gpgpu-sim`; only directed unit tests call it. Consequently current bypass occupancy/slack is not a workload measurement and `BYPASS_*` bank operation labels have no production producer.

## Ownership contract to preserve

For every live allocation, exactly one slot owns `(line-address, generation)` and every in-flight fill holds that exact ID/generation. A slot cannot be reassigned while its pending sector mask is non-empty. A lower read for a sector must be recorded once (`note_resident_lower_read` asserts no duplicate). At terminal drain, no pending sector, bank retry, descriptor, WAD, or live transaction may remain; existing terminal checks are emitted in `l2cache.cc:2049-72`.

## Implication for M1/M2

M1 must replace static **location assumptions**, not weaken the contract. `payload_id` must become a global physical ID and its role must live in slot metadata. A tag-index-to-payload-ID mapping is required because the present direct `cache_index == resident_id` identity is exactly what prevents a resident tag from using slots 1024–1151. M2 must add a real bypass/pending lifecycle before it can claim that capacity moves between roles.
