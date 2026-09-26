# Diagnostic path-model contract

## B0: CURRENT_SEQUENTIAL

- accepted `WARP_VPN_DEDUP_REFERENCE` at 10/80;
- translation completes and is applied before L1D latency-queue admission;
- 10-cycle L1 TLB and 32-cycle L1D intervals are sequential;
- source/config/binary authority remains Lane B `9efe8236...`.

## B1: VIPT_LIKE_PARALLEL_L1_DIAGNOSTIC

Scientific role: bounded access-path diagnostic, not a mechanism or hardware
claim.

- grouping, logical UIDs, mapping, page size, permissions, ports, MSHR/PTW,
  cache policy, data request count, and fallback are B0-identical;
- credit only `min(L1_TLB_lookup_latency, L1D_lookup_latency)` cycles of
  overlap;
- for frozen 10/32 this makes the effective initial L1-TLB interval zero;
- a TLB miss still executes L2/MSHR/PTW normally; its tail is not hidden;
- physical L1D outcome and lower request still occur after translation apply;
- no unverified physical tag, future information, virtual synonym shortcut,
  extra port, cancellation, or free translation service exists.

The accepted reference 0/80 runs from `32854024...` implement this conservative
timing equivalence exactly and are reused without rerun.

## B2: VIRTUAL_L1_FILTER_BOUND_DIAGNOSTIC

Status: `NOT_IMPLEMENTED_SOURCE_SEMANTICS_INSUFFICIENT`.

Logical bound only:

- a load fully served by an assumed virtual L1 with a valid cached permission
  could complete without translation service;
- every L1D miss requires normal translation before lower physical levels;
- store/atomic use baseline translation in the conservative fixture.

The integrated simulator lacks the virtual tag, permission, ASID/synonym,
coherence, reverse-mapping, and shootdown state needed to make that behavior
architecturally correct. No workload cycles or service counts are produced for
B2. This avoids turning an idealized cache hit into free oracle translation.

## Interpretation boundary

B1 measures how much accepted 0/80 sensitivity can be explained by one
source-consistent overlap model. It is deliberately more conservative than a
full VIPT implementation on long translation misses. Neither B1 nor B2 is an
upper bound on a real GPU or evidence about undisclosed Ada internals.
