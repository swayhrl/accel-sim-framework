# Paper experiment gaps

## BLOCKING_FOR_PAPER

None for the scoped claims in `PAPER_CLAIM_MATRIX.tsv`.

## HIGH_VALUE_NONBLOCKING

- cross-model simulator-native validation beyond the current Qwen2.5 lineage;
- a project-approved standard-cell library and physical-design flow for real
  technology-specific area/Fmax;
- an accepted exact target-to-Native-time mass mapping for an end-to-end
  `NATIVE_TIME_WEIGHTED_ESTIMATE`;
- deeper attribution of the T2/A1 schedule-sensitive regressions.

## OPTIONAL

- more contexts within already represented Flash/GEMM/GEMV/Reduce families;
- larger-context points beyond Pair A/C;
- alternative finite delivery microarchitectures for the RTL proxy.

No new capture is required to support the current scoped core claims. If a
future expansion is authorized, it should be one batch—not piecemeal—covering
one different model lineage with four preregistered roles: prefill attention,
prefill GEMM, short/long-context decode GEMV, and reduction/normalization. Each
must have immutable model/input/trace hashes, SM89 grammar qualification and an
OFF-first simulator signature. This Goal does not start node109.
