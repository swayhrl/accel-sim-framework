# Final independent hardware resource and timing review

Root downstream cost package `root_hardware_resource_cost_v1`, manifest `1ffc08f7ff786c11453d91dc67fbdc197f0370c617d2f91d32d43ad78220da49`, **passes independent source/unit/arithmetic review**. Reused first16 resource statements were preserved; this supplement rechecked every source SHA/text against the fixed Core Git blob and6 accepted BlackScholes CH/DH P0/F128/F256 effective-option records (a configuration witness, not a performance-population selection). Same-F designs retain the exact7 declared L1 differences; within each design only the FR queue field changes acrossF. No source/model/registry/v0.23 change occurred.

## Downstream logical counts and units

| Profile | FR pending request slots/controller | All20 controllers | Extra FR slots vsP0 | Shared credits/memory partition | Extra shared allowance over20 |
|---|---:|---:|---:|---:|---:|
| P0 |64|1280|0|255|0|
| F128 |128|2560|1280|319|1280|
| F256 |256|5120|3840|447|3840|

`shared_limit = FR + return_queue192 − (subpartitions2−1)` because separate write queue is0; each L2 subpartition also retains one private credit. `l2cache.cc131–175`, `dram.cc164–176`, `dram_sched.cc72–86` establish the coupled control and mixed read/write pending-window semantics. FR entries count pending `dram_req_t` requests; credits count arbitration allowance, not another independent SRAM payload queue. **Do not add extra FR slots and extra credits as two buffer arrays.** ReturnQ192 and partition FIFOs64:64:64:64 remain fixed.

20controllers×2subpartitions=40L2 banks, each128sets×128B×16ways=256KiB, total10MiB data geometry. Per-bank192 sector-MSHR keys, merge bound4 including first reference, missQ32 remain fixed:7680 keys,30720 request-reference bound,1280 missQ slots chip-wide. Sector keys are32B atoms, not128B line tags. Core/ICNT/L2/DRAM clocks remain1410/1410/1410/850MHz. These counts do not establish hardware bit layout, queue occupancy or physical timing closure.

## L1 active resources and timing

**Raw option ≠ active path ≠ physical area.** Units below are perSM unless stated.

| Item | CH PAPER_BASE | DH PAPER_OO |
|---|---|---|
| Conventional cache geometry | N32×128B×24:96KiB,768ordinary line tags | S32×128B×4:16KiB compatibility geometry,128ordinary line tags; not OO pool |
| OO physical/reference pool | Raw640 field does not instantiate an OO frontend |640whole128B physical identities:80KiB payload-capacity model; references can retain a line after Tag mapping loss |
| Searchable OO Tags | No separate OO512-tag array; ordinary cache tags above |64sets×8ways=512logical tags,64KiB nominal searchable-line coverage, separate from physical640 and compatibility tags |
| Active instruction admission | Common PIB256 plus common4-bank Tag scheduling | OO PIB128 with slot generations/references/dependencies; rawcommonPIB8 is not active OO capacity |
| MSHR fields | RawDTC512 overrides ordinary cache in mode1; DSL512:8 | RawDTC32 does not override in mode3 and is not an OO MSHR capacity; compatibility cache retains DSL512:8 for eligible route |
| Hash/Tag service | OrdinarycacheB uses bank-preserving XOR helper with32sets; commonTag4banks×1/request perbank/cycle,4total | Same XOR family with64sets; OO Tag4banks×1/request perbank/cycle,4total; different row geometry |
| Allocation/reference bounds | Conventional path; no OO physical/refcount allocator | Structural allocation_width4;ref_count_bits13 bounds count≤8191; these are not a specified physical encoding or guaranteed4 allocations every cycle |
| Completion | finite_service0; conventional LD/ST/cache plus active common admission/Tag timing | finite_service1: refill/create/inject/retire quota1grant each perabsolute corecycle;collection4sectors/cycle,return metadata+1edge,wakeup4waiters/cycle,OO retirement≤1instruction/cycle;progressive_wakeup0 |
| Shared lower cap |32768global outstanding lower-request allowance |Same global scalar allowance, not equal achieved concurrency |
| Raw unified declaration / ordinary timing |96KB /L1_latency20,4ordinary banks,mem_unit_ports1,adaptive0 |128KB /same raw scalar knobs; selectedOO loads use the OO Tag/finite-service path and do not inherit identical ordinary20cycle service |

The constructor builds DH ordinary `m_L1D` (`shader.cc4414–4433`) **and** the separate OO frontend. It is incorrect to call this cache globally inactive: `shader.cc4017–4019` intercepts only non-atomic, nonbypass loads forOO; `4067–4069` retains `process_memory_access_queue_l1cache(m_L1D,inst)` for other eligible nonbypass operations, such as applicable stores/atomics. Bypass traffic retains the ICNT route. Thus16KiB does not serve the intercepted load path, but cannot be deleted from area as though no route can use it. Actual instruction policy/routing determines use.

Qualified static trace records provide relevant classes (BlackScholes6250ordinary-store records; histo649960ATOMIC_L2 and1154560ordinary-store records), **not** measured per-route conventional-cache hits/occupancy. `COMPATIBILITY_ROUTE_EVIDENCE_GAP.json` binds those inputSHA and units. No claim that every such operation traversed compatibility L1, or that all bypassed it, is made by this cost review.

80KiB OO pool +16KiB compatibility geometry must not be advertised as a single unified96KiB effective cache or equal-area comparison. Likewise rawunified128 is not measured OO usable data. The declaration influences a maximum geometry multiplier, while adaptive_cache_config0 preserves the configured active associativity. CH96KiB also excludes the active common admission/Tag control cost; CH is not an untouched vanilla cache frontend.

## What remains unquantified

Physical Tag/state/address/ECC widths; OO/compatibility array sharing or duplication; PIB/waiter/reference/generation encoding; banking, ports, fanout and wiring; FR request metadata/search state; timing closure, area and energy. C++list/vector/map/pointer sizes or hostRSS do not measure these chip resources. Credits are accounting, not free independent storage. Fixed simulated clocks do not prove expanded windows retain physical frequency. Matching downstreamF therefore measures exact unequal L1 organizations; it does not establish isoarea, equivalent hit/completion timing, an optimalF or isolated queue causality.

`SOURCE_EVIDENCE_RECHECK.json` supplies all fixedCore path/line/SHA anchors, including the new fallback eligibility callsites. `L1_TAG_POOL_PIB_TIMING_TABLE.json`, `DOWNSTREAM_FORMULA_INDEPENDENT_REVIEW.json` and `ACCEPTED_EFFECTIVE_OPTIONS.json` carry machine-readable quantities and complete accepted identity pins. CPU qualification has7 independent invariant families and101 loop/assertion checks; assertion volume is not an added evidence level. Only Root publishes; prior reports and historical configurations remain frozen.
