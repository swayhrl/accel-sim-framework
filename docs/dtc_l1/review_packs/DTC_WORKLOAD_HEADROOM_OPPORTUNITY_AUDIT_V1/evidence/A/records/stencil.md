# stencil: observed opportunity record

Full input identity `c885293ad99e21ee6f270647dc47f1e6b214c71856b189cd011266ce4ae21266`; Parboil; fixed CORE32.

CH-P0 4,965,921 cycles; DH-P0 4,662,889. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|4965921|N/A|
|StageII_sixcell|CH F256|4965921|N/A|
|StageII_sixcell|CH P0|4965921|N/A|
|StageII_sixcell|DH F128|4662889|1.0|
|StageII_sixcell|DH F256|4662889|1.0|
|StageII_sixcell|DH P0|4662889|1.0|
|StageI_DH_singlefactor|DH E384|4662889|1.0|
|StageI_DH_singlefactor|DH E768|4662889|1.0|
|StageI_DH_singlefactor|DH M8|4662550|1.0000727069950992|
|StageI_DH_singlefactor|DH M16|4662691|1.000042464748361|
|StageI_DH_singlefactor|DH Q64|4662889|1.0|
|StageI_DH_singlefactor|DH Q128|4662889|1.0|
|StageI_DH_singlefactor|DH F128|4662889|1.0|
|StageI_DH_singlefactor|DH F256|4662889|1.0|

Use the measured single-factor response spectrum and explicit initial-state/traffic exposure to distinguish low observed response from an untested structure opportunity.

Counterexample/boundary: No structure/combination measurements outside the fixed8: a flat downstream result cannot falsify every internal design opportunity or establish a theoretical upper bound.

Best observed DH cycles 4,662,550 (self speedup 1.000072707) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/c885293ad99e21ee6f270647dc47f1e6b214c71856b189cd011266ce4ae21266.json.gz`; 100 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: NOT_MEASURED_OUTSIDE_FIXED8 / NOT_MEASURED_OUTSIDE_FIXED8.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
