# Independent E source review: common64× capacity diagnostic

Reviewed the published e2859cd4 source and the clean worktree correction 697e2ade4b3db82f4a1183c40ac16126c3323a64 against frozen d010911e. This is source inspection, with zero compiler/native/main/application invocation and zero registry/CLIENT changes. A2's final formal producer identity remains required; e285 BUILD_SPEC hashes do not identify the corrected sources.

The source implements a finite, traditional-S diagnostic. The master default is0; ON selects free payload-bank service and the common finite geometry. No production correctness failure was established by this static review. New native evidence and independent version-specific acceptance remain necessary. A concrete observational hot loop requires ordinary implementation attention before spending complete-application starts.

## Geometry, identity and behavior

`l2_cache_config::init()` sets4096sets×16ways,8192 line MSHRs,32768 descriptors,2048 per-address targets,8192 WADs,1024 static-WB slots,8192 MissQ and4096 result-config field; actual subpartition FIFOs become4096:8192:4096:4096. It rejects nontraditional S, RO/V/MQ2/RG1, ideal metadata/read-hit/WB, copy-free, incompatible geometry/policy and master values>1. The memory init additionally rejects forced-hit, simple-DRAM and texture-only. OFF does not enter these branches.

The payload store uses65536resident+8192bypass+1024WB=74752 finite slots. Role-range tests, native Tag array allocation and Tag→payload handle storage scale together. ON overrides the native maximum-cache multiplier to1, so native Tag backing is65536, rather than the unrelated historical4× allocation reserve. Resident/bypass/WB IDs remain disjoint and payload handles retain generation, per-sector ready/pending masks, pins and four version symbols. The owner and live/pending indices replace large repeated scans; terminal `ownership_consistent_deep()` explicitly reconciles indices with actual storage. The697 correction refreshes the pending index after absorbed writes; without it, the e285 new index could remain stale after a state transition. No E code was substituted for this producer fix.

For native IPOLY, partition address is still obtained through the original address mapping. The extension computes the exact prior IPOLY64 result as low6bits and uses the next6partition-line bits for the high group. Set indices are0..4095; full block-address Tags still disambiguate lines. This is a documented new 4096-set mapping, not a claim that the old helper supports a4096 polynomial or that set conflict behavior is unchanged. LINEAR remains supported. The native fixture requests both mappings and constructs real congruent addresses.

ON selects the existing L2_DATA_FREE service, whose grant path records logical operations/exempt services and returns without consuming physical bank grants. It does not replace data or lifetime transitions. The fixed one-cycle COPY_READ→COPY_WRITE latch branch remains because copy_free stays0; version symbols are copied into actual staging. Sector-fill identities/readiness checks, same-address WAD waiting, normal lower FIFO acceptance, payload release at actual lower acceptance and final WAD retirement at `set_done` remain in the production path. The source keeps DRAM/interconnect timing/bandwidth and ROP latency. Larger local queue capacities are part of the diagnostic and must be labeled as such.

OFF adds observational counters/terminal CONFIG output, but no capacity or mechanism intervention. Source inspection cannot replace the requested old-exact/default-OFF/explicit-OFF native equivalence on the new build.

## Per-cycle cost: concrete high-priority engineering finding

`memory_sub_partition::cache_cycle()` calls `ep_l2_b0_sample()` every cache cycle for every active slice (`l2cache.cc:1721`). B0 sampling (`:2160–2162`) calls resident_valid, resident_dirty, bypass_pending and bypass_ready. In697, `gpu-cache.h:2369–2372` routes these through `count_state()` (`:2834`), which scans **all74752slots**. resident_valid scans twice, so this chain costs five complete slot passes per slice per cycle. B0 is enabled in the original accepted input configs.

At300000GPU/cache cycles and64slices this is approximately **7,176,192,000,000 slot visits**, versus112,128,000,000 at1168slots. This is a source-derived operation count, not a measured walltime. It gives no defensible assurance of fitting10800s and is large enough to threaten the campaign without changing simulated cycles. `ms_sample()`, used-role counts, pending-sector counts and large allocation cleanup have already been optimized; this B0 path remains outside those changes.

An ordinary A-owned optimization can maintain exact state counts/indices at every mutation and reconcile them against deep scans at bounded checkpoints. That must preserve B0 semantics, assertions and source identity; simply disabling B0, skipping correctness checks or pretending absent counters are zero would change the contract. E does not edit A's production code. Source should be re-reviewed after any such correction; exact new build/native identity must follow it.

