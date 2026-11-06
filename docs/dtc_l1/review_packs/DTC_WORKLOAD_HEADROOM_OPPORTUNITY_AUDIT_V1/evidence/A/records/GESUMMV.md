# GESUMMV: observed opportunity record

Full input identity `769e6d9fd5f9cd5386556211112b1a1dec6d2b46bf69881db357257752aa22e4`; PolyBench/GPU; fixed CORE32.

CH-P0 114,860,845 cycles; DH-P0 89,502,220. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|106901261|N/A|
|StageII_sixcell|CH F256|112286106|N/A|
|StageII_sixcell|CH P0|114860845|N/A|
|StageII_sixcell|DH F128|86464623|1.03513109633289|
|StageII_sixcell|DH F256|90151547|0.9927973837209915|
|StageII_sixcell|DH P0|89502220|1.0|
|StageI_DH_singlefactor|DH E384|89424572|1.0008683072030806|
|StageI_DH_singlefactor|DH E768|89424572|1.0008683072030806|
|StageI_DH_singlefactor|DH M8|89502220|1.0|
|StageI_DH_singlefactor|DH M16|89502220|1.0|
|StageI_DH_singlefactor|DH Q64|91097040|0.982493174311701|
|StageI_DH_singlefactor|DH Q128|89958750|0.9949251184570707|
|StageI_DH_singlefactor|DH F128|86464623|1.03513109633289|
|StageI_DH_singlefactor|DH F256|90151547|0.9927973837209915|

One closed kernel exposes nonmonotone F response: DH-F128 gains while F256 regresses; source traffic and retry direction must be considered separately.

Counterexample/boundary: Fewer OO misses/retries can coexist with slower execution; no isolated causal bottleneck follows from endpoint totals.

Best observed DH cycles 86,464,623 (self speedup 1.035131096) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/769e6d9fd5f9cd5386556211112b1a1dec6d2b46bf69881db357257752aa22e4.json.gz`; 1 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: NOT_MEASURED_OUTSIDE_FIXED8 / NOT_MEASURED_OUTSIDE_FIXED8.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
