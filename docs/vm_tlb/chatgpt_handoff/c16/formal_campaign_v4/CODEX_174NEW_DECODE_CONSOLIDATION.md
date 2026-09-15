# Codex Goal — 174-new Qwen0 Decode consolidation and analysis

## Execution identity

Use a fresh worktree/branch based on the accepted hardening implementation:

`670a681f96adc3be463b2f8d9bc4a8c1c08fe7b8`

Suggested branch:

`hrl/c16-qwen0-decode-analysis-174new-v4`

Producer authority to consume:

`20ee2e015d3b3eb72b67d03657242887932a925d`

Read `CURRENT_STATE_AND_SCOPE.md` first.

This is CPU-only. Do not run a GPU workload. Do not mutate node164 raw. Do not rewrite older accepted review packs.

## Goal

Independently verify, decode, harden and consolidate all three admitted Qwen0 S2_TEXT Decode formal runs, then produce an analysis-ready Qwen0 Prefill+Decode baseline without violating replay/address-space boundaries.

Accepted Decode run IDs and manifest SHAs must come from the producer review pack, not from guessed paths. Use the node164 catalog entry as the runtime location authority. If the storage layout has been reorganized, follow the catalog/manifest rather than hard-coded historical directory names.

## Stage 0 — inline parser/receipt hardening

Fold these small fixes into this substantive task; do not create another repair round:

1. In generic C16WARP1 ingest, `MREF_SHARDED_COMPLETE_SET` must default to:
   - per-shard footprint = formal;
   - cross-shard absolute-VA/page/line union = `REPLAY_UNION_DIAGNOSTIC`;
   - no cross-shard object union;
   - no cross-shard temporal order/reuse distance;
   unless explicit shared-address-space evidence is present.
2. Do not classify a shard against an object map from another process/address-space ID.
3. Derived receipts must bind each output path, byte size, SHA256, parser commit, CLI/config and UTC creation timestamp.
4. Preserve all RTX3090 Q2 exact regressions and existing hardening unit tests.

## Stage 1 — independent raw verification

For each Decode run:

- resolve catalog entry;
- rehash `RUN_MANIFEST.json` against catalog authority;
- independently verify every declared artifact size/SHA;
- verify `WARP_SHARD_MANIFEST.json` exact static-set count/uniqueness;
- verify every C16WARP1 header, static index, occurrence, record count, terminal proof and zero overflow/drop;
- verify every per-shard `ADDRESS_CONTEXT.json` is declared/hash-closed and matches that shard's trace SHA/static-map SHA/target/static index/function occurrence;
- verify GPU UUID and process/address-space identity fields are internally consistent;
- classify each static row as `EXECUTED_SHARD` or `ZERO_EXECUTION_PROVEN` fail-closed.

Expected producer anchors are useful cross-checks, not analysis inputs to copy:

- Early Heavy: 16 total, 3 executed / 13 zero, 33 active addresses;
- Early KV/Attention: 41 total, 3 executed / 38 zero, 4158 active addresses;
- Late KV/Attention: 41 total, 3 executed / 38 zero, 4158 active addresses.

Any disagreement must be explained from raw evidence; do not force-match the producer summary.

## Stage 2 — access and width hardening

For every selected static MREF:

- access kind from exact static map metadata only;
- validated width from exact SASS mnemonic only;
- `STG.E.128` / `LDG...128` may become 16B only when the hardening validator proves the mnemonic match;
- bare widthless forms stay `WIDTH_UNKNOWN`;
- report start-address bucket metrics for unknown-width accesses, and touched-range metrics only for exact-width subsets.

Do not import producer `ACCESS_WIDTH_METADATA.tsv` as truth; independently derive and compare it.

## Stage 3 — per-shard object attribution

Decode V3 supplies same-process `C16_ADDRESS_CONTEXT_V1` with object ranges. For each shard independently:

- validate the context's process/address-space binding to the trace;
- join active addresses only to that context's own ranges;
- classify as `WEIGHT`, `KV_CACHE`, `QUANT_METADATA`, `ACTIVATION` only if the range evidence supports it; otherwise `UNKNOWN_RUNTIME`;
- preserve aliases deterministically and document priority if overlapping ranges occur;
- emit per-shard object counts and per-object start/touched page/line footprints.

