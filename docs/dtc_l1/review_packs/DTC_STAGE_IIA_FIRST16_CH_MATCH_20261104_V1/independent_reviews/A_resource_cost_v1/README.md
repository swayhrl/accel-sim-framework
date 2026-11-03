# Hardware resource and fairness cost disclosure

Authority `5001c3f35052f7f91f1ad41eeff83f2947a0878d`; Core `9eedb3131937748f0492fa83aad37d3691118d70`; Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`. This report is read-only and does not revise experiments, release work or modify English LaTeX v0.23.

**Declared geometry ≠ active modeled path ≠ physical hardware area.** CH means the frozen conventional-cache PAPER_BASE control, not an unmodified LEGACY frontend. DH means frozen whole-line PAPER_OO. Exact source lines and per-file SHA are in SOURCE_EVIDENCE.json; all16 config identities are in CONFIG_IDENTITY.json.

## Coupled downstream factor

| Configuration | FR-FCFS slots/controller | Slots over20 controllers | Shared credits/controller | Slot/credit increase/controller fromP0 |
|---|---:|---:|---:|---:|
| P0 | 64 | 1280 | 255 | +0 |
| F128 | 128 | 2560 | 319 | +64 |
| F256 | 256 | 5120 | 447 | +192 |

Fixed source l2cache.cc131–149 sets private limit1 per subpartition and shared limit `F + returnQ192 − (2−1)`, giving255/319/447. Separate write queue is disabled, so the FR-FCFS pending window is not an isolated read-only buffer. ReturnQ192 and partition FIFOs64:64:64:64 remain fixed. The two private credits/controller are separate accounting state, not extra independent SRAM queue entries to add into an asserted total outstanding count.

L2 remains40 subpartitions ×128sets ×128B ×16ways =10MiB. Each subpartition retains192 MSHR keys, merge/request-list bound4 including the first request, and missQ32. Global logical bounds are7680 MSHR keys,30720 request references and1280 missQ slots. The sector cache uses32B MSHR atom keys; keys are not128B data-cache lines. Clocks remain1410/1410/1410/850MHz. All non-target downstream options are equal at matchedF; no memory bandwidth or data-array capacity increase was configured.

## Active L1 resources and timing

| Resource | CH | DH |
|---|---|---|
| Mode and active cache path | mode1=PAPER_BASE: ordinary L1D plus common admission/Tag scheduling | mode3=PAPER_OO: whole-line OO frontend for its selected load path; ordinary compatibility L1D object also constructed |
| Ordinary L1D declared geometry | N:32:128:24 =>768 normal128B lines,96KiB data geometry | S:32:128:4 =>128 sector-cache128B lines,16KiB compatibility geometry; not the OO physical pool |
| OO physical-line capacity model | No oo_frontend constructed;640 raw physical_lines option is not a CH OO data pool | 640 whole128B physical-line identities =>80KiB payload capacity model; tagless referenced lines can outlive tag mapping |
| OO searchable logical Tag array | No512-entry OO Tag array; ordinary cache has768 line tags from32x24 geometry | 64sets x8ways=512 OO logical Tag entries, nominal64KiB address-line coverage; separate from640-line pool and128-line compatibility tags |
| Actual instruction admission/PIB | common paper_frontend pib_entries256 is ACTIVE; live-instruction set stops admission at256 | OO frontend oo_pib_entries128 is ACTIVE. common pib_entries8 is a raw option for inactive PAPER_BASE admission under mode3; it is not OO PIB capacity |
| MSHR interpretation | dtc_l1_mshr_entries512 overrides ordinary L1D MSHR in PAPER_BASE; cache DSL A:512:8 | dtc_l1_mshr_entries32 does not override ordinary cache under mode3. OO frontend owns merge/lifetime and does not depend on conventional L1D MSHR. Compatibility cache still declares A:512:8 |
| Tag service and index | common Tag scheduling4banks x1request/bank/cycle,4total; ordinary cache B row index uses shared bank-preserving XOR helper with32sets | OO Tag scheduling4banks x1request/bank/cycle,4total; tag_hash_bankrow1 calls same helper with64sets. Same family, different row geometry |
| Allocation and reference tracking | No OO physical allocator/refcount resources; ordinary cache allocation remains its cache policy | OO allocation_width4;640 physical lifetime states;ref_count_bits13 bounds count<=8191;slot generations and waiter/reference lists modeled; physical bit layout unknown |
| Finite return/completion service | finite_service0: no DH finite-service pipeline. Conventional cache/LDST plus common admission/Tag timing still apply; this does not mean zero latency | finite_service1. Default refill/create/inject/retire quota1 each/cycle;collection4sectors/cycle;return metadata edge+1 and wakeup budget4waiters/cycle;OO retire max1/cycle. progressive_wakeup0 preserves whole-line notification gate |
| Global lower outstanding cap | 32768, active for PAPER_BASE | 32768, active for PAPER_OO; not a claim of same achieved concurrency |
| Unified-cache declaration | 96KB configuration parameter | 128KB configuration parameter; neither value is the measured OO data storage or physical area |
| Shared unchanged timing knobs | L1 latency20,mem_unit_ports1,adaptive_cache_config0;same values across P0/F128/F256 | Same scalar knob values do not make distinct completion paths cycle-equivalent; unchanged within DH |

The conventional CH hashB and DH bank-row hash invoke the same fixed bank-preserving XOR helper. They use32 versus64 sets, so row geometry differs; neither per-program hash selection nor a new mapping is introduced.

DH80KiB denotes a640×128B whole-line capacity model, not a verified physical data SRAM layout. The ordinary16KiB compatibility-cache geometry and OO data-pool representation must not be silently collapsed into either “DH totalL1=80KiB” or “DH usable data=128KiB.” Nor does arithmetic80+16=96 establish a unified physical layout or equal area. CH96KiB is declared conventional data geometry; its768 tags differ from the OO512 searchable tags and compatibility tags.

## What the experiment can support

At eachF, the experiment measures two frozen L1 organizations under identical configured downstream service. CH/DH capacities, metadata, admission structures and completion timing differ. S_CH, S_DH, matched CH/DH and interaction I are performance measures for these exact modeled designs; I>1 favours the relative DH change even when both designs slow down. No equal-area or constant critical-path claim follows.

FR-FCFS expansion adds1280 or3840 logical request slots across20 controllers versusP0 and increases the shared-credit limit by64 or192/controller. Request addresses, bank/row metadata, ordering/search state, counters, queue ports/wires and routing need hardware implementation cost. The source uses software lists/maps, not a synthesized SRAM/CAM layout. The larger search window can alter scheduling/locality/concurrency together; capacity alone does not identify which effect caused a measured speedup.

Unknowns retained: physical Tag/address/state widths, ECC, waiter/PIB/dependency encoding, memory arrays and port topology, comparator/arbitration critical paths, clock-frequency impact, silicon area and dynamic/leakage energy. Configured logical widths such as ref_count_bits13 constrain semantics; C++ uint64/vector/map sizes or host RSS do not equal physical bit costs. Host RSS is an execution-resource observation, not a hardware area proxy. No uncompleted cycles are estimated in this report.

## Terminology audit and forward clarification

TERMINOLOGY_AUDIT.json records exact fixed5001 and current execution REL narrative paths, line numbers and content SHA. No explicit sentence asserting all CH common PIB resources inactive, or DH actual OO PIB=8, was found in this scoped search. Generic “some inactive/inert knobs” warnings and the literal256/8 config-difference table remain correct but need this active-path clarification. Do not edit frozen source text or change raw parameters.

Forward wording: “CH PAPER_BASE actively models common instruction admissionPIB256 and four-bank Tag scheduling while retaining the conventional L1D/cache-MSHR path. DH PAPER_OO uses its OO PIB128 and separate physical/reference lifecycle; common pib_entries8 is not its active OO PIB capacity. Geometry, active mechanism and hardware physical area are separate.”

The old planning warnings needing this explicit supplement occur at agents/A/README.md:15, agents/C/SCIENTIFIC_REVIEW.md:34, STATISTICS_AND_HARDWARE_BOUNDARIES.md:30 and the current execution copy of that boundaries file. The machine-readable agents/C/INDEPENDENT_HARDWARE_FAIRNESS.json:37 lists the pib_entries key as a raw config difference; its line70 warning specifically says no DH-mode3 path is instantiated for CH and is not an assertion that common PAPER_BASE admission is disabled.

All science identities, first8 order, original350/named336 separation, single-owner execution and remaining48 lock remain unchanged. This is cost disclosure and interpretation only.
