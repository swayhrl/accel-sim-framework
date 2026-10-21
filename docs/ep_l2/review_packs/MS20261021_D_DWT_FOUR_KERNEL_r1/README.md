# DWT four accepted endpoints: incremental Lane D consumption

D consumed E031/E032 after E's acceptance, retaining E017/E018 as the existing S/F anchors. All four use main61, the same complete DWT input (148,684,429 instructions, ten kernels), and E's 64-slice terminal closure. Receipt hashes, direct-parent native exit receipts (exit 0 / wait status 0), process identities and acceptance pointers are independently checked. This is analysis only: zero application starts, zero native rebuilds/tests, no registry or CLIENT writes. The exact E publication is `b8a1ddc5995456332ef4ac8e36d028ec8f77e097`.

| Kernel ordinal | S | S_COPY_FREE | W_ONLY | F | F − W_ONLY |
|---:|---:|---:|---:|---:|---:|
| 1 | 22,169 | 22,109 | 22,255 | 22,018 | −237 |
| 2 | 25,759 | 25,691 | 25,727 | 25,667 | −60 |
| 3 | 12,262 | 12,252 | 12,259 | 12,254 | −5 |
| 4 | 9,075 | 9,074 | 9,075 | 9,074 | −1 |
| 5 | 28,101 | 27,893 | 27,871 | 28,869 | +998 |
| 6 | 12,260 | 12,248 | 12,263 | 12,252 | −11 |
| 7 | 9,074 | 9,075 | 9,074 | 9,075 | +1 |
| 8 | 26,496 | 26,895 | 26,938 | 27,095 | +157 |
| 9 | 12,249 | 12,243 | 12,256 | 12,264 | +8 |
| 10 | 9,074 | 9,075 | 9,074 | 9,075 | +1 |
| Final residual | 0 | 0 | 0 | 0 | 0 |
| Program total | 166,519 | 166,555 | 166,792 | 167,643 | **+851** |

The **+851-cycle W_ONLY→F regression** closes exactly: kernels 5 and 8 contribute **+1,155**, offset by **−304** elsewhere. Both are `fdwt53Kernel<192,8>` (second and third occurrences after the source-components kernel). Kernel 1 is faster by 237 cycles. Full names and raw clock line locations are retained in the CSV/snapshots; the repeated function names are distinguished by ordinal.

At kernel 5, W_ONLY→F changes physical bank grants 470,437→470,467, lower-read packets 131,072→128,788 and lower-WB bytes 5,900,928→6,172,288. F records 68,107 V queries and 3,139 V read responses, with **zero new RO admissions/queries**. At kernel 8, F records 65,536 V queries, zero new V responses and zero new RO admissions/queries; lower reads remain 131,072, while physical grants increase 457,245→457,729 and lower-WB bytes 4,194,304→4,250,240. The per-kernel observations make DWT F_MINUS_R a useful next contrast against the accepted F endpoint: it tests the enabled RO path and its prior-state effects while retaining V. They do not establish that RO or V alone caused the measured delay.

W_ONLY→F is a **joint V plus RO/state** contrast; request waits and lookup counts are nonexclusive observations, not independently additive GPU stalls. RO/V families absent in OFF logs are retained as `UNKNOWN` in the generic observer rather than silently converted to measured zero. The exact runtime feature vector establishes that the path was disabled. COPY_FREE is a diagnostic counterfactual that exempts copy services **and fixed copy-staging retry delay**; it is not a physical hardware endpoint. Its +36 program cycles versus S, despite selected faster kernels, demonstrates why local service removal cannot be equated with whole-program critical-path benefit.

## Sensitivity recommendation

**Do not spend the first batch on L2/DRAM parameter sensitivity.** DWT's accepted S/W_ONLY/F final mean DRAM channel utilization is respectively 26.10%, 26.05% and 25.38% (all channel maxima <26.2%). L2 miss rates are 71.57%, 71.56% and 70.72%. These cumulative measurements show traffic and misses, but do not identify a critical capacity, latency or bandwidth bottleneck; low average utilization also cannot exclude transient/latency constraints. Current evidence therefore does not justify a particular L2 capacity, DRAM latency or bandwidth change. No grid or parameter change is proposed. This recommendation is scoped to the measured evidence, not a proof that memory sensitivity is zero; supported mechanism controls have higher immediate information value.

`L2_DRAM_SENSITIVITY_EVIDENCE.json` records the bounded 4 MiB final-tail reads, expected accepted raw hashes and observed tail hashes. Existing S/F timing snapshots were reused after their published hash manifests were checked; only the two new accepted raw logs were decoded once. No trace body was read. `FILES_SHA256.json` binds this report and the retained projection artifacts.
