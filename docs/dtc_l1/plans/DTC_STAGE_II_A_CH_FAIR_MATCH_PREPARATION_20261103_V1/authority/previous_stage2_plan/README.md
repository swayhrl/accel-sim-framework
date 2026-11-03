# DTC-L1 Stage II: CH-matched L2 service and workload-phase attribution — research preparation V1

**Branch proposal only; NO new simulation launched, NO scope registered.** Source snapshot is immutable DTC-MAIN commit `c3e3bef274568abc058643c96f9c6277941f770b` at 2026-11-03T07:18:40Z (15:18:40 Asia/Shanghai). Live owner PID/UUID from that time is not a present-time guarantee. All scientific claims remain tied to this timestamp.

## Decision

The user approved the research direction: after natural registered Stage I closeout, compare CH against DH at **identical downstream F128 and F256**, then investigate phase-specific effects and evidence-gated combinations. This proposal prepares the exact scientific contract and source-to-experiment bridge. It does **not** replace a separate DTC-MAIN scope/identity/resource admission gate for launching new work.

Stage I as of source: original 350 = **330 accepted** (324 new +6 ratified P0 references), **18 negative archives**, **1 typed engineering negative** (scan M16), **1 running** (lavamd DH-Q64), **0 unstarted**. Independent named35 view335 is a *different* population (four IR and one R2 accepted) and never overwrites original350. Three old EP tails have strict closure under distinct EP contracts. First-stage full35 scientific acceptance is false even if Q64 finishes.

### Verified Stage I missingness
- 31/35 programs have 10/10 original strict/reference accepted.
- scan 9/10; hybridsort 5/10; lavamd 6/10; SYRK 0/10.
- CH-P0 and DH-P0 are both accepted for 33/35; DH F128 and DH F256 have 33/35 accepted pairs **separately**; both DH F128/F256 coexist for **32/35**. Across CH-P0,DH-P0,DH-F128,DH-F256 the intersection is **32/35**.
- F128 vs F256 on the all-profile same31 set: 1.008258561 vs 1.011580804 DH/P0 geometric means; marginal F128→F256 on same31 1.003295032. F256 available33 GM1.022440468 does NOT use the same31 denominator.
- No non-P0 CH profile is registered or accepted. Therefore `CH speedup(F)` and the CH/DH interaction remain UNKNOWN.

## Artifacts

- [GOAL_FOR_DTC_MAIN.md](GOAL_FOR_DTC_MAIN.md): staged, ready-to-review new Codex/DTC-MAIN scope. Explicit no-launch gate until Stage I terminal and new owner authorization.
- [BASELINE_COVERAGE_GATE.tsv](BASELINE_COVERAGE_GATE.tsv): 35 unmodified frozen input SHA identities, all relevant original acceptance states and future controls not registered.
- [ANALYSIS_AND_DECISION_RULES.md](ANALYSIS_AND_DECISION_RULES.md): paired comparison mathematics, fair configuration and predeclared combination decision gates.
- [WORKLOAD_PHASE_HYPOTHESES.tsv](WORKLOAD_PHASE_HYPOTHESES.tsv): source-anchored per-phase testable hypotheses and evidence caveats.
- [VALIDATION.json](VALIDATION.json): deterministic checks against pinned upstream 35×10 and source status.

## Authority / scope

- DTC Stage I [accepted source review package](https://github.com/swayhrl/accel-sim-framework/tree/c3e3bef274568abc058643c96f9c6277941f770b/docs/dtc_l1/review_packs/DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_V1/current_closeout_chatgpt_review_20261103_v1).
- Public [Workload Atlas V1R1](https://github.com/swayhrl/accel-sim-framework/blob/47a097aad4406893a07f8d230e1e0a850609bf39/docs/workload_atlas/README.md).
- Stage I Core `9eedb3131937748f0492fa83aad37d3691118d70`; Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`; simulator binary SHA256 `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`; DRAM850MHz, L2 10MiB, clocks1410/1410/1410/850MHz.
- Legacy 44 rows, accepted AG7/AG8 evidence, seven unresolved, previous EP and original-author attribution preserved. English v0.23 remains unchanged.

**NO reset/restart of DTC-MAIN, no new native simulator, capture, branch takeover, owner/ready/controller/budget mutation, model migration or existing source rewrite in this preparatory GitHub publication.**
