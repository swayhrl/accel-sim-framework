# FAST64.0 Pivot Handoff

Status: **FAST64_0_PIVOT_PASS**

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

## Verified pivot inventory (2026-09-07)

### Isolated worktree and authority

| item | result |
| --- | --- |
| FAST64 worktree | `/workspace/worktrees/accel-sim-decoupled-l1-fast64` |
| Framework branch / HEAD | `hrl/decoupled-l1-fast64-v0` / `81f8c67b4955ffd8f8a975ba59f13ccacbd2ac13` |
| pivot ancestry | PASS: `a9cdb3328a346cbc9a76b7ffadae3725b4209ab5` is an ancestor |
| Core authority | PASS: `hrl/decoupled-l1-m5-v0@15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9` |
| FAST64 worktree status | clean before this handoff update |
| legacy M5 worktree | left on its own branch with its four pre-existing untracked compact artifacts preserved; no checkout, reset, clean, or pull was applied |

The pivot used a new worktree because the legacy M5 worktree remains the
working-directory reference for existing auxiliary jobs and artifacts.  No
running process was signalled, paused, reniced, attached, or otherwise
perturbed by the pivot.

### Live legacy auxiliary work at the pivot snapshot

| PID | identity / namespace | disposition |
| ---: | --- | --- |
| 943020 | old-runtime ATAX `PAPER_BASE`, `/tmp/dtc-l1-m5-t2-clean-build.7tN1Dz`; M5 immutable ATAX trace | retained, non-FAST64 legacy diagnostic; do not duplicate or relabel |
| 944237 | old-runtime MVT `PAPER_BASE`, `/tmp/dtc-l1-m5-t2-clean-build.7tN1Dz`; M5 immutable MVT trace | retained, non-FAST64 legacy diagnostic; do not duplicate or relabel |
| 1094956 | repaired-runtime 80-SM ATAX `PAPER_BASE`, `/tmp/dtc-l1-m5-lowerq-runtime.hvGL1q`; M5 immutable ATAX trace | `BACKGROUND_HEAVY_REPAIR_STRESS`; may continue if healthy/affordable, never a FAST64 gate |

At the snapshot each listed simulator was CPU-active and had no pivot-induced
change.  The previously observed ATAX IO/OO recovery PIDs were no longer live
at this snapshot; this handoff makes no terminal/result claim for them.

### Tier and heavy-evidence disposition

The compact Tier-A/Tier-C index is
`FAST64_0_EVIDENCE_INDEX.md`.  In particular:

- repaired BICG and valid SpMV remain Tier-A mechanism-fidelity anchors;
- large ATAX is Tier-C `BACKGROUND_HEAVY_REPAIR_STRESS`;
- SYR2K and 2MM are Tier-C `DEFERRED_HEAVY_AUXILIARY`;
- 2MM's verified 3,416,630,277-byte compressed archive is retained and was
  not unpacked, deleted, or relabelled;
- Extended-20 remains `DEFERRED_OPTIONAL_GENERALIZATION` and is not a FAST64
  completion gate.

### FAST12 payload accessibility

All twelve frozen FAST12 source trace roots are locally readable.  FAST64.1
must hash and freeze their exact ordered members before any formal FAST64
result.  No payload was copied, modified, or selected based on DTC benefit at
this pivot.

| family | locally accessible canonical source family |
| --- | --- |
| PolyBench: ATAX, BICG, GESUMMV, GEMM, 2DConvolution | `accel-sim-decoupled-l2/hw_run/c2p-polybench-full-20260821/polybench/11.0/.../traces` |
| Rodinia: Btree, DWT2D, Gaussian, Hotspot1, LUD, NN | `accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/rodinia-first-batch/rodinia-3.1/9.1/.../traces` |
| Parboil: MRI-Q | `accel-sim-decoupled-l2/hw_run/decoupled-l2-extract/parboil.current.small8.stage/parboil/11.0/.../traces` |

### FAST64.0 HARD checklist

| HARD item | result |
| --- | --- |
| branch descends from pivot parent | PASS |
| frozen Core authority recorded | PASS |
| M5 evidence classified without deletion/relabel | PASS |
| 2MM / SYR2K deferred heavy auxiliary | PASS |
| large ATAX background auxiliary only | PASS |
| FAST12 frozen before FAST64 IO/OO observation | PASS |
| historical M5 identities not rewritten | PASS |

## Next executable action

Enter FAST64.1: materialize resolved FAST64 Base/IO/OO configurations from
the approved 64-SM shell, freeze the twelve exact payload identities, and run
the required non-binding lower-cap/smoke qualification.  Do not start a
FAST64 primary performance row before FAST64.1 PASS.

## PASS transition

On PASS:

- change status to `FAST64_0_PIVOT_PASS`;
- commit/push compact evidence;
- immediately enter FAST64.1 without a researcher pause.
