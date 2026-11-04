# Tag/physical liveness and design — Agent A, CPU preparation only

The two 512-Tag reorganizations pass the directed original-header tests and have a conditional allocation-headroom argument for the eight frozen declared trace inputs. They are parameter-only candidates for a separately authorized experiment. The original 1024-Tag/640-slot trap is reproducible. An isolated global-idle-reclamation prototype makes progress in that trap; its production integration and hardware timing remain HOLD.

No simulator, GPU job, scientific request, controller or service was started. Production Core, V1 results, active source pins, owner, budgets and the v0.23 manuscript were unchanged. All compilation/execution artifacts and temporary files stayed in this true164 directory. CPU work used one legal CPU at nice 19 with 2 GiB address-space, 60-second CPU and zero-core-dump limits; the original execution policy and actual logs are retained.

## Identity and evidence

Core is `9eedb3131937748f0492fa83aad37d3691118d70`, Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`. Baseline remains DH-P0, 64 SM, 10 MiB L2, DRAM 850 MHz; neither old P0 nor V1 experiments were rerun. `SOURCE_BINDINGS.json` binds the exact original header and isolated prototype. `SOURCE_EVIDENCE.json` gives fixed-Git-equal bytes, SHA and numbered excerpts, including:

- `dtc-l1-common.h:597–698`: lookup, local victim and physical allocation; `709–862`: completion/retirement; `1013–1147`: physical lifecycle, victim and free-slot search.
- `shader.cc:2745–2785`: incomplete-registration retirement guard; `3349–3456`: reference registration; `5297–5313`: dispatch held until memory-cycle completion; `450–469`: LDST construction.
- `abstract_hardware_model.cc:488–606`: global-memory coalescing, including end-byte crossing. `dtc-l1-tag-index.h:1–54`: bank/row mapping.

V1 A4001 configuration manifest and C6446219f independent original-header evidence remain historical, unchanged sources. This packet does not promote their sixteen original Tag1024 safety-HOLD cells or manufacture performance results.

## Distinguish three physical-pool conditions

| State | Evidence and permitted interpretation |
| --- | --- |
| Target set has a ready, Ref0 replaceable local victim | Existing allocator progresses. The directed full-target-set test uses the original lifetime path. |
| Slots are held by live references or pending returns | Reclamation must refuse them. Ready alone does not imply reclaimable: ready+Ref1 remains protected. Progress depends on eventual returns and legal instruction retirement. |
| Pool is full of idle Ref0 mappings in other sets while requested set has an invalid way | Original local-only allocator returns NO_FREE repeatedly despite reclaimable resources. Both Tag64×16 and Tag128×8 with pool640 reproduce this class. |

There is also an API-only adversarial case: admit 128 simultaneously partial entries, each requiring six references but registering only five, then finish all 640 references. None can legally retire. Original and prototype both HOLD. This is a useful interface-boundary counterexample; it is not established reachable through the unchanged single-dispatch production LDST and is not evidence of a measured application deadlock.

## A1: total Tag512, pool640, parameter-only candidates

| Candidate | Exact option changes from 64×8 | Total lookup mappings | Physical slots |
| --- | --- | ---: | ---: |
| TAG128x4_PHYS640 | logical_sets 128; logical_ways 4 | 512 | 640 |
| TAG32x16_PHYS640 | logical_sets 32; logical_ways 16 | 512 | 640 |

`A1_PARAMETER_CONFIGS_AND_PLAN16.json` records all eight fixed full input digests, legal original DH-P0 references/aliases, input-binding SHA, copied four-file config SHA and 270-option expected vectors. Every normalized option delta is exactly the two fields above. Its sixteen PLAN IDs are not native cohorts, UUIDs, registrations or execution authorization. Configs are in `A1_configs/`.

Both shapes completed 2,048 sequential distinct-line allocation/fill/legal-retirement operations in the exact original header, followed by a retained-hit check. This finite sequence is not a universal progress proof or performance measurement.

With bank-row hash enabled and four banks, `line=address>>7`, `s=log2(sets)`:

`set = 4 * (((line>>2) ^ (line>>s)) & ((sets/4)-1)) + (line&3)`.

Base 64 sets uses s=6/four row bits; 128 sets uses s=7/five row bits; 32 sets uses s=5/three row bits. The low two bank bits stay fixed. Mapping and associativity change together; these candidates cannot be described as an isolated associativity effect, equal hardware timing, or equal PPA.

### Conditional allocation argument and its scope

The fixed options use one memory unit and one memory-unit port. The unchanged LDST retains the same dispatch instruction until all its grouped references are registered and refuses retirement before full registration. Subject to those source-path premises, there is at most one partially registered cacheable load in that LDST. If all other fully registered entries eventually receive returns, collect, write back and legally retire, retained allocations at the relevant quiescent point are bounded by `512 + (N−1)`. With N≤32, this is at most 543, below pool640. Thus a free physical slot exists for continuing that partial load, independently of either 512-Tag shape's set associativity.

The fixed eight existing declared-body qualification receipts report max grouped 128B references: 2DCONV 2, GEMM 1, convolutionSeparable 2, scan 32, ATAX 32, MVT 32, BICG 32, vectorAdd 1. `FIXED8_REFERENCE_BOUNDS.json` pins all eight binding files. The parser counts both start and last-byte 128B lines; it does not assume natural alignment. Scan contains 439,384 unaligned lane addresses. D independently bridged parser bytes/widths to the fixed Core coalescer; `EXTERNAL_REFERENCE_BOUND_EVIDENCE.json` pins that review and actual parser source SHA.

These are bounds on the qualified declared trace bodies, not certification that they capture a complete native application. Numeric correctness remains UNPROVEN. The argument additionally assumes healthy lifetime invariants, fair downstream completion/collector/writeback/retirement, and no external dependency or fence that permanently prevents those retirements. It is not a full-GPU termination theorem, support for arbitrary input/opcode/reference counts, or a guarantee against unrelated failures. Unknown domains must obtain their own reference-bound qualification.

## A2: isolated global-idle reclamation and reservation protocol

`global_idle_lru_v2cpu.patch` changes only the isolated OO header. On no free slot and no reclaimable target-set victim, it scans valid Tags and selects the oldest eligible idle mapping globally. Eligibility requires allocated+ready+tag_valid, Ref0, empty waiters, matching physical generation and no queued return for the same identity/generation. Only that mapping is invalidated and released through the existing lifetime helper. Allocation width4, physical640, reference width13, generation checks and finite create/inject/retire service are not expanded. LaneX source-event invalidation is not called or repurposed.

This changes replacement policy and introduces a new reclaim mechanism. It is not a configuration-only repair, nor a silent replacement of V1 safety-HOLD evidence. Its one-successful-reclaim-per-cycle quota limits functional admissions but does not model a full Tag scan in one cycle. Search latency, comparators, read ports, Tag-bank writes, arbitration, fairness, area and critical-path cost remain unspecified. A future implementation needs distinct local/global reclaim and search-stall counters.

The separate fixture-level reservation protocol obtains actual complete grouped-reference count N before instruction admission, accepts only N in 1..32, reserves full initial N and retains tokens through full registration, completion and legal retirement. Repeated UID admission is idempotent; unsupported N is rejected, not clamped or dropped. `sum(reserved N) <= physical P` is maintained. A physical slot with a live reference is charged to an already registered reference. With an unregistered reserved reference, live allocations cannot consume all P; under healthy original lifetime invariants a full pool must therefore contain an eligible idle mapping. Global recycling plus fair completions/retirement gives a conditional progress route.

Reservation alone does not fix the idle retained-Tag trap: the actual fixture preserves that counterexample. Conservatively reserving N=32 for every instruction would admit only floor(640/32)=20 simultaneous entries despite raw PIB128, potentially reducing MLP substantially. Computing exact N before production admission and integrating token lifetime into actual LDST/PIB are not implemented here. The prototype does not claim a free optimization.

## Actual CPU coverage

`CPU_EXECUTION_RESULTS.json` records 22 original-header and 24 isolated-prototype cases (46 total case executions). PASS includes intentionally expected NO_FREE/HOLD classes and expected assertion deaths; it does not mean every tested state should progress. The two additional prototype cases test one-reclaim-per-cycle and exclusion of a fault-injected pending generation. The latter is deliberately corrupted interface state, not a claimed healthy production state.

`LIFECYCLE_COVERAGE.json` maps more than the requested ten categories to named cases: no active refs; multiple live refs; pending returns; Tag replacement; different sets; repeated address and de-duplication; full pool; partial PIB; generation reuse; duplicate release; duplicate return; stale PIB waiter; reservation conservation; quota. Tests preserve production retirement's full-registration condition. Shadow ref accounting, return generation and waiter generation are checked. Private-member exposure is confined to this CPU harness for observation and explicit fault injection.

## Release status and next implementation qualification

| Route | This packet's status | Missing before scientific execution |
| --- | --- | --- |
| A1 two Tag512 organizations | CPU-directed PASS plus fixed-domain conditional argument; parameter proposal only | Separate authorized native identities, exact runtime option/guard/strict qualifications; retain full trace/numeric/hardware boundaries. |
| Original Tag1024/pool640 | SAFETY_HOLD unchanged | No auto-retry, no hidden pool enlargement and no conversion into a performance negative. |
| A2 global reclaim / reservation | CPU prototype PASS for directed classes; PRODUCTION_AND_SCIENCE_HOLD | Independent Core version/binary; real LDST known-N/reservation integration; finite victim search, bank arbitration and timing; fresh lifecycle and regressions; proper counters and separately authorized experimental contract. |

The next A2 implementation Goal should implement bounded fair search, explicit search/write stalls and integration with partial registration/PIB retirement, then recheck pending returns, stale generations, ref overflow, fences, cacheable stores/atomics/bypass routing and failure cleanup before any simulation. Source-event invalidation and host-upload coherence remain separate issues. No fixture here establishes numeric payload correctness, numerical equivalence or universal coherence; no absence of a tested fault establishes safety of untested paths.

Physical slots here are 128B address/dependency identities. Slot-count×128B is nominal accounting, not demonstrated functional data payload or SRAM/PPA. Tag512 names at most 512 lookup mappings, not a continuous address span. No C++ sizeof result is a hardware-area estimate. Existing finite completion costs and original non-equal CH/DH L1/Tag/PIB structures remain disclosed; this work does not claim equal area or free port expansion.

## Reproduction

See `REPRODUCE.md`. The replay script compiles and runs only the small CPU harness into a new exclusive true164 output directory. It never opens a model log or invokes native registration/launch. Original recorded outputs are immutable evidence; reruns must not overwrite this packet. Final manifest excludes operational binaries and temporary files.
