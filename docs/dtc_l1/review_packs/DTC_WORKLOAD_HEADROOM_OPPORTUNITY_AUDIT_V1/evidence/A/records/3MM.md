# 3MM: observed opportunity record

Full input identity `977a2f7007cb1f9673fe3a5c17cdbb469335c619c172a0a882eb18410049eb3d`; PolyBench/GPU; fixed CORE32.

CH-P0 4,191,465 cycles; DH-P0 2,402,871. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|4191465|N/A|
|StageII_sixcell|CH F256|4191465|N/A|
|StageII_sixcell|CH P0|4191465|N/A|
|StageII_sixcell|DH F128|2402871|1.0|
|StageII_sixcell|DH F256|2402871|1.0|
|StageII_sixcell|DH P0|2402871|1.0|
|StageI_DH_singlefactor|DH E384|2402871|1.0|
|StageI_DH_singlefactor|DH E768|2402871|1.0|
|StageI_DH_singlefactor|DH M8|2402871|1.0|
|StageI_DH_singlefactor|DH M16|2402871|1.0|
|StageI_DH_singlefactor|DH Q64|2402871|1.0|
|StageI_DH_singlefactor|DH Q128|2402871|1.0|
|StageI_DH_singlefactor|DH F128|2402871|1.0|
|StageI_DH_singlefactor|DH F256|2402871|1.0|

Retain zero downstream response under current trace/preload policy, independent from historical Hash studies.

Counterexample/boundary: Candidate source copies uninitialized E/F/G and uses +=; capture binding/numerical correctness is unproved. Do not infer historical numerical error or repair the input.

Best observed DH cycles 2,402,871 (self speedup 1.000000000) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/977a2f7007cb1f9673fe3a5c17cdbb469335c619c172a0a882eb18410049eb3d.json.gz`; 3 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: NOT_MEASURED_OUTSIDE_FIXED8 / NOT_MEASURED_OUTSIDE_FIXED8.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
