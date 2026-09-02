# M2-RF validation summary

All results below are `VERIFIED_RUN` at Core `3b93e243` and Framework handoff
`e6b8d6b6`, with the cold-built RTX3070 binary and 10 GiB virtual-memory cap.
Raw paths are indexed in [RAW_LOG_INDEX.tsv](RAW_LOG_INDEX.tsv).

| Check | Result | Key evidence |
| --- | --- | --- |
| cold Core+Framework build | PASS | new `accel-sim.out` linked against `3b93e243` |
| M1 directed and disabled/ideal transparency | PASS | normalized one-kernel diff is empty |
| G2-1/G2-2/G2-3/G2-4 | PASS | exact unit assertions remain intact |
| RF pending-retry/non-starvation | PASS | A: 1 L1+1 L2 initial miss; 9 bypasses; B uses shared L2 port; two exact wakeups |
| kernel-boundary persistence | PASS | warmed L1 translation hits after focused ordinary-boundary model |
| one-kernel, LUD, BFS functional replay | PASS | normal exit and MSHR/PWQ/walker quiescence |
| latency 5 versus 50 sensitivity | PASS | 7 walks in both; L2 misses 16 to 19, not polling-driven explosion |
| provisional G3-1 backend/no-recursion test | PASS | `vm_m3_g3_1_test PASS` |

The ordinary-kernel lifetime source proof complements the focused test:
`gpgpu_sim` constructs `m_vm_translation` once in `gpu-sim.cc` constructor
(around lines 1024–1052); ordinary `init()` (around 1264) and
`set_kernel_done()` (around 977) do not reset or replace it.
