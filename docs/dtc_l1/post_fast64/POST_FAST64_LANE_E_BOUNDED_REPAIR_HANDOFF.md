# POST-FAST64 Lane E bounded repair handoff

## 0. Purpose and current status

Repair the artifact/QA layer of Lane E without changing the accepted science, rerunning simulation, or modifying FAST64/Core.

Base reviewed commit:

- branch: `hrl/decoupled-l1-fast64-post-analysis-v0`
- science package commit: `f376786206fabb75d9002c64cfa8582cc2e71461`
- frozen FAST64: `18a68dcccd795f1b6cda75504e9450d00c9cee02`
- pinned Lane A: `c1774a452e244d431c215010b1039e9d3e074f2a`
- pinned Lane B: `757b8cbf2c536b04f8a6ef4db847af04f337378d`
- pinned Lane C: `18800873478576309b08b538974c3872fc2cb6df`
- pinned Lane D experiment history: `d33d236c0338d7ab4420c6ceceae3d5733e0a3ad`
- selected Lane D revision: `dfdf09850f133927d98aba51accd8ef082a4b6b0`

Until the repair below is actually executed and all acceptance checks pass, treat the state as:

`LANE_E_SCIENCE_PASS_ARTIFACT_QA_REPAIR_REQUIRED`

Do **not** use `POST_FAST64_PAPER_ANALYSIS_AND_MECHANISM_EXPLORATION_READY_FOR_REVIEW` merely because the current generated checklist/report says PASS.

## 1. Hard boundaries

This is one bounded Lane-E repair only.

### Must not do

- Do not launch any simulator, trace capture, GPU job, or new architectural experiment.
- Do not modify FAST64 accepted evidence, any pinned Lane A/B/C/D source commit, Core, observer scientific semantics, simulator configuration, or accepted primary numerical results.
- Do not recompute primary results from raw SIM_HOST directories.
- Do not invent new causal claims.
- Do not silently replace source denominators, memberships, deadlock markers, or qualified OO duplicate evidence.
- Do not broaden this into a new research lane.

### Allowed changes

Keep changes limited to the Lane-E builder/tests/QA records and regenerated final review package, principally:

- `util/dtc_l1/build_post_fast64_lane_e.py`
- a small executable Lane-E QA/self-test driver under `util/dtc_l1/` if useful
- explicit negative-fixture/visual-review records under `docs/dtc_l1/post_fast64/lane_e/` if needed
- `docs/dtc_l1/post_fast64/review_packs/POST_FAST64_FINAL/**` regenerated from the repaired flow
- this handoff and narrowly related Lane-E documentation

Any additional file outside this scope requires a concrete reason in the final report.

## 2. Confirmed defects in the current artifact layer

These are not speculative; they are visible in the current builder/package.

1. **F07 is indexed twice.** `build_figures()` calls `add("F07", ...)` twice. The first call also reuses the stale `series` variable left by the F04-F06 sensitivity loop, then the second call overwrites the F07 assets. The final asset is the ten-panel version, but `FIGURE_INDEX.{tsv,md}` contains duplicate F07 entries. Remove the obsolete first F07 path; require exactly unique F01-F09 IDs.
2. **Negative fixtures are declarations, not executed tests.** `build_validation_report()` writes six `negative fixture: ... | PASS` rows without mutating an input/output and verifying rejection.
3. **Visual QA is self-asserted by code.** `visual_qa()` only opens PNGs/checks dimensions/signatures, then writes prose claiming actual bars/labels were inspected. Builder code must never claim a human/agent visual inspection it did not perform.
4. **Determinism report is static prose.** `final_docs()` writes `DETERMINISM_COMPARISON.md` saying two isolated builds and `diff -qr` were executed, but no such execution exists in the code path.
5. **Checklist is circular.** `build_all()` writes the checklist `IN_PROGRESS`, builds artifacts, then unconditionally rewrites every item `PASS`; `validate_package()` subsequently accepts `all planned_status == PASS`. PASS must be produced from check results/evidence, never assumed and then used to validate itself.
6. **Coverage is hard-coded.** `build_coverage()` writes expected=observed constant strings such as 12/36/18 and `29 launches + 1 exact Btree reuse`, rather than computing observed values from the pinned data.
7. **Sensitivity validation is incomplete.** Current checks cover selected physical-boundary cases but do not exhaustively validate accepted membership/row kinds/plot membership for all logical/physical/PIB sensitivity tables from the pinned sources.
8. **12-workload explanations lost most Lane-A evidence.** The current final table repeats one generic interpretation for all 12 workloads even though Lane A already provides performance behavior, pressure signature, HOL, OO retire/reclaim, traffic contrast, accepted label/caveat, etc. Lane C/D adds exact duplicate evidence and D4/D6 adds qualified mechanism evidence.
9. **Claim/evidence register is too small.** It has only six rows and does not cover the paper-facing result/mechanism claims or the D6 mechanism-arrow boundaries with sufficient granularity.
10. **Build provenance is incomplete.** The builder depends on Python + Pillow and also uses DejaVu font files when present, but the final package does not record Python/Pillow/builder provenance. Reproducibility claims must state the real toolchain.

