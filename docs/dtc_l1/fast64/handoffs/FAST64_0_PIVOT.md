# FAST64.0 Pivot Handoff

Status: **READY_TO_EXECUTE — NOT YET PASS**

## Approved pivot anchors

- Framework pivot parent: `a9cdb3328a346cbc9a76b7ffadae3725b4209ab5`
- FAST64 Framework branch: `hrl/decoupled-l1-fast64-v0`
- Core authority: `hrl/decoupled-l1-m5-v0@15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`

## Approved scientific disposition

- Primary performance evaluation moves to FAST64.
- FAST12 membership is frozen by `FAST64_WORKLOAD_MANIFEST.tsv` before any
  FAST64 IO/OO performance is observed.
- Existing repaired BICG and valid SpMV evidence remain mechanism-fidelity
  anchors.
- Large 80-SM ATAX becomes background heavy repair/stress evidence.
- SYR2K and 2MM primary-path work becomes `DEFERRED_HEAVY_AUXILIARY`.
- Extended-20 becomes `DEFERRED_OPTIONAL_GENERALIZATION` for FAST64 purposes.

## What Codex must verify before marking FAST64.0 PASS

1. Re-read the old M5 latest handoff/current state only to inventory live jobs
   and preserved artifacts.
2. Confirm no healthy scientific process is accidentally terminated by the
   branch pivot.
3. Record which existing live jobs, if any, continue as background auxiliary
   work and their PIDs/namespaces.
4. Confirm no 2MM/SYR2K data is deleted or relabelled.
5. Confirm FAST12 source trace roots are still locally accessible or identify
   the exact source-correct materialization step needed before FAST64.1.
6. Create the Tier-A/Tier-C evidence index with exact historical references.
7. Check branch cleanliness while preserving pre-existing untracked artifacts.
8. Check every HARD item in the FAST64.0 section of
   `FAST64_ACCEPTANCE_CONTRACT.md`.

## PASS transition

On PASS:

- change status to `FAST64_0_PIVOT_PASS`;
- commit/push compact evidence;
- immediately enter FAST64.1 without a researcher pause.
