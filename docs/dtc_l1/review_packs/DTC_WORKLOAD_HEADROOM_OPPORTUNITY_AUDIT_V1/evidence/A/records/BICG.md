# BICG: observed opportunity record

Full input identity `ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef`; PolyBench/GPU; fixed CORE32.

CH-P0 26,298,698 cycles; DH-P0 28,685,812. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|24464891|N/A|
|StageII_sixcell|CH F256|24651923|N/A|
|StageII_sixcell|CH P0|26298698|N/A|
|StageII_sixcell|DH F128|29210480|0.9820383643130821|
|StageII_sixcell|DH F256|28883488|0.9931560897354226|
|StageII_sixcell|DH P0|28685812|1.0|
|StageI_DH_singlefactor|DH E384|28830072|0.9949961970264938|
|StageI_DH_singlefactor|DH E768|28830072|0.9949961970264938|
|StageI_DH_singlefactor|DH M8|29657807|0.967226336053775|
|StageI_DH_singlefactor|DH M16|28338906|1.0122413335221903|
|StageI_DH_singlefactor|DH Q64|29825144|0.9617996144461197|
|StageI_DH_singlefactor|DH Q128|29194658|0.9825705784941889|
|StageI_DH_singlefactor|DH F128|29210480|0.9820383643130821|
|StageI_DH_singlefactor|DH F256|28883488|0.9931560897354226|
|Structure|DH TAG64x16_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS768_TAG64x8|30892841|0.9285585615126819|
|Structure|DH TAG128x8_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS1024_TAG64x8|30892841|0.9285585615126819|
|Structure|DH OO_PIB192|28685812|1.0|
|Structure|DH TAG4BANK_PERBANK2_TOTAL8|28685812|1.0|
|R1_combo|DH PHYS768_OOPIB192_TAG64x8|30892841|0.9285585615126819|
|R1_combo|DH PHYS1024_OOPIB192_TAG64x8|30892841|0.9285585615126819|

Physical enlargement retains an observed negative control; K2 response must remain separate from K1. More physical capacity or fewer OO misses alone does not guarantee throughput.

Counterexample/boundary: Compare same-contract K2 lower/L2/DRAM volume and finite-service counters; stable or lower misses with slower K2 falsifies a monotone miss-count explanation.

Best observed DH cycles 28,338,906 (self speedup 1.012241334) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef.json.gz`; 2 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: FIXED8_MEASURED / FIXED8_MEASURED.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
