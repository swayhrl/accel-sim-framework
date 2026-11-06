# ATAX: observed opportunity record

Full input identity `eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950`; PolyBench/GPU; fixed CORE32.

CH-P0 28,428,842 cycles; DH-P0 31,880,220. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|29882110|N/A|
|StageII_sixcell|CH F256|31081550|N/A|
|StageII_sixcell|CH P0|28428842|N/A|
|StageII_sixcell|DH F128|31894637|0.9995479804331995|
|StageII_sixcell|DH F256|31321955|1.0178234404589368|
|StageII_sixcell|DH P0|31880220|1.0|
|StageI_DH_singlefactor|DH E384|30987395|1.0288125219948305|
|StageI_DH_singlefactor|DH E768|30987395|1.0288125219948305|
|StageI_DH_singlefactor|DH M8|31438336|1.014055578514079|
|StageI_DH_singlefactor|DH M16|32527908|0.9800882368457264|
|StageI_DH_singlefactor|DH Q64|32321602|0.9863440555947691|
|StageI_DH_singlefactor|DH Q128|33774401|0.943916666353313|
|StageI_DH_singlefactor|DH F128|31894637|0.9995479804331995|
|StageI_DH_singlefactor|DH F256|31321955|1.0178234404589368|
|Structure|DH TAG64x16_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS768_TAG64x8|30602022|1.0417684164791463|
|Structure|DH TAG128x8_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS1024_TAG64x8|30602022|1.0417684164791463|
|Structure|DH OO_PIB192|31880220|1.0|
|Structure|DH TAG4BANK_PERBANK2_TOTAL8|31880220|1.0|
|R1_combo|DH PHYS768_OOPIB192_TAG64x8|30602022|1.0417684164791463|
|R1_combo|DH PHYS1024_OOPIB192_TAG64x8|30602022|1.0417684164791463|

F-relative improvement must be decomposed into CH regression versus DH own improvement; preserve both serial kernels and absolute matched R.

Counterexample/boundary: A positive I with R<=1 does not show DH surpasses CH; use actual own-design kernel deltas and preserve opposite CH response.

Best observed DH cycles 30,602,022 (self speedup 1.041768416) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950.json.gz`; 2 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: FIXED8_MEASURED / FIXED8_MEASURED.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
