# Bounded authority search

## Scope and cutoff

Historical R102 authority: `056daae4082aafb4bfaab10db19f004d4d76ec73`, completed 2026-09-27. This round inspected only:

1. node109 AWMA directories and model revisions newer than the old closeout;
2. node164 top-level AWMA provenance directories/model revisions newer than the old durable path;
3. current Helix public metadata;
4. PULSE paper code/artifact pointers;
5. HF/TRL delta-sync PRs and their explicitly linked public bucket;
6. current one-covenant/GRAIL repository, releases and checkpoint interface.

No full node164 rescan was performed.

## Local and node164 delta search

The only newer local/durable roots are R101 and Lane-F/VLA work. Candidate-name hits are unrelated package/checkpoint utilities. No new R102 before/after weights, real patch chain, Helix/PULSE dump, or model revision appeared.

## Helix / SparseRL-Sync

`scitix/helix` main remains `867f76a82822dd87413da4fec617b7f8e7cf6414`, unchanged from old R102; tags=0, releases=0. It still provides source/statistics paths but no full adjacent version chain.

## PULSE

Primary source: `https://arxiv.org/abs/2602.03839v2`. The paper describes real consecutive BF16 checkpoints and PULSE, but provides no standalone public tensor chain. Its public implementation references resolve to TRL/GRAIL, audited below.

## HF/TRL candidate

- PR #5417 head: `d6504b7e39e0cece60b1034db7cad05b4d69990f`; superseded.
- PR #5937 head: `8bbc35f4bc7f030053d39063979af6df89a6c925`; closed/unmerged public source.
- Public bucket: `aminediroHF/async-grpo-delta-demo`, private=false, 61 files, 23,615,823,566 bytes.
- Tree: four full anchors (steps 1/20/40/60) and 57 delta objects.
- Bounded read: metadata/tree plus safetensors headers for anchor step1 and deltas steps2–4 only; no payload bytes were downloaded.

The candidate is a real published chain and has Xet hashes for each file. It still fails Form B:

1. `PatchMetadata` contains only format/version/sparse/model_version/count/sparsity/encoding fields; no run/model/base hash/target hash.
2. step2–4 headers contain no base hash and no reconstructed target hash. Xet hashes authenticate patch files, not the reconstructed target weights.
3. the receiver decodes and applies absolute values but does not validate expected base version/hash or target hash.
4. `AdamWInversionChangeDetector` documents that pre-step recovery is exact only up to floating-point error and that BF16 boundary flips may be missed; periodic anchors bound drift. This is not the contract's direct bitwise comparison of authoritative adjacent working-precision versions.

Whole-file sparsity fields were incidentally visible in headers during authority inspection. No per-tensor/bucket sparsity was inspected, no bucket was frozen, and those reported fields are not used as scientific evidence.

## GRAIL

Current main: `54d6342928dc516b1169342d801596fe4b88ef6f`; 64 tags and 59 releases, but release assets=0 and tracked checkpoint/tensor payloads=0. Source implements FULL/DELTA chains and xxh3 target verification, yet real objects reside in R2/S3 coordinated through credentials/Bittensor. The Goal forbids credential requests or network joining, so no public chain is admitted.

## Gate

No Form A or Form B input meets the frozen contract. Decision: `R102_REAL_UPDATE_INPUT_AUTHORITY_NOT_QUALIFIED_V2`; CUDA=0.
