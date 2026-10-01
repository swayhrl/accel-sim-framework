# Same-input activity and capacity ledger — diagnostic, not an A/B experiment

For the only scientific shape B1024, memory admission left `15125/16376 MiB` free (`92.36%`) after one conditional graph capture and two replays; B512/B256 were never tried. The author descriptor requested `nconmax=48` per world and `njmax=192`; resulting pooled `naconmax=49152`, `naccdmax=49152`, `njmax_nnz=4445`, `nvmax=35`. No true capacity-overflow bit appeared in any of the 32 discovery steps, so the one permitted capacity expansion was not used. The per-step raw table and complete per-world arrays are on node164.

| Same discovery data | Observed range / amount | Interpretation |
| --- | ---: | --- |
| Active contacts `nacon` | 3985–7860 / pooled 49152 | occupancy only, not traffic or performance headroom |
| Per-world valid constraints `nefc` | 0–137 / per-world 192 | no `NEFC` capacity overflow |
| Per-world solver rounds | 1–10 | all 32 steps had active-set shrinkage |
| Derived active-slot fraction | 0.296–0.505; mean 0.3733 | `sum_j A_j/(B*J)` from exact solver_niter and monotonic done; not SM utilization or speedup bound |
| Iteration-limit worlds | at most 8/1024 in one step | keep separate from non-limit exits; not all worlds censored |
| Line-search-limit worlds | at most 37/1024 in one step | separate stop/accuracy signal, not capacity loss |
| True capacity-overflow worlds | 0 | contact/constraint coverage not truncated by an observed capacity flag |

The full Data inventory contains 138 nonempty array fields. Sum of logical bytes is `99,024,904`; device-address interval union after alias de-duplication is also `99,024,904` bytes (no overlapping backing intervals in this B1024 inventory). This covers Data-resident state/workspace arrays, not graph-local solver temporaries. The latter's bytes are `UNKNOWN`; the roughly 405 MiB overall device-memory delta after model/Data/graph creation also includes model arrays, CUDA context, JIT and allocator reservations and must **not** be assigned to solver scratch or DRAM traffic. There was no capacity A/B, shrinking, alternate allocator or traffic estimate. Detailed field paths, pointers and bytes are in node164 `raw/CAPACITY_POINTER_LEDGER.json`; unknowns remain explicit.
