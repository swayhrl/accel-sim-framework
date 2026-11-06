# Implementation and CPU qualification

The real option is -gpgpu_dtc_oracle_mode:0=OFF_MATCHED,1=M_DATAREAD,2=L2_DATAREAD,3=L1_DATAREADY. Eligibility originates at logical OO admission: cacheable non-atomic global loads excluding explicit/configured bypass. Parent UID, physical generation and required-sector mask propagate through actual carrier constructors and sector breakdown. Stores, writebacks, atomics, instruction/constant/texture traffic and fence ordering retain their original paths. Stock perfect_mem and l2_ideal stay0.

| Mode | Actual intervention | Retained limits |
|---|---|---|
| M_DATAREAD | After real lower-create/local inject acceptance, replace eligible downstream transport/L2/DRAM by a finite cluster RR return sequencer: at most one32B reply per cluster/core tick, earliest next tick. | **Original ICNT-full admission still gates the push before interception.** This is not unlimited/ideal ICNT admission. Lower credits, bounded shared FIFO, normal-traffic fairness and finite receiver/refill/notify/collect/WB/retire remain. |
| L2_DATAREAD | After real routing, sector breakdown, ROP delay and finite bank admission, use the original HIT return path without real read-miss/MSHR/DRAM allocation. | Original L2 data-port occupancy, bank/return-FIFO gates and reverse ICNT remain. This source has no additional post-ROP HIT-latency queue. Virtual reads do not probe or warm physical tags. |
| L1_DATAREADY | After original Tag/physical admission, one generation-bound next-tick event per eligible new line replaces lower/refill work and enters original finite completion service. | Tag512/physical640/PIB128, replacement/Ref registration, partial-dispatch obligations, finite completion and scoreboard remain. No fake lower request or ordinary response is created. |

M parents close only after every required sector; the receiver checks UID/id/generation/mask and rejects unknown/duplicate/stale replies. Original lifecycle checks remain. Virtual work has separate counters; an absent counter is not zero.

CPU evidence:

- M:335 positive checks and12 expected-abort controls under UBSan, including real constructors/breakdown, scheduler/shared FIFO and receiver methods.
- L2:119 extracted-method checks for active bank/port/FIFO service, normal-path controls and invalid ownership/type rejection.
- L1:105 positive checks, five expected-abort controls, sanitizer execution and an18-tick OFF method differential.
- Complete Core/Framework builds and18 existing CPU ctests pass, with assertions retained and independent review.
- The real configuration parser passes32 inputs x four modes=128 CPU cases and34,560 comparisons of original270 values. There are271 unique keys/272 physical rows because historical -gpgpu_shmem_warp_parts is registered twice identically. Invalid/unknown modes are rejected. Duplicate options retain historical last-wins behavior, so frozen configurations/argv must require one Oracle enum declaration.

CPU checks do not establish actual input completion, runtime exposure, numerical correctness, GPU cycles or acceptance. Every actual mode still needs its public qualifier, natural strict lifecycle, true164 archive/SHA and native restore.

Pending-only GDB bootstrap returnsQUEUED=0 but fails to execute from unbounded Main join within15seconds. Separate direct-Main GIL CPU tests pass eight cases covering join, real threading._shutdown, preserved wait/FD/locks, exceptions and later typed continuation.

The subsequent read-only actual-owner observation is decisive: threading._SHUTTING_DOWN=True, futures.thread already loaded, futures._shutdown=False, and sys.is_finalizing=False. An early atexit keeper blocks before futures shutdown. The matching R CPU lifecycle and D independent replay both pass actual ThreadPoolExecutor jobs before and after later Main-thread continuation, preserving FD locks and private flags. Thus ThreadPoolExecutor is not a current-owner HOLD. The earlier CPU failure without preloaded futures remains an initialization-specific negative; it must not be generalized to this owner.

The aligned R3/runtime and owner/shared-pool preparation passes128 native CPU-only /usr/bin/true layout cases:32 initial rows plus96 extension rows, with0 science UUIDs, registrations or model starts. These are engineering fixtures, not hidden model canaries or scientific results. Final independent Gate0 admission is still pending.
