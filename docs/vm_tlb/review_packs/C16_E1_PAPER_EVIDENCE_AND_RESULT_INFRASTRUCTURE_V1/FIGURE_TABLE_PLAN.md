# Figure and table plan

Each panel answers a distinct question. Values come from `PAPER_RESULTS_CURRENT` or the cited accepted review pack. Pending simulator points are omitted, never drawn at zero.

| ID | Research question | X / Y or columns | Input artifact | Supported claim | State |
|---|---|---|---|---|---|
| F1 | Does packing create a plausible residency opportunity? | storage class / MiB (packed AWQ, RTX 4080 L2, dense FP16) | Semantic NCU V2 `CAPACITY_RESIDENCY_CONSISTENCY.json` → `FIG_FOOTPRINT.svg` | Packed footprint crosses the L2 capacity comparison; consistency only [E1-002] | Available |
| F2 | Do local savings become decode savings? | native budget / local up, whole decode and self-attention saving in ms | Cost/benefit `INDEPENDENT_BUDGET_EFFECT_ANALYSIS.json` → `FIG_NATIVE_BUDGET.svg` | Local benefit coexists with offset elsewhere [E1-009] | Available |
| F3 | Which top-level work offsets the BFULL local benefit? | non-overlapping semantic category / median saving in ms | Cost/benefit `INDEPENDENT_BUDGET_EFFECT_ANALYSIS.json` → `FIG_COST_DECOMPOSITION.svg` | Self-attention is the largest directly measured BFULL offset, without a unique cause [E1-009, E1-010] | Available |
| F4 | Which work offsets operator-family expansion? | UP28/GUD84 / local FFN saving and outside-FFN residual in ms | Operator family `INDEPENDENT_RESIDUAL_DECOMPOSITION.json` → `FIG_OPERATOR_FAMILY.svg` | Broad protection does not solve the whole-decode gate [E1-008] | Available |
| F5 | What does elastic protection change? | schematic: tagged/ordinary fills, quota occupancy, set-local victim paths and denial branch | `FIRST_SIMULATOR_MECHANISM_SPEC.md`, `SEMANTIC_ADDENDUM.md`, implementation `FINAL_DECISION.json` | Specifies the bounded counterfactual, no performance claim [E1-012] | Schematic ready; manual vector drawing only |
| F6 | Where does natural reuse/pressure arise? | target role and tested dose / local DRAM and timing ratios; optional set-pressure only after accepted simulator counters | Natural-reuse `INDEPENDENT_REFILL_ANALYSIS.json`, `INDEPENDENT_KNEE_ANALYSIS.json`; future accepted counters | Natural execution loses isolated warm behavior [E1-004] | Native reuse available; set pressure pending |
| F7 | Does B16 improve the simulator reuse window, and is budget response coherent? | B8/B16/B24/BFULL / baseline-to-candidate cycle ratio, with absent points blank | Future `PAPER_SIM_RESULTS_ACCEPTED.json` → `FIG_SIM_BUDGET.svg` | Counterfactual system effect | **PENDING_B16_TIMING_RESULT**; later budgets pending |
| T1 | Did the mechanism activate for the same admitted trace? | budget, terminal/correctness, activations, protected hits, denials, local/window timing | Future accepted review pack and `PAPER_RESULTS_CURRENT.tsv` | Separates integration, protection and timing outcomes | **PENDING_B16_TIMING_RESULT** |

F1-F4 are current generated figures. F5 is a ready specification for one compact schematic. F6 should be included only if its characterization adds information beyond F2-F4. F7/T1 wait for accepted simulator evidence.
