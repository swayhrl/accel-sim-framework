# convolutionSeparable: observed opportunity record

Full input identity `4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449`; CUDA Samples; fixed CORE32.

CH-P0 825,151 cycles; DH-P0 800,572. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|702940|N/A|
|StageII_sixcell|CH F256|602100|N/A|
|StageII_sixcell|CH P0|825151|N/A|
|StageII_sixcell|DH F128|674364|1.187151152789888|
|StageII_sixcell|DH F256|562886|1.4222631225505697|
|StageII_sixcell|DH P0|800572|1.0|
|StageI_DH_singlefactor|DH E384|805436|0.9939610347687464|
|StageI_DH_singlefactor|DH E768|805436|0.9939610347687464|
|StageI_DH_singlefactor|DH M8|800572|1.0|
|StageI_DH_singlefactor|DH M16|800572|1.0|
|StageI_DH_singlefactor|DH Q64|798296|1.0028510727850322|
|StageI_DH_singlefactor|DH Q128|789240|1.0143581166692008|
|StageI_DH_singlefactor|DH F128|674364|1.187151152789888|
|StageI_DH_singlefactor|DH F256|562886|1.4222631225505697|
|Structure|DH TAG64x16_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS768_TAG64x8|794413|1.0077528942753957|
|Structure|DH TAG128x8_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS1024_TAG64x8|794413|1.0077528942753957|
|Structure|DH OO_PIB192|820871|0.975271388561662|
|Structure|DH TAG4BANK_PERBANK2_TOTAL8|800572|1.0|
|R1_combo|DH PHYS768_OOPIB192_TAG64x8|818340|0.9782877532565926|
|R1_combo|DH PHYS1024_OOPIB192_TAG64x8|818340|0.9782877532565926|

Rows and Columns both respond to coupled downstream expansion. Compare shared CH benefit with the smaller additional DH benefit; whole DH speedup is not DTC-exclusive.

Counterexample/boundary: Large speedup with near-constant read traffic argues against volume reduction alone; retry direction can disagree within a kernel.

Best observed DH cycles 562,886 (self speedup 1.422263123) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449.json.gz`; 2 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: FIXED8_MEASURED / FIXED8_MEASURED.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
