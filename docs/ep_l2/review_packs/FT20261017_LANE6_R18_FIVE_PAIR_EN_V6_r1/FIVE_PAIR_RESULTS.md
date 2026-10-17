# Independent five-pair paper results

| Workload | B16 cycles | U-WB16 cycles | B/U | Cycle reduction (%) |
|---|---:|---:|---:|---:|
| sad | 110773 | 110749 | 1.0002167062 | +0.021666 |
| vectorAdd_4M | 73696 | 73549 | 1.0019986676 | +0.199468 |
| cfd_097k | 79093 | 79262 | 0.9978678307 | -0.213673 |
| convolutionSeparable | 292932 | 291525 | 1.0048263442 | +0.480316 |
| FWT_7_21 | 493189 | 491662 | 1.0031057922 | +0.309618 |

Geomean B/U = **1.0016002037656606x**; speed-ratio gain **0.160020%**. This is a ratio geomean, not a mean of cycle reduction percentages. All five predeclared complete inputs retained, including CFD regression. No repetitions/statistical inference, holdout/general GPU performance or independent capacity-performance claim.

All rows come from hash-bound native packet and64-slice raw counters, not Lane5 SUMMARY. ARM_METRICS.csv provides actual WB, copy, logical bank operations, successful model bank grants, per-operation waits, WBUF/WAD events, downstream admission events/DRAM bytes and eligible denominators. Counters are application cumulative over64 slices; cycles/instructions are native GPU totals, not slice sums. Maxima are max across slices, never sums of averages.

Logical operations and successful model bank grants happen to match at drained termination for every arm; they remain separate measured fields. Neither count is elapsed GPU time or RTL service/energy. The B16/U difference in logical operations is not universally2×B16 copies because evictions, fills, retries and rollback work can differ. Completed WB and DRAM write bytes also differ; preserve those actual counts.

WBUF-full falls to0 in all U arms; the three pressured B16 workloads vectorAdd/Convolution/FWT show much higher U L2-to-DRAM full-block attempts. This supports a downstream-pressure hypothesis, not proven causal migration or DRAM saturation. Such events count repeated slice/frontend admission denials and can overlap other reasons. Bank-wait totals are completed per-operation conflict waits. Do not add/subtract either from GPU cycles. SAD is a near-tie negative control. CFD loses169 cycles despite fewer copies/bank waits; WAD hazard events rise9841→13400, WB completed31123→31063, and bytes also change. These are competing explanations, not a diagnosis.

The original SAD pack is unchanged; its two rows were rebound to the live authority alongside the eight newly received rows. Initial prepared legacy adapters failed exact certificate-byte checks; attempt1 failures remain intact. The replacement metadata binds the actual official r2 certificate, full original body hashes and native zero-mask semantic proof without changing the scientific scope, producer, input or runtime config.
