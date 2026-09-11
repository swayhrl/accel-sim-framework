# C13 minimal diagnostics — acceptance matrix

## Gate A — Reference provenance

Before any simulator arm starts:

- Framework diagnostic branch descends from C12 closeout `a268aba0d01310294074ded5bb8017e2092394c0`;
- C12 reference Core = `57bb71ecd015b6ec0ab32e45b0815e5beaf69172`;
- C12 linked binary SHA-256 = `2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`;
- Prefill trace-list = 692 entries / SHA `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f`;
- Decode1 trace-list = 740 entries / SHA `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`;
- C12 registrations and `MODELED_DRIVER_PA / C5_MODELED_PA_HIGH_UNUSED_BIT_V1` contract are available;
- Operator-aware reference map comes from accepted commit `8801f2e9fea4e0df1d79853a5e4440c4da463486` and is used only for post-run attribution.

Any unexplained reference mismatch blocks launch until resolved.

## Gate B — Matrix closure

Primary C13 matrix is exactly the 7 `PRIMARY` rows in `C13_DIAGNOSTIC_EXPERIMENT_MATRIX.tsv`.

Conditional rows are executed if and only if selective eligibility requires a new Core/binary.

No primary point may be omitted because an earlier result appears decisive.

No extra architecture point may be silently promoted into the primary matrix.

## Gate C — Config-only identity

`C13-LAT-P8`, `C13-LAT-P9`, `C13-LAT-D11`, `C13-CAP-P320`, and `C13-CAP-P768S10` must use the exact C12 Core and linked binary.

Within each ROI:

- trace-list unchanged;
- modeled PA mapping unchanged;
- registration semantics unchanged except explicit Segment enable/geometry fields already supported by the frozen system;
- only the experiment-matrix fields may differ.

Capacity diagnostic arms are intentionally non-equal-budget and must carry label `DIAGNOSTIC_NON_EQUAL_BUDGET` in every result/report.

## Gate D — Selective eligibility correctness

The selective policy must satisfy `C13_SELECTIVE_SEGMENT_CONTRACT.md`.

Hard requirements:

- selector is parameter/object-range based, never kernel-index based;
- excluded parameter/range is derived from immutable sidecar;
- common VA→modeled-PPN mapping is unchanged;
- conventional PTW returns the same modeled PPN for excluded pages;
- non-target Weight pages retain baseline Segment eligibility;
- tied embedding/output Weight, if present, is reported as a shared object-range exclusion rather than falsely split by semantic use.

If new binary is required:

- default-OFF / all-eligible control must be run for both Prefill and Decode1;
- selective speedup is computed only against same-ROI same-new-binary control;
- new Core commit and binary SHA are frozen and reported;
- C12 historical results remain reference evidence but are not mixed into cross-binary speedup.

## Gate E — Per-arm terminal correctness

Every new full-ROI arm must have:

1. simulator exit = 0;
2. exact expected kernel markers: Prefill 692 / Decode1 740;
3. telemetry records = expected kernels;
4. terminal quiescence / exact-once PASS;
5. PTE request/response conservation PASS;
6. object attribution conservation PASS;
7. Segment/PWC/TLB arm-specific invariants PASS;
8. trace/config/registration-or-eligibility/binary provenance recorded;
9. immutable raw log + `/usr/bin/time -v` sidecar;
10. canonical parser output with no silently defaulted missing critical field.

Parser-only fixes may reparse immutable logs without replay; parser version/hash must be recorded.

## Gate F — H1 selective comparison

For each ROI, candidate and valid comparator must have same binary identity.

Required outputs:

- cycles / IPC / delta;
- Segment attempts/hits/L2 suppressions;
- L2 TLB misses;
- translation walks;
- PTE requests / PTE DRAM;
- requester translation latency;
- operator-level cycles for Embedding/Output, FFN, Attention Projection;
- kernel 691 exact cycles for Prefill;
- target-range exclusion coverage and non-target preservation audit.

A selective win is not enough if common PA correctness or non-target eligibility is violated.

## Gate G — H2 capacity factorial

All four Prefill factorial points A/B/C/D must be present, with A and D explicitly linked to immutable C12 rows.

Required measured contrasts:

- B-A;
- C-A;
- D-B;
- D-C;
- interaction `(D-B) - (C-A)`.

Required mechanism counters:

- L2 TLB misses;
- L2 port stalls;
- walks;
- PTE requests / PTE DRAM;
- requester latency;
- Segment activity when enabled;
- per-operator and kernel-691 cycles.

The interaction is labeled `DIAGNOSTIC_INTERACTION_ONLY`; do not call it a general causal law.

## Gate H — H3 fine latency measurements

New L8/L9/L11 arms must preserve F7 geometry except Lseg.

Combine with existing C12 F7 L5/L10/L20 only after confirming identical frozen execution identity.

Final report must use new **measured** values first. Old Deep Dive 8.75/10.83 values are only prior empirical interpolation anchors.

Explicitly report whether:

- Prefill L8 is positive/negative vs F0;
- Prefill L9 is positive/negative vs F0;
- Decode L11 is positive/negative vs F0;
- the old interpolation is supported, shifted, or contradicted.

No out-of-range extrapolation.

## Gate I — Post-run operator attribution

Use accepted frozen `KERNEL_OPERATOR_MAP.tsv` only after proving compute-list identity.

Additive per-kernel cycle sums must equal each arm full-ROI total.

Any per-kernel cumulative `vm_*` attribution must retain the hardened continuity/monotonicity/delta-to-terminal rules from the accepted Operator-aware parser.

Units remain distinct:

- lane refs;
- cache transactions;
- TLB accesses/misses;
- PTW/walks;
- PTE requests;
- cycles.

## Gate J — Evidence and failure discipline

- raw logs never overwritten;
- failed attempts isolated;
- no `git add .` / `git add -A`;
- no hidden mid-run change to primary matrix;
- resource/OOM failure is retriable, not an architecture blocker;
- semantic identity change requires same-identity controls for affected comparisons;
- C13 findings never rewrite C12 formal review-pack truth.

## Final success

All required gates pass and all 7 primary points plus any mandatory conditional controls are terminal PASS:

`C13_MINIMAL_DIAGNOSTICS_COMPLETE_READY_FOR_REVIEW`

Otherwise, if a true architecture/provenance/correctness blocker remains after reasonable repair attempts:

`C13_MINIMAL_DIAGNOSTICS_HARD_BLOCKER_WITH_EVIDENCE`