## 3. Required repair tasks and acceptance criteria

### R1 — Fix F07 and figure identity

- Delete the obsolete first F07 generation path; do not retain a hidden/stale-series F07.
- Generate the intended ten-panel physical-pool observer F07 once.
- Assert `FIGURE_INDEX.tsv` contains exactly nine rows with ordered unique IDs `F01` ... `F09`.
- Assert `FIGURE_INDEX.md` contains exactly one heading for each F01-F09.
- Assert each ID has SVG/PDF/PNG assets and source mapping.

### R2 — Execute real negative fixtures

Implement an executable self-test (standard-library `unittest` or an equally small explicit runner is preferred; do not introduce a large test dependency just for this repair). Each fixture must create a temporary copy/mutation, invoke the real validator, and PASS only if the validator rejects the corruption.

At minimum execute these six fixtures:

1. wrong FAST12 membership/order;
2. observer/non-primary contamination of the primary/GM set;
3. BICG/GESUMMV 16.5-KiB physical boundary changed from NONNUMERIC to numeric;
4. OO duplicate proxy/unqualified source substituted for the qualified exact D5 metric;
5. invented 40-KiB D4 observer point / wrong exact D4 capacity membership;
6. lower-request payload relabeled as DRAM/total-link/total-memory traffic.

For every fixture record: fixture ID, exact mutation, validator invoked, expected failure, observed exit/result, and PASS/FAIL. `E_VALIDATION_REPORT.md` must be generated from these actual results, not from a literal PASS list.

### R3 — Separate machine figure checks from real visual review

- Machine checks may verify file existence, signatures, dimensions, XML readability, etc. Put those in a machine-QA artifact if useful.
- The builder must **not** write text such as “inspected actual bars/lines/cells” by itself.
- Codex must actually open/render the generated F01-F09 PNGs (a contact sheet plus individual figures where needed is acceptable) and inspect: clipping, overlap, unreadable labels, wrong units, wrong legend/series identity, scope notes, and scientific caption/plot consistency.
- Record the review per figure in an explicit review record with findings and any fixes. If a figure was repaired, record what changed and inspect the regenerated figure again.
- The final `E_VISUAL_QA.md` must derive from that explicit review record. Missing review record => E2.2 is NOT_RUN/FAIL, never PASS.

For reproducible packaging, it is acceptable to treat the completed visual-review record as a frozen Lane-E QA input after the actual inspection has occurred.

### R4 — Make determinism a real executable test

Implement a real QA command/function that:

1. builds from the same committed compact inputs into two isolated directories;
2. validates both builds;
3. recursively compares file sets and SHA-256/bytes;
4. reports exact file count and mismatches;
5. after the QA/visual record is frozen, regenerates the formal final package and verifies the intended final-package determinism scope.

`rebuild_reports/DETERMINISM_COMPARISON.md` must be generated from measured comparison results. It must not be static prose claiming commands ran when they did not.

Avoid circularity from the determinism report itself. A clean solution is a two-phase deterministic orchestration: compare deterministic build cores first, generate the comparison record from those actual results, include the same frozen QA records in the formal packages, then compare the formal package trees. If a very small explicitly named post-comparison audit file must be excluded, document exactly why and separately hash/validate it; do not quietly weaken the claim.

### R5 — Remove checklist self-certification

