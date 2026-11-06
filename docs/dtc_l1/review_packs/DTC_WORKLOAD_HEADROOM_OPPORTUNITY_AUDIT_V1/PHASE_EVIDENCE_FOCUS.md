# Observed kernel-localized contrasts

Only accepted closed results are compared; no new measurements. Each structure kernel sequence matches the same input's ordinal/name/instructions/cumulativeCTA and sums to the actual whole-replay cycles. Complete path/SHA/UUID/config/source evidence remains in the linked record. [Exact machine table](PHASE_EVIDENCE_FOCUS.json) retains F128 and both R1 combinations too.

MVT's physical-only improvement is concentrated in K1:33032429→28955953 cycles (4076476 fewer); K2 changes1655111→1653902 (1209 fewer). BICG shows the opposite physical response in K2:27030465→29237494 (2207029 more), while K1 stays1655347. This locates measured time changes and supplies a positive/negative control. It does not prove physical occupancy, miss count or any one event is the critical-path cause. Similar instruction counts do not establish identical addresses, cache history or native input semantics.

For convolutionSeparable, DH-F256 improves both row and column kernels. Physical-only affects the column kernel modestly, while PIB192 regresses both phases; actual physical+PIB remains slower than DH-P0. Multiplying individual speedups would miss this observation. CH also gains from F256, so the shared downstream response is distinct from DTC-specific advantage. F256 traffic gaps stay explicitly unqualified where original counter audits lack coverage.

## MVT

Full input SHA: `f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079`; [accepted source record](evidence/A/records/MVT.json).

|Kernel ordinal/name|CH-P0|CH-F256|DH-P0|DH-F256|DH-P768|DH-PIB192|DH-P768+PIB192|
|---|---:|---:|---:|---:|---:|---:|---:|
|1 `_Z11mvt_kernel1PfS_S_`|24828424|22592365|33032429|33440529|28955953|33032429|28955953|
|2 `_Z11mvt_kernel2PfS_S_`|1752751|1750563|1655111|1652917|1653902|1655111|1653902|

## BICG

Full input SHA: `ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef`; [accepted source record](evidence/A/records/BICG.json).

|Kernel ordinal/name|CH-P0|CH-F256|DH-P0|DH-F256|DH-P768|DH-PIB192|DH-P768+PIB192|
|---|---:|---:|---:|---:|---:|---:|---:|
|1 `_Z12bicg_kernel1PfS_S_`|1749396|1749396|1655347|1655347|1655347|1655347|1655347|
|2 `_Z12bicg_kernel2PfS_S_`|24549302|22902527|27030465|27228141|29237494|27030465|29237494|

## convolutionSeparable

Full input SHA: `4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449`; [accepted source record](evidence/A/records/convolutionSeparable.json).

|Kernel ordinal/name|CH-P0|CH-F256|DH-P0|DH-F256|DH-P768|DH-PIB192|DH-P768+PIB192|
|---|---:|---:|---:|---:|---:|---:|---:|
|1 `_Z21convolutionRowsKernelPfS_iii`|379655|288224|365625|269306|365625|378275|378275|
|2 `_Z24convolutionColumnsKernelPfS_iii`|445496|313876|434947|293580|428788|442596|440065|

No new per-kernel traffic or stall totals are inferred from final cumulative endpoints. No Oracle cycles or theoretical performance bound is introduced.
