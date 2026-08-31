# EP-L2 Streaming-Reuse Prefinal — ChatGPT Review

Status: **PASS_FOR_SCIENTIFIC_DIRECTION; FIX_REQUIRED_BEFORE_FINAL_PROMOTION**

Reviewed checkpoint:

- Core runtime candidate: `ca3e7bc0b8f61b5d7c052bcda2a91955a1e5c919`
- Framework runtime candidate: `db1c90182fad02aacbd282b67ecdc57b8e4cc365`
- Prefinal publication branch head reviewed from `hrl/ep-l2-streaming-reuse-v0`
- Pack: `docs/ep_l2/review_packs/STREAMING_REUSE_PREFINAL_r1/`
- `scan`: intentionally excluded and still `RUNNING_PENDING_FINAL_DELTA`

Do not stop/restart the currently running scan solely because of this review.
Do not overwrite or mutate `STREAMING_REUSE_PREFINAL_r1/`; it is now an immutable checkpoint.

## 1. What passes now

### 1.1 Sector-aware scientific direction — PASS

The new split is scientifically useful and directly fixes the interpretation problem in Figure-1-r1:

- `cold_new_line_sector`: first sector touch while the line is unseen in request prestate;
- `spatial_new_sector`: first touch of a new sector in an already-seen line;
- `temporal_sector_reuse`: repeat of the exact 32-B sector identity.

The conservation and exact-sector temporal-reuse semantics are appropriate for the intended distinction between spatial streaming and true temporal reuse.

### 1.2 Key hypothesis is confirmed — PASS

The extension demonstrates that high 128-B line reuse can be almost entirely spatial rather than temporal.

Strong examples in the current completed set:

- `vectorAdd_4M`: line reuse fraction 0.75, sector temporal reuse fraction 0.0, spatial-new fraction 0.75, one-touch sector fraction 1.0.
- `BlackScholes`: line reuse fraction 0.75, sector temporal reuse fraction 0.0, spatial-new fraction 0.75, one-touch sector fraction 1.0.

Therefore both are clean streaming/spatial-only controls under the new metric.

### 1.3 Additional low-temporal-reuse candidates — PASS, selection remains provisional until screening expansion

Current selected additions are quantitatively defensible:

- `BlackScholes`: 0% temporal sector reuse;
- `mergeSort`: ~10.50% temporal sector reuse, ~90.27% one-touch sectors;
- `transpose`: ~15.79% temporal sector reuse, ~93.75% one-touch sectors.

No candidate is accepted merely because of its benchmark name.

### 1.4 Far temporal reuse is already visible in the original workload cohort — IMPORTANT POSITIVE RESULT

The new metric reveals a stronger result than the first Motivation figure could show.

Conditional on a true temporal-sector reuse event, the share with reuse distance `>1024` is approximately:

- `FWT_7_21`: 61.44%
- `convolutionSeparable`: 39.27%
- `dwt2d`: 23.25%
- `btree`: 19.03%
- `cfd_097k`: 18.01%
- `spmv`: 9.54%

Thus the final interpretation should distinguish at least:

1. spatial-only / streaming (`vectorAdd_4M`, `BlackScholes`);
2. low true temporal reuse (`dwt2d`, convolution, sad/spmv, mergeSort/transpose);
3. strong far temporal reuse when reuse exists (`FWT_7_21`, convolution; weaker secondary cases cfd/dwt2d/btree);
4. reuse-rich (`gemm`, btree/cfd under different mixes).

Do **not** state that no far-reuse behavior exists. The correct statement is only that no **additional screened candidate so far** met the strong-far criterion.

### 1.5 Preservation — PASS

The prefinal preservation manifest reports matching content-root SHA-256 values for both immutable historical roots:

- `MOTIVATION_FIGURES_r1/`
- `/workspace/results/ep_l2_motivation/`

and reports no rewrite of `hrl/ep-l2-motivation-v0`.

## 2. Required fixes before final promotion

### R1 — Expand screening to satisfy Gate M

Current `SCREENING_CANDIDATES.csv` contains only 10 attempted candidates, of which 8 are `COMPLETE_VALID`, one failed simulator, and one was stopped for nonformal resource closeout.

This does not satisfy the stated target of 12–16 candidates / broad suite diversity when the existing runnable trace inventory is not materially limiting.

While scan continues, screen at least 4–6 additional candidates on the **same frozen runtime candidate**, chosen from currently underrepresented suites/semantic families. Target final screening inventory:

- 12–16 attempted candidates;
- preferably >=12 valid rows if practical;
- >=4 suite/semantic families where runnable traces exist.

Prefer candidates with plausible streaming or long-range behavior, but choose from trace inventory and raw metrics rather than benchmark names. Suitable families to consider include currently runnable Parboil, PolyBench, Pannotia/graph, SHOC, or other non-CUDA-SDK/non-Rodinia roots already present in the trace pool.

