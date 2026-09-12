# POST-FAST64 Review Adjustments After Lanes A/B/C

Status: **REVIEWED INPUT FOR LANE D / LANE E INTEGRATION**

Reviewed branch heads:

- Lane A `c1774a452e244d431c215010b1039e9d3e074f2a`
- Lane B `757b8cbf2c536b04f8a6ef4db847af04f337378d`
- Lane C `18800873478576309b08b538974c3872fc2cb6df`

These adjustments do not invalidate any lane PASS. They constrain later integration wording and define additional observer requirements.

## A. Lane-A presentation adjustments

1. Prefer the paper label `HOL-exposed SM-cycle fraction` for
   `io_hol_ready_younger_cycles / (64 * io_cycles)`. It is not a total stall fraction or memory-pipeline-active stall ratio.
2. Preserve the accepted FAST64 historical causal label as provenance, but add a separate paper-facing interpretation label. In particular Gaussian should be presented as a modest ~1.108x beneficiary with IO approximately equal to OO, not mechanically as a non-beneficiary.
3. Base pressure per-million-instruction is valid derived data but mixes memory-intensity differences across workloads. Final paper figures should retain raw counts and prefer/add a denominator closer to exposure, such as per SM-cycle or a source-defined memory-domain denominator when available. Never fabricate a denominator.

## B. Lane-B H2 refinement

Lane-B correctly rejects a universal cross-workload causal story. However final integration must not reduce the BICG/GESUMMV evidence to a simple null.

For BICG/GESUMMV IO, existing accepted physical-sweep data show that as pool grows from 24 to 48 KiB, normalized no-free exposure per SM-cycle decreases while L2 reservation failures/misses per lower request and cycles rise. This is a meaningful measured association. Btree remains a counterexample/control with largely invariant 24–48-KiB behavior.

Therefore integration must use this distinction:

- universal H2 across workloads: `DATA_DOES_NOT_SUPPORT` / not universal;
- BICG/GESUMMV local H2: at least `MEASURED_CORRELATION`, causal status pending Lane-D occupancy/inflight/lifetime evidence.

Lane-D adds exact time-integrated physical occupancy/full and lower-inflight exposure so that retry-event counts are not misused as occupancy duration.

## C. Lane-C duplicate-request extension

Lane-C source semantics and accepted IO quantification are accepted. The following derived metric is required for paper-facing integration:

`duplicate_traffic_inflation = duplicate / (lower_created - duplicate)`

This expresses duplicate lower-request payloads per non-duplicate lower request. It must be labeled request-payload inflation, not DRAM traffic and not total link traffic.

Examples from accepted Lane-C IO evidence, for intuition only and to be regenerated from the committed table:

- LUD: duplicate share ~6.08%, traffic inflation ~6.47%;
- GEMM: ~10.34%, inflation ~11.53%;
- 2DConvolution: ~42.22%, inflation ~73.07%;
- Gaussian: ~50.20%, inflation ~100.8%.

Lane-E must regenerate these values from committed Lane-C evidence and retain exact provenance rather than copy rounded prose.

The scientific claim boundary remains:

- Lane C proves duplicate **lower request payload** at 128 B each for accepted PAPER_IO semantics;
- it does not prove equivalent DRAM traffic, total interconnect traffic, or performance improvement from hypothetically removing duplicates;
- OO needs Lane-D exact observer semantics rather than an inferred proxy.

## D. Integration priority

The strongest post-FAST64 question is now whether the following chain can be supported beyond correlation:

`physical pool -> occupancy/inflight exposure -> L2 pressure -> pending lifetime -> pending Tag eviction -> duplicate request feedback -> performance`

A second OO-specific chain is:

`Tag eviction -> deferred physical lifetime -> final reclaim -> exposed concurrency/performance`.

Lane-D must collect only the minimal observer data needed for these arrows, prove observer equivalence first, and preserve all negative or nonmonotonic outcomes.
