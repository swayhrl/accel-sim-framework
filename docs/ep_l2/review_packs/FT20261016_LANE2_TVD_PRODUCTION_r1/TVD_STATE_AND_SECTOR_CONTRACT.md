# Actual state, data and producer contract

The sole R0 payload allocator owns data/sector versions, generation, bank arbitration and pins. A single combined 128-entry WAD/TVD address directory is instantiated only when either new flag is enabled; the old WAD address set is not populated in that mode. The existing address birth map is timing instrumentation. D512 descriptors/MSHR and mandatory lower request backing are not duplicated.

| State | Payload visibility and next transition |
|---|---|
| EMPTY | no address/handle; may reserve for mandatory WB or optional clean victim |
| CLEAN | ready mask captured from the actual evicted clean resident; read in place, write/atomic same-handle promotion; missing sector drops optional entry before ordinary miss |
| WB_STAGED | actual dirty victim and mandatory WAD reservation; wait for real WB bank readout and lower acceptance; no speculative forward before accepted |
| WB_INFLIGHT | actual memport push copied independent sector-version packet backing; mandatory address retained; requested valid sectors may forward before generic WAD rejection and before set_done; writes/atomics/missing-sector reads wait |
| WB_COMPLETE | real memory_sub_partition set_done cleared mandatory hazard; retained handle clean and eligible for promotion/reclaim; WAD-only entry instead disappears |

Partial dirty bytes without a complete ready sector are WAD-only: retain no directory payload pointer, never claim a forwardable full sector, release ordinary WB data at actual lower acceptance. This applies to both ordinary replacement and promotion's dirty victim. The actual partial-write test verifies no false forward and no promotion deadlock. Complete-sector symbolic labels are the independent reference model; there is no full-byte SASS input or numerical atomic callback validation.

The frontend follows actual Tag probe. A Tag miss waits until the following cycle for the directory lookup, even when the directory is absent for that address. Existing Tag HIT/SECTOR_MISS/HIT_RESERVED takes normal paths. Dirty lookup occurs before generic WAD denial. Valid read takes a directory lease plus allocator pin, requests the existing same-bank arbiter, copies existing versions to the real mem_fetch response, records requester admission, and commits/unpins only after actual L2->ICNT queue enqueue. Backpressure and same-bank denial cannot create an extra response. One existing frontend head is serviced per cycle; no new 512-slot response pool.

Promotion selects an eligible way in the actual set with the same bank class (payload_id%4 == Tag index%4), invalid first then oldest eligible. It preserves the authoritative handle/generation, binds Tag/sector visibility, and performs no data copy. A dirty resident victim receives a real L2_WRBK_ACC and mandatory WAD entry; its address atomically reuses the promoted entry's slot, so no transient 129th address is needed. Miss queue capacity/pending WB/pins are checked before commit. Normal replacement reserves only a disjoint same-bank landing slot; when exhausted, completed opportunistic TVD can be reclaimed, mandatory WB cannot. Optional clean retention does not preempt mandatory entries.

Flush/invalidate checks directory epoch_ready and no live read lease; outstanding mandatory WB is rejected. Drained optional entries are reclaimed via the actual allocator before declaring cleanup. Tests exercise real flushL2/invalidateL2 and assert requester closure, WAD0 and existing no-resource-leak/ownership invariants. Mandatory=0 can coexist with live optional TVD before cleanup and must not be misreported as leaked WB.

PRODUCTION_GATES.csv scopes the tests: default 1set/1way directed cases, one 1024set/1way pool-pressure case and one primary 64set/16way promotion case. All use one channel/slice. Not a full-GPU application, all sector-order interleavings, C8 qualification or independent scientific approval.
