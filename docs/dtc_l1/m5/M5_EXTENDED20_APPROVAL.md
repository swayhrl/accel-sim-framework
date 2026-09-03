# M5 Extended-20 Portfolio Approval

Status: **APPROVED FOR FORMALIZATION — REVIEW-REFINED PRIMARY 20 FROZEN; FORMAL RUNS WAIT FOR M5.2 ANCHOR**

Review date: 2026-09-04.

Selection evidence branch:

- Framework branch: `hrl/decoupled-l1-exp-m5-extended20-select-v0`
- reviewed selection commit: `d43b6eec93f68efa94057f34ffa699463b53e6a6`
- selection status: `M5_EXTENDED20_SELECTION_READY_FOR_REVIEW`

## 1. Independent review verdict

The selection methodology is accepted. It satisfies the intended anti-cherry-picking design:

- all 52 locally available candidates were inventoried;
- Paper-10 direct duplicates and microbenchmarks were excluded;
- no PAPER_IO/PAPER_OO/DTC benefit data was used in selection;
- source/Base-only pressure, operation mix, domain diversity and historical cost were used instead;
- irregular, structured, reuse-heavy, reduction/search, write/atomic and compute-heavy controls are represented.

One **pre-performance portfolio refinement** is made during independent review:

- replace selected PolyBench `3mm` with alternate Rodinia `lud`.

Reason: the purpose of Extended-20 is to broaden coverage beyond Paper-10. Paper-10 already contains `2mm`; `3mm` is source-valid but remains a closely related chained dense-matrix family and is historical Q4 cost. `lud` provides a more distinct blocked LU/factorization/update behavior while preserving dense/reuse-heavy compute coverage. This decision is made before any Extended DTC performance is observed.

After the refinement the suite mix is:

- CUDA SDK: 8
- Rodinia: 6
- Parboil: 6

This still satisfies the original >=3-suite and <=50%-single-suite portfolio constraint. The pressure mix remains within the intended high/medium/low balance, and the Q4 count is reduced by removing `3mm`.

The portfolio is therefore suitable as a **supplemental generalization set**, not a replacement for the thesis Paper-10.

## 2. Approved primary 20

1. CUDA SDK `BlackScholes`
2. CUDA SDK `convolutionSeparable`
3. CUDA SDK `fastWalshTransform_11_19`
4. CUDA SDK `scalarProd_13920`
5. CUDA SDK `scan`
6. CUDA SDK `sortingNetworks`
7. CUDA SDK `transpose`
8. CUDA SDK `vectorAdd_6000000`
9. Rodinia `cfd_097k`
10. Rodinia `btree`
11. Rodinia `dwt2d`
12. Rodinia `gaussian`
13. Rodinia `hotspot1`
14. Rodinia `lud`
15. Parboil `bfs`
16. Parboil `cutcp`
17. Parboil `histo`
18. Parboil `mri-q`
19. Parboil `sad`
20. Parboil `stencil`

## 3. Ranked alternates after review

1. PolyBench `3mm`
2. Parboil `sgemm`
3. CUDA SDK `fastWalshTransform_7_21`
4. CUDA SDK `scalarProd_8192`
5. CUDA SDK `vectorAdd_4000000`

Rodinia `lud` is promoted from the selection proposal's ALT02 into the primary set.

An alternate may replace a primary workload only for source/provenance/build/correctness/runtime infeasibility discovered **before using DTC benefit to choose the replacement**. Re-run P1-P6 portfolio checks and document the exact pre-performance reason.

## 4. Metadata correction from independent review

A second review correction applies to CUDA SDK `BlackScholes`:

- use algorithm name `Black-Scholes option pricing`;
- do not label it `Monte Carlo option pricing` unless the recovered source explicitly implements Monte Carlo sampling;
- in the existing taxonomy, use primary domain `OTHER_SOURCE_BACKED_COMPUTE` with a secondary note such as `FINANCIAL_OPTION_PRICING`;
- retain its role as a compute-heavy/low-memory-pressure control only if source/Base evidence supports that classification during E1.

This metadata correction does not change workload membership.

## 5. Formal launch re-freeze gate

The historical selection evidence is trace/roster anchored. Before each workload enters M5.E2 FORMAL runs, M5.E1 must freeze:

- exact source repository/version/commit;
- source path and wrapper/build command;
- executable and PTX SHA-256;
- canonical/deterministic input path and byte SHA-256;
- output checker/reference and reference hash;
- launch geometry/work amount;
- M5 Core SHA;
- M5 Framework SHA;
- Base/IO/OO config hashes;
- parser/schema identity.

Historical L2 trace completion is evidence of prior runnability only. It is not an M5 performance result.

If exact source/input recovery materially changes workload identity, re-evaluate E1-E8 eligibility and portfolio constraints before formal launch.

## 6. Scientific reporting boundary

Use these names consistently:

- `PAPER_10` / `GM-PAPER10`: original ten thesis compute workloads;
- `EXTENDED_20` / `GM-EXTENDED20`: this review-refined supplemental set;
- `ALL_COMPUTE_30` / `GM-ALL-COMPUTE30`: union, supplemental generalization view only.

Do not merge Extended-20 into thesis Figure 4.x aggregate labels or `GM-ALL-PAPER`.

## 7. Activation boundary

M5.E1 source/build/input formalization may begin when convenient without disturbing active Paper-10 jobs.

M5.E2's 60 Base/IO/OO formal simulations are authorized only after M5.2 freezes the common formal behavior/config/metric/parser anchor required by `M5_EXTENDED20_FORMAL_MATRIX.md`.
