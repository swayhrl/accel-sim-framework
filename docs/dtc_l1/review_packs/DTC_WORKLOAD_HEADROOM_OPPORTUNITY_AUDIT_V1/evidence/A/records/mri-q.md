# mri-q: observed opportunity record

Full input identity `dc7a91531846c1134c197a6e83509c91b2768151692a7b1286f6be9c431cabd4`; Parboil; fixed CORE32.

CH-P0 362,244 cycles; DH-P0 360,174. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|362244|N/A|
|StageII_sixcell|CH F256|362244|N/A|
|StageII_sixcell|CH P0|362244|N/A|
|StageII_sixcell|DH F128|359855|1.000886468160787|
|StageII_sixcell|DH F256|359855|1.000886468160787|
|StageII_sixcell|DH P0|360174|1.0|
|StageI_DH_singlefactor|DH E384|360174|1.0|
|StageI_DH_singlefactor|DH E768|360174|1.0|
|StageI_DH_singlefactor|DH M8|360174|1.0|
|StageI_DH_singlefactor|DH M16|360174|1.0|
|StageI_DH_singlefactor|DH Q64|359731|1.0012314757415959|
|StageI_DH_singlefactor|DH Q128|359731|1.0012314757415959|
|StageI_DH_singlefactor|DH F128|359855|1.000886468160787|
|StageI_DH_singlefactor|DH F256|359855|1.000886468160787|

Small DH gain and CH zero response provide a low-response control; preserve interkernel upload boundary.

Counterexample/boundary: Reduced misses do not establish reduced full DRAM-service or application critical-path latency.

Best observed DH cycles 359,731 (self speedup 1.001231476) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/dc7a91531846c1134c197a6e83509c91b2768151692a7b1286f6be9c431cabd4.json.gz`; 4 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: NOT_MEASURED_OUTSIDE_FIXED8 / NOT_MEASURED_OUTSIDE_FIXED8.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
