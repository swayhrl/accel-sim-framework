# G3-2B — generic trace-width extension and G3-2 resume

Status: `AUTHORIZED AFTER G3-2A CASE-A REVIEW`

## Architecture decision

G3-2A proves that the generic Accel-Sim trace stream contains legitimate, active, trace-derived global transactions whose raw/coalesced `SimVA` requires 56 bits. Therefore the generic M1-M3 VM substrate must not hard-code the Segmentation paper's 49-bit VA width.

For the generic M1-M3 baseline:

- keep the frozen M1 meaning that the coalesced trace address is `SimVA`;
- do not mask, truncate, canonicalize, sign-extend, or otherwise rewrite `SimVA`;
- preserve the resident identity-like data mapping: `SimPA == SimVA`;
- make the generic PTE-backend VA width configurable;
- use **56 bits** for the current generic M3 trace-driven baseline because the complete disabled/ideal BFS controls observed a maximum width of 56 bits;
- a request requiring more than the configured generic width remains a hard correctness stop;
- the Segmentation paper's 49-bit address width remains a **paper-specific later configuration**, not a generic trace contract.

This is a simulator modeling decision, not a claim that commercial SM86 hardware exposes a 56-bit architectural VA.

## Important trace-encoding observation

The first high address is `0x00fffdc0000000cd`. It is suggestive of a 49-bit payload represented with repeated high bits, while the target paper itself assumes a 49-bit VA. Do **not** use that observation to rewrite generic M3 addresses.

As part of this stage, record a non-blocking provenance audit over all available BFS transactions at/above `2^49`:

- raw/coalesced address;
- bits `[63:56]`, `[55:49]`, and bit 48;
- lower-49-bit value;
- whether the observed form is consistent with a deterministic 49-bit sign/canonical extension pattern;
- whether two distinct raw addresses collapse to the same lower-49-bit value.

Label the result `TRACE_ENCODING_OBSERVATION` only. It is evidence for the later paper-specific trace adapter, not authorization to canonicalize generic M3.

## G3-2B.1 — make generic backend width configurable

Remove the semantic hard-code `virtual_address_bits == 49` from the generic page-table backend.

Required:

- accept an explicitly configured supported width that safely fits the 64-bit simulator address type;
- current generic M3 default/test configuration = 56 bits;
- retain a directed 49-bit configuration test because the later target-paper configuration still needs it;
- compute VPN namespace width, required PTE reserved bytes, bounds and overflow checks from the configured width;
- no undefined `1ULL << 64` or arithmetic overflow;
- do not change page size, levels, ASID-0 scope, TLB semantics, identity mapper semantics, or PTE request type.

## G3-2B.2 — reserved physical ranges

For the 56-bit generic baseline, application identity-like `SimPA` values must remain below the PTE-reserved region.

The implementation may use equivalent explicit/config-derived values, but must prove at least:

- generic application physical limit covers every valid 56-bit `SimPA` and is exclusive;
- PTE physical base is at or above that limit;
- the complete PTE namespace for 64KB and 2MB × four levels fits in the reserved PTE range;
- PTE range end does not overflow 64 bits;
- application and PTE physical ranges do not overlap;
- all page-size-class/level namespaces remain pairwise disjoint at min/max VPN boundaries.

For the current flat deterministic PTE-identity scheme, 56-bit VA with 64KB base pages implies a 40-bit maximum VPN namespace. With 4 levels, 2 page-size classes and 8-byte PTE identities, the theoretical reserved namespace is 64 TiB. This arithmetic is only address-space reservation; it must not allocate 64 TiB of host memory.

Do not claim this synthetic reserved range is a commercial GPU physical-address layout.

## G3-2B.3 — directed tests

Add/extend machine-checkable tests for:

1. original 49-bit G3-1 cross-page-size collision remains impossible;
2. 56-bit generic backend accepts the exact G3-2A offender;
3. boundary address below `2^56` is accepted;
4. request requiring more than 56 bits is rejected/stops explicitly;
5. all 8 `(64KB/2MB × level0..3)` namespace min/max ranges are disjoint under 56-bit configuration;
6. 49-bit configuration still passes its original namespace tests;
7. PTE request remains physical and translation-bypassing;
8. identity data mapping still returns the original raw `SimVA` numerically as `SimPA`.

## G3-2B.4 — re-run G3-2 real memory path

After the width/range contract passes directed tests, reapply or reimplement the local G3-2 WIP against the accepted source. Historical stash is not evidence and must not be blindly popped.

Re-run:

- standalone multi-walker/out-of-order PTE response identity test;
- one-kernel cold PTE DRAM test;
- BFS small-TLB replay through the previously failing kernel and to normal completion where feasible;
- LUD functional/integrated smoke;
- M1 transparency and repaired M2 directed regressions;
- PTE request/response conservation;
- zero response misassociation;
- final MSHR/PWQ/walker quiescence;
- shared-resource-pressure evidence.

G3-2 PASS requires the previously failing `0xfffdc0000000c0` transaction to translate without changing its raw `SimVA` identity-like data address.

## G3-2B.5 — STOP before PWC

Even if G3-2 closes, STOP before G3-3.

Reason: current G3-1/G3-2 PTE identity is a collision-free flat per-level/full-VPN synthetic model. Before PWC/timing characterization, ChatGPT must separately approve the hierarchy-prefix/PTE-sharing semantics so PWC locality is not based on an accidental flat-address model.

## Explicitly forbidden

Do not:

- canonicalize/mask/truncate the raw SimVA;
- reinterpret the current 56-bit generic baseline as target-paper exact;
- change TLB replacement/MSHR/PWQ/replay semantics;
- change page size defaults beyond the already authorized 64KB/2MB generic support;
- expand to multi-ASID;
- implement PWC;
- implement Segmentation/sub-entry/synthetic KV;
- implement page fault/migration/UVM/MCM;
- hide an address-width assertion by silently modulo-mapping PTE addresses.

## Deliverables

Update:

- `docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`
- `docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`
- `docs/vm_tlb/review_packs/M3_TIMING_REALISTIC_BASELINE/`

Add compact evidence for:

- trace high-bit encoding audit;
- configured-width/range arithmetic;
- 49-bit and 56-bit namespace tests;
- exact former BFS offender;
- G3-2 integrated PTE memory-path validation.

Commit/push safe Core + Framework results and STOP for ChatGPT review before G3-3.
