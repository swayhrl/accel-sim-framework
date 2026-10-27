# Event timeline source and engineering handoff

Scope: EP_L2_MULTIWORKLOAD_TAG_OPPORTUNITY_AND_EVENT_TIMELINE_V1. This is an engineering component handoff, not application acceptance. Parent EP-MAIN owns final integration, production CPU controls, source qualification, native operations, and scientific claims.

## Frozen source

Core 78f4b59e865b136eede74df74c44c210f5b4ca04, parent c67b332db703f09571ba6628222c77d71440e141. Framework remains 9dd1ee57a83d83b56b7874bc7c716185ab52c8f7. No Framework changes or CMake changes are required: the event observer is inline C++17 and uses existing zlib/pthread linkage. B stopped Core writes before Main committed and built it. Main reports a complete production build PASS; this handoff does not substitute B header controls for that build receipt.

| Artifact | SHA256 |
|---|---|
| src/gpgpu-sim/ep-l2-event-timeline.h | 43abce5b30c3628e9ee7232f2f98c5a1c1bd471537f05139869be82df098f978 |
| src/gpgpu-sim/ep-l2-event-timeline-contract.json | e5b078dc5a544c9ae5ba0d3415b017be92f2961b36e8a7ad2a219098388f8bfa |
| src/gpgpu-sim/ep-l2-reservation-lifetime.h | 7e9e3219e7d573ba6c812e366bd969131e0485eab51eb39881665477d3c253a7 |
| src/gpgpu-sim/ep-l2-lifetime-wire-mode-contract.json | 4af9cb073d391830f4d95f3fec1ca7fad923242c688f4c1bf1ad13a99ff85cbd |
| EVENT_OBSERVER_SOURCE.patch | a745e5b7e8e266729af18daca024998c5a1ff7c52cc2f33fb3ad00ed105d87dc |
| SOURCE_STATIC_REVIEW.json | 8ef3e7277ddaa492e2b2b182a1fe98ac0b4aa1bb2bc7a26bffe532ed85e4a31c |

## API, resources, and wire

EP_L2_EVENT_TIMELINE=1 enables; absent/other values remain OFF. The public API is ep_et::{enabled,geometry,clock,emit,packet,pressure,kernel_launch,kernel_finish,finish}. All calls guard OFF before locking/allocating observer state. This is a cheap branch claim, not a measured host overhead result.

The observer has 64 rings of 512 records and four captures of PRE512/POST1536 records. Three slots accept first distinct high-pressure sets; one prioritizes full-way NEW and then actual production TagFAIL. A true fail may replace the reserved full-NEW capture. Replacement, capacity misses, uncaptured full/fail triggers, pre-loss and incomplete post-context are explicit metadata. Timeline capture is partial coverage; absence from retained snapshots is not proof of absence from execution.

Each record is 80 little-endian bytes: nine uint64 fields (ordinal,core_cycle,l2_edge,dram_edge,address,generation,aux,uid,parent_uid), two uint16 (slice,set), four uint8 (kind,domain,way,sector_mask). UINT*_MAX denotes UNKNOWN. No UID/generation truncation. The binary record's generation namespace depends on kind; tag incarnation, payload generation, and RO Tag-binding generation must never be joined by equality alone. RO_DETACH has primary payload generation and aux original Tag-binding t.generation, not payload slot.

State hard cap is 8MiB, compressed event and total event wire hard caps are each 16MiB. The 2MiB target is not a guarantee. META state_bytes is sizeof(observer)+8192 auxiliary allowance; it is not total ELF data/BSS, allocator, executable mapping, RSS, or host-process memory. Main must measure those separately. Fixed zlib arena is included in the object. Output/clock/catalog failures are explicit and the strict decoder rejects them.

EPL2_LIFE_WIRE defaults to historical FULL. SUMMARY_STAGE suppresses only WINDOW_SET emission, retains the same per-window accumulate/reset and WINDOW_STAGE, and retains all terminal Set/incarnation/histogram/stage/counter math. Its META explicitly says wire_mode=SUMMARY_STAGE and window_set_emission=0. Per-set window areas/carry are NOT_EMITTED, not zero. Both paired observer arms must use the same LIFE mode. Original LIFE 16MiB state/output guards are unchanged.

