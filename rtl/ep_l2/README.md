# EP-L2 finite-WB single-slice RTL, first cost flow

Authority: Framework f1980a84c8e637ff2050048bd11b3c1fa5362583, RTL task §4.
Finite protocol source: Core9bd30ed913c5058b5d952fbeb2e67cb5e4644b3f.

`ep_l2_slice` connects the changed-path controller and four explicit payload
SRAM boundaries. MODE0=B16 (1024/128/16), MODE1=Unified (1168 shared),
MODE2=S64 (1024/80/64). All have1168 physical128B lines,4 banks,128 WAD.
The cost entry maps the SAME `ep_l2_slice_ctrl` at the SRAM interface cut.
No Ideal, TVD, RO, atomic, P2 or full GPU qualification is claimed.

Read [pipeline differences](docs/SIM_RTL_TIMING_GAP.md) and
[widths and excluded memories](docs/WIDTHS_AND_MEMORY.md) before using costs.
This first controller does **not** match SIM frontend/copy/arbitration
throughput. Native Tag/LRU/dirty-mask/MSHR cost and146KiB SRAM technology
area/delay are UNKNOWN. Controller WNS is not whole-slice Fmax.

[Flow instructions](flow/README.md) provide the existing Yosys/Liberty/
OpenSTA path and the same-RTL DC entry. DC remains UNRUN. No SRAM macro is
replaced with DFF data arrays for area reporting.

The full integration top passed the same independent byte-reference tests
for B16/Unified/S64 and generation exhaustion under central lease
65e7378fe2fd495baff151a1dfc7b974. A same-edge pin/admission defect was
reproduced old-red and corrected before the final source freeze. Exact
old/new source/binary/stimulus identities and logs are in
[validation/pin_admission_r1](validation/pin_admission_r1). Full-size cost
usesGEN32; GEN3 is only the bounded exhaustion test. See
[stimulus contract](docs/SHARED_STIMULI.json) for the twelve test categories.
`run_functional.py --full-top` requires a central lease in this shared host.

All previous simulator candidates and test qualifications remain unchanged.
