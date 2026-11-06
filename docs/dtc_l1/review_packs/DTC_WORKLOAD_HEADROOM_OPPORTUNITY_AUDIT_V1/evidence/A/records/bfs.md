# bfs: observed opportunity record

Full input identity `1df9d5479504d9c7c5f5ef176e9604ce1b43421c7b6be440597259607d3971c0`; Parboil; fixed CORE32.

CH-P0 4,330,430 cycles; DH-P0 4,170,294. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|4330430|N/A|
|StageII_sixcell|CH F256|4330430|N/A|
|StageII_sixcell|CH P0|4330430|N/A|
|StageII_sixcell|DH F128|4170294|1.0|
|StageII_sixcell|DH F256|4170294|1.0|
|StageII_sixcell|DH P0|4170294|1.0|
|StageI_DH_singlefactor|DH E384|4170294|1.0|
|StageI_DH_singlefactor|DH E768|4170294|1.0|
|StageI_DH_singlefactor|DH M8|4170305|0.9999973623032368|
|StageI_DH_singlefactor|DH M16|4170305|0.9999973623032368|
|StageI_DH_singlefactor|DH Q64|4170294|1.0|
|StageI_DH_singlefactor|DH Q128|4170294|1.0|
|StageI_DH_singlefactor|DH F128|4170294|1.0|
|StageI_DH_singlefactor|DH F256|4170294|1.0|

Use the measured single-factor response spectrum and explicit initial-state/traffic exposure to distinguish low observed response from an untested structure opportunity.

Counterexample/boundary: No structure/combination measurements outside the fixed8: a flat downstream result cannot falsify every internal design opportunity or establish a theoretical upper bound.

Best observed DH cycles 4,170,294 (self speedup 1.000000000) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/1df9d5479504d9c7c5f5ef176e9604ce1b43421c7b6be440597259607d3971c0.json.gz`; 11 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: NOT_MEASURED_OUTSIDE_FIXED8 / NOT_MEASURED_OUTSIDE_FIXED8.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
