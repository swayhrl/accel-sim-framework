# particlefilter_naive: observed opportunity record

Full input identity `3f85d1878aba9f04916ec52cc1162b37673f92a88be07c4db815240c9564755e`; Rodinia; fixed CORE32.

CH-P0 511,136 cycles; DH-P0 384,601. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|511136|N/A|
|StageII_sixcell|CH F256|511136|N/A|
|StageII_sixcell|CH P0|511136|N/A|
|StageII_sixcell|DH F128|384601|1.0|
|StageII_sixcell|DH F256|384601|1.0|
|StageII_sixcell|DH P0|384601|1.0|
|StageI_DH_singlefactor|DH E384|384601|1.0|
|StageI_DH_singlefactor|DH E768|384601|1.0|
|StageI_DH_singlefactor|DH M8|384601|1.0|
|StageI_DH_singlefactor|DH M16|384601|1.0|
|StageI_DH_singlefactor|DH Q64|384601|1.0|
|StageI_DH_singlefactor|DH Q128|384601|1.0|
|StageI_DH_singlefactor|DH F128|384601|1.0|
|StageI_DH_singlefactor|DH F256|384601|1.0|

Use the measured single-factor response spectrum and explicit initial-state/traffic exposure to distinguish low observed response from an untested structure opportunity.

Counterexample/boundary: No structure/combination measurements outside the fixed8: a flat downstream result cannot falsify every internal design opportunity or establish a theoretical upper bound.

Best observed DH cycles 384,601 (self speedup 1.000000000) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/3f85d1878aba9f04916ec52cc1162b37673f92a88be07c4db815240c9564755e.json.gz`; 9 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: NOT_MEASURED_OUTSIDE_FIXED8 / NOT_MEASURED_OUTSIDE_FIXED8.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
