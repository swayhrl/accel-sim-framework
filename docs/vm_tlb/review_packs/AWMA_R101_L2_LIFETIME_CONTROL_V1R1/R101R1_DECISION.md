# R101R1 scientific decision

**`R101R1_EXISTING_L2_CONTROL_INSUFFICIENT_READY_FOR_ARCH_REVIEW`**

The accepted Qwen-derived HiMuon tile payload hashes matched R101 exactly. The pinned five-step coefficients and the XXT → ba_plus_cAA → fused_bmm_add recurrence were unchanged. SM89 executed `discard.global.L2 [ptr], 128` naturally; PTX and SASS showed the instruction, and the runtime smoke passed. D1 B0/discard outputs were bitwise identical for K128 and L512, including repeated graph replay and input perturb/restore. NSYS showed identical non-discard kernel sequence, exact name, grid and block, plus 15 discard nodes.

| Exact paired graph control | Baseline median | Control median | NS-family DRAM write | Decision |
| --- | ---: | ---: | ---: | --- |
| K128 B0 → D1 | 0.52525 ms | 0.54003 ms | K128 NCU pair not joinable: XXT autotune block drift | No runtime benefit; no K128 traffic ratio claimed |
| L512 B0 → D1 | 1.42259 ms | 1.47078 ms | 346.92 → 255.81 MB (−26.26%) | D1 below the 50% write gate and 3.39% slower; D2 admitted |
| L512 A0 arena → D2 persist+discard | 1.41718 ms | 1.45402 ms | 337.55 → 338.22 MB (+0.20%) | D2 did not suppress writeback and is 2.60% slower |

Rows are *within-row* paired controls only. R101R1's manual wrapper preserves author arithmetic/output/kernel strata but changes surrounding compiled normalization/launch organization; its B0 time is not compared numerically to accepted R101's historical median. L512 NCU B0/D1 and single-process A0/D2 have matching arithmetic kernel name/grid/block strata. NCU durations are not used as primary times. D1 discard kernels are separate from NS-family metrics; on L512 they contributed 15 launches and ~0.0474 ms summed NSYS kernel duration (profiler-only). D2 policy was set on the 44 MiB A+B window at hitRatio 1.0 after a 44 MiB set-aside succeeded. The CUDA graph active-capture API exposed 33 of 35 kernel nodes; the two later nodes are the terminal B/old-X discards, as source and NSYS order show. All producer/consumer arithmetic nodes received graph-node access-policy attributes with successful API readback.

The interpretation is bounded. D1's residual write traffic is consistent with dirty lines having escaped L2 before last-use discard, or with the 128-byte hint's implementation limits; the data does not distinguish those microcauses. D2's nominal set-aside covers all A+B bytes but is a priority *hint*, not a reservation guarantee, and in this run it did not reduce NS writes. Complete CUDA Graph timing and NCU/NSYS GPU counters rule out Python launch overhead as the explanation for the remaining measured write traffic. They do **not** imply that a new architecture would be fast, nor isolate a predicted hardware gain. A later review must compare an exact-map stronger software implementation and specify the precise granularity/capacity/early-eviction hypothesis before any mechanism.

Neither D1 nor D2 met the >=5% and >3×noise timing gate, so the accepted layer12 holdout payload was verified but **not executed** under the handoff's conditional rule. No threshold, tile size, coefficient, NS step count, model, or alternate optimizer was swept.

Excluded attempts are indexed in `EXCLUDED_ATTEMPTS.md`. In particular, an external-arena Tensor-lifetime bug invalidated an early arena NSYS/timing attempt; those artifacts were retained as OBSOLETE and the corrected arena path was rerun with every timed output checked bitwise. K128 NCU block drift remains a stated diagnostic limitation, not silently averaged into the L512 conclusion.
