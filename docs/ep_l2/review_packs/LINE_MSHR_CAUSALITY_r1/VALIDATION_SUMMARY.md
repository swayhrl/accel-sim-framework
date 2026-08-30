# Validation summary

| Gate | Result |
| --- | --- |
| E0 source/isolation | PASS: dedicated Lane-E Framework/Core worktrees and result root; formal and D512 semantic parents recorded. |
| E2 Line-MSHR cardinality audit | PASS: allocator uses configured `m_num_entries`; Line-MSHR histogram has 1025 bins and delta/p95 handling; parser accepts values above 128. |
| E3 MSHR128 equivalence | PASS: both required D512 rows have seven byte-identical parsed CSV artifacts versus Lane B. |
| E4 directed boundaries | PASS: 127/128/129 and 255/256 plus exact full reason, release/reuse, and zero-leak test. |
| E5 effective config delta | PASS: each MSHR256 overlay changes only `dl2 ... A:128:1` to `A:256:1`. |
| E6 build/regression | PASS: Release build, existing descriptor/MSHR test, new boundary coverage, config-diff test, parser production paths, and `git diff --check`. |
| E7 convolution 2x2 | PASS locally: all four rows have normal exit, parser success, terminal clean, and payload consistency. |
| E8 spmv control | PASS locally: 23,560 cycles and all reported counters are unchanged at MSHR256. |

The exact frozen Lane-B candidate has now passed `D512_PREFLIGHT_PASS` and was
promoted 26/26. Exact matching D512/M256 and D512/spmv/M256 rows are therefore
`PROMOTED_VALID_CALIBRATION` without rerun. No result is a primary-baseline
promotion.
