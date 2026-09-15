# C16 Next Wave Plan — Qwen0 Decode Expansion V3

## Current accepted state

- Pipeline V1: accepted with documented SSHFS fallback limitation.
- Analysis prep: PASS.
- Sharded V2 analysis: PASS.
- First formal Qwen0 V2 producer: PASS_WITH_SCOPED_EVIDENCE.
- First independent V2 ingest: PASS.

The first producer-consumer crosscheck is exact for the asserted closure quantities. This is sufficient to scale the capture method, but analysis semantics must be hardened before relying on access-kind, width, object attribution or cross-replay absolute-VA unions.

## Parallel wave

Run two independent goals:

### node174-new

Execute `CODEX_174NEW_ANALYSIS_HARDENING.md`.

Purpose:

- audit current all-WRITE output;
- recover/limit width semantics;
- audit address-space identity;
- correct cross-shard union labels;
- retain exact closure and Q2 regressions.

CPU-only. No GPU dependency.

### node109

Execute `CODEX_109_QWEN0_DECODE_EXPANSION.md`.

Purpose:

- capture Qwen0 S2 Decode early/late formal evidence;
- add same-process per-shard address context;
- retain MREF complete-set method;
- Pipeline ACK every accepted target.

## Coordination rule

The 174 hardening result may tighten labels used for 109 derived summaries, but it must not require node109 to rerun already accepted Prefill GPU traces.

The 109 Decode capture may proceed while 174 hardens analysis. The producer should preserve enough sidecar metadata that 174 can analyze the new runs without assuming shared replay VA space.

## Not in this wave

Do not let these block Qwen0 Decode:

- AWQ `awq_ext` source acquisition;
- raw Qwen2.5-7B true-capacity admission;
- Qwen3/DeepSeek prospective input authority;
- final cross-model conclusions.

These return after Qwen0 Prefill+Decode forms a coherent baseline.
