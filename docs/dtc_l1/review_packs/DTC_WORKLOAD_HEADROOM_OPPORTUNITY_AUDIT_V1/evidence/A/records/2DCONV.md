# 2DCONV: observed opportunity record

Full input identity `d984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0`; PolyBench/GPU; fixed CORE32.

CH-P0 1,548,909 cycles; DH-P0 462,740. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|1548909|N/A|
|StageII_sixcell|CH F256|1548909|N/A|
|StageII_sixcell|CH P0|1548909|N/A|
|StageII_sixcell|DH F128|437573|1.0575149746442307|
|StageII_sixcell|DH F256|429253|1.0780122678234048|
|StageII_sixcell|DH P0|462740|1.0|
|StageI_DH_singlefactor|DH E384|461703|1.0022460326227034|
|StageI_DH_singlefactor|DH E768|461703|1.0022460326227034|
|StageI_DH_singlefactor|DH M8|446511|1.0363462490285793|
|StageI_DH_singlefactor|DH M16|446511|1.0363462490285793|
|StageI_DH_singlefactor|DH Q64|461980|1.0016450928611629|
|StageI_DH_singlefactor|DH Q128|461647|1.0023676098837424|
|StageI_DH_singlefactor|DH F128|437573|1.0575149746442307|
|StageI_DH_singlefactor|DH F256|429253|1.0780122678234048|
|Structure|DH TAG64x16_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS768_TAG64x8|462740|1.0|
|Structure|DH TAG128x8_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS1024_TAG64x8|462740|1.0|
|Structure|DH OO_PIB192|470776|0.9829303108059884|
|Structure|DH TAG4BANK_PERBANK2_TOTAL8|462740|1.0|
|R1_combo|DH PHYS768_OOPIB192_TAG64x8|470776|0.9829303108059884|
|R1_combo|DH PHYS1024_OOPIB192_TAG64x8|470776|0.9829303108059884|

Use CH downstream zero response and DH response as controls; physical-only and physical×PIB changes are distinct interventions.

Counterexample/boundary: An observed PIB/combination regression must remain even if physical-only is exactly zero. No unreviewed F256 counter mechanism is implied.

Best observed DH cycles 429,253 (self speedup 1.078012268) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/d984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0.json.gz`; 1 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: FIXED8_MEASURED / FIXED8_MEASURED.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
