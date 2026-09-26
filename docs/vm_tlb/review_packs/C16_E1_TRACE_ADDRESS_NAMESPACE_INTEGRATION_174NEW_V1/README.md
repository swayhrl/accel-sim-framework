# C16 E1 Trace Address Namespace Integration 174-new V1

Status: `C16_E1_TRACE_TO_SIM_L2_NAMESPACE_QUALIFIED_V1`.

The accepted 109 D1-D3 bounded trace is admitted unchanged. Three real-artifact canaries from layers 0, 14 and 27 preserve the exact same numeric address through trace parsing, instruction operands, coalesced `mem_access_t`, `mem_fetch`, L2 entry and the oracle lookup. The oracle returns target=true with target classes 1, 15 and 28.

General global traffic remains in the same CUDA/NVBit numeric namespace. Coalescing and L2 sector splitting deterministically form aligned transaction/sector addresses but do not introduce a VA-to-different-namespace mapping. All 28 target intervals are 128-byte aligned, so the exact `[begin,end)` sidecar can be used without address rewriting.

The generated 28-region sidecar is bound to the complete 4515-kernel D1-D3 manifest, not to the three canary kernels. All 28 regions have at least one observed D2 traceg access. Gate/down qweight, qzeros, scales, self-attention/ordinary traffic, PTE, write, writeback and instruction cases are excluded.

All simulator executions in this pack are labeled `ADDRESS_INTEGRATION_CANARY_ONLY`. No baseline/candidate comparison, budget sweep, speedup or mechanism-effectiveness result was produced.

Review order:

1. `TRACE_ADDRESS_NAMESPACE_FINAL_DECISION.json`
2. `TRACE_TO_SIM_ADDRESS_PATH.md`
3. `REAL_ARTIFACT_ADDRESS_CANARIES.json`
4. `ORACLE_SIDECAR_PROVENANCE.json`
5. `ORACLE_TAG_ACTIVATION_CANARY.json`
6. `UPSTREAM_TRACE_ADMISSION_AUDIT.json`
