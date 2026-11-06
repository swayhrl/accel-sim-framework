# scan: observed opportunity record

Full input identity `6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39`; CUDA Samples; fixed CORE32.

CH-P0 6,710,840 cycles; DH-P0 6,648,993. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|5695578|N/A|
|StageII_sixcell|CH F256|5273582|N/A|
|StageII_sixcell|CH P0|6710840|N/A|
|StageII_sixcell|DH F128|5748280|1.1566926106591884|
|StageII_sixcell|DH F256|5179817|1.283634730725043|
|StageII_sixcell|DH P0|6648993|1.0|
|StageI_DH_singlefactor|DH E384|6606877|1.006374570012428|
|StageI_DH_singlefactor|DH E768|6606877|1.006374570012428|
|StageI_DH_singlefactor|DH M8|6687187|0.9942884803430799|
|StageI_DH_singlefactor|DH M16|PRESERVED_ENGINEERING_NEGATIVE_NO_RESULT|N/A|
|StageI_DH_singlefactor|DH Q64|6676810|0.9958337888902036|
|StageI_DH_singlefactor|DH Q128|6688280|0.994125993528979|
|StageI_DH_singlefactor|DH F128|5748280|1.1566926106591884|
|StageI_DH_singlefactor|DH F256|5179817|1.283634730725043|
|Structure|DH TAG64x16_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS768_TAG64x8|ARCHIVED_NEGATIVE_NO_PERFORMANCE|N/A|
|Structure|DH TAG128x8_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS1024_TAG64x8|ARCHIVED_NEGATIVE_NO_PERFORMANCE|N/A|
|Structure|DH OO_PIB192|ARCHIVED_NEGATIVE_NO_PERFORMANCE|N/A|
|Structure|DH TAG4BANK_PERBANK2_TOTAL8|ARCHIVED_NEGATIVE_NO_PERFORMANCE|N/A|
|R1_combo|DH PHYS768_OOPIB192_TAG64x8|6680780|0.9952420226380752|
|R1_combo|DH PHYS1024_OOPIB192_TAG64x8|6651571|0.9996124223886357|

Use the actual33-kernel ordered sequence, not11 assumed identical triplets. Preserve V1 monitor-cadence negative identities separately from acceptedR1.

Counterexample/boundary: V1 structure failure is not a negative performance value or family-safety proof; R1 cannot fill single-factor J terms that never accepted.

Best observed DH cycles 5,179,817 (self speedup 1.283634731) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39.json.gz`; 33 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: FIXED8_MEASURED / FIXED8_MEASURED.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
