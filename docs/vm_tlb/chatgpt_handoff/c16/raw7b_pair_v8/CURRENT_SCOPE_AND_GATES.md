# C16 Raw7B Paired Replay V8 — Scope and Gates

Accepted producer base: `2a05cadcbcc0e0b477b83d28aabe0c0aee270150`.

Accepted AWQ formal authority: `2274ee94c86cac9d37f7ef60c8afee58f8fc74b8`.
Accepted AWQ consumer authority: `11c8da9df6401f5d2458903ca6be38940739162b`.
Accepted raw7B asset-readiness authority: `1d64cd3b996592916e9e34e15c152cbf5a468fa9`.
Accepted model-completion/helper-fix authority: `cd74256d698d9949d222703db8bb077a3581792a`.

## Scientific objective

Close the first controlled Qwen2.5-7B BF16-vs-AWQ deployment pair on RTX4080. This is a deployment-level comparison, not a claim that quantization alone is the only changed mechanism: the representation and corresponding kernel implementation differ by construction.

Do not compare absolute VAs across deployments. Do not claim full-model cache/TLB history from layer replay.

## Hard gates

1. Pair input gate: canonicalize the exact executed AWQ S2 2048-token sequence and the historical raw7B S2 sequence. If identical, record common historical sequence identity. If different, do not retokenize. After verifying raw7B vocab/token compatibility, freeze a new prospective pair binding that reuses the exact AWQ-executed 2048 token IDs on the raw7B side. Preserve all historical bindings unchanged.

2. Semantic target gate: the matched pair must bind an exact semantic operator/layer and input shape. First attempt to map the accepted AWQ `DECODE_FUSED_GEMM` formal occurrence to a unique WQLinear module/layer using deterministic module-level NVTX/NSYS correlation. If the existing target cannot be mapped losslessly, it may not be used for a causal pair. In that case, create at most one new semantically explicit AWQ decode-linear formal target and use that as the pair anchor.

3. Raw replay gate: raw7B full-resident RTX4080 remains disallowed. Implement semantically exact layer streaming with exact BF16 weights and exact model runtime semantics. Freeze target-layer input state and layer-local KV/state sufficient for replay.

4. Equivalence gate: exact target-layer replay must match the semantic-streaming reference within an explicitly justified deterministic numerical criterion before profiling/formal capture.

5. Formal capture gate: audit the complete raw target function for direct GLOBAL MREF, LDGSTS/global-to-shared, other address-bearing paths, and memory-control instructions separately. Formalize only after full-function address-path audit. Admission concurrency = 1.

## Small carry-forward fix

V7 NCU capture is accepted, but Git contains only metric availability plus report hashes. Export compact numeric values for `l1tex__t_bytes`, `lts__t_bytes`, and `dram__bytes` for the two accepted AWQ S2 NCU targets and create a long-term report receipt. Do not recapture if the accepted reports remain intact.

## Boundaries

No Qwen3 or DeepSeek execution in this Goal. No network model download. Do not alter canonical raw/catalog evidence. Do not rewrite the 21 historical Qwen2.5 bindings.
