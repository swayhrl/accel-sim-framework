# M4 WAD-backed TVD Source Map

## Current dirty victim lifecycle

```text
preview sees MISS + dirty victim
 -> l2_cache::access reserves WAD by victim block address
 -> data_cache/tag_array access destructively replaces victim and emits L2_WRBK_ACC
 -> writeback waits/drains through MissQ and L2->DRAM
 -> DRAM completes no-return writeback
 -> memory_partition_unit::set_done -> memory_sub_partition::set_done
 -> ep_l2_wad_complete removes WAD entry
```

Anchors: preview `gpu-cache.cc:2603-20`; WAD reservation and rollback `gpu-cache.cc:2460-2507`; dirty writeback construction in base cache `gpu-cache.cc:1928-49` and equivalent write-policy paths; lower routing `l2cache.cc:557-850`; true WAD release `l2cache.cc:2269-74`. Current WAD state is an address-indexed `std::set` plus timestamps, not a data store (`gpu-cache.h:2515-69`).

## TVD implication

The dirty victim's data bytes are carried by the generated writeback `mem_fetch`; the existing WAD does not own a copy or a payload ID. Therefore “WAD-backed TVD” cannot mean adding data magically to WAD metadata. It needs either:

1. a temporary victim payload slot from the same fixed 1152-entry pool, held by the WAD record until no-return completion; or
2. an explicitly budgeted transfer of the evicted resident payload slot into a TVD role, with tag ownership removed but payload identity/generation retained.

Option 2 is preferred for comparable storage: it does not allocate an extra 128-B line. The WAD record must add `payload_id` (11 bits for 1152 IDs), generation (current unsigned; width must be specified), dirty sector mask (4 bits), victim line address, writeback-issued state, and timing/debug fields. It releases/reassigns the transferred slot only from the same `set_done` completion point. A new resident allocation may not overwrite the ID during the live writeback.

## Required M4 source changes later

`l2_cache::access` must bind the pre-eviction resident handle to the WAD before tag mutation; writeback creation must carry/validate that handle; `ep_l2_wad_complete` must validate and release it. The tag-to-payload sidecar from M1 is prerequisite. Dirty-sector semantics and bank WB readout must remain accounted. M4 must separately report TVD bytes (= live TVD entries × 128 B) and metadata bits, subtract any transferred resident payload from resident occupancy, and prove total payload slots never exceeds 1152.

No M4 implementation should begin until M0 measures dirty-victim payload hold time and overlaps it with real resident allocation pressure.
