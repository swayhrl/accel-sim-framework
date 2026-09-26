# Native interpretation freeze

Frozen before any 174 simulator result for the Native Atlas targets.

Authority:
`hrl/awma-ai-translation-native-atlas-capture-109-v1`
at `39548abdd83bf5058abc5ffedd9513286ddab271`.

The Native handoff status is
`READY_FOR_AI_TRANSLATION_RESIDUAL_174NEW`. All address statistics are virtual-
address observations only. They do not establish physical contiguity, PPN
stability, TLB behavior, Avatar prediction accuracy, or comparable raw runtime
between model families.

## L1 and M1: exact implementation, 8x scale control

- exact function SHA-256 for both:
  `e52f28ddc664202dcf583dfef5266a7d06e21d90dcaf3c98eb3b6c993036ea9d`;
- block for both: `16,4,1`;
- L1 grid: `2048,1,1`; M1 grid: `256,1,1`;
- scale ratio: exactly 8 CTAs;
- per CTA for both: 514 dynamic memory instructions and 16,388 active-lane
  references;
- per CTA for both: exactly 258 one-page instructions and 256 two-page
  instructions under the Native 4KB analysis.

Therefore L1/M1 compare scale and aggregate working-set/capacity effects for
the same implementation. They are not evidence that MoE changes local GEMV
page behavior. Raw cycles across the two models are not normalized runtime
claims; per-CTA and per-memory-instruction quantities are required.

Native aggregate virtual pages differ: L1 observes 8,198 unique 4KB pages and
M1 observes 1,026 under separately frozen tokenizations. This is an aggregate
working-set observation, not a local-instruction semantic difference.

## M2: low translation-demand control

M2 is one CTA with two dynamic memory instructions, nine active-lane refs and
two virtual 4KB pages. It is preregistered as
`LOW_TRANSLATION_DEMAND_CONTROL`. It cannot support a scenario-wide MoE claim
and receives no adaptive diagnostic unless strong-baseline evidence is
unexpectedly material.

## L2: blocked attention-like target

L2 has a distinct attention-like structure and retains useful Native virtual
page behavior, but its simulator trace is
`TRACE_GRAMMAR_BLOCKED` due to `LDC.U8` width representation. It has no
simulator result unless the width can be reconstructed deterministically from
accepted producer/consumer semantics with zero ambiguity.

The original L2 artifact remains immutable. No replacement target is selected.

## Pre-result decision rules

- L1/M1 first run B0 `WARP_VPN_DEDUP_REFERENCE` at 10/80.
- If hit-dominated with low miss-side pressure, run only the accepted B1-
  equivalent 0/80 path diagnostic.
- M2 runs B0 only by default.
- No target receives a walker/MSHR diagnostic unless its measured pressure is
  material and survives B1.
- No mechanism/prototype exists unless the differentiated residual gate passes.
