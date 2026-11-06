# histo: observed opportunity record

Full input identity `2c506bf13c81ff5dd4c286fa2f6d7a9edea513a5c8f38c60cfc746e36e9c5f64`; Parboil; fixed CORE32.

CH-P0 5,636,037 cycles; DH-P0 5,865,589. This is an evidence dossier, not a theoretical upper bound or a release for experiments.

|Source family|Profile|Accepted cycles|DH own speedup|
|---|---|---:|---:|
|StageII_sixcell|CH F128|5551616|N/A|
|StageII_sixcell|CH F256|5502955|N/A|
|StageII_sixcell|CH P0|5636037|N/A|
|StageII_sixcell|DH F128|5789155|1.013202963126743|
|StageII_sixcell|DH F256|5731388|1.0234150959593034|
|StageII_sixcell|DH P0|5865589|1.0|
|StageI_DH_singlefactor|DH E384|5872359|0.9988471413277015|
|StageI_DH_singlefactor|DH E768|5872359|0.9988471413277015|
|StageI_DH_singlefactor|DH M8|5875753|0.9982701791583138|
|StageI_DH_singlefactor|DH M16|5872783|0.998775027103845|
|StageI_DH_singlefactor|DH Q64|5879400|0.9976509507772902|
|StageI_DH_singlefactor|DH Q128|5859602|1.0010217417496956|
|StageI_DH_singlefactor|DH F128|5789155|1.013202963126743|
|StageI_DH_singlefactor|DH F256|5731388|1.0234150959593034|

Use the measured single-factor response spectrum and explicit initial-state/traffic exposure to distinguish low observed response from an untested structure opportunity.

Counterexample/boundary: No structure/combination measurements outside the fixed8: a flat downstream result cannot falsify every internal design opportunity or establish a theoretical upper bound.

Best observed DH cycles 5,731,388 (self speedup 1.023415096) is an exploratory per-program reference with tied exact source IDs in JSON. It is never combined into a best-per-program suite GM.

Kernel-cycle detail: `kernel_cycles/2c506bf13c81ff5dd4c286fa2f6d7a9edea513a5c8f38c60cfc746e36e9c5f64.json.gz`; 80 positions, six accepted source cells. All request/traffic/service facts retain cumulative endpoint units and missingness; no retry count or gauge is interpreted as critical-path time.

Structure and combination scope: NOT_MEASURED_OUTSIDE_FIXED8 / NOT_MEASURED_OUTSIDE_FIXED8.

Source/initial-state limits and exact source SHA are in the companion JSON. Capture/ELF/numerical correctness remains unproved; static reuse is not a cache-hit/merge measurement.
