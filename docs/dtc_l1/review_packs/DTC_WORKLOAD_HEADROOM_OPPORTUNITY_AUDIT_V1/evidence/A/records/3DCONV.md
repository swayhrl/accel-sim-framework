# 3DCONV: observed opportunity record

Full input identity `79f8ab6241faeed64b49d05deecb1ad239fac5f123c4ceec75f7e0f6a9c5166d`; PolyBench/GPU; fixed CORE32.

CH-P0 2,958,083 cycles; DH-P0 2,200,332. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|2956986|N/A|
|StageII_sixcell|CH F256|2958542|N/A|
|StageII_sixcell|CH P0|2958083|N/A|
|StageII_sixcell|DH F128|2205628|0.9975988698003471|
|StageII_sixcell|DH F256|2211632|0.9948906508858617|
|StageII_sixcell|DH P0|2200332|1.0|
|StageI_DH_singlefactor|DH E384|2203091|0.9987476686165029|
|StageI_DH_singlefactor|DH E768|2203091|0.9987476686165029|
|StageI_DH_singlefactor|DH M8|2186097|1.006511604928784|
|StageI_DH_singlefactor|DH M16|2186097|1.006511604928784|
|StageI_DH_singlefactor|DH Q64|2204420|0.9981455439526044|
|StageI_DH_singlefactor|DH Q128|2205117|0.9978300471131464|
|StageI_DH_singlefactor|DH F128|2205628|0.9975988698003471|
|StageI_DH_singlefactor|DH F256|2211632|0.9948906508858617|

Preserve254 actual instances and small opposite design responses; no scalar loop index is assigned from ordinal.

Counterexample/boundary: Source scalar_i/capture binding remains unknown; small aggregate counter shifts do not establish critical-path cause.

Best observed DH cycles 2,186,097 (self speedup 1.006511605) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/79f8ab6241faeed64b49d05deecb1ad239fac5f123c4ceec75f7e0f6a9c5166d.json.gz`; 254 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: NOT_MEASURED_OUTSIDE_FIXED8 / NOT_MEASURED_OUTSIDE_FIXED8.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
