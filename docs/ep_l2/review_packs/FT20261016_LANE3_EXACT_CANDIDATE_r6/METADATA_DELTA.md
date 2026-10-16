# r6 metadata/control delta

No new persistent production field, data array, descriptor pool or bank port is added relative to Lane 3 r5. prefill_allowed reads existing open/ever_open/selected/drain state; prefill_complete advances the existing Tag-generation vector. RO physical_cycle now delegates to the exact common Lane 1 helper; it does not add a new clock. Test grant snapshots and offset checks are fixture variables only.

The initialization guard and identity/sector comparisons still require control/reduction logic in a physical implementation; zero additional persistent fields does not mean zero gates, timing or area. Untimed pre-epoch host initialization is not free timed GPU bank service. Existing r4/r5 field ledgers and oracle costs remain applicable. Physical data remains1168/1160×128B per slice, common128B copy latch, four single-op banks; shared D512/native128/address32. RO completion rows are1168/1160 with active transactions additionally bounded by D512, not T_RO=128.

Exact-parent audit preserves Lane 1's common resource protections. Closed-world whole-commandlist certificates, FWT negative coverage and dataless symbolic-sector limits remain unchanged. No RTL/PPA/energy/performance or numerical application result is claimed.
