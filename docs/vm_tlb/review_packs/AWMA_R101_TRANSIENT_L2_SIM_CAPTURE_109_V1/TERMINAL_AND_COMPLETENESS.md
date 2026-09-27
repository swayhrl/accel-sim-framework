
# Terminal and completeness

FORMAL status **COMPLETE** for all 18 ordered members in one context `0x43c6c760` and stream `0`. Every member has a matching `ROUTEB_TERMINAL_COMPLETE` after device completion, explicit channel flush, receiver drain, xz close and atomic rename. Reported packets equal accepted and written records for every member. Aggregate drop=0, overflow=0. There were no extra selected kernels.

`kernelslist` and `kernelslist.g` each contain 18 unique, present members; every `.trace.xz` and `.traceg.xz` passed `xz -t`. The accepted full grammar validator and independent frozen trace-parser-only harness each passed 18/18, with the same total dynamic instruction count. Grammar checks memory opcode/byte-width/address syntax and sync/control semantics. Re-reading every traceg produced stable SHA256. `TRACE_SEMANTIC_SUMMARY.json` records 193816568 validated dynamic instructions, 11926244 memory opcodes and 8016316 sync/control opcodes.

The runtime region map was created before cuProfilerStart. A/B/X0/X1 each have actual aligned base, 23,068,672 bytes, BF16 shape/stride and nonoverlapping ranges. `REGION_LIFETIME.tsv` is an 18-boundary join to exact captured kernel IDs; it never encodes per-line future last use.
