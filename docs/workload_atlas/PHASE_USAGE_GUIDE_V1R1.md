# Atlas V1R1 — kernel/phase feature index: reading contract

[Kernel/phase table](KERNEL_PHASE_FEATURES_V1R1.tsv) contains **100 rows**: 98 individually named source-kernel identities across 42 ordinary-program slots (35 selected frozen programs + 7 unresolved/conditional slots), plus two **explicit non-new-kernel subphases** (heartwall later-frame dormant branch and srad_v1 reduction second pass). It is not a 100-kernel capture certificate.

The five [phase_sources](phase_sources/) JSON files are curated, separately reviewable projections from existing Atlas V1 program reports §§3–7, not new captures. Their tuple order is validated against the source-kernel identity list in unchanged V1 `ARCH_FEATURE_MATRIX.tsv`. Each row includes program ID, source symbol, stage, global access, static reuse opportunity, dependencies/synchronization, source/capture boundary, and a stable relative evidence reference.

### Correct interpretation
- **Source-fixed candidate behavior:** A row tells what the inspected candidate source *would do* in the listed phase. Actual capture producer source/ELF/ROI and complete SASS body remain separate, per [EVIDENCE_SCHEMA_V1R1.md](EVIDENCE_SCHEMA_V1R1.md).
- **Program launch count, not per-kernel launch count:** `program_registered_launch_count` comes verbatim from V1, including conditional lists and `SEE_REPORT`. It must never be repeated per row and summed to obtain launches.
- **Potential reuse, not measured merging:** Addresses, stride and halo relationships establish static opportunity. They do not prove L1 hit, outstanding overlap, L2 MSHR merge, DRAM read or stall-cycle contribution.
- **CPU/GPU boundary:** Especially particlefilter_naive and myocyte, host computations and host-mediated repeated kernel launches must not be counted as GPU instructions.
- **Branch and input scope:** `cfd/time_step` is SOURCE_ONLY / ZERO_IN_CAPTURE; `heartwall/BRANCH-LATER` is dormant for frame0; `nn` includes two alternative program versions, not a joint trace. The two extra rows do not add a new kernel definition.
- **Comparison:** A DTC/EP/AWMA project view may reuse these formula/phase descriptions after checking actual trace identity. EP and DTC simulator binaries remain independently authoritative, even when member-set trace SHA matches.

### Quality-gate and known incompleteness
- Matrix consistency checks: **42 program slots**, exactly **35 frozen + 7 conditional**, **98 unique-source-kernel entries**, **2 additional identified source subphases**, no missing per-program override and no row with blank core descriptions.
- The selected programs' original capture ELF and numeric raw input provenance are still **not independently certified**. Do not use this table to upgrade `SOURCE_VERIFIED` to `capture_source_link`, or a conditional candidate to a frozen ordinary member.
- Heavy source-body replays, benchmark builds, native workload execution, GPU captures, simulations and changes to accepted scientific artifacts were outside this revision.
- The original V1 programs have detailed source code line references. The V1R1 phase index deliberately cites the *program report* rather than inventing a fresh line reference for every copied summary.

See [PROJECT_SCOPE_ADVISORIES_V1R1.md](PROJECT_SCOPE_ADVISORIES_V1R1.md) for CFD/heartwall/host-size/PolyBench limitations.