Secondary costs: `l2_char_tracking_refresh_line()` recomputes the maximum across4096sets when a previously maximum-reserved set loses a reservation (`gpu-cache.cc:303–307`); this is event-driven rather than every slice-cycle. Optional legacy L2CHAR collector copies/scans the4096-entry reserved-set vector each cycle when enabled (`l2cache.cc:1093`); verify its actual effective enable flag before cost prediction. Descriptor chain snapshots scan live MSHR entries, not all32768 allocated descriptors. WB preview scans at most the1024-slot static region; tag probes remain16ways. Deep ownership/Tag mapping scans occur at print/terminal checkpoints, and native flush scans scale with65536Tag lines; they must remain intact.

## Capacity evidence and honest labels

The source emits11 cache resource rows plus four subpartition FIFO rows per slice when ON. Each row's `capacity_denial_checks` counts observed checking events, not unique requests or disjoint stall cycles.

| Resource | Peak/refusal interpretation |
|---|---|
| Tag | Resident-identity peak is a conservative bound, including lazily invalidated Tags. Denials cover all-reserved probe failures; ordinary full-set replacement is not a denial. Global occupancy<=50% cannot prove absence of set conflicts. |
| Resident | Allocation-event peak; Tag all-reserved denials reused as admission evidence. |
| Bypass | Traditional-S production has no bypass allocation; zero denial is a structural scope fact, not an observed generic allocator test. |
| WB, WAD | Allocation peaks with actual WB-space/WAD-full refusal checks. WAD survives lower acceptance until actual completion. |
| Payload | Sum of independent resident+WB peaks is an upper bound on simultaneous use. |
| Line MSHR, descriptor, per-address | Peaks updated at real add/merge; specific full_reason checks count capacity denials. RAW/WAR/sector restrictions remain separate. |
| MissQ | Actual enqueue peak; admission checks count missing slots; RO-only enqueue is out of scope. |
| Ready responses | All-live-descriptor peak bounds the ready population; no additional independent ready allocator is claimed. result_fifo_field is not that allocator. |
| Four FIFOs | Push-event highwater; full() check failures counted. `is_avilable_size(unsigned)` does not increment this denial counter. |

Capacity coverage must be interpreted per actual source path. A missing/uncovered refusal counter is **UNKNOWN**, never an invented zero. The approved operational threshold is zero covered denials and every applicable highwater<=50% capacity. It does not prove conflict-free Tags, remove same-address hazards, or establish an infinite-cache/hardware upper bound. Valid data can still be accepted as large-finite when the operational label is not justified; no automatic rerun or sweep follows.

## RAM estimate and native scope

The vector implies4,784,128payload slots,4,194,304native Tags and2,097,152descriptors over64slices. With ordinary64-bit GNU C++ layout, source-derived estimates are about80B/payload slot,136B/sector Tag object plus pointer/allocator overhead, and40B/descriptor plus4B free-list ID. These are **unmeasured ABI estimates**, not sizeof claims. Those three primary structures are roughly1.0GiB before live owner/set maps, active MSHR/list nodes, packets, core state or trace readers. Fully occupied resident owner/live indices add several hundredMiB; worst live packets can addGiBs depending on actual mem_fetch/layout and shared population bounds. A total8GiB RSS upper bound is not proven by source alone.

The `ON64.config` used by the11-invocation native plan sets32memory partitions×2subpartitions. `exec_gpgpu_sim` creates all64 through its constructor (`gpu-sim.cc:1178–1193`); the directed fixture additionally constructs one standalone partition. Thus its measured RSS covers at least64-slice static geometry, but only the extra partition receives the bounded directed traffic. It does not simulate full-application trace-reader/core/live-packet worst cases. Actual new64-slice native maxRSS, independent available RAM/reservations and the normal per-application8GiB guard remain required; high I/O alone is not a rejection reason.

## Native fixture applicability

The new fixture has real production requests, out-of-order sector returns,20 scoped requesters, dirty16-way conflict replacement, real version-copy checking, observed fixed latch, same-address read held until actual WB completion, and final MSHR/descriptor/WAD/pending closure. It tests role boundaries at high indices, stale payload-handle generation rejection, finite1024WB exhaustion and release. ON checks zero physical grants and actual logical copy services. The plan includes LINEAR/IPOLY and64-slice geometry allocation, three illegal-option cases, old-reference/default-OFF/explicit-OFF and affected OFF stale-sector/physical-clock fixtures.

It supports the intended qualification design but does not itself establish completion: no native invocation had been independently read back during this source review. Particularly review whether final evidence covers ON stale-fill/reused Tag-generation behavior through the actual production route, not only standalone payload handle reuse, and any changed state-counter/index bookkeeping after the hot-loop repair. Missing performance counters can remain UNKNOWN; data/version/ownership correctness gates cannot be replaced by aggregate counters. Reuse unaffected evidence only with an explicit source-scope argument on the final producer identity.
