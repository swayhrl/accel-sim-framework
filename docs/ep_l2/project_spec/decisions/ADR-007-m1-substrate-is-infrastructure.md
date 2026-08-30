# ADR-007 — M1 Elastic Substrate Is Infrastructure, Not a Long-Term Functional Feature

Status: **ACCEPTED**

Date: 2026-08-30

## Context

The experiment-mode contract requires the same post-implementation source/binary family to run the calibrated baseline and mechanism ablations through explicit configuration. Lane-F proposed an `elastic_substrate` feature bit in addition to Unified/RO/TVD bits.

M1, however, is intentionally behavior-preserving plumbing: global payload-ID representation, explicit slot role/owner/generation state, tag-to-payload sidecar and static allocation policy. Keeping both the pre-M1 payload implementation and the M1 substrate as long-lived runtime-selectable functional paths would duplicate state machines and increase correctness risk without providing an architectural ablation.

## Decision

After M1 is accepted, the M1 substrate becomes the sole implementation substrate in that source family. It is **not** a long-term functional mechanism bit.

The authoritative functional feature vector is conceptually:

```text
unified_payload      0/1
ro_pending_state     0/1
tvd                  0/1
adaptive_policy      0/1
```

with any later mechanism-specific bits added explicitly.

All functional bits OFF plus `payload_policy=static` means the accepted calibrated baseline semantics.

## M1 validation model

M1 itself is validated across source revisions:

```text
accepted D512 parent source / BASE
        vs
post-M1 source / all functional features OFF / static policy
```

Required equivalence includes simulated cycles, deterministic existing telemetry, request/fill/response behavior, bank mapping/grant order and terminal invariants on representative workloads.

A temporary development-only selector may be used locally while bringing up M1, but it must not be required by the long-term experiment interface and must not leave two competing payload state machines in the formal post-M1 source.

## Consequences

- Formal mechanism experiments after M1 use one payload implementation substrate.
- `BASE` is unambiguous: all functional mechanism bits OFF, static policy.
- `M2_UNIFIED` differs from `BASE` only by the Unified policy/feature fields.
- M3/M4 ablations remain orthogonal to the base-resource configuration and to one another where composable.
- Runner labels do not need an `M1_STATIC` row in final paper experiments; that label may remain only in M1 validation evidence.
