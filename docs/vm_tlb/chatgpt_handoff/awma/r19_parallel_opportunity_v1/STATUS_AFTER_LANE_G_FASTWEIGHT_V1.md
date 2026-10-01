# R19 Lane G final review — fast-weight / TTT

Date: 2026-10-01

Execution authority:
- branch: `hrl/awma-r19-fastweight-authority-109-v1`
- commit: `4ef10349b198d6989ab666309fbe95ce8993bc56`
- tree: `401b06c233cc2d2e31c6bb41c2eab7a844b03ec4`
- formal label: `R19_FASTWEIGHT_STRONG_SOFTWARE_SUFFICIENT`

## Authority

Accepted artifact:
`hungngo04/gemma-3-1b-it-ttt-tinystories-500k@c4ec10a9e061c64c7db5fd6277b3fa545292a49f`

Classification:
`PUBLIC_REPRODUCTION_ARTIFACT`

It is not an official In-Place-TTT / TTT-NTP paper checkpoint.

The official TTT-NTP and In-Place-TTT sources were correctly rejected as checkpoint authorities because their public paths require training/continual pretraining before inference-time TTT is semantically valid.

Input:
- public Banking77-derived HELMET prompt
- source commit `57ec275d8078af65b7731c2a98be812d844a6d6b`
- seed 1337
- natural first 256 tokens
- ttt_chunk=128
- two chunks
- adapted layers [0,6,12,18,24]

## Semantic qualification

Accepted:
- all five adapted layers produce nonzero prompt-derived fast-weight deltas;
- the second chunk consumes updated `W_down + eta * delta`;
- updated consumer differs materially from base/no-write consumer;
- model parameters themselves do not mutate;
- reset/repeat final logits are bitwise identical;
- total ephemeral fast-weight state = 79,626,240 bytes.

This establishes a real local inference-time fast-weight path for this reproduction artifact.

## Software counterfactual

Released local organization:
- batched chunk organization;
- materializes/uses cat+cumsum weight-history style operations;
- complete five-layer local boundary median = 2.079488 ms.

Bounded two-chunk closed-form reorganization:
- keeps the same mathematical two-chunk update relation;
- computes chunk0 with base W and chunk1 with `W + eta*delta`;
- median = 1.592320 ms;
- improvement = 23.43%.

Important numerical scope:

The closed form is **mathematically equivalent**, but not bitwise/elementwise identical to the released BF16 execution. The canary intentionally accepts tight finite-precision differences caused by a different contraction / reduction organization:
- per-layer cosine >= 0.99999;
- per-layer mean absolute error <= 5e-3;
- layer 0 has max_abs=0.5 and fails rtol=atol=1e-2 allclose despite cosine ~0.9999974 and mean_abs ~0.001176.

Therefore the 23.43% result must be described as:
> a strong software execution reorganization under the frozen semantic/numerical contract,

not:
> a bitwise-equivalent implementation speedup.

No end-to-end model-quality equivalence was established beyond this local contract.

## State-read boundary

Five-layer first dependent consumer with updated state ready:
- 0.237568 ms median

Same consumer with base/no-write state:
- 0.245760 ms median

The updated-state read is not slower in this bounded test.

Therefore the 79.6 MB fast-weight state size does not translate into an independently observed post-update state-read/lifetime penalty here.

The update-only path is 1.192192 ms and consists of dense, method-mandated gate/up, depthwise Conv1D, target projection and outer-product work. Current evidence does not isolate a separate state-management residual from that required math.

## Final project interpretation

Accept:
`R19_FASTWEIGHT_STRONG_SOFTWARE_SUFFICIENT`

with narrow meaning:

> On this public reproduction artifact, real prompt-derived fast-weight updates are present and material, but the observed implementation headroom is explained by software execution organization, while the first dependent read of the updated 79.6 MB state shows no independent penalty. No fast-weight state hardware line is admitted.

Do not generalize to:
- official TTT-NTP / In-Place-TTT checkpoints;
- all test-time training algorithms;
- longer contexts / more chunks;
- algorithms with different normalization or recurrent update rules;
- end-to-end accuracy or throughput.

## Current lane state

Lane G / fast-weight: STOP in current scope.
Do not add NSYS/NCU to rescue this result.
Do not start 174 or a hardware mechanism.

Lane F R19F1 continues independently.
Lane E R19E1 continues CPU/source-only.
