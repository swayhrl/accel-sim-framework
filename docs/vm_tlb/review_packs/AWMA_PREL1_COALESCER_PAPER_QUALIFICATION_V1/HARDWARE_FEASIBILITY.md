# Hardware feasibility

Status: **TECHNOLOGY_PROXY_ONLY / PPA_TECH_LIBRARY_UNAVAILABLE**

Tools: `Yosys 0.9 (git sha1 1979e0b)`; `Icarus Verilog version 11.0 (stable) ()`. No project-accepted standard-
cell `.lib/.db/.lef` was available, so real area, critical delay and Fmax are
not reported or estimated.

The RTL proxy is synthesizable and passes all directed variants, including a
completion/exact-request same-cycle race. Generic synthesis gives
12,676 cells/2,543 DFFs for the same-cycle
minimal proxy and 88,273 cells/21,588
DFFs for the conservative metadata proxy. The registered variants add exactly
197/490 DFFs for their request pipeline. All four generic netlists have
combinational depth 21 after excluding FFs.

The registered input cuts the external request-to-CAM decision boundary, but
the proxy-wide generic longest path remains dominated by other drain/storage
mux logic. Thus same-cycle compare is not shown to be the sole proxy critical
path; neither variant proves GPU integration timing closure.

The exact CAM compares two 132-bit keys. Same-cycle proxy state,
including two 6-bit drain cursors, ranges from 2,470 to
21,222 bits/SID. For the simulated 76-SID platform these scale
to 187,720--1,612,872 bits. Registered
timing adds 197/490 bits/SID.
These are logical storage/proxy bounds, not layout area.

Remaining proxy limitations are explicit: there is one request input and one
unbackpressured follower output per cycle; page-class and completion-tag
mismatch are structurally compared but not separate directed-test rows; and
the proxy does not establish full GPU-controller integration equivalence.
