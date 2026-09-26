# Residual-headroom diagnostic preregistration

Recorded before any new diagnostic result was generated.

## Strong baseline

`WARP_VPN_DEDUP_REFERENCE` from Lane B commit
`9efe8236e0c6338addfef5480e1da91bffb504eb` at frozen 10/80.

Historical OFF and PREL1 are not performance baselines for this stage.

## Fixed Phase-C diagnostic

Run exactly one configuration-only causal diagnostic on the four targets
preselected by the Goal:

- T0: prefill Flash and the largest strong-reference improvement;
- T1: prefill GEMM with the largest translation work;
- T2: decode GEMV and a strong-reference regression/control;
- A2: long-context exact GEMV and a positive strong-reference response.

Comparator: the same frozen Lane-B binary and reference mechanism, changing
only modeled L1-TLB lookup latency from 10 to 0 cycles while keeping L2 at 80.
Name: `REFERENCE_L1_0_L2_80_DIAGNOSTIC`.

This is a causal diagnostic, not a mechanism, hardware proposal, or upper
bound. It does not change grouping, request generation, ports, capacity,
mapping, L2/MSHR/PTW policy, page size, or trace identity.

## Decision rule

`MATERIAL_RESIDUAL` requires more than 1% cycle reduction relative to the
accepted WARP reference on at least one preregistered target, with identical
instruction/CTA/logical coverage, zero untranslated/unobserved/duplicates,
terminal quiescence, and unchanged non-latency service counts unless a
source-explained timing interleaving changes them.

The 1% cutoff is a preregistered project decision, not a literature fact. Raw
responses are always reported.

If no target exceeds 1%, stop with
`CURRENT_AI_TRANSLATION_MECHANISM_SEARCH_NOT_JUSTIFIED`.

If material residual exists, localize it before any candidate code. A zero-
modeled-translation-service diagnostic is allowed only on the target(s) that
pass this gate and only if 0/80 plus existing Observatory evidence cannot
separate hit-path latency from miss-side/downstream hiding.

## Explicit exclusions

- no H1 or H2 performance policy;
- no extra observer run before examining existing evidence and this fixed
  diagnostic;
- no candidate implementation, parameter sweep, PREL1 repair, new trace,
  node109, RTL, or PPA;
- maximum new full-kernel runs at this point: four of the Phase-C budget of
  eight.
