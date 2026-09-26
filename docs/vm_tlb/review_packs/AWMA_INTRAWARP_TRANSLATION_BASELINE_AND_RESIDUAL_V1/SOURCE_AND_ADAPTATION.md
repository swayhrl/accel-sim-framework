# Source and adaptation

Within-run classification identity is kernel-local CTA sequence + warp-in-CTA + per-warp dynamic memory-instruction ordinal. PC, hardware warp slot, and raw simulator UID are recorded only as attributes and are never used alone to classify source. Request identity is ASID/VPN/page-size/generation/access compatibility.

The reference observes the already-built data-coalescer accessq at the same resident prelaunch point as frozen V1, scans in the same reverse order, and chooses the first legally eligible group member. One real frozen translation proceeds; completion PA and source are copied to same-instruction compatible members while preserving each member offset, lane/byte/sector masks, access UID, cache transaction, downstream PA, and atomic/data semantics. No completion is selected from the future and no old TLB service is cancelled.

This is one classic capability reference, not an ASPLOS-system reproduction.

The accepted passive observer authority `6441fe9f91266220a52587c0313fb767007b5d92` is reused for instrumented-OFF evidence. Cross-run CTA/warp/ordinal digests are diagnostic, not a set-equality gate; they differ on T0/T1/SPLITKV. Exact intersection/difference is instead co-observed in each PREL1 source run, and cross-arm identity is closed by immutable trace SHA, logical instruction/CTA coverage, and canonical functional mapping digest.
