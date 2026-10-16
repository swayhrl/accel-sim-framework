# R1.1 static repair findings — no runtime PASS

The Lane5 published combined candidate applies without conflict to both exact
Lane1 R1 be651ccf and Lane4 b8b3d55b in private indices. Their repaired runtime
sources are identical (the original difference is CMake test targets). Clock
and warmup candidate bytes are retained with producer publication/hash.
This is not an official repaired release; the warmup delta remains uncompiled.

1. Ideal-read replacement timestamp: the bank request already receives physical
   GPU cycle, which must stay physical. The same value currently reaches
   ep_l2_ideal_touch_resident -> tag_array::access, whereas native accesses add
   m_memcpy_cycle_offset. The attached one-call delta restores native Tag time
   while leaving bank/response timing unchanged. It is UNCOMPILED and requires
   a nonzero-offset ideal warm-hit/LRU test on official R1.1. Default OFF is
   unaffected. Apply only after the exact combined repair parent tree recorded
   in SOURCE_REPAIR_AUDIT, or rebase against official R1.1 and re-audit.

2. Dirty warmup victim: candidate force_tag_access releases a live RESIDENT
   after checking pins/pending, but has no explicit dirty-victim rejection or
   lower writeback before release. ft_drained() does not mean all resident
   cache lines are clean. Lane1 must test/preserve dirty data or explicitly
   reject the unsupported warmup phase. No assertion should be disabled.

3. Repeat/partial-sector warmup: requested sectors are reset to version-zero;
   other sectors retain versions. A drained but previously written line may
   still be dirty. The ideal ReferenceMemory is a separate address/producer
   version store and this candidate adds no host-reinitialization hook there.
   Initial-before-GPU prefill is consistent with cold symbolic version-zero;
   post-producer host rewrites require a defined model or explicit rejection.
   Do not infer an expanded host/oracle scope from this static replay.

4. Reservation/Tag agreement: a slot is reserved using the initial Tag probe,
   then baseline_cache::force_tag_access performs native Tag work. Actual
   chosen index, owner generation, partial-sector reset, warm immediate read,
   subsequent eviction/WB/set_done and final response drain need production
   evidence. I_READ_HIT bypasses ordinary hits and cannot by itself establish
   that the ordinary warm payload-owner path is repaired.

Only Lane1's official R0.1/R1.1 source freeze and Lane5's new physical_bank_clock
and memcpy_payload_identity plus per-ideal gates can qualify application runs.
No budget, input, oracle or new I_BANK point is introduced here.
