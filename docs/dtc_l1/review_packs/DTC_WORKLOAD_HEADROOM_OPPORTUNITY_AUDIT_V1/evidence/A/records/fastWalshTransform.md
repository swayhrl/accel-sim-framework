# fastWalshTransform: observed opportunity record

Full input identity `f7f22a2ccc836a8a9b2096d4df50caf00a2c4bcebc7b16d064b8b0287ce593d3`; CUDA Samples; fixed CORE32.

CH-P0 191,732 cycles; DH-P0 185,317. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|191314|N/A|
|StageII_sixcell|CH F256|191430|N/A|
|StageII_sixcell|CH P0|191732|N/A|
|StageII_sixcell|DH F128|185382|0.999649372646751|
|StageII_sixcell|DH F256|185740|0.9977226230214278|
|StageII_sixcell|DH P0|185317|1.0|
|StageI_DH_singlefactor|DH E384|185345|0.999848930373088|
|StageI_DH_singlefactor|DH E768|185345|0.999848930373088|
|StageI_DH_singlefactor|DH M8|185317|1.0|
|StageI_DH_singlefactor|DH M16|185317|1.0|
|StageI_DH_singlefactor|DH Q64|185420|0.9994445043684608|
|StageI_DH_singlefactor|DH Q128|185534|0.9988304030528097|
|StageI_DH_singlefactor|DH F128|185382|0.999649372646751|
|StageI_DH_singlefactor|DH F256|185740|0.9977226230214278|

CH/DH opposite small F responses remain a counterexample to monotone retry/miss reasoning. K6 is a read-active print interval.

Counterexample/boundary: Read-active does not prove cold-start/compulsory misses or request-origin membership; prefill and later intervals remain explicit.

Best observed DH cycles 185,317 (self speedup 1.000000000) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/f7f22a2ccc836a8a9b2096d4df50caf00a2c4bcebc7b16d064b8b0287ce593d3.json.gz`; 16 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: NOT_MEASURED_OUTSIDE_FIXED8 / NOT_MEASURED_OUTSIDE_FIXED8.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
