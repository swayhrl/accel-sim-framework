# GEMM: observed opportunity record

Full input identity `fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318`; PolyBench/GPU; fixed CORE32.

CH-P0 1,395,216 cycles; DH-P0 826,089. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|1395216|N/A|
|StageII_sixcell|CH F256|1395216|N/A|
|StageII_sixcell|CH P0|1395216|N/A|
|StageII_sixcell|DH F128|826089|1.0|
|StageII_sixcell|DH F256|826089|1.0|
|StageII_sixcell|DH P0|826089|1.0|
|StageI_DH_singlefactor|DH E384|826089|1.0|
|StageI_DH_singlefactor|DH E768|826089|1.0|
|StageI_DH_singlefactor|DH M8|826089|1.0|
|StageI_DH_singlefactor|DH M16|826089|1.0|
|StageI_DH_singlefactor|DH Q64|826089|1.0|
|StageI_DH_singlefactor|DH Q128|826089|1.0|
|StageI_DH_singlefactor|DH F128|826089|1.0|
|StageI_DH_singlefactor|DH F256|826089|1.0|
|Structure|DH TAG64x16_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS768_TAG64x8|826089|1.0|
|Structure|DH TAG128x8_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS1024_TAG64x8|826089|1.0|
|Structure|DH OO_PIB192|814235|1.014558450570167|
|Structure|DH TAG4BANK_PERBANK2_TOTAL8|826089|1.0|
|R1_combo|DH PHYS768_OOPIB192_TAG64x8|814235|1.014558450570167|
|R1_combo|DH PHYS1024_OOPIB192_TAG64x8|814235|1.014558450570167|

Retain exact F-zero response and observed structural responses as controls under the actual prefilled replay.

Counterexample/boundary: Zero DRAM exposure only limits this replay test of the FR window; it does not establish compute-bound execution or a universal headroom ceiling.

Best observed DH cycles 814,235 (self speedup 1.014558451) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318.json.gz`; 1 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: FIXED8_MEASURED / FIXED8_MEASURED.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
