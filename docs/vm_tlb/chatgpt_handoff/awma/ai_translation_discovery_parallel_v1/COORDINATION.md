# AWMA AI Translation Problem Discovery — Parallel V1

Date: 2026-09-26

This is a ChatGPT-owned coordination package. It does not modify accepted scientific results.

## Accepted starting point

- Strong classic baseline:
  - branch `hrl/awma-intrawarp-translation-baseline-residual-v1`
  - commit `9efe8236e0c6338addfef5480e1da91bffb504eb`
  - judgement: `CLASSIC_INTRAWARP_CAPABILITY_COVERS_CURRENT_BENEFIT`
- Post-classic residual discovery:
  - branch `hrl/awma-post-classic-baseline-residual-discovery-v1`
  - commit `32854024b1b92313cf2dffc6280247a629033991`
  - status: `NO_NOVEL_RESIDUAL_MECHANISM_IDENTIFIED_V1`
- Bottleneck Observatory:
  - `b85d388abe98e5da70b749b52075c33fad7cede4`
- Literature notebook:
  - branch `hrl/awma-chatgpt-literature-notes-v1`
  - commit `177863f325d77278013e195528903ddc8b292e4e`
- Important literature constraints:
  - classic warp-instruction VPN dedup is prior capability;
  - Pichai/Virtual Caching already cover ordinary TLB-hit-path hiding/filtering;
  - ISCA 2018 covers instruction-aware page-walk completion/scheduling;
  - LATPC covers unique-VPN regularity, MSHR compression, and walk batching;
  - MPW HPCA 2025 covers page-walker queueing and batched concurrent walks;
  - Avatar MICRO 2024 covers speculative translation + rapid validation and includes OPT ML evaluation.

## New objective

Do not search for another mechanism on the same Qwen2.5 evidence.

Instead, discover whether materially different AI workload dimensions create a translation problem that:
1. survives a reasonable classic warp-VPN-dedup baseline,
2. is not an artifact of one translation/cache path model,
3. is localized to a concrete finite resource/service level,
4. is not already covered by closest prior work.

## Parallel lanes

### Node109
Run a bounded Native workload atlas and capture a small, preregistered batch of simulator-native kernels spanning genuinely different AI dimensions.

### Node174-new
In parallel, qualify alternative translation/cache access-path diagnostics on existing accepted traces. If the node109 batch is ready at the designated one-time handoff check, consume it and continue residual qualification; otherwise close PREP and wait for the next coordination round.

## Shared rules

- No model downloads.
- No modification of accepted strong baseline or historical results.
- No candidate mechanism unless the residual-problem gate is passed.
- No paper packaging or PPA in this stage.
- No arbitrary "positive result" selection.
- All new targets are selected from predeclared workload dimensions and Native time/structural evidence, never from simulator candidate performance.
- Keep Native evidence and simulator claims separate.
- Physical mapping/PPN properties are NOT inferred from virtual addresses.
- Same-PC 2MB virtual-chunk locality is not Avatar-style physical contiguity.
- Access-path variants are diagnostic models, not claims about RTX4080 internals.

## Cross-lane handoff

Node109 publishes:
`NATIVE_ATLAS_CONSUMER_HANDOFF.json`
and qualified trace authority under node164.

Node174 performs exactly one fetch/check for the node109 branch after finishing its independent access-path work. No polling loop.

If the batch is unavailable:
`PREP_COMPLETE_AWAITING_NATIVE_ATLAS`

If available:
continue directly into new-trace strong-baseline/path/residual qualification.

