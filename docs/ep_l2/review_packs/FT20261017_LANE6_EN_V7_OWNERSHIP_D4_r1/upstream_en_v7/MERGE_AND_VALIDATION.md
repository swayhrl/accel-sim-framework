# EP-L2 EN-v7 Ownership Story — Merge guide and verification boundaries

Scope: standalone editorial draft, separate from Lane6, not an authorized scientific publication and not a verified PDF. User asked to elevate research significance and write a paper, not a mechanical checklist. The manuscript source in `EP_L2_EN_v7_ownership_candidate.tex` was made by exact-boundary rewrites of Lane6's EN-v6-r21 at `606d54610c2800ff4d8cf9178b23bc35cb2eff3d`; this did not replace the original file.

## What actually changed

- Title: from generic storage optimization to **tag-residency versus dirty-data lifetime**.
- Abstract and Introduction: chronological resource-lifetime mismatch → relocation tax → ownership-transfer insight → fixed-budget difficulty → actual quantitative result. No improvement of +0.160% is promoted into significant speedup.
- Design: mechanism now describes actual `tag_array::bind_ft_replacement` and `tag_array::probe` reuse of the held victim on a pending request, plus `ft_access` reservation, `ft_rollback`, lower acceptance and WAD completion. This replaces the previously hypothetical 'preserve OR rollback' phrasing with source-grounded behavior.
- Reader-facing organization: mechanism section titles emphasize ownership, independent retirement and cost; Methods compresses internal Lane/V2/receipt administration; Results and Conclusion distinguish fewer bank/copy operations from execution improvement.
- Figure 4 progress dashboard removed; H0/Q4/D4 actual settings now presented in a small condition table (not fabricated downstream performance). No new r19 cycles are inserted.
- Fig. 1 caption emphasizes the physical ownership transition; original H0 figures 2/3 and references remain linked by relative path. The unused placeholder `MEASUREMENTS PENDING` macro is removed.
- Related Work keeps VWQ, last-write prediction, DBI and resource sharing; no 'first decoupling' statement.

## Exact reproducibility and scientific boundaries

**Original frozen H0 result must stay:** five full nonatomic pairs (SAD, vectorAdd, CFD, Convolution, FWT), B/U geomean `1.0016002037656606x`, CFD negative, other pairs retained; same verified Core `7b8e6ac70b8fe0f1bd37efca11acb5284938825d`, producing Framework `9bd17f9db3e8cbbc3fdad7283d1e292918546fd5`, binary `23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee`.

**No additional physical claim:** no RTL/STA/power result, no numeric SASS-output verification; source-level handle counts not net PPA; simultaneous dynamic bypass + TVD/RO unqualified; static `1024/112/32` equal-total baseline not implemented; r19 diagnosis still evolving. 0.160% by itself cannot establish a worthwhile hardware performance/energy tradeoff.

**Evolving r19:** Lane5 already independently accepted D4 Convolution B16=267521/U=268544 (U 1023 cycles slower), per a separate live snapshot, but this first D4 condition is not inserted in the frozen H0 rewrite until Lane6 applies its native/science acceptance process. Later FWT/Q4 results may change the discussion. Do not omit any negative points.

## How Lane6 should use this

1. In its **original** branch/worktree, fetch newest current Lane5 V2 scientific authority and the newest Lane6 result intake; preserve all previously published H0 and r19 assets.
2. Copy this editable candidate into a NEW Lane6 revision while preserving `figures/fig2_results.pdf`, `figures/fig3_pressure.pdf` and the accurate existing `references_verified.bib`; build with real assets. This standalone editorial branch contains LaTeX source only and is not self-contained for figures or references.
3. Verify each sentence in the updated replacement algorithm against the producing Core commit, especially pending request/victim binding, physical bank service, rollback and the two separate lower retirements. No TVD/RO results may be absorbed into WB-only numbers.
4. Verify input-workload table: add actual data scales and exact benchmark/trace scopes from accepted manifests; don't infer input size merely from workload names. Keep stronger equal-total static and concrete area/timing items flagged as unmeasured, not as achievements.
5. Recompile with `pdflatex → bibtex → pdflatex ×2`, verify actual 4 technical + 1 reference page if possible and inspect rendered page images at readable size. Do not reduce IEEE margins/fonts to force it. Current editorial copy was **not** compiled and lacks page-render proof.
6. Check all `\label{}` / `\ref{}` links, BibTeX keys, live figure-data provenance, complete result ratios and no progress dashboard. If the recent r19 accepted data have arrived, merge verified sensitivity findings as a separate experiment group (never overwrite H0).
7. Publish revised paper and exact evidence map on Lane6 branch; preserve EN-v6-r21 and this editorial candidate as separate snapshots; new scientific effects or PPA claims need real evidence.

## Validation already performed on the standalone editorial text

- Readback of complete source through GitHub; matching original H0 `1.001600` retained; figures 1/2/3 source references present; new `tab:headroom` present; old `fig:controls` progress reference absent.
- All six declared `\label` identifiers in the candidate have no unresolved local `\ref` references; 3 figure, 2 table, 1 equation environments have matched begin/end tags.
- There is no local LaTeX compilation or PDF visual audit for this candidate. Layout cannot be claimed to be 4+1 until Lane6 builds it.

**Decision principle:** The value of the revised narrative is that the reader understands the fundamental problem before seeing a single counter. Whether dynamic allocation beats strong static alternatives is still a scientific question and must be answered experimentally.