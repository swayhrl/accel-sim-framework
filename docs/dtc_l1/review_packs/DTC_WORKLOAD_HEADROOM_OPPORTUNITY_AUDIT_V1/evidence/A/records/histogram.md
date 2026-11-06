# histogram: observed opportunity record

Full input identity `3722a5c85d91a9482233c2bf128a6721e3fb194db3e5e54be6cbec9598518a58`; CUDA Samples; fixed CORE32.

CH-P0 101,432 cycles; DH-P0 98,202. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|101432|N/A|
|StageII_sixcell|CH F256|101432|N/A|
|StageII_sixcell|CH P0|101432|N/A|
|StageII_sixcell|DH F128|98202|1.0|
|StageII_sixcell|DH F256|98202|1.0|
|StageII_sixcell|DH P0|98202|1.0|
|StageI_DH_singlefactor|DH E384|98202|1.0|
|StageI_DH_singlefactor|DH E768|98202|1.0|
|StageI_DH_singlefactor|DH M8|98202|1.0|
|StageI_DH_singlefactor|DH M16|98202|1.0|
|StageI_DH_singlefactor|DH Q64|98202|1.0|
|StageI_DH_singlefactor|DH Q128|98202|1.0|
|StageI_DH_singlefactor|DH F128|98202|1.0|
|StageI_DH_singlefactor|DH F256|98202|1.0|

Use the measured single-factor response spectrum and explicit initial-state/traffic exposure to distinguish low observed response from an untested structure opportunity.

Counterexample/boundary: No structure/combination measurements outside the fixed8: a flat downstream result cannot falsify every internal design opportunity or establish a theoretical upper bound.

Best observed DH cycles 98,202 (self speedup 1.000000000) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/3722a5c85d91a9482233c2bf128a6721e3fb194db3e5e54be6cbec9598518a58.json.gz`; 8 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: NOT_MEASURED_OUTSIDE_FIXED8 / NOT_MEASURED_OUTSIDE_FIXED8.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
