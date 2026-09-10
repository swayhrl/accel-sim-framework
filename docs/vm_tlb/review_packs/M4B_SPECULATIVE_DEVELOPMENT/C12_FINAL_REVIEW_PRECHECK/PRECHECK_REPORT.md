# C12 Final Review Precheck

Source C12 branch at precheck time: `hrl/vm-m4b-speculative-v0`

Source commit: `269c274712f4eeaee15d304033a9e6d61b5b3206` (`checkpoint 07`)

Status at source commit: `20/22 terminal PASS`; remaining Prefill F1 and Prefill F8-Lseg20 are not yet final and are excluded from any terminal review conclusion.

This precheck is read-only and does not modify C12 execution or evidence.

## 1. Gate status that can already be reviewed

### Gate A — input / execution identity: PRELIMINARY PASS for existing terminal arms

Frozen identity remains:

- Framework functional/config anchor: `d64408a97d76a320a6d49468653d416e33677af8`
- Core: `57bb71ecd015b6ec0ab32e45b0815e5beaf69172`
- binary SHA-256: `2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`
- Prefill trace SHA: `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f`
- Decode trace SHA: `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`
- Prefill registration SHA: `6ae0e18cc3bba29871002c4ff1877052489740163424723a845ead45c4a5f4b0`
- Decode registration SHA: `3dc77c1f348028ba7b8abfef3dc6c4cffa0c9678f003bc23bdc9158d62762b48`

Checkpoint 07 explicitly states the identity did not change and newly closed Prefill F8-L5 / F7-L20 use the same frozen identity.

Final review still needs a 22-row machine-readable provenance check rather than relying only on the checkpoint narrative.

### Gate B — F0 baseline: PRELIMINARY PASS

Both ROI F0 arms are terminal PASS and are the only legal speedup baseline for C12.

Final review must re-check:

- exit 0;
- exact 692/740 kernel markers;
- exact 692/740 telemetry records;
- object conservation PASS;
- PTE conservation PASS;
- raw-log SHA and `/usr/bin/time -v` provenance.

### Gate C — 22/22 terminal: OPEN

Current source commit is 20/22. Final acceptance cannot be issued until all 22 primary points are PASS.

### Gate D — arm-specific correctness: PRELIMINARY PARTIAL PASS

Existing terminal F1/F2/F5/F7/F8/F9 points have arm-specific telemetry fields and charged-bit identities in `ARM_RESULTS.tsv`. F7-L20 parser-only late-discard issue is documented as a C9 HIT_FIRST accounting correction, not a simulator rerun.

Final review must specifically re-check:

- both ROI F1 G96 geometry / `REFERENCE_APPROX_SUBENTRY_16`;
- both ROI F5 physical PWC120 geometry and payload-vs-arm budget accounting;
- F7 N=8, 35 replicas, exact320 remainder, Lseg 5/10/20;
- F8 N=8 + G32, Lseg 5/10/20, both labels preserved;
- F9 exact656 comparator identity.

### Gate E — fairness: PRELIMINARY PASS for existing terminal arms

Current result rows show common same-ROI trace / registration / binary / Core / Framework identities. This is the central fairness property and must remain unchanged when the last two rows close.

Final review should machine-check that the only differences among arms are the frozen arm configs and charged-state allocation.

### Gate F — result completeness: NEEDS FINAL AUDIT

Important: the acceptance matrix requires more than the compact columns visible in `ARM_RESULTS.tsv`, including MSHR high-watermark/lifetime and walker/PWQ evidence. The compact result schema does not expose every one of those as dedicated columns.

Final review must therefore not infer completeness from `ARM_RESULTS.tsv` alone. It must point to the raw/sidecar or structured summaries that carry each required field, or explicitly mark a requirement as unavailable and decide whether that violates Gate F.

### Gate G — required comparisons: CAN BE PRECOMPUTED NOW

Decode1 is already 11/11 terminal, so all Decode comparisons can be independently recomputed now.

Prefill comparisons that do not need F1 or F8-L20 can also be recomputed now.

Final review must independently recompute rather than trust only stored `speedup_vs_f0`:

- F1 vs F2;
- F5 vs F0;
- F7-L10 vs F0;
- F7 L5/L10/L20;
- F8-L10 vs F9;
- F8-L10 vs F1;
- F8 L5/L10/L20;
- Prefill vs Decode mechanism sensitivity.

### Gate H — interpretation boundary: NEEDS SCIENTIFIC REVIEW

Already visible signals that require careful wording:

- large reductions in translation slow-path counters do not necessarily translate into proportional full-ROI speedup;
- Segment shows strong Lseg sensitivity;
- Sub-entry-only and physical-PWC gains are small on Decode in current full-ROI results;
- F8 may add little beyond F7 at matched Lseg in currently observed points;
- Cache/object behavior can explain context but cannot be promoted to causal proof without counterfactual cache experiments.

Final report must separate `MEASURED_FULL_ROI_FACT`, `SUPPORTED_MECHANISM_SIGNAL`, and `UNRESOLVED`.

### Gate I — engineering / evidence management: PRELIMINARY PASS, one final consistency action recommended

Failure/retry audit records parser-only corrections, launcher/scheduler issues, resource observations and no-identity-change handling.

However, because multiple arms were parsed at different moments while the parser evolved, the final review should perform a **canonical parser convergence audit**: run the final parser version over all 22 immutable raw logs and generate one normalized validation/results table. This must be parser-only; no simulator replay. The old per-arm parser hashes remain preserved as history.

This is strongly recommended before final acceptance.

## 2. Highest-priority pre-final checks

1. **Canonical parser convergence** — verify every currently terminal raw log can be re-parsed by the final parser with identical core metrics/status; record any intentional semantic differences such as C9 HIT_FIRST late-discard handling.
2. **20-arm provenance matrix** — exact match of Framework/Core/binary/trace/registration and expected arm config hash.
3. **Marker / telemetry / conservation sweep** — independently count PASS invariants for all 20 terminal arms.
4. **Fair-budget audit** — compare charged bits and geometry against the frozen C11 arm matrix, including F5 payload-vs-total-arm accounting.
5. **Independent speedup recomputation** — calculate cycles-based speedups from raw terminal values, never A/C4 baselines.
6. **Mechanism sanity** — ensure Segment hits/suppressed path, Sub-entry hits/misses and PWC counters appear only where legal and satisfy conservation/accounting.
7. **Gate-F inventory** — map every required acceptance metric to an actual artifact; do not silently treat absent compact columns as zero.
8. **Finalizer output checklist** — prepare expected file list and fail final acceptance if required final tables are missing or internally inconsistent.

## 3. Items that must wait for 22/22

Only these parts fundamentally require the last two arms:

- Gate C final terminal verdict;
- Prefill F1 vs F2 and F8-L20 latency point completion;
- full 22-row canonical provenance / parser audit;
- final Lseg sensitivity table including Prefill F8-L20;
- final paper-facing ranking/summary;
- final status `C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`.

Everything else can and should be reviewed before completion.

## 4. Precheck disposition

Current disposition:

`C12_FINAL_REVIEW_PRECHECK_IN_PROGRESS_WAITING_22_TERMINAL`

No evidence at source commit 269c2747 requires invalidating existing 20 PASS arms. The two items requiring the most attention at final review are:

1. canonical parser convergence across all immutable raw logs;
2. explicit Gate-F coverage for required metrics that are not represented as dedicated `ARM_RESULTS.tsv` columns.
