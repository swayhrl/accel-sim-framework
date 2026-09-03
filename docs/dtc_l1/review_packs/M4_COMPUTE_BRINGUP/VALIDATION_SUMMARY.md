# M4 HARD-gate validation summary

| Gate | Evidence | Result |
| --- | --- | --- |
| R4C.0--R4C.8 | UID 15888 / PC `0x148` duplicate IO completion was traced to a re-admitted cacheable load; state-machine repair, CTests, and 2DConv IO/OO reruns are in `implementation/M4_COMPLETION_ACCOUNTING_RECOVERY_EVIDENCE.md` | PASS |
| W01/W02 | `m4_store_hit_miss` reaches two normal global-store instructions on one line; audited baseline write path remains intact and all Base/IO/OO runs pass | PASS |
| W03/W04 | Base/IO/OO preserve source dynamic counts `(loads,stores,atomics,FENCE_OP)=(5,2,0,0)`; IO/OO Store admit=complete=retire=2 with no DTC read allocation for the sidecar | PASS |
| A01 | `atomic_contention` passes in Base/IO/OO; IO/OO each close 8 admitted atomic instruction lifecycles | PASS |
| A02 | directed `m4_atomic_pair` PTX contains two `atom.global.add` instructions to one address; Base/IO/OO return counter=16, dynamic atomics=2; IO/OO admit=complete=retire=2 | PASS |
| A03/A04 | deterministic CTest external-dependency case blocks FIFO IO behind the older unresolved sidecar and permits OO retirement of a younger ready load first; the older identity then retires exactly once | PASS |
| F00A | lexer recognizes only `membar -> MEMBAR_OP`; parser/decode has no PTX `FENCE_OP` producer and no proxy-fence setter call site | PASS |
| F00B | Core range `bfb3b633..cdeec769` changes no `src/cuda-sim` or `abstract_hardware_model.h` file; no membar mapping, forced proxy state, or regular-fence bypass introduced | PASS |
| F00C | all five accepted Base/IO/OO workload triplets have equal source-domain `(loads,stores,atomics,FENCE_OP)` and `FENCE_OP=0` | PASS |
| F00D | dynamic proxy-fence branches remain source-identical in the M4 change range; normal PTX runs only record observational zero fence count | PASS |
| F01/F02/F03 | current PTX source cannot construct dynamic proxy fences; classified under authorized resolution, not executed and not silently substituted | SOURCE_UNREACHABLE_NA |
| BP01/BP02 | `.cg` maps to `CACHE_GLOBAL`; directed `m4_mixed_cg` uses a real `ld.global.cg`, preserves Base/IO/OO output, and IO/OO each close one bypass-load lifecycle without DTC Tag/physical ownership | PASS |
| MIX01 | normal load + `ld.global.cg` bypass + store + same-address atomic passes in LEGACY/Base/IO/OO; paper modes have `(6,1,1,0)`, IO/OO lifecycle=3/3/3 | PASS |
| Workload manifest | five provenance-resolved compute workloads accepted; PB_2DCONV is explicitly diagnostic because Base is slow but progressing | PASS |
| Parser/provenance/hygiene | strict parser output for workload and directed summaries; release CTests pass; `git diff --check` and clean worktree are closeout requirements | PASS |

Accepted workload operation tuples:

| Workload | Base = IO = OO `(loads, stores, atomics, FENCE_OP)` |
| --- | --- |
| PB_ATAX | `(16704, 8256, 0, 0)` |
| PB_GEMM | `(17536, 8320, 0, 0)` |
| PB_FDTD2D | `(6628, 764, 0, 0)` |
| PARBOIL_SPMV | `(12400, 100, 0, 0)` |
| PARBOIL_SGEMM | `(1196, 72, 0, 0)` |
