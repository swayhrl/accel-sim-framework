# C13 selective Segment eligibility contract

## Purpose

This contract defines the only allowed meaning of `EXCLUDE_EMBEDDING_OUTPUT_WEIGHT_RANGE` in C13.

The diagnostic asks whether the Weight range classified as Embedding/Output by the accepted Operator-aware analysis should remain on conventional exact translation instead of participating in Weight Segment lookup. It does **not** authorize kernel-index-based bypass, phase-order heuristics, or special-casing the measured hotspot after observing performance.

## Allowed selector

The selector must be derived from immutable runtime sidecar `weight_layout` parameter names/ranges.

Primary target names:

- `model.embed_tokens.weight`
- `lm_head.weight` only if a distinct range actually exists in the immutable sidecar.

If input embedding and final output projection are weight-tied and share one range, C13 must exclude that complete shared Weight range and document this explicitly. It must not pretend to isolate only the final output kernel.

No hard-coded SimVA literal is allowed unless it is generated from and cross-checked against the immutable sidecar in the same run artifact.

## Functional invariants

Selective exclusion may change only **Segment eligibility** for the selected Weight range.

It must not change:

- trace addresses;
- object attribution boundaries;
- driver VA allocation;
- `MODELED_DRIVER_PA` mapping;
- conventional page-table translation result;
- PPN returned for an address when conventional translation is used;
- page size;
- L1/L2 TLB semantics outside the normal consequences of Segment hit/miss/race behavior;
- any non-target Weight range's Segment eligibility.

For every excluded address, conventional PTW must return the same modeled PPN as the C12 common-PA contract.

## Preferred implementation path

### Path A — input/registration-only

Prefer an existing input/registration mechanism that can express Segment descriptors/eligibility independently from VA→modeled-PPN registration.

Before replay, produce an audit proving:

1. C12 and selective runs have identical trace-list SHA;
2. identical modeled VA→PPN mappings for all registered 64 KiB Weight pages;
3. identical conventional PTW contract;
4. only Segment descriptor/eligibility coverage differs for the selected parameter range;
5. every non-target eligible Weight page has identical Segment coverage.

If a single legacy registration artifact contains both PA mapping and Segment eligibility, a changed file/hash is allowed only if the semantic diff proves the VA→PPN portion is identical and the only intentional change is Segment eligibility.

### Path B — minimal Core support

Use only if Path A is impossible.

Requirements:

- create/use a separate C13 Core branch; do not modify the C12 Core branch;
- feature must be config-gated and default OFF;
- default-OFF behavior must reproduce the C12 F7-L10 control under the new binary;
- selector is sidecar/range-driven, not kernel-index-driven;
- no change to common modeled PA backend;
- add focused static/unit validation for target-range exclusion and non-target preservation;
- build and freeze a new binary SHA;
- execute same-new-binary F7-L10 controls for Prefill and Decode1 before using selective-vs-control speedups.

A source/binary change invalidates **only cross-binary direct performance comparisons**. It does not invalidate historical C12 evidence, but C13 selective claims must compare candidate and control under the same C13 binary.

## Required selective telemetry

For each ROI report at minimum:

- selected excluded SimVA intervals and parameter names;
- total bytes / complete 64 KiB pages excluded from Segment eligibility;
- Segment attempts/hits/L2-suppressed for target range if directly observable, otherwise operator/kernel-attributed activity with scope stated;
- full-ROI cycles/IPC;
- conventional L2 TLB misses, walks, PTE requests, PTE DRAM;
- exact operator deltas for Embedding/Output, FFN, Attention Projection;
- exact kernel 691 delta where applicable;
- proof that non-target direct-layer Segment behavior is not silently disabled.

## Interpretation boundary

A positive selective result supports an object-selective translation policy hypothesis. It does not by itself prove that Embedding/Output is universally unsuitable for Segment, because the current workload/model/phase and tied-weight layout remain part of the experiment context.
