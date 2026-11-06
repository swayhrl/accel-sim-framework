# MVT: observed opportunity record

Full input identity `f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079`; PolyBench/GPU; fixed CORE32.

CH-P0 26,581,175 cycles; DH-P0 34,687,540. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|25573002|N/A|
|StageII_sixcell|CH F256|24342928|N/A|
|StageII_sixcell|CH P0|26581175|N/A|
|StageII_sixcell|DH F128|35332620|0.981742650276147|
|StageII_sixcell|DH F256|35093446|0.9884335667691341|
|StageII_sixcell|DH P0|34687540|1.0|
|StageI_DH_singlefactor|DH E384|34862954|0.9949684699695843|
|StageI_DH_singlefactor|DH E768|34862954|0.9949684699695843|
|StageI_DH_singlefactor|DH M8|34685750|1.00005160620716|
|StageI_DH_singlefactor|DH M16|34686183|1.0000391222060958|
|StageI_DH_singlefactor|DH Q64|35375514|0.9805522543078808|
|StageI_DH_singlefactor|DH Q128|35470077|0.9779381082257025|
|StageI_DH_singlefactor|DH F128|35332620|0.981742650276147|
|StageI_DH_singlefactor|DH F256|35093446|0.9884335667691341|
|Structure|DH TAG64x16_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS768_TAG64x8|30609855|1.133214776744287|
|Structure|DH TAG128x8_PHYS640|SAFETY_HOLD_CPU_PROGRESS_NEGATIVE|N/A|
|Structure|DH PHYS1024_TAG64x8|30609855|1.133214776744287|
|Structure|DH OO_PIB192|34687540|1.0|
|Structure|DH TAG4BANK_PERBANK2_TOTAL8|34687540|1.0|
|R1_combo|DH PHYS768_OOPIB192_TAG64x8|30609855|1.133214776744287|
|R1_combo|DH PHYS1024_OOPIB192_TAG64x8|30609855|1.133214776744287|

Physical-lifetime interaction has observed positive evidence; compare K1 rather than using Tag eviction count alone. R1 and physical single factors test whether the observed response survives PIB enlargement.

Counterexample/boundary: If extra physical capacity changes misses/lower traffic but does not consistently shorten K1, a simple miss-volume critical-path account is insufficient.

Best observed DH cycles 30,609,855 (self speedup 1.133214777) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079.json.gz`; 2 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: FIXED8_MEASURED / FIXED8_MEASURED.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
