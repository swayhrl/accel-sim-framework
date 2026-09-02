# DTC-L1 Current State

Last coordination update: 2026-09-02

Status: **M1 BLOCKED AT B07; B07 RECOVERY AUTHORIZED**

## Source anchors

Frozen M0 framework anchor:

- official: `accel-sim/accel-sim-framework:dev`
- official base SHA: `d930ad6d02c09bb56867132583735aba0389cff4`
- project M0 branch: `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-v0`
- M0 documentation SHA: `4ce6da7f000aa3cd68cc011cbc004d4774383e66`

Active framework goal branch:

- `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0`
- created directly from the M0 branch; M0 remains read-only.

Frozen M0 core anchor:

- official: `accel-sim/gpgpu-sim_distribution:dev`
- official base SHA: `91880c53383d5a6a6742bfb1be2c5f34e39c7871`
- project M0 branch: `swayhrl/gpgpu-sim:hrl/decoupled-l1-v0`
- M0 documentation SHA: `5e35de9914f1ad28647ef3a416d054b86f3e44a5`

Active core goal branch:

- `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0`
- created directly from the M0 branch; M0 remains read-only.

Latest stopped-run report recorded:

- Core SHA: `581fff76cf1dabbf1b2b9fe709a0f2142ab0d8e7`
- Framework implementation/evidence base SHA: `1f63d0c793784b41dbf02343c6442af5e68141a3`
- stop reason: M1 HARD gate `B07` merge-full test deadlocked.

## Authoritative design specification

Core repository:

`docs/dtc_l1/DTC_L1_SPEC.md`

Frozen paper-mode defaults remain unchanged, including:

- logical Tag 16KB, 128B line, 32 sets x 4 ways, LRU;
- 4 Tag banks, 1 request/bank/cycle;
- fixed 80KB physical array;
- RR allocation, width 4, partial allocation retained/no rollback;
- Baseline PIB 8 and Baseline traditional MSHR 32;
- IO PIB 256, OO PIB 128;
- IO/OO retire width 1;
- per-SM lower issue width 1 and global lower outstanding cap 256;
- OO Ref Count per coalesced 128B line reference;
- whole-line paper mode before sector extension.

No M0 architecture decision is changed by the B07 recovery.

## M1 implementation progress before stop

Codex reports that the following M1 infrastructure exists on the active goal branches:

- source integration audit;
- default-off `LEGACY` / `PAPER_BASE` mode plumbing;
- explicit Paper-Base PIB admission/backpressure;
- Paper-Base Tag-bank arbitration;
- Paper-Base traditional MSHR entry override (default 32);
- global lower-request outstanding cap;
- common counters/parser plumbing;
- deterministic M1 tests/build integration.

Reported evidence before B07 stop includes exact LEGACY equality on a small integrated kernel and successful directed evidence for several other M1 resource gates. These remain diagnostic until M1 is fully revalidated and the M1 review pack is produced.

## Current blocker — B07

B07 intentionally drives the conventional L1 MSHR merge-full path with many warps reading the same address. The stopped run observed `MSHR_MERGE_ENRTY_FAIL` and then simulator deadlock instead of recovery.

The stop was correct: M2-M4 must not proceed while a M1 HARD gate fails.

## ChatGPT source-review finding

Independent source review found a concrete high-priority defect in the current Paper-Base PIB lifecycle:

- the L1-latency `HIT` completion path in `ldst_unit::L1_latency_queue_cycle()` calls `m_core->warp_inst_complete(mf_next->get_inst())` when the load actually completes;
- that path does not call `dtc_l1_retire(...)`;
- other tracked `ldst_unit` completion paths already pair `warp_inst_complete(...)` with `dtc_l1_retire(...)`.

This can leak a live Paper-Base PIB UID on an L1-hit completion. B07 is a natural trigger: the first same-line access misses; after it fills, later same-line accesses become hits. If their PIB entries do not retire, an 8-entry PIB can remain permanently full even though the cache accesses themselves complete.

This source-level explanation must be verified with bounded pre-fix diagnostics before applying the minimal fix.

## Authorized recovery

Execution authority is now:

`docs/dtc_l1/goal/B07_RECOVERY_SPEC.md`

Required sequence:

1. localize the pre-fix failure and confirm/disprove the hit-completion PIB leak;
2. if confirmed, minimally pair the true L1-hit completion event with idempotent DTC PIB retirement;
3. add a permanent hit-completion PIB-leak regression/invariant;
4. re-run B07 with reproducible source-supported conventional MSHR entry/max-merge settings;
5. run frozen clean-upstream differential evidence under the same conventional MSHR geometry;
6. re-run all M1 HARD gates and LEGACY neutrality.

If full M1 revalidation passes, Codex is authorized to create `review_packs/M1_FOUNDATION/` and resume the existing M2 -> M3 -> M4 continuous goal automatically. Any HARD failure still requires STOP.

## Scientific boundary

M1-M4 remains an implementation/correctness/workload-bring-up goal. It does not authorize final thesis speedup reproduction, final Chapter-4 figures, equal-area conclusions, graphics proxy claims, or M5 work.