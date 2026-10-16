# Lane 6 — review_r2 delivery

Status: `READY_FOR_REVIEW` — same task and execution branch; old r1 preserved.
Review authority: `aec01450d3c527524ee09ee59242f582fafe5354`.
Original scientific contract: `6c136e2a56a008695f8c8b815723bf8f1a760db9`.
Framework branch: `hrl/ep-l2-ft20261016-lane6-v1`.
Offline tool producer: `219fe14be00374f206e549794704c36ff66ba143` (not simulator runtime).
Host: huangrulin-174. Worktree: `/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane6-v1`.
Lane 6 Core/build/binary/active runs/leases: none. Initial Goal was not restarted.

Delivered r2: concise Chinese WB-first manuscript, claim-evidence map, three-column
PPA ledger, three compact PDF/SVG figures and incremental native result intake.
Common 128B/slice latch is outside the 1168/1160 RAM slots; actual RO module
completion capacity is N slots, not the old illustrative T_RO=128. Area/power/Fmax
remain unknown without matched RTL/process; no C++ sizeof estimate is used.

Consumed Lane 1 R0 release 02982b65e87f170103b44c6dbd562a8ffb03841e, later
Lane 5 independent qualification and b47b721d1be26210ffaea178fbbf3f5c839c2b9c
formal sad pair. Exact R0 Core126394be/FW37dec04d/binary0b504f55/config/trace
identities are in RECEIPT and FORMAL_WB_PAIR_INPUTS. Qualification is restricted
to B16/U_WB16 and symbolic sector-version/request identity, not numeric SASS.

sad: 110593 vs 110573 GPU cycles (1.0001808759823827x), effectively tied.
Peak staging is 1 on both sides; no capacity-pressure relief is demonstrated.
Copy3975->0 and Bank logical operations485175->477225; DRAM bytes unchanged.
The other four declared workload pairs are pending in the consumed publication;
whole-group geomean stays null. No local in-flight result is promoted to evidence.

Historical evidence remains separate: all13 Streaming rows revalidated; old
static vectorAdd optimistic-read 1.721259x is a diagnostic reference, not R0
speedup, strict upper bound or suite mean. All18 new matched-R1 cells remain missing.
TVD/RO production and R1 ideal are not prerequisites for Lane 5 R0 experiments.

Validation:12 intake tests pass;15 generated files reproduce byte-identically;
26 pinned source blobs;3 final figures visually checked;all33 old r1 files unchanged.
No mechanism/config/trace/original science CSV/binary/registry was modified; no
simulator experiment, rebuild, reservation, stop or reset was performed by Lane 6.

Review pack: `docs/ep_l2/review_packs/FT20261016_LANE6_PAPER_PPA_r2/`.
Current deliverable has no blocker. Further evidence: remaining four WB pairs,
matched-R1 diagnostics, separately qualified TVD/RO and physical PPA.
