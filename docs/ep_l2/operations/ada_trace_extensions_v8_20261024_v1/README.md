# Ada trace extension stage 2: embedded REL CALL and full-width PC

The isolated ADA8 candidate captures an embedded CALL.REL.NOINC/RET.REL.NODEC without dropping callee instructions, and its independently rebuilt Core64 consumer issues the complete validated trace. This is a scoped semantic result, not a promotion of the V100 EP baseline or an RTX4080 timing calibration.

## Exact application attempts

The eight-attempt parent compatibility ceiling has consumed four attempts. No failure was refunded.

| Attempt | Exact request | Result |
| --- | --- | --- |
| 1 | EP_ADA_TRACE_COMPAT_MICRO65_20261024_V1 | 1997 lane uops issued; perfect constant cache enabled, so limited rather than a real constant-request qualification |
| 2 | EP_ADA_TRACE_COMPAT_CONST65_V7_20261024_V1 | 1802 lane uops, 579 constant lane instructions, real L1C/L2 requests; scoped serialized constant profile passes |
| 3 | EP_ADA_TRACE_COMPAT_CALL65_V8_20261024_V1 | Failed: 75 decoded uops, zero issued instructions. Legacy Core scheduler/pdom PC fields truncated original 64-bit code addresses. Exit 0 was not accepted. |
| 4 | EP_ADA_TRACE_COMPAT_CALL65_PC64_V8_20261024_V1 | 1932 = 1483 source + 449 auxiliary lane uops; 514 constant lane instructions; 2 CTAs issued/completed; L1C 18 accesses/11 misses/7 hits and 6 constant requests. Scoped candidate passes. |

Attempt 4 native root: /root/data/ep_l2_main_ada_call_pc64_compat_20261024_v1  
Run: run/f29b01fff6504be2a10c4922b34c7808  
Its SELF_STRICT_TERMINAL_JOIN.json binds the original trace, decoded counts, terminal issue/cache statistics and saved native mappings. The runtime sampled its mapping hash list before a later base.info snapshot: the list contains only the initial loader/ELF. The independent terminal join rehashed every file in the saved map and checked frozen pre/post pins, including the new Core library. This observation limitation is explicit; no live completeness claim is made. Future entries must accumulate checked mappings throughout execution. Old registered entries and pins remain unchanged.

## Producer evidence and contract

ADA8 producer prototype SHA 5106378b9be1ae76bfdbde55d14118c50b607fed28ddbe1be48420803f10a9f6 uses NVBit 1.7.7.1 and CUDA 12.8. NVBit's new module flush mechanism is used. The first module-loading prototype failed because a flush cubin included managed globals; failed attempts and debugger output are retained. Separating record types from managed global definitions fixed that case.

Every source PC is the full original NVBit loaded-function address plus the relative offset. There is no relocation or low-32-bit mapping. The static sidecar binds full PC, function, original SASS and the typed operand map. CALL's nvdisasm transitive ABI/clobber summary is preserved separately and is not fabricated as physical RF reads/writes. RET captures actual R2/R3 return-target values. Per-lane CALL/RET targets, next executed PCs and return frames are validated.

CALL65 has 60 source records, 1483 active source lane instances, 15 serialized constant auxiliary uops/449 active instances, 3 CALL and 3 RET records covering 65 lanes each. Its source binary SHA is a8aac4f452059f7bf7c93ff4dc87c48c100d0ae523536d60af85fe75cbc73db2. Its grouped trace SHA is 5bab177d507937fb67700e270891a70236dc807261b4f0d7459a884b80a486b3.

A separate real GPU block37/N65 leaf capture tests physical partial warps: 2 CTAs, 4 warps with 32/5/32/5 launched lanes. All 57 source records pass active/predicate/effective mask bounds; 1094 source lane instances, 482 constant lane instructions and 417 auxiliary lane instances are observed. Adding an impossible sixth lane to a five-lane warp is rejected without producing qualification. CALL65 also passes this strengthened full-record validator. This GPU capture does not consume an application simulator credit.

## Core64 repair and reproducibility

Isolated Core source base snapshot: dfdba4903e342d27fe67153a63f65454a957a7ad  
Repair HEAD: f31c166cc952957fd764c31dc48efe183a8eb8ef  
The private Core bundle preserves both commits; CORE64_SOURCE.patch carries the 23-file width change. Scheduler/pdom interfaces, PTX call-frame/RPC and thread PC fields, PC lookups, instruction latency information and relevant diagnostics now preserve address_type. No frozen old Core/source/library is modified.

Directed tests link the actual new library and preserve two distinct full addresses sharing identical low 32 bits through SIMT pdom, ifetch, call frame and PC-key lookup. The actual new library SHA is 91a8cc47fd44999836e7d52bd3669eae6fc3314dfbe471ac5eafce8dda3662dc; consumer ELF SHA is 970a57c099cead2a747d9d139062d8bef96d7e76f4a001b34dc516108656a32a. Build logs preserve two repair failures and the final successful build. Only the isolated clone's broken zlib include links were pointed to system headers, recorded in the source snapshot.

## Scope and remaining work

This stage qualifies embedded relative calls in the measured single code body and the existing per-kernel cold symbolic constant namespace with serialized auxiliary loads. Auxiliary operations are consumer-internal work, never extra GPU SASS. Original instruction count, internal uop count and active lane work stay separate. UR/P/internal scoreboard tokens do not become GPR occupancy or RF-port operands.

CALL.ABS, indirect calls, ABI windows across related functions, actual JIT-loaded code, legacy Driver launch geometry, texture/surface/async memory, Graph and multi-context/concurrent timing remain separate active qualification work. The new producer explicitly rejects unsupported Graph/Capture, multi-context, multi-thread launch and multi-stream cases, but code guards alone are not hardware negative-test proof. Optimized __syncwarp microprograms assembled to NOP; they are not WARPSYNC qualification. A debug fixture does contain WARPSYNC but also unqualified CALL.ABS and is not admitted.

Input byte identity and execution repeatability are separate. Runtime clock/time-seeded host RNG needs actual bounded HtoD byte snapshots; source/argv alone does not freeze those bytes. Device clock-controlled loops can vary even with identical input snapshots. These enhancements remain pending and cannot silently upgrade existing ordinary v7 assets.

The frozen ordinary v7 producer and previously released bulk pipeline continue independently. This ADA8 candidate is not a replacement release for all suites.
