# scalarProd: observed opportunity record

Full input identity `2b93f70cd0666c5112f5550aae7b3a8d0565de1de40604d494bdc36c503f6954`; CUDA Samples; fixed CORE32.

CH-P0 420,477 cycles; DH-P0 411,009. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|421185|N/A|
|StageII_sixcell|CH F256|422012|N/A|
|StageII_sixcell|CH P0|420477|N/A|
|StageII_sixcell|DH F128|411440|0.9989524596538985|
|StageII_sixcell|DH F256|409181|1.0044674606103412|
|StageII_sixcell|DH P0|411009|1.0|
|StageI_DH_singlefactor|DH E384|411009|1.0|
|StageI_DH_singlefactor|DH E768|411009|1.0|
|StageI_DH_singlefactor|DH M8|411009|1.0|
|StageI_DH_singlefactor|DH M16|411009|1.0|
|StageI_DH_singlefactor|DH Q64|411009|1.0|
|StageI_DH_singlefactor|DH Q128|411009|1.0|
|StageI_DH_singlefactor|DH F128|411440|0.9989524596538985|
|StageI_DH_singlefactor|DH F256|409181|1.0044674606103412|

Use the measured single-factor response spectrum and explicit initial-state/traffic exposure to distinguish low observed response from an untested structure opportunity.

Counterexample/boundary: No structure/combination measurements outside the fixed8: a flat downstream result cannot falsify every internal design opportunity or establish a theoretical upper bound.

Best observed DH cycles 409,181 (self speedup 1.004467461) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/2b93f70cd0666c5112f5550aae7b3a8d0565de1de40604d494bdc36c503f6954.json.gz`; 1 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: NOT_MEASURED_OUTSIDE_FIXED8 / NOT_MEASURED_OUTSIDE_FIXED8.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
