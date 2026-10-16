# Independent clean TVD production checkpoint

Four actual producer scenario groups PASS at pinned Core 8ae60ff1 and immutable
4320583b... directed binary. Binary, configs and stimulus were independently
checked; independent stdout equals the frozen producer log byte-for-byte.
Small-geometry memory_sub_partition tests cover retained clean victim/version,
+1-cycle lookup, common-bank refusal, actual ICNT backpressure, no read promotion,
partial-sector fallback, same-handle write promotion with real dirty-victim WB,
and epoch cleanup. Matched actual lower reads: 2 packets/64B OFF, 1 packet/32B ON.
Served bytes are response service; no physical DRAM savings are inferred.

This does not qualify dirty TVD, the final integrated R2, primary-geometry
behavior, or an application result. Earlier seven module groups were not rerun.
Final Lane1 R2 needs incremental source/binary/production boundary qualification;
this exact older checkpoint cannot silently qualify later code.