## Event/time population boundaries

Global ordinal preserves same-CORE-cycle order, including DRAM-only clock edges. CORE is the simulator core-total boundary, L2/DRAM edge counts are distinct clock-domain counters from actual next_clock_domain masks. Event kind domain is the execution domain of that notification, not a latency-conversion formula. ICNT_INJECT is emitted on CORE execution of the injection, not evidence of an ICNT transfer edge. No physical subcycle or nanosecond inference is authorized.

FRONTEND_ADMIT_DECISION (kind5) is a cached controller decision before access; FRONTEND_COMMIT (kind29) is the existing common FT1/FT2 ft_access result != RESERVATION_FAIL. Their populations differ and are separately counted. Early TVD-handled, bypass/ideal, and paths outside that wrapper are outside this frontend population. True TagFAIL is taken from the existing actual production probe, before relieve; pressure uses cached LIFE R and never issues an extra probe/CAM lookup.

The shared head/FT production path supports S/FT1 as well as F/FT2 when LIFE and detach diagnostic dependencies are enabled. It does not require m_ro. However, missing dependencies mean NOT_INSTRUMENTED. NEW is the frontend raw MISS/RESERVATION_FAIL head exposure, including repeated heads, not an accepted-allocation population. A retained NEW snapshot is not itself proof of 16/8-way actual probe failure. T eligibility/detach remains N/A where RO/T is disabled.

Finalization is only at streamID ~0ULL with !active() and !cycle_insn_cta_max_hit(). Per-kernel stats never close the application observer. With event ON, still-open LIFE observers are passively/idempotently finished at that sentinel, including RO-disabled S. Old c67 S terminal absence is unchanged historical evidence, not repaired retroactively. The kernel catalog cap64 is separate from old R4/R5 cap16; initial accepted candidates must satisfy the latter. No 19-kernel application may be silently cropped.

DRAM_COLUMN is a real RD/WR column issue notification. LOWER_DEQUEUE and existing LIFE DRAM_SERVICE/EPL2DRAM successful_* are lowerpop admission, not actual DRAM service. Fixed-delay enqueue reports the existing deadline; actual MC push can be later because of edge quantization and resource backpressure. Delay residence is known only for retained matching packet endpoints, not the entire workload.

## Executed controls and remaining requirements

B executed standalone header controls only, using CPU19/nice10/AS512MiB/one child/no GPU/no model. The preserved 13-step receipt is header_cpu_runs/637f6f61-3f27-40f3-8d4a-ce788fa3c6d5/RESULT.json (SHA14654ffebdace5f5a486375f8654572557c24a4a9e25b44bb1aae925a1ccde83). It covers 64-bit identity, same-CORE ordering, critical capture upgrade/loss, clock/overflow/catalog rejection, OFF no allocation/wire, reference digest equality, LIFE double finish, and FULL/SUMMARY terminal+stage equality.

The final four affected controls (new actual COMMIT event and final contract) are header_cpu_runs/f11e0fe7-60f2-4162-ba0f-dee50d38b0a7/RESULT.json, SHAba683e18a8c0d61e6e5a2a37833c1d3c633ee426acd0efed7724b796e6a7cbee. Compile, normal, and public API OFF/ON passed; dispatch ON recorded 2200 actual commit notifications. Earlier receipts remain immutable.

C independently decoded final43ab/e5b wires and passed 11 component controls, including valid-CRC unknown-kind and duplicate-ordinal rejection. Receipt: ../agent_c/epet_tests/a3636e31-f40e-4f1b-8fd0-6d3448c33049/RESULT.json, SHA5a515a627afdd68d6bfa9b7ee531560257b43db01a8af70e6baf500f6455aa79. These are COMPONENT_ONLY, not native application acceptance.

PROVEN by tiny controls: bounded component operation, explicit rejection/loss states, retained identity/order, LIFE output-mode terminal equivalence. PROVEN by source inspection: notifications use existing decision/event points; counted textual probe/preview/queue-operation sites remain unchanged. UNKNOWN until Main completes production controls: real-linked OFF/ON model semantics, application closure/kernel catalog, full event endpoint reachability, process RSS, application wire size and host overhead <=5%. Source inspection and sizeof do not establish any of these empirical claims.
