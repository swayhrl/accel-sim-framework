# C16 node109 — AWQ Characterization V7 Scope

Accepted producer base:

`2274ee94c86cac9d37f7ef60c8afee58f8fc74b8`

Current accepted deployment:

- Qwen/Qwen2.5-7B-Instruct-AWQ
- revision `b25037543e9394b818fdfca67ab2a00ecc7dd641`
- exact S2_TEXT B1/T2048/D32 runtime admitted
- RTX4080 / SM89
- isolated AutoAWQ environment
- built canonical AutoAWQ kernels source commit `c7b0e88c327694c715b0a758d9ce8fd414a1fa21`

Formal V6 portfolio:

- Prefill AWQ dequant: 11 direct-GLOBAL shards, all executed
- Decode fused GEMM: 43 direct-GLOBAL shards, 27 executed / 16 ZERO_EXECUTION_PROVEN
- no LDGSTS or other detected special address-bearing paths for either accepted target

The earlier phase-mislabeled bundle remains excluded and immutable.

## V7 purpose

Use the already-qualified AWQ deployment efficiently before moving to a new model:

1. add application-context NCU cache/DRAM evidence for the two accepted S2 targets;
2. cheaply census exact historical S1/S3/S4 AWQ scenarios with NSYS/runtime receipts;
3. formalize at most one additional target only if the scenario census proves a materially new implementation/path/shape behavior worth preserving.

Do not start Qwen2.5-7B raw layer replay in this goal.
Do not start Qwen3 or DeepSeek in this goal; Lane B is still closing those assets/authorities.

## Small V6 closure improvements to fold in

Do not create a separate repair goal. While producing the V7 source/build receipt, additionally record where available:

- canonical source `HEAD`;
- `HEAD^{tree}`;
- clean/dirty worktree state;
- wheel SHA256;
- SHA256 for every installed AWQ extension `.so` actually used (`awq_ext`, `awq_v2_ext`, and other built extensions if installed/used);
- Python / torch / torch CUDA runtime / nvcc / host compiler versions.

Do not rebuild solely to add metadata if the accepted V6 wheel/environment remains intact and verifiable.

## Claim boundaries

NCU application-context evidence is target-run/cache-counter evidence, not a full-model global-cache-state reconstruction.

NSYS scenario census is implementation/census evidence, not formal address coverage.

Only formally capture another scenario target if it is materially distinct. Formal Pipeline admission concurrency remains 1.