- Replace `build_checklist(..., "PASS")` with a result map populated only by executed checks.
- Every E0.1-E2.4 row must have `status`, `evidence_path`, and preferably `check_command/check_id` or equivalent lineage.
- PASS only when the corresponding validation actually ran and succeeded.
- On missing evidence, use NOT_RUN/FAIL, not PASS.
- `validate_package()` must validate underlying facts/evidence; it must not accept the package because the checklist says PASS.
- Final READY_FOR_REVIEW status may be emitted only after all mandatory checks are independently successful.

### R6 — Make coverage and sensitivity checks data-driven

Compute observed coverage from source/output tables rather than embedding observed constants.

Required checks include at least:

- exact ordered FAST12 membership;
- exact 12 × {Base,IO,OO} primary cell identity / no diagnostic rows in primary GM;
- primary GM recomputation from integer cycles;
- D4 exact cartesian membership `{BICG,GESUMMV,Btree} × {24,32,48 KiB} × {IO,OO}` = 18 cells, derived from the rows;
- observer denominator field/scope remains `observer_sample_sm_cycles`, never substituted with `64*global_cycles`;
- D4 launch/reuse accounting computed from the pinned D7/source index rather than a hard-coded observed phrase;
- D5 exact 12 IO/OO pairs, exact qualified OO evidence status, and 7 lower / 3 higher / 2 both-zero classification recomputed from integer/ratio fields;
- logical/physical/PIB sensitivity tables checked against accepted source membership and row-kind semantics;
- physical 16.5-KiB: BICG/GESUMMV nonnumeric boundary markers and Btree numeric accepted points preserved exactly;
- plotted sensitivity numeric points must equal accepted numeric membership; boundary markers must not silently enter numeric curves.

Generate `E_COVERAGE_AND_IDENTITY.tsv` from these calculations, including expected source, observed value, and check status.

### R7 — Rebuild the 12-workload explanations from Lane A + Lane C/D

Use the richer Lane-A table
`docs/dtc_l1/post_fast64/generated/paper_workload_explanations.tsv`
from pinned Lane A, then integrate qualified Lane C/D evidence rather than replacing the interpretation with one generic sentence.

For each of the exact 12 workloads preserve or derive fields covering:

- primary IO/OO performance behavior and exact speedups;
- Lane-A Base pressure signature + nonexclusive-counter boundary;
- IO HOL evidence;
- OO retire/reclaim evidence;
- traffic contrast;
- Lane-A measured interpretation + caveat/alternative;
- exact IO/OO duplicate counts/shares from Lane C/D, plus direction `OO_LOWER`, `OO_HIGHER`, or `BOTH_ZERO`;
- D4 physical-pool sensitivity only for BICG/GESUMMV/Btree; explicitly `NOT_COVERED_BY_D4` for the other nine;
- D6/source-proven mechanism statement where actually applicable;
- strongest paper-safe interpretation;
- explicit forbidden overclaim / caveat;
- source lineage.

Cross-check the duplicate classification: 7 OO-lower, 3 OO-higher, 2 both-zero. Preserve the important absolute-scale nuance (for example Btree OO/IO ratio can be high while both duplicate shares remain tiny).

Do not blindly copy a Lane-A label if it conflicts with the selected reconciliation. For example, retain raw historical labels in a lineage field if useful, but paper-facing wording must preserve the reviewed fact that Gaussian is an approximately 1.108x modest beneficiary, not “no benefit.”

### R8 — Expand the claim/evidence register

Expand `E_CLAIM_EVIDENCE_REGISTER.tsv` to cover the actual paper-facing claims and mechanism boundaries, not just six summary rows.

Recommended schema:

`claim_id, claim_text, evidence_class, source_artifact, source_key_or_rows, supported_scope, forbidden_overclaim`

Cover at least:

