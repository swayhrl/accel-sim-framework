# R20R3 authorization

Date: 2026-10-01

R20R2 authority:
- execution branch: `hrl/awma-r20r2-linesearch-semantic-materiality-109-v1`
- commit: `e645b5e011c18f1e44b7a1509fb55c49486adff5`
- tree: `a84dfb574feed44d8b64c4e5ea41858351be721e`
- formal label: `R20R2_LINESEARCH_DIAGNOSTIC_THRESHOLD_ONLY`

Accepted revised numerical boundary:
- solver-entry identity, world/constraint identity, nefc, outer solver_niter, true capacity-overflow absence, finite outputs, ctx.done, frozen floating output contract and qfrc source relation remain hard gates;
- LS_ITERATIONS is reported with location/alpha/improvement but is not a hard equality gate by itself;
- any LS difference accompanied by changed outer niter/coverage, output outside contract, materially propagated path difference, or hidden-state evidence remains failure.

Authorized next stage:
- handoff branch: `hrl/awma-r20r3-active-world-solver-native-handoff-v1`
- handoff HEAD: `2b9783a4a28691c7c762bcfb7c8c3a8c115cff36`
- execution branch: `hrl/awma-r20r3-active-world-solver-native-109-v1`
- Goal: `docs/vm_tlb/chatgpt_handoff/awma/r20r3_active_world_solver_native_v1/LANE_F_R20R3_ACTIVE_WORLD_SOLVER_NATIVE_109_GOAL.md`

R20R3 is the first authorized active-world performance diagnostic.

Scope:
1. OFF baseline regression on the frozen discovery solver entries.
2. At most one B0 NSYS capture to select one eligible complete solver substage using a frozen selection rule.
3. Exactly one online active-world/worklist software diagnostic.
4. Complete solver.solve paired timing on the four discovery entries.
5. Holdout entries 384/392/400/408 only if discovery complete-solver response is stable and >=5% under the frozen investment gate.

No second candidate, worker-count sweep, whole-trajectory timing, NCU/NVBit/SASS, node174/Accel-Sim or hardware design is authorized.

Lane F becomes ACTIVE only for R20R3.
Lane E/G and node174 remain STOP.
