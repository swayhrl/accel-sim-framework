# M2-D — Runtime Memory Allocation Diagnosis Before G2-4 Resume

## Status

**AUTHORIZED NOW.**

M2 reached G2-4 but real VM-mode trace replay is blocked by reproducible abnormal host-memory growth before trace replay. M3 remains blocked.

This stage is a narrow diagnosis/fix stage. Its purpose is to determine whether the failure is caused by the M2 functional-translation integration, simulator/config interaction, or the host/baseline environment. Do not bypass the problem by merely moving to a larger-memory host unless diagnostics first show that the same-head VM-disabled/baseline path has comparable legitimate memory demand.

## Why this is a correctness blocker

The one-kernel trace is only about 54 KiB, yet the VM-mode simulator grows to about 65 GiB RSS before useful replay evidence. The intended M2 structures are finite and small (per-SM L1 TLB, one shared L2 TLB, finite translation MSHR, PWQ, and walkers); tens of GiB of pre-replay incremental RSS is not an accepted modeling cost.

Therefore, "run on a bigger host" is not a valid closeout by itself. Root cause must be isolated first.

## Frozen anchors

Core Track-A branch:
`hrl/vm-m1-m3-v0`

Relevant Core commits:

- M1: `82fa2bc79cf09dd137073431dc41e48bc2f30cec`
- G2-1: `06f0ae7a24f1deacd86ddf95237e0ffa5e1a1b83`
- G2-2: `740d96f8be80977c150ffc911063969cafd25b8f`
- G2-3: `e579c40d907c201728331a1208c64bb18b869549`
- G2-4 checkpoint: `c1431e01f593719f9201d4ad4d7666bebead8a4f`

Framework blocked report commit:
`200e6ddf14b6247a25c6aa4108195ee0904702d8`

Use the already-prepared one-kernel trace/list that reproduced the issue. Do not acquire a new workload for diagnosis.

## D0 — Same-head mode-control experiment

At the current Core checkpoint, run the same one-kernel trace/config with the same binary and host conditions under:

1. `VM_DISABLED` (`-gpgpu_vm_mode 0`);
2. `VM_IDEAL_IDENTITY` (`-gpgpu_vm_mode 1`), if useful;
3. functional VM (`-gpgpu_vm_mode 2`).

Use a bounded virtual-memory limit high enough for the known M1 baseline but low enough to fail before destructive host exhaustion (the previously used 10 GiB limit is acceptable if mode 0 is shown to fit it).

Required evidence:

- exact command/config;
- exit status;
- `/usr/bin/time -v` maximum RSS;
- last initialization banner/checkpoint reached;
- whether trace replay started;
- mode 0/1/2 comparison table.

Interpretation:

- if mode 0/1 also exhibit the same failure on the same head, do not blame M2 yet; continue baseline/environment isolation;
- if mode 0/1 are normal and mode 2 alone explodes, treat the issue as M2-specific until disproved.

## D1 — First-bad-commit isolation

Use the same one-kernel command and bounded-memory procedure to identify the earliest functional-VM commit that exhibits abnormal growth:

`G2-1 -> G2-2 -> G2-3 -> G2-4`.

Do not infer from runtime timeout alone. Record max RSS / fail point for each relevant commit.

At minimum answer:

- does the abnormal memory behavior already exist at G2-1?
- if yes, G2-2/G2-3/G2-4 are not the root introduction;
- if no, identify the first offending semantic commit.

## D2 — Validate effective VM configuration before allocation

Before constructing the production `translation_controller`, capture the effective values actually parsed at runtime:

- `num_sms`;
- page size;
- L1 entries/assoc/ports;
- L2 entries/assoc/ports;
- MSHR entries;
- PWQ entries;
- walkers;
- fixed walk latency.

Also calculate and report a conservative expected storage footprint for the M2 VM structures from these values.

This instrumentation may be temporary diagnostic output. It must not alter timing or semantics.

Hard check: no parsed resource count may be unexpectedly huge or uninitialized.

## D3 — Standalone production-size controller test

Create/run a small standalone test that constructs the same M2 `translation_controller` using the actual production values from D2 (including actual `num_sms`) and then exits.

