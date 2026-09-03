# M5 Extended-20 Portfolio Approval

Status: **APPROVED FOR FORMALIZATION — PRIMARY 20 FROZEN, FORMAL RUNS WAIT FOR M5.2 ANCHOR**

Review date: 2026-09-04.

Selection evidence branch:

- Framework branch: `hrl/decoupled-l1-exp-m5-extended20-select-v0`
- reviewed selection commit: `d43b6eec93f68efa94057f34ffa699463b53e6a6`
- selection status: `M5_EXTENDED20_SELECTION_READY_FOR_REVIEW`

## 1. Review verdict

The proposed portfolio is accepted. It satisfies the intended anti-cherry-picking design:

- all 52 locally available candidates were inventoried;
- Paper-10 direct duplicates and microbenchmarks were excluded;
- no PAPER_IO/PAPER_OO/DTC benefit data was used in selection;
- four suites are represented: CUDA SDK 8, Rodinia 5, Parboil 6, PolyBench 1;
- source/Base-only pressure classes are balanced 7 high / 7 medium / 6 low;
- only four selected workloads are historical Q4-cost items;
- irregular, structured, reuse-heavy, reduction/search, write/atomic and compute-heavy controls are all represented.

The selection is therefore suitable as a **supplemental generalization portfolio**, not as a replacement for the thesis workload set.

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
14. Parboil `bfs`
15. Parboil `cutcp`
16. Parboil `histo`
17. Parboil `mri-q`
18. Parboil `sad`
19. Parboil `stencil`
20. PolyBench `3mm`

## 3. Ranked alternates

1. Parboil `sgemm`
2. Rodinia `lud`
3. CUDA SDK `fastWalshTransform_7_21`
4. CUDA SDK `scalarProd_8192`
5. CUDA SDK `vectorAdd_4000000`

An alternate may replace a primary workload only for a source/provenance/build/correctness/runtime infeasibility discovered **before viewing DTC benefit for replacement selection**. Re-run the portfolio P1-P6 diversity checks after any substitution and document the exact reason.

## 4. Metadata correction from independent review

The selection remains accepted, but one taxonomy label must be corrected during M5.E1 formalization:

- CUDA SDK `BlackScholes` is the Black-Scholes option-pricing sample; do not describe its algorithm as "Monte Carlo option pricing" unless the recovered source explicitly implements Monte Carlo sampling.
- Use `Black-Scholes option pricing` as the algorithm name.
- In the existing taxonomy, use primary domain `OTHER_SOURCE_BACKED_COMPUTE` with a secondary note such as `FINANCIAL_OPTION_PRICING`, while retaining its role as a compute-heavy/low-memory-pressure control if source/Base evidence supports that classification.

This is a metadata correction only and does not change membership of the selected 20.

## 5. Formal launch re-freeze gate

The historical selection evidence is trace/roster anchored. Before each workload can enter M5.E2 FORMAL runs, M5.E1 must freeze:

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

If exact source/input recovery materially changes a workload identity, re-evaluate E1-E8 eligibility and portfolio constraints before formal launch.

## 6. Scientific reporting boundary

Use these names consistently:

- `PAPER_10` / `GM-PAPER10`: original ten thesis compute workloads;
- `EXTENDED_20` / `GM-EXTENDED20`: this approved supplemental set;
- `ALL_COMPUTE_30` / `GM-ALL-COMPUTE30`: union, supplemental generalization view only.

Do not merge Extended-20 into the thesis Figure 4.x aggregate labels or `GM-ALL-PAPER`.

## 7. Activation boundary

M5.E1 source/build/input formalization may begin when convenient without disturbing the active Paper-10 Goal.

M5.E2's 60 Base/IO/OO formal simulations are authorized only after M5.2 freezes the common formal behavior/config/metric/parser anchor required by `M5_EXTENDED20_FORMAL_MATRIX.md`.
