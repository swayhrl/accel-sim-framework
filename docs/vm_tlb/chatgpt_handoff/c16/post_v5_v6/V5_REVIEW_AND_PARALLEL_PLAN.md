# C16 Post-V5 Review and Parallel Plan

## Accepted producer authority

109 V5 branch:

`hrl/c16-ldgsts-special-path-109-v5`

HEAD:

`ea43fa6331dcb2d7d6553f6a48000bdd004458e0`

Decision:

`LDGSTS_CAPTURE_PASS`

Accepted operand semantics:

- NVBit MREF operand 1 = LDGSTS GLOBAL SOURCE.
- NVBit MREF operand 0 = shared destination.
- Decision basis is exact SASS operand order plus NVBit two-MREF metadata; address magnitude is corroborative only.

Accepted complete frozen special-path sets:

- S2 Prefill GEMM: 18 LDGSTS rows, 18 executed.
- S2 Prefill Attention: 48 LDGSTS rows, 48 executed.
- S2 Decode Early KV/Attention: 84 LDGSTS rows, 33 executed + 51 ZERO_EXECUTION_PROVEN.
- S2 Decode Late KV/Attention: 84 LDGSTS rows, 33 executed + 51 ZERO_EXECUTION_PROVEN.
- S3 Prefill Attention: 48 LDGSTS rows, 48 executed.

All 282 special-path shards are terminal-complete, overflow/drop zero, and belong to five Pipeline-ACKed formal bundles on node164.

The correct scope after V5 is:

`ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL`

for the five representative target sets when direct-GLOBAL-MREF evidence and LDGSTS-global-source evidence are considered together.

This does NOT establish:

- cross-path temporal ordering;
- one whole-kernel absolute-VA stream;
- cross-replay absolute-VA equality;
- whole-kernel reuse distance.

## Nonblocking process issue

V5 exposed a receiver-side catalog `.partial` collision when two formal bundles were admitted concurrently. Recovery was scientifically correct: un-ACKed data remained isolated, exact local-closed bundles were reverified, admitted serially, and ACKed without GPU rerun or raw mutation.

This is not a scientific blocker. Future formal admissions MUST respect the already accepted Pipeline-V1 constraint:

`FORMAL_ADMISSION_CONCURRENCY = 1`

Do not open a separate infrastructure repair round for this unless the same failure appears under serial admission.

## Parallel next wave

Three independent tracks may now run without changing scientific authority:

1. **174-new mainline window**: independently ingest/analyze the five V5 LDGSTS bundles and integrate them with the accepted direct-path Qwen0 baseline at set level.
2. **174-new asset-readiness window**: continue the already-started CPU-only asset/Qwen7 replay-prep Goal. Do not redirect it.
3. **109 fresh window**: use the newly archived AutoAWQ_kernels source to qualify a true fused Qwen2.5-7B-AWQ deployment and, if qualified, capture a small representative formal portfolio.

Do not start Qwen7 raw layer replay until the asset-readiness Goal closes and the post-V5 tracer/analysis contract is available.