Record max RSS with `/usr/bin/time -v`.

Purpose:

- if the standalone controller itself consumes abnormal memory, isolate/fix the controller/config;
- if it remains small, the explosion comes from integration/lifecycle/another simulator allocation triggered by functional mode.

Do not weaken production TLB/MSHR/PWQ/walker capacities simply to make this test pass.

## D4 — Allocation-location diagnosis without relying on GDB

Because GDB could not start under the 10 GiB limit, use lightweight allocation evidence available on the host. Prefer at least two of the following when practical:

- `/usr/bin/time -v`;
- periodic `/proc/<pid>/status` and `/proc/<pid>/smaps_rollup` snapshots;
- `pmap -x <pid>` snapshots;
- `strace -f -e trace=brk,mmap,mremap,munmap` around initialization;
- heap profiler only if already installed and low-risk.

Add narrow initialization checkpoints if needed around:

- translation-controller construction;
- shader/memory statistics construction;
- memory-partition/subpartition construction;
- interconnect creation;
- SIMT-cluster creation / first launch;
- trace parser/replay entry.

The objective is to identify the allocation phase and, if possible, the specific allocation size/caller class.

Do not commit noisy debug prints in the final fixed source unless they are useful permanent observability.

## D5 — Fix authorization

If D0-D4 identify a concrete M2 source/config/integration bug, Codex is authorized to implement the **minimal semantic fix** on the Track-A branch without another human round, provided all of the following hold:

1. root cause is documented with evidence;
2. fix does not change frozen VM semantics merely to reduce memory;
3. finite TLB/MSHR/PWQ/walker behavior remains intact;
4. no test/resource is weakened;
5. M1 disabled/ideal transparency is rerun after the fix;
6. all G2-1/G2-2/G2-3 directed tests still pass;
7. G2-4 directed replay/store/atomic checks still pass.

If the only apparent fix would materially change the architecture contract, STOP and report instead.

## D6 — Runtime memory regression gate

Before G2-4 can resume, show on the same one-kernel trace/config:

- VM-disabled path completes initialization/replay normally;
- functional VM no longer exhibits runaway pre-replay RSS;
- functional VM reaches actual trace replay;
- incremental functional-VM pre-replay RSS versus VM-disabled is bounded and explainable by the small M2 structures.

Use a relative result rather than hiding the issue with a huge host. As a practical sanity criterion, functional mode should not add GiB-scale pre-replay RSS over mode 0; any >256 MiB incremental pre-replay RSS requires explicit explanation/evidence before acceptance.

Then rerun the required real G2-4 VM-mode replay and obtain actual end statistics.

## Resume rule

If D6 PASS and the original G2-4 acceptance criteria PASS:

1. update `TARGET_PROGRESS.md` with `M2-D PASS` and `G2-4 PASS`;
2. complete M2 closeout;
3. resume the previously authorized continuous target-mode flow into M3 automatically.

No additional human pause is required if the diagnosis/fix is narrow and all gates pass.

If diagnosis instead proves the same legitimate memory requirement exists in the unchanged VM-disabled/baseline path on an isolated host, close M2-D as `BLOCKED_HOST_CAPACITY` with evidence and request a larger isolated simulator host. Do not make this classification from functional-mode evidence alone.

## Deliverables

Create:

`docs/vm_tlb/review_packs/M2_RUNTIME_MEMORY_DIAG/`

At minimum include:

- `README.md`;
- `MODE_COMPARISON.tsv`;
- `COMMIT_BISECT.tsv`;
- `VM_CONFIG_FOOTPRINT.md`;
- `ALLOCATION_PHASE_EVIDENCE.md`;
- `FIX_SUMMARY.md` if a source fix is made;
- `VALIDATION_SUMMARY.md`;
- `RAW_LOG_INDEX.tsv`.

Update:

- `docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`;
- `docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`.

## STOP conditions

STOP if:

- a proposed fix changes frozen VM semantics;
- baseline transparency regresses;
- request/replay invariants fail;
- diagnosis remains ambiguous after D0-D4;
- the evidence indicates a host-wide/external failure that cannot be safely isolated locally.

Do not enter M3 until G2-4 real replay acceptance is complete.
