# V2 corrected-census final update

Status: FINAL_INPUTS_CONSUMED_PENDING_REVIEW

Selector policy is unchanged. Its final census input is Lane A
hrl/awma-qwen25-s2-census-reclass-v2 at
24f21db0aa921190ca40e4d3969aced7471347b6. The durable raw V2 inventory SHA-256
is 222d5dfeeb1e7aaae3423f13873053c37c27f5c6290d8a58bd3186a0803ca77a.

V2 contains 34,677 launches and 154,876,910 ns. It attributes 980 Prefill
launches and 32,229,639 ns, including V1 UNKNOWN work recovered by CUPTI
correlation. The selector pool coverage is 67,308,000 / 126,440,396 ns
(53.232987%): Decode 55.638032%, Prefill 44.426367%, Auxiliary 0%.

The final asset join uses Lane C authority
hrl/awma-existing-ai-sim-trace-coverage-audit-v1 at
03924689da9c9691501d93567365c9265178b8a5. V2_ASSET_JOIN.tsv records 2
REUSABLE_NOW and 5 REQUIRES_REQUALIFICATION suite matches. Those seven rows
are explicitly NO_NEW_CAPTURE. The remaining 41 rows are
MISSING_SIM_TRACE only under the conservative phase/grid/block/step join and
remain NOT_REQUESTED_PENDING_REVIEW; their priority is now V2 selection order,
not Lane C's historical V1 weights.

The function-text representation differs between V2 census and Lane C
inventory, so exact-function reconciliation is an explicit remaining review
field. It must not be guessed. No Node109 work is authorized.
