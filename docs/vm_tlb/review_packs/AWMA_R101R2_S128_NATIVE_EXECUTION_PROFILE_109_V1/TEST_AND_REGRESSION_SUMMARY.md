
# Tests and regression summary

- Accepted S128 payload SHA and pinned HiMuon source commit/file hashes verified before GPU work; accepted output/timing receipts retained.
- SM89 NCU `all` and `launch` query frozen before profiling; 21 supported profiling metrics plus 2 launch metrics in the final set. Unsupported `smsp__inst_executed_pipe_fp32.sum` and `smsp__warps_issued.sum` recorded explicitly.
- Exact F128/K128 graph outputs and same-map author tolerance passed, including perturb/restore liveness. Diagnostic NSYS showed F128 fused 1 kernel and K128 5 each XXT/BA/BMM-add; exact author name/grid/block matched accepted R101.
- Five unique selected JIT cubins were hash-closed and statically disassembled; library fill cubin marked unavailable, never guessed.
- F128 final NCU report SHA256 `523a904c6f68ef44dcb8eb08314f1089c00c0205453e320a0970905a9a1058da`; K128 final report SHA256 `566edf28778770b1a71aaa0f03064aba91538ad64cee1a9ed4756960e3831f58`. Both target receipts verify accepted bitwise outputs; profile kernel strata were independently matched to canary.
- ATTEMPT0 omitted the supported LDGSTS warp-opcode counter. It was archived as metric-engineering obsolete; a single source-motivated same-config retry per arm added only that metric. No counter/timing result guided source or parameter selection.
- Additive counters summed only across launches; occupancy/eligible-warps/register/shared remained per-family medians and ranges. NCU replay duration is not primary timing.