Do not union absolute VAs across shards.

## Stage 4 — object-relative normalization where proven

Attempt a stronger cross-replay comparison only where semantic object identity can be proven across address spaces.

A normalized object identity should use stable metadata such as object class, runtime name/path, layer/cache index, storage size, dtype, shape and other exact range metadata. Do not use absolute pointer value as identity.

If an object identity matches exactly, normalize each address to `(object_identity, address - object_start)` and compare relative offsets/pages/lines across replays.

If semantic identity is not sufficiently proven, keep that comparison unsupported rather than guessing.

Priority comparisons:

- Early KV/Attention vs Late KV/Attention;
- KV-cache relative footprint/growth if the same logical cache objects can be matched;
- weight-relative footprint stability;
- activation/runtime unknown changes only descriptively.

## Stage 5 — Qwen0 Prefill+Decode consolidated baseline

Produce a compact dataset/report joining the already accepted Prefill targets with the three new Decode targets, while respecting differences in evidence quality.

At minimum include:

- phase / target / function / occurrence;
- static MREF count, executed/zero count;
- read/write/atomic event counts;
- exact-width vs unknown-width event counts;
- per-shard address/page/line footprint summaries;
- object-class attribution coverage;
- object-relative normalized metrics where proven;
- replay-union diagnostics clearly separated from formal metrics;
- supported and unsupported claims.

Do not report a physical whole-kernel absolute-VA footprint from MREF-sharded replays.

## Stage 6 — opportunistic AWQ source acquisition, nonblocking

After the analysis goal is complete enough to pass, spend at most a bounded small effort attempting to acquire the source for `AutoAWQ_kernels` from a network-capable path.

If successful:

- freeze source commit/tag or exact archive;
- generate SHA256 receipt;
- store under the long-term canonical asset root on node164, suggested:
  `/root/share/mnt164/huangrulin/c16_ai_workload/assets/sources/autoawq_kernels/<identity>/`
- do not install into the base Python environment;
- do not build GPU code on 174-new;
- write a small source receipt that node109 can consume.

If network/TLS is unavailable, record `SOURCE_ACQUISITION_NOT_AVAILABLE` and continue; this must not fail the analysis goal.

## Tests

Required CPU-only tests:

- all prior hardening tests;
- RTX3090 Q2 exact regression unchanged;
- address-context SHA/binding mismatch rejection;
- cross-process object-map rejection;
- exact same-process object attribution positive fixture;
- object-relative normalization positive and mismatch fail-closed fixtures;
- generic ingest cross-replay union remains diagnostic;
- derived receipt includes complete output hashes.

## Review pack

Create:

`docs/vm_tlb/review_packs/C16_QWEN0_DECODE_ANALYSIS_174NEW_V4/`

Include at minimum:

- `FINAL_DECISION.json`
- `RUN_VERIFICATION.tsv`
- `MREF_CLOSURE.tsv`
- `ACCESS_WIDTH_AUDIT.tsv`
- `PER_SHARD_OBJECT_ATTRIBUTION.tsv`
- `OBJECT_RELATIVE_NORMALIZATION.tsv`
- `EARLY_LATE_KV_COMPARISON.tsv`
- `QWEN0_PREFILL_DECODE_BASELINE.tsv`
- `SUPPORTED_CLAIMS.md`
- `OPEN_ISSUES.md`
- `DERIVED_RECEIPT.json`
- `REGRESSION_RESULTS.tsv`
- `SHA256SUMS`

## Acceptance

PASS requires:

- three producer run containers independently hash-close;
- all declared static MREFs close as executed or proven-zero;
- access/width semantics follow hardening rules;
- same-process object attribution is independently validated or conservatively unknown;
- cross-replay absolute-VA union is never promoted to a physical whole-launch claim;
- prior Q2 regressions remain exact;
- raw is unchanged.

The optional AWQ source acquisition is not a PASS requirement.

STOP only after the review pack is hash-closed and the branch is pushed.
