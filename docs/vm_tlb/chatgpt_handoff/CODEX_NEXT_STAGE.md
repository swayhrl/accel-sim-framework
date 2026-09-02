# CODEX_NEXT_STAGE — Track A

## Status

`M1_VM_CORE_FOUNDATION`: **PASS**.

`M2_FUNCTIONAL_TRANSLATION` reached `G2-4` and is currently **BLOCKED** by reproducible abnormal pre-trace memory growth in functional VM mode. M3 has **not** started.

Do not move to a larger-memory host as the first response. The current evidence is not sufficient to classify ~65 GiB pre-replay RSS as a legitimate simulator requirement, because M1 baseline runs succeeded and the intended M2 structures are finite/small.

## Next authorized stage

Execute immediately:

`stage_specs/M2_RUNTIME_MEMORY_DIAG.md`

This is a narrow diagnosis/fix substage inserted before G2-4 can resume.

## Required execution order

1. read `CURRENT_STATE.md`;
2. read repository-root `AGENTS.md`;
3. read `stage_specs/M2_RUNTIME_MEMORY_DIAG.md`;
4. review existing `TARGET_PROGRESS.md` and `review_packs/M2_FUNCTIONAL_TRANSLATION/G2_4_RUNNING.md`;
5. perform M2-D D0 -> D6 in order;
6. if a concrete M2 bug is identified, implement only the minimal authorized fix and rerun regressions;
7. if M2-D PASS, resume original G2-4 real replay validation;
8. only after G2-4 + complete M2 closeout PASS, resume the already-authorized target-mode M3 flow;
9. after M3 PASS, create `M1_M3_VM_BASELINE_CLOSEOUT` and STOP before later mechanisms.

Do not modify `chatgpt_handoff/*`.

## Source anchors

Current blocked Track-A anchors:

- Core branch: `swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`
- Core G2-4 checkpoint: `c1431e01f593719f9201d4ad4d7666bebead8a4f`
- Framework branch: `swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`
- Framework blocked report checkpoint: `200e6ddf14b6247a25c6aa4108195ee0904702d8`

Relevant Core history to isolate first-bad behavior:

- M1: `82fa2bc79cf09dd137073431dc41e48bc2f30cec`
- G2-1: `06f0ae7a24f1deacd86ddf95237e0ffa5e1a1b83`
- G2-2: `740d96f8be80977c150ffc911063969cafd25b8f`
- G2-3: `e579c40d907c201728331a1208c64bb18b869549`
- G2-4: `c1431e01f593719f9201d4ad4d7666bebead8a4f`

Use the existing one-kernel trace/list that already reproduces the issue. Do not acquire another workload for diagnosis.

## Diagnostic decision rule

The first question is same-head causality:

`same binary + same one-kernel trace + same config`

compare:

- VM mode 0;
- VM mode 1 where useful;
- VM mode 2.

Then isolate the first offending M2 commit and measure effective VM configuration / expected storage footprint.

A larger host is justified only if evidence demonstrates that the corresponding unchanged VM-disabled/baseline path has a comparable legitimate memory requirement. Functional-mode-only 65 GiB RSS is not sufficient evidence for `BLOCKED_HOST_CAPACITY`.

## Fix authorization

If diagnostics identify a concrete source/config/integration bug, Codex may fix it without another human pause only when the fix is minimal and does not alter frozen VM semantics or weaken finite-resource modeling/tests.

After any fix, rerun:

- M1 disabled/ideal transparency;
- G2-1 mapper/TLB tests;
- G2-2 MSHR tests;
- G2-3 PWQ/walker tests;
- G2-4 directed replay/store/atomic tests;
- one-kernel functional VM memory regression;
- real G2-4 trace replay with end statistics.

## Target-mode continuation

Keep the overall Goal alive, but mark the active internal gate as:

`M2-D_RUNTIME_MEMORY_DIAG`

Maintain:

`docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`

If M2-D and G2-4 PASS, continue automatically:

`M2 closeout -> M3 -> M1-M3 macro closeout`.

If M2-D remains ambiguous, requires a semantic redesign, or proves a true external host-capacity blocker, push evidence and STOP.

## Reporting

Active report:

`docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`

Diagnostic review pack:

`docs/vm_tlb/review_packs/M2_RUNTIME_MEMORY_DIAG/`

Existing M2 evidence remains under:

`docs/vm_tlb/review_packs/M2_FUNCTIONAL_TRANSLATION/`

## STOP conditions

STOP immediately on:

- proposed fix changes frozen VM semantics;
- baseline transparency failure;
- request loss / duplicate wakeup / duplicate store or atomic;
- deadlock / unexplained nondeterminism;
- diagnosis remains materially ambiguous after D0-D4;
- unsafe host-wide resource pressure prevents bounded diagnosis.

**Do not enter M3 until a real functional VM replay passes G2-4.**
