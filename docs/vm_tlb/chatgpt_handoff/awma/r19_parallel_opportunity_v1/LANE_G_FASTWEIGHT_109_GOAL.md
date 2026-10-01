# Codex Goal — Lane G / node109
## R19 fast-weight / TTT real-artifact authority and bounded Native boundary V1

Execution branch:
`hrl/awma-r19-fastweight-authority-109-v1`

## Question

Can we obtain a real, provenance-qualified test-time-training / fast-weight path on node109, and if so, does its actual update->read/commit phase expose a material local execution/state-management cost after the released software path?

This lane must not manufacture fast weights from random matrices.

## G0 — source and checkpoint authority, CPU first

Pin and inspect:
- `yancyou/TTT-NTP@c11da918d9a5aebf3f3cb0f45a79c2e66d9ad79a`
- `ByteDance-Seed/In-Place-TTT@be2324829b0e91c8fd10a74d4b43714fde6676e1`

Important:
- TTT-NTP Qwen3-0.6B release recipe requires training before its closed-form inference checkpoint is valid; base Qwen3 alone is not a qualified TTT-NTP model.
- do not launch the 100-step/0.2B-token training campaign just to manufacture input.
- official In-Place-TTT source likewise does not make an arbitrary base checkpoint a trained TTT checkpoint.

Search public/local artifacts narrowly:
1. existing node164/local assets;
2. official paper/project release locations;
3. public third-party HF artifacts with explicit provenance/config.

A third-party artifact may be admitted only as:
`PUBLIC_REPRODUCTION_ARTIFACT`
if exact model files/config/remote-code identity and training provenance are documented well enough to run a real fast-weight path. Never call it the official paper checkpoint.

If no qualified real TTT checkpoint exists:
`R19_FASTWEIGHT_INPUT_AUTHORITY_NOT_QUALIFIED`
with CUDA=0, STOP.

No self-training.

## G1 — platform admission

Prefer the smallest qualified artifact.

A 4B public TTT artifact may be used only if:
- exact model/config fit on RTX4080 for a bounded context;
- actual TTT/fast-weight modules are present and exercised;
- no offload mode changes the local state-update question.

Use one public real text sample from the corresponding evaluation family, with a small bounded context first (e.g. 4k or shorter if the method legally supports it). The goal is execution qualification, not benchmark score reproduction.

If the qualified model cannot run on 16 GiB without changing the algorithm/model:
`R19_FASTWEIGHT_PLATFORM_NOT_QUALIFIED`, STOP.

## G2 — semantic canary

Prove:
- which weights/state actually change at inference;
- exact update equation/path used;
- update happens on real prompt-derived activations;
- consumer reads the updated state afterward;
- no parameter/state mutation outside the intended fast-weight scope;
- repeated runs reset to the same pre-update state.

Save before/after hashes or numerical deltas for the updated tensors.

## G3 — bounded timing

Only after semantic qualification.

Use shared GPU lock.

Primary region:
`prompt-derived update inputs ready -> fast-weight update committed -> first dependent consumer output committed`

Also time:
- update-only subregion
- first dependent consumer
- one no-write diagnostic if it can be constructed without pretending algorithm equivalence.

Do not use no-TTT versus TTT end-to-end latency as architecture headroom; they are different algorithms.

Formal:
- 3 groups
- 2 warmups + 5 formal repeats
- exact reset before each measured run
- save all samples.

Record:
- bytes of mutable fast-weight/state
- update granularity
- number of adapted layers
- temporary allocations
- synchronization/launch count.

## G4 — strong software / algebra check

Before any mechanism claim, compare the executed update against:
- released closed-form path if applicable;
- obvious batched/fused operations already present;
- known linear-attention/scan equivalence only where mathematically valid.

If the chosen artifact's update is already reducible to a known closed-form/linear operation and no extra state-management residual remains:
`R19_FASTWEIGHT_STRONG_SOFTWARE_SUFFICIENT`.

At most one NSYS capture if a local residual remains. No NCU unless a single exact kernel is needed to distinguish compute versus state traffic.

## Decisions

- `R19_FASTWEIGHT_INPUT_AUTHORITY_NOT_QUALIFIED`
- `R19_FASTWEIGHT_PLATFORM_NOT_QUALIFIED`
- `R19_FASTWEIGHT_STRONG_SOFTWARE_SUFFICIENT`
- `R19_FASTWEIGHT_STATE_UPDATE_RESIDUAL_PRESENT`
- `R19_FASTWEIGHT_RESULT_MIXED_NEEDS_REVIEW`

Residual-present is review-only. No hardware, no 174, no new training campaign.

Review pack:
`docs/vm_tlb/review_packs/AWMA_R19_FASTWEIGHT_109_V1/`

Publish exact source/checkpoint/input receipts and STOP.
