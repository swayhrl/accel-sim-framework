# ADR-004 — Baseline / Mechanism Switching Is a First-Class Architecture Interface

## Context

EP-L2 will be evaluated through repeated baseline, single-mechanism, ablation, composition, and headroom experiments. If each mechanism requires a different branch, binary, or hand-edited config, source/config provenance becomes difficult to audit and mechanism comparisons can accidentally include unrelated deltas.

The calibrated resource baseline (for example Descriptor D256 vs D512) is also a different decision dimension from functional mechanisms such as Unified Payload, RO pending-state decoupling, or TVD.

## Decision

EP-L2 implementations will separate:

```text
calibrated base resource configuration
from
functional mechanism feature vector
```

Formal comparisons should use the same source/binary family with explicit mechanism feature switches. The all-OFF feature vector must reproduce the accepted parent baseline. Mechanism combinations must be represented by explicit orthogonal features where practical, with deterministic runner/config/manifest support.

The detailed contract is `../EXPERIMENT_MODE_SWITCH_CONTRACT.md`.

## Alternatives rejected

### One branch/binary per mechanism

Rejected for formal evaluation because branch/source differences become a confound and ablation/composition becomes cumbersome.

### One monolithic numeric mode encoding all resources and mechanisms

Rejected because it couples baseline calibration to mechanism semantics and makes pairwise config auditing/ablation less transparent.

### Enable experimental behavior by default

Rejected because missing config fields could silently change baseline semantics.

## Consequences

- M1 must expose a baseline/static-compatible OFF mode and prove exact equivalence.
- M2/M3/M4 must be explicit feature switches above the calibrated base-resource configuration.
- runners/manifests must record the feature vector and mode label.
- integrated EP-L2 must support clean ablation without rebuilding unrelated source variants.
- unsupported feature combinations fail closed.

## Evidence / review

This is a design-governance decision before functional implementation. Source-level option names and exact plumbing are to be finalized by Lane F / M1 implementation review.
