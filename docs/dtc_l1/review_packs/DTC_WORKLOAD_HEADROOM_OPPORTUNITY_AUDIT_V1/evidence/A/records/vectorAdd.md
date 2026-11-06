# vectorAdd: observed opportunity record

Full input identity `e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799`; CUDA Samples; fixed CORE32.

CH-P0 220,803 cycles; DH-P0 217,305. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|214503|N/A|
|StageII_sixcell|CH F256|223020|N/A|
|StageII_sixcell|CH P0|220803|N/A|
|StageII_sixcell|DH F128|213053|1.0199574753699783|
|StageII_sixcell|DH F256|236217|0.9199380230889395|
|StageII_sixcell|DH P0|217305|1.0|
|StageI_DH_singlefactor|DH E384|215407|1.0088112271188958|
|StageI_DH_singlefactor|DH E768|215407|1.0088112271188958|
|StageI_DH_singlefactor|DH M8|217305|1.0|
|StageI_DH_singlefactor|DH M16|217305|1.0|
|StageI_DH_singlefactor|DH Q64|216368|1.0043305849293795|
|StageI_DH_singlefactor|DH Q128|219002|0.9922512123176958|
|StageI_DH_singlefactor|DH F128|213053|1.0199574753699783|
|StageI_DH_singlefactor|DH F256|236217|0.9199380230889395|
|Structure|DH TAG64x16_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS768_TAG64x8|217305|1.0|
|Structure|DH TAG128x8_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS1024_TAG64x8|217305|1.0|
|Structure|DH OO_PIB192|217305|1.0|
|Structure|DH TAG4BANK_PERBANK2_TOTAL8|217305|1.0|
|R1_combo|DH PHYS768_OOPIB192_TAG64x8|217305|1.0|
|R1_combo|DH PHYS1024_OOPIB192_TAG64x8|217305|1.0|

Streaming-like candidate source is a negative/zero response control; all measured regressions stay in the opportunity record.

Counterexample/boundary: No locality/port/PIB improvement is presumed from source form; only actual accepted cycle/counter changes can support it.

Best observed DH cycles 213,053 (self speedup 1.019957475) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799.json.gz`; 1 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: FIXED8_MEASURED / FIXED8_MEASURED.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
