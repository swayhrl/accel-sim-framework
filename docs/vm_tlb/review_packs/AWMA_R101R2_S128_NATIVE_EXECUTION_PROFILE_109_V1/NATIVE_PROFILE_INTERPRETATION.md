# R101R2 S128 Native execution profile interpretation

**Native-side classification: `NATIVE_PROFILE_MIXED`.** This is a diagnostic fact pack for joint review with Lane E O2, not the final R101R2 outcome. The accepted R101 graph timing remains F128 0.493408 ms versus K128 0.623488 ms (20.8633% F128 improvement). No NCU replay duration replaces that timing.

All graph-node additive counters, including two small graph-runtime fill nodes per arm:

| Measured quantity | F128 | K128 | F/K |
| --- | ---: | ---: | ---: |
| Executed warp instructions (inst) | 37,342,130.000 | 97,245,554.000 | 0.3840 |
| Issued warp instructions (inst) | 37,351,298.000 | 97,392,283.000 | 0.3835 |
| Direct global LDG/LD warp instructions (inst) | 37,184.000 | 474,096.000 | 0.0784 |
| Async global→shared LDGSTS warp instructions (inst) | 0.000 | 2,881,760.000 | 0.0000 |
| Global STG/ST warp instructions (inst) | 37,186.000 | 966,786.000 | 0.0385 |
| L1/TEX requested bytes (Mbyte) | 149.331 | 1,404.068 | 0.1064 |
| L2 requested bytes (Mbyte) | 128.688 | 1,389.593 | 0.0926 |
| DRAM read bytes (Mbyte) | 19.185 | 51.769 | 0.3706 |
| DRAM write bytes (Mbyte) | 31.134 | 302.740 | 0.1028 |
| HMMA warp instructions (inst) | 8,924,160.000 | 7,436,800.000 | 1.2000 |
| Active SM cycles summed across kernels (cycle) | 86,180,085.000 | 106,171,020.000 | 0.8117 |
| Derived LDG/LD + LDGSTS issue (warp inst) | 37,184.000 | 3,355,856.000 | 0.0111 |

Family decomposition (resource entries are per-family medians in raw NCU units, not sums):

| Arm | Family | Launches | Executed warp inst | LDG/LD | LDGSTS | STG/ST | HMMA | Active cycles | Occupancy % | Eligible warps/active cycle | Registers/thread | Shared/block (Kbyte/block) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| F128 | F128_FUSED_NS5 | 1 | 37,342,032 | 37,184 | 0 | 37,184 | 8,924,160 | 86,178,449 | 16.64 | 0.15 | 255 | 66.560 |
| F128 | GRAPH_RUNTIME_OTHER | 2 | 98 | 0 | 0 | 2 | 0 | 1,636 | 7.95 | 0.02 | 16 | 1.024 |
| K128 | K128_NORMALIZATION | 1 | 3,960,096 | 148,736 | 0 | 223,104 | 0 | 19,158,615 | 86.16 | 0.09 | 26 | 1.088 |
| K128 | K128_XXT | 5 | 29,991,220 | 0 | 1,115,520 | 278,880 | 2,231,040 | 25,916,491 | 23.37 | 0.39 | 128 | 33.792 |
| K128 | K128_BA | 5 | 35,719,880 | 139,440 | 1,115,520 | 278,880 | 2,231,040 | 29,740,022 | 23.50 | 0.41 | 128 | 33.792 |
| K128 | K128_BMM_ADD | 5 | 27,574,260 | 185,920 | 650,720 | 185,920 | 2,974,720 | 31,354,257 | 15.60 | 0.28 | 254 | 50.176 |
| K128 | GRAPH_RUNTIME_OTHER | 2 | 98 | 0 | 0 | 2 | 0 | 1,635 | 7.95 | 0.02 | 16 | 1.024 |

F128 removes 61.60% of executed warp instructions and changes NS core from 15 arithmetic kernel launches to one fused launch, yet executes 20% more HMMA warp instructions. It also removes most global-memory instruction and hierarchy traffic. These simultaneous changes support clear execution-work reduction but do not isolate whether instruction issue, dependency/launch organization, or memory service caused the accepted 20.86% timing response. Thus `NATIVE_PROFILE_MIXED` is the appropriate Native-only label.

The direct global-load metric counts LDG/LD; K128 also uses LDGSTS global→shared instructions, measured separately. The derived sum above combines two distinct warp-opcode classes and is **not** one hardware counter or per-thread instruction count. Static SASS counts in `STATIC_SASS_SUMMARY.tsv` are per selected binary; they are not dynamic counts or weighted speedups. Active-cycle sums are profiler counters, not graph elapsed time. L1/TEX/L2 requested bytes and DRAM bytes are different hierarchy semantics, not interchangeable. No causality or novelty is claimed from these counters alone.

Two requested names were not supported on this SM89 NCU build: `smsp__inst_executed_pipe_fp32.sum` and `smsp__warps_issued.sum`. FMA and issued instructions are separately named supported quantities, never silent substitutes. The first two reports omitted the available LDGSTS class and are archived as ATTEMPT0. One source-motivated metric-engineering retry per arm added exactly `smsp__inst_executed_op_ldgsts.sum` to the frozen set; it did not change input, source, configurations or performance selection. Full counter/unit/aggregation bindings are in `NCU_RAW_METRIC_BINDING.tsv`.