After expansion, regenerate `SCREENING_CANDIDATES.csv`, add required `SCREENING_RANKING.csv` and `SCREENING_NOTES.md`, and re-run formal selection. `BlackScholes` is already a strong streaming control and should remain unless a correctness issue appears. `mergeSort` / `transpose` may remain or be replaced if the expanded pool yields a more distinct archetype or a genuinely strong additional far-reuse case.

### R2 — Figure 1 v2 currently fails Gate Q

Current `FIG1V2_L2_SECTOR_TEMPORAL_REUSE` only visualizes:

- cold/new-line sector fraction;
- spatial continuation fraction;
- true temporal-sector fraction.

It does **not** visualize the required reuse-distance distribution conditional on true temporal reuse.

Final Figure 1 v2 must expose both in the same paper-facing figure:

- **Panel A — amount/type of locality:** cold new-line + spatial continuation + true temporal reuse, normalized over all sector-reference events; annotate temporal fraction and/or one-touch sector fraction.
- **Panel B — conditional true temporal reuse distance:** stacked distance distribution for temporal reuse instances only.

For zero-temporal-reuse workloads (`vectorAdd_4M`, `BlackScholes`), Panel B must explicitly show `NO TEMPORAL REUSE` / `N/A`; do not normalize an empty denominator into a visually full bar.

The exact CSV may preserve all 11 bins. The plotted Panel B may merge adjacent bins for readability only if the mapping is explicit and the exact 11-bin CSV remains authoritative. In particular, the final figure must make `>1024` far-reuse mass visually apparent for `FWT_7_21` and `convolutionSeparable`.

Keep `FIG1S_LINE_VS_SECTOR_REUSE` as the supplemental direct line-vs-sector comparison.

### R3 — Harden final aggregation fail-close

Current `aggregate_streaming_reuse.py` checks count closure but does not yet fail closed on all final provenance requirements.

Before final pack generation, aggregation must validate at least:

- every sector manifest schema is `EPL2SRV1`;
- all formal rows use the intended Core SHA, Framework runtime SHA and config SHA;
- workload names and trace identities match the formal manifest;
- the paired `EPL2MOTV1` result/manifest belongs to the same run/provenance;
- no duplicate workload input;
- exact expected formal workload set is present (original 10 + final 2–3 additions);
- no missing/timeout row is silently omitted;
- sector classification and distance closure;
- original-10 Motivation compatibility checks required by Gate H.

Do not rely only on the existence of parsed CSV files.

### R4 — Prove current formal data are not affected by multi-sector request ordering ambiguity

The producer correctly classifies all sector bits from request prestate, but it then inserts multiple sectors from one request into the recency stack in a deterministic sequential order. That can create an arbitrary tie order for **future** reuse-distance calculations if a formal request carries more than one sector bit.

Before changing simulator source, first determine whether this matters for the current formal dataset.

Using already available `EPL2MOTV1` and `EPL2SRV1` counts, publish for every completed formal/screening row:

```text
eligible_demand_references
 total_sector_reference_events
 sector_events_per_demand_reference
```

For the completed original Motivation rows already inspected, sector-event totals equal old eligible-demand-reference counts, strongly indicating one active sector per frontend demand request. Extend/prove this for all final rows.

If every formal row has exactly `sector_events_per_demand_reference == 1.0`, document that the latent same-request recency tie cannot affect the paper-facing dataset; no simulator rerun is required solely for this latent path.

If any formal row has ratio >1, stop final promotion and either:

1. implement a truly batch-invariant/tied-recency distance definition and refreeze/rerun affected formal evidence, or
2. provide an equally rigorous source-proven definition that removes arbitrary sector-index ordering.

Do not silently accept multi-sector ordering ambiguity.

### R5 — Final validation evidence / pack completeness

The final `STREAMING_REUSE_CHARACTERIZATION_r1/` must satisfy Gate R, including:

- `SCREENING_RANKING.csv`
- `SCREENING_NOTES.md`
- `validation/` with actual command/results evidence
- old-Motivation compatibility across every rerun original-10 workload
- host wall/RSS
- Release/direct/parser/aggregator tests
- git cleanliness/diff-check
- checksum verification

The prefinal checkpoint is allowed to remain lighter; do not rewrite it in place.

## 3. Scan handling

The current scan run may continue naturally.

Its completion alone is **not** sufficient for final promotion. Complete R1–R5 in parallel while scan runs where possible.

If no simulator-source/runtime change is needed, retain the frozen runtime candidate:

- Core `ca3e7bc0b8f61b5d7c052bcda2a91955a1e5c919`
- Framework runtime `db1c90182fad02aacbd282b67ecdc57b8e4cc365`

Tooling-only aggregation/figure/packaging commits do not invalidate runtime evidence.

## 4. Next acceptable terminal state

After scan closes and R1–R5 pass, publish a **new** final pack:

`docs/ep_l2/review_packs/STREAMING_REUSE_CHARACTERIZATION_r1/`

and update:

`docs/ep_l2/codex_handoff/LANE_STREAMING_REUSE_LATEST.md`

Only then report:

`STREAMING_REUSE_FIG1V2_REVIEW_READY`

and stop for independent ChatGPT final review.

Do not self-declare scientific final PASS.
