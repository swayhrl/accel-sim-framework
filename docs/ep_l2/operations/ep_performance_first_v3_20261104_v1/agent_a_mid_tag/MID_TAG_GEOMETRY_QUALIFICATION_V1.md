# Mid-Tag geometry qualification V1

**PASS: production geometry, CPU protocol and 282-option engineering qualification. HOLD: formal activation pending new scope authorization and Main installation.**

Accepted Source78 Core 78f4b59e865b136eede74df74c44c210f5b4ca04 and ELF 78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a are unchanged. Framework/vendor/library identities are pinned in evidence/SOURCE78_READBACK.json. No Source92, P1 correction, host-write V3, CLEAN quota or high-clock repair is included.

| Geometry | Logical Tags/slice | Nominal addressability, 64 slices | Physical Payload/slice | Engineering status |
|---|---:|---:|---:|---|
| REF32x8 |256|2 MiB|1168 line slots|accepted reference reused|
| G32x16 |512|4 MiB|1168 line slots|PASS, not application accepted|
| G64x8 |512|4 MiB|1168 line slots|PASS, not application accepted|
| G64x16 |1024|8 MiB|1168 line slots|accepted reference reused|

Both candidates keep32 DRAM channels,64 subpartitions,128B lines/32B sectors, four Payload banks, one operation/bank/CORE cycle, nominal Resident1024/Bypass128/staticWB16, descriptor512, WAD128 and ordinary Line-MSHR128. Nominal Tag capacity is distinct from physical Payload capacity. Static S retains its declared fixed allocation partition; WV uses the already qualified unified allocation policy.

Actual production mapping is used. gpu-cache.cc:97-169 dispatches set_index to configured P/IPOLY;32 sets use the32-set polynomial rather than masking a64-set index. Existing Source78 actual constructor controls G32W16_S/G64W8_S cover all active sets and are reused. gpu-cache.h:3335-3431 retains finite-policy and geometry/resource guards. gpu-cache.h:3052-3079 binds dense logical Tag indices and checks Payload identity/bank color; physical Resident capacity remains fixed.

## Tests actually executed this round

The owned harness changes only the prior external protocol fixture's coupled sets/ways choice into two explicit geometry arguments. It links unchanged accepted production archives; no cache source or assertions are edited.

Four geometry/mode controls, each with MS111 and MS011: **eight runs PASS**. The fixture drives real memory_sub_partition frontend, Tag allocation, dirty replacement/WB, WAD retention/completion, reversed independent responses and complete drain. G32x16 produces17 replies/one dirtyWB/15 reverse returns; G64x8 produces9 replies/one dirtyWB/7 reverse returns. P1, ownership, physical capacities and drain assertions pass. S and WV are independently exercised with RO OFF and TVD disabled/enabled respectively.

Every MS011/111 pair has identical semantic markers including fixture cycles, replies, WB count and drain. This proves bounded MS-only CPU NI; B0/M0a remain ON. It is not application NI, timing calibration or application performance. No new observer is introduced.

All eight prospective workload/mode/geometry configurations passed the real Source78 plus trace option parser: exactly282 unique options, no conflicts; only -gpgpu_cache:dl2 differs from each exact original mode reference. Read evidence/ACTUAL282_CPU_RECEIPT.json, EXACT_282_DELTAS_BY_POINT.json and PRODUCTION_CPU_AND_MS_NI.json.

No full GPU application model, Trace-body scan/input copy, new scientific budget or production registry write occurred.
