# CODEX_EXTENDED20_SELECTION

Status: **ACTIVE SELECTION-ONLY TASK**

Branch:

`hrl/decoupled-l1-exp-m5-extended20-select-v0`

This is an isolated Framework-only research branch for selecting 20 Extended Compute workloads from the user's local pool of 52 already-runnable workloads.

## Mandatory first read

1. branch `AGENTS.md`;
2. `docs/dtc_l1/m5/M5_EXTENDED20_SELECTION_SPEC.md`;
3. current Paper-10 workload manifest and M5 compute workload manifest for duplicate avoidance;
4. any local manifest/log/index that identifies the 52 runnable workloads.

## Objective

Inventory all 52 locally runnable workloads, classify them using source/provenance and conventional/Base-only behavior evidence, and propose a scientifically broad Extended-20 set plus 5 alternates.

Do not run Extended-20 formal Base/IO/OO experiments on this branch.

Do not inspect or use PAPER_IO/PAPER_OO/DTC speedup to select workloads.

Do not modify the GPGPU-Sim Core.

Do not touch, kill, reprioritize, or consume resources needed by the active M5.0B/R5DV compute Goal.

## Local discovery

The user states that 52 workloads have already run successfully locally. Find the authoritative local source of this fact rather than assuming filenames:

- existing workload manifests;
- experiment-result indexes;
- run directories/scripts;
- prior PASS summaries;
- benchmark-suite checkouts.

If multiple lists disagree, reconcile them by executable/source/input identity and document the difference. The target inventory must contain exactly the 52 workloads that have actual prior successful-run evidence, unless the user's local evidence proves the stated number refers to a different grouping convention.

## Evidence discipline

Prefer reusing prior successful-run evidence. Do not launch long simulations merely to classify the candidates.

If a candidate's behavior cannot be classified from source or existing conventional/Base evidence, mark it `UNKNOWN` with confidence rather than using DTC results.

Static/source inspection and lightweight metadata scripts are allowed. Small non-simulator commands for hashes, source inventory, launch/input metadata, and prior-log parsing are allowed.

## Required selection method

Follow `M5_EXTENDED20_SELECTION_SPEC.md` exactly:

- E1-E8 hard eligibility;
- characterize all 52 across domain, memory-access pattern, operation mix, Base structural tendency, runtime cost;
- enforce P1-P6 portfolio constraints;
- use the 100-point score only after hard constraints;
- perform adversarial self-review;
- select 20 + 5 alternates;
- record a reason for every candidate not selected.

The set must contain both likely beneficiaries and likely non-beneficiaries. A compute-heavy or low-memory-pressure application is useful as a negative/control workload and must not be discarded simply because it appears uninteresting for DTC.

## Outputs

Create exactly the selection artifacts required by the specification under:

`docs/dtc_l1/m5/extended20/`

and:

`docs/dtc_l1/m5/handoffs/M5_E0_EXTENDED20_SELECTION.md`

The handoff must include:

- local 52-workload inventory source(s);
- Paper-10 duplicate exclusion proof;
- selected 20 table;
- five alternates;
- suite/domain/access/runtime coverage summary;
- explicit no-DTC-performance-use attestation;
- open provenance uncertainties;
- exact files/hashes needed by the later formal runner;
- do-not-redo list.

## Git rules

- Framework branch only.
- Never `git add .` or `git add -A`.
- Stage explicit selection metadata/scripts/docs only.
- Do not commit binaries, PTX, raw simulator logs, datasets, build trees, or large generated files.
- Do not push changes to `hrl/decoupled-l1-exp-m5-v0`.
- Keep the active compute Goal worktree untouched.

## Stop condition

Continue autonomously through inventory, classification, selection, self-review, and handoff creation.

Stop only at:

`M5_EXTENDED20_SELECTION_READY_FOR_REVIEW`

or if a true researcher decision is required because the local definition of the "52 runnable workloads" cannot be resolved from available evidence without choosing a different experiment population.

Ordinary missing metadata is not a stop condition: inspect source/manifests, mark uncertainty, and continue where scientifically defensible.
