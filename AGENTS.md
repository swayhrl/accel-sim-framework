# AGENTS.md — M5 Extended-20 Selection Branch

This branch is a **selection-only research workspace** for choosing 20 additional GPU compute workloads from the user's local pool of 52 already-runnable workloads.

Branch:

`hrl/decoupled-l1-exp-m5-extended20-select-v0`

It must not interfere with the active compute Goal on `hrl/decoupled-l1-exp-m5-v0` and must not modify the GPGPU-Sim Core.

## Mandatory read order

1. `docs/dtc_l1/m5/M5_EXTENDED20_SELECTION_SPEC.md`
2. `docs/dtc_l1/chatgpt_handoff/CODEX_EXTENDED20_SELECTION.md`
3. current Paper-10 workload/compute manifests only for duplicate avoidance and terminology
4. local manifests/result indexes/source trees that prove which 52 workloads have already run successfully

Do not execute the main M5 compute Goal from this branch.

## Scientific objective

Produce a broad, reproducible, non-cherry-picked Extended-20 generalization set.

The Extended-20 is supplemental to the thesis Paper-10 set. It must contain both likely DTC beneficiaries and likely non-beneficiaries and cover multiple suites, domains, access patterns, operation mixes, Base structural-pressure levels, and runtime costs.

**Never use PAPER_IO/PAPER_OO/DTC speedup or DTC benefit to select, rank, or tie-break workloads.**

Allowed evidence is source/provenance, deterministic input/output checking, prior successful-run evidence, source/static access structure, existing conventional/Base-only evidence, launch geometry/work amount, operation mix, and historical wall-clock cost.

## Branch ownership

Allowed:

- inspect local workload/source/result metadata;
- write compact inventory/classification/selection TSV/Markdown;
- write lightweight metadata/parsing scripts if needed;
- create the M5_E0 selection handoff;
- commit/push this branch.

Forbidden:

- edit GPGPU-Sim Core;
- change DTC mechanisms/config semantics;
- launch the 60 Extended-20 Base/IO/OO formal runs;
- use DTC performance for selection;
- modify/push the active compute M5 branch;
- kill/reprioritize active M5.0B/R5DV jobs;
- commit binaries, PTX, datasets, raw logs, traces, or build trees.

Prefer existing run evidence. Do not launch long simulator jobs just to classify a candidate.

## Selection workflow

Execute autonomously:

`S0 inventory 52 -> S1 eligibility/dedup -> S2 behavior matrix -> S3 20+5 portfolio -> S4 adversarial self-review -> S5 handoff`

Follow all E1-E8 eligibility gates and P1-P6 portfolio constraints in `M5_EXTENDED20_SELECTION_SPEC.md`.

Required final artifacts:

- `docs/dtc_l1/m5/extended20/EXTENDED52_INVENTORY.tsv`
- `docs/dtc_l1/m5/extended20/EXTENDED52_BEHAVIOR_MATRIX.tsv`
- `docs/dtc_l1/m5/extended20/EXTENDED20_SELECTED.tsv`
- `docs/dtc_l1/m5/extended20/EXTENDED20_ALTERNATES.tsv`
- `docs/dtc_l1/m5/extended20/EXTENDED20_NOT_SELECTED.tsv`
- `docs/dtc_l1/m5/extended20/M5_EXTENDED20_SELECTION_REPORT.md`
- `docs/dtc_l1/m5/handoffs/M5_E0_EXTENDED20_SELECTION.md`

## Git discipline

- never `git add .` or `git add -A`;
- explicit-path staging only;
- keep compact evidence in Git;
- do not force-push;
- `git diff --check` before final handoff.

## Stop condition

Stop only at:

`M5_EXTENDED20_SELECTION_READY_FOR_REVIEW`

or a genuine researcher-decision boundary where the local definition of the stated "52 runnable workloads" cannot be resolved from available evidence without changing the experiment population.

Ordinary missing metadata is not a stop condition: investigate source/manifests, mark uncertainty, and continue where scientifically defensible.