- exact primary IO/OO GM and FAST12-only scope;
- IO regressions for ATAX/BICG/GESUMMV;
- Gaussian modest-benefit wording;
- Base pressure counters are nonexclusive exposure counters;
- IO HOL metric/formula/scope;
- OO out-of-order-retire metric/formula/scope;
- logical/physical/PIB sensitivity claims and no-universal-optimum boundary;
- physical 16.5-KiB numeric/nonnumeric distinction;
- D4 controlled capacity -> end-to-end sensitivity;
- capacity -> pool-full exposure;
- active-SM-time no-free versus per-instruction burden distinction;
- occupancy/pool-full -> inflight (measured correlation only);
- inflight -> L2 pressure (measured correlation only);
- L2 pressure -> alloc-to-ready lifetime (measured correlation only);
- lifetime -> pending Tag eviction (insufficient);
- pending Tag eviction -> duplicate lower request (source-proven semantics);
- duplicate traffic -> performance (not supported);
- OO pending eviction -> deferred lifetime and deferred lifetime -> final reclaim (source-proven lifecycle semantics);
- final reclaim/concurrency -> performance boundaries;
- universal larger-pool -> downstream-pressure-transfer is not supported;
- L2-dominant + duplicate-secondary-feedback statement remains insufficient;
- D5 7/3/2 duplicate distribution; OO does not universally remove duplicates;
- `duplicate * 128 B` is lower-request payload only, never DRAM/total-link/total-memory traffic or recoverable performance;
- D4 scope limited to BICG/GESUMMV/Btree;
- diagnostic observer data never enter primary FAST12 GM;
- Lane E repair performs zero simulation and zero scientific changes.

Add an executable claim audit that verifies required claim IDs exist and that paper/figure/workload artifacts reference only existing registered claim IDs or an equivalent explicit mapping. The audit need not pretend to perform NLP; it must provide deterministic traceability.

### R9 — Record actual build provenance

Add a deterministic provenance artifact (TSV/MD) containing at least:

- Python implementation + version;
- Pillow version;
- Lane-E builder repository path;
- builder Git blob SHA and/or SHA-256;
- selected input manifest SHA-256;
- platform information needed to interpret reproducibility;
- because raster output depends on font rendering, record whether DejaVuSans/DejaVuSans-Bold were used and their SHA-256 when present, or the exact fallback path/state.

Update `REPRODUCE.md` to name Pillow as a real dependency. Do not describe the builder as standard-library-only.

### R10 — Regenerate the formal final package, still with zero simulation

After R1-R9 succeed:

- regenerate `POST_FAST64_FINAL` from the pinned compact inputs and explicit QA records;
- run the repaired validator, negative fixtures, visual inspection, claim audit, coverage/sensitivity audit, and determinism test;
- verify input hashes/pinned commits remain unchanged;
- verify no FAST64/Core/scientific-source file changed;
- verify Git diff contains only bounded Lane-E repair artifacts;
- update `LANE_E_FINAL.md` only from real results;
- set final status to `POST_FAST64_PAPER_ANALYSIS_AND_MECHANISM_EXPLORATION_READY_FOR_REVIEW` only if every mandatory check is truly PASS.

If a required item cannot be made true, stop with the strongest truthful non-ready status and explain the blocker. Never manufacture PASS to finish the lane.

## 4. Expected commands/evidence in the closeout

Codex may improve command names, but the final report must show real invocations equivalent to:

```bash
# build canonical package from committed compact inputs
python3 util/dtc_l1/build_post_fast64_lane_e.py --build \
  --inputs docs/dtc_l1/post_fast64/lane_e/inputs \
  --output <isolated-output>

# package validation
python3 util/dtc_l1/build_post_fast64_lane_e.py --validate \
  --inputs docs/dtc_l1/post_fast64/lane_e/inputs \
  --output <isolated-output>

# executable negative/QA suite
python3 <lane-e-qa-runner> ...
```

The closeout must include:

- branch and start/end commit;
- exact modified files;
- exact commands run and exit status;
- negative-fixture matrix with observed rejection;
- visual-review summary for F01-F09 and any repairs;
- determinism comparison counts/hashes/mismatches;
- coverage/sensitivity audit result;
- claim-audit result;
- provenance summary;
- confirmation of zero simulation and zero scientific-source/Core changes;
- final status.

## 5. Problem-solving rule for Goal mode

Work autonomously through ordinary implementation/test failures. When a check fails, inspect the actual data/code, diagnose it, make the smallest scope-correct repair, and rerun the relevant checks. Try reasonable alternatives rather than stopping at the first obstacle.

Only stop without completing the repair when continuing would require crossing a hard boundary above, inventing scientific evidence, launching new simulation, or making an irreversible/destructive change. In that case preserve the work, report the exact blocker and evidence, and leave the status non-ready.
