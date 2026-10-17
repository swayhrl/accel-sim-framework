# Lane1: finite RTL/SIM timing review before performance pairing

No official Core patch or formal app is requested/run by this pack.
Actual B16 worst path: p_old[0] mapped DFF1490329 -> native_gen[31];
its first Q has fanout1027 and1,715.137939fF load in reference STA.
Actual Unified worst path: metadata[0].generation[2] mapped DFF1865 ->
p_tag[8] mapped DFF1933286. The source free-generation/bank-compatible
landing scan and req_ready/req_fire transaction enable create this path.
See raw critical_paths and the canonical controller source around the
free_landing loop, install_ok, landing_generation and native_gen expressions.

Independent issues: (1) reference netlist timing/DRC is unclosed, including
hierarchical fanout and serial priority logic; optimization/balancing/
rebuffering needs a same-effort three-mode engineering revision. (2) RTL
frontend II4/II3, static-copy and return phases, round-robin arbitration and
held native approval differ from SIM, independently of cell sizing.

Before paper area/performance coupling, review the exact delta in
SIM_RTL_TIMING_GAP. Choose an actual matched microarchitecture/throughput
contract and a real SRAM macro interface. Any SIM adaptation belongs to
Lane1 as an explicit default-off controlled release; do not silently add a
cycle to every hit or infer that current ROP delay hides this work.
The current cost table remains prototype-only. Atomic/RO/TVD are unqualified.
