# Evidence conflicts and limits

**Evidence label: `SPECULATIVE_DIAGNOSTIC`**

No B8 statement is a full-workload, formal, or performance conclusion.

## Scope ledger

| ID | Evidence | Permitted support | Not supported |
|---|---|---|---|
| L1 | B7 B1 static/phase partials | Partial-prefix traffic mix, local sequentiality, and observed attribution. | Full phase comparison, full working-set union/reuse, or full population result. |
| L2 | B7 B2 smoke | Single-kernel configuration deltas and telemetry-path viability. | Continuous ROI throughput, stable occupancy, queues, or sensitivity. |
| L3 | B7 B2 object telemetry | Weight/UNKNOWN requester and PWC/PTE counts in smoke kernels. | Complete attribution or phase-wide causal attribution. |
| L4 | C4 bounded replay | Recorded sub-entry dynamic outcome and segment telemetry in three selected decode kernels. | Workload-wide sub-entry/segment result or prefill conclusion. |
| L5 | C7 static proxy/descriptor | Descriptor range coverage and selected-prefix static grouping. | Runtime classified coverage, post-L1 locality, physical counterfactuals, or all 740 kernels. |
| L6 | B7 coverage/resume accounting | Which B evidence classes are absent or partial. | Ranking from observed full-ROI payoff. |

## Conflicts and resolution

### Unequal B phase coverage

B prefill and decode mining cover different partial fractions (134/692 and 96/740). The observed exact-adjacent rates, decode 77.759% and prefill 47.567%, are not matched populations. C4 contains only three selected decode kernels. This can generate H1 but cannot confirm it. E07--E10 require matched, budgeted, signature-stratified B mining before a phase statement.

### PWC smoke is not a stable effect

B `b2-pwc-off/decode1` changed PWC hits/misses from 1/5 to 0/0, PTE requests from 7 to 8, and IPC by -1.0583% for one kernel. It is compatible with a PWC effect and with tiny-sample path behavior; most B2 smoke OFAT points are invariant. E01--E03 reproduce a finite ladder and E11 tests continuous decode. No direction is presumed.

### Static sibling grouping conflicts with bounded dynamic locality

C7's selected-prefix proxy has 62 Weight pages in 10 groups (83.871% static compression); the full descriptor projects 15,443 pages in 966 groups. C4 instead records post-L1 occupancy always 1/16, no existing-group fills, and no group evictions; standard and sub-entry finish at 34 accesses, 2 hits, and 32 misses. Static grouping is therefore not a benefit proof. Only C-owned E16 can falsify H4 with post-L1 observables.

### Segment counters are not physical savings

C4 has 512 segment hits only in kernel 1464, and its segment path has a different lookup count from standard/sub-entry. Suppression accounting is not a physical counterfactual. E17 is a candidate-versus-candidate discriminating run, not confirmation of saved translations, memory requests, or time.

### Descriptor coverage is not classified traffic coverage

C7's descriptor covers its declared Weight range exactly, while its 25-file proxy reports only 7.9601% Weight global lanes. B partial attribution is 79.060% UNKNOWN in prefill and 90.964% UNKNOWN in decode. Range coverage therefore does not show that relevant runtime traffic was identified. E09/E10 must retain map/version/boundary provenance and report Weight/KV/UNKNOWN mass. This remains `NEEDS_RUNTIME_EVIDENCE` for a Weight-targeted candidate.

### Conventional mechanisms are stronger alternatives than the candidate

B has smoke paths for PWC, L1/L2 TLB, MSHR, PWQ, and walkers; C has bounded candidate replay only. B3 runtime cache and B5 TLBxL2 grid have no real coverage. E01--E06 and E11--E15 give conventional PWC/TLB/page/PTW explanations an explicit opportunity to win, tie, or falsify the candidate narrative.

### Cross-window values are not poolable

B7 and C4/C7 use different framework/core/binary contexts. B8 uses separate evidence to pose shared questions but never combines counts, ratios, IPC, or deltas. Every experiment has an owner; C rows require C authorization.

### Missing is not zero

B7 has 0 `REAL_PASS`, 2 `REAL_PARTIAL`, 37 `SMOKE_ONLY`, 38 `PLANNED_ONLY`, 12 `STATIC_ONLY`, and 17 `MISSING` cells. An absent or planned metric is not a zero, no-difference, or negative result. B8 selects only measurements that resolve a named ambiguity.

## Later-reporting guardrails

- Report exact workload, continuous ROI status, kernel coverage, realized config, provenance, and evidence label.
- A null result needs a confidence limit or documented measurement sensitivity.
- Never split a stateful ROI into one simulator process per kernel.
- Preserve object-map version, range/boundary policy, and UNKNOWN accounting.
- Keep B and C result tables separate unless a future controlled study proves compatibility.
- Do not advance a candidate from `SPECULATIVE_DIAGNOSTIC` based on static proxy, smoke, opportunity analysis, or bounded replay.
