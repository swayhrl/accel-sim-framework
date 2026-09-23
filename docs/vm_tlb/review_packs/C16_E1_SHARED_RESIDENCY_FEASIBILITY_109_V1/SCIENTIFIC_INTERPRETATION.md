# C16 E1 shared-residency feasibility interpretation

Stage label: `SHARED_RESIDENCY_LOCAL_ONLY`. The prior producer/consumer decision-rule divergence remains frozen and is not overwritten.

Installed-NCU discovery resolves kernel duration, L2 TEX-read hit/miss sectors, DRAM-read bytes, long-scoreboard stall, LSU utilization, and active-warps metrics. Up-proj policy timing changes are concentrated in the quantized GEMM; reduction duration is nearly unchanged. Target persistence modestly shifts L2 hits/misses, while long-scoreboard and duration can also improve under matched unrelated persistence. DRAM-read bytes move far less than aggregate DRAM and native timing, confirming aggregate DRAM is a poor standalone critical-path proxy. Down-proj's native timing benefit is not reproduced by the profiled duration/stall counters.

The isolated A/B/A experiment qualifies rotating windows without reset. Its Normal/Normal matched control performs the same three API updates but marks no qweight persisting. Persistent rotation lowers target DRAM/misses and increases L2 hits, so full-model sharing proceeds on qualified semantics.

Under one fixed global set-aside, SHARE2_UP, SHARE2_L0, and SHARE3 retain material local timing benefits for at least two selected targets. However, stable D1-D3 decode-step improvements versus ROTATE_CONTROL_3 remain below 0.5%, far short of the registered 2% threshold. Policy calls cost roughly a few microseconds each and are reported separately; ROTATE_CONTROL_3 itself has negligible decode impact versus SETASIDE_ONLY.

The hardware evidence therefore supports multi-target local residency but not end-to-end decode benefit in this bounded configuration. It does not authorize NVBit, full address tracing, Accel-Sim mechanism implementation, or mechanism simulation.
