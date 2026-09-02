# CODEX_NEXT_STAGE — Track A

## Status

`M1_VM_CORE_FOUNDATION`: **PASS**.

Codex reported `M2_FUNCTIONAL_TRANSLATION` closeout PASS, but independent ChatGPT review has **reopened M2 before further M3 work**.

The prior runtime-memory blocker is closed. The remaining issue is architectural retry semantics/observability: while a waiter is already registered in an active translation MSHR, the current path re-enters `translation_controller::translate()` each cycle and probes/consumes L1/L2 resources before rediscovering the same waiter. Existing sensitivity evidence shows this pollutes L2 misses as fixed PTW latency grows.

G3-0 entry/freeze has completed. One G3-1 Core commit already exists:

`8c613a356e6a146951cd59c9929046c6c4cfd856`

Treat it as **provisional/unaccepted**. Do not force-rewrite it, but do not start G3-2 or any further M3 semantic work.

## Next authorized stage

Execute only:

`stage_specs/M2_REVIEW_FIX_BEFORE_M3.md`

Do not modify `chatgpt_handoff/*`.

## Source anchors

Core branch:
`swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`

Important Core anchors:

- M1: `82fa2bc79cf09dd137073431dc41e48bc2f30cec`
- M2 closeout: `e7999554200760b31b4efe16d98e050370e1ea71`
- provisional G3-1: `8c613a356e6a146951cd59c9929046c6c4cfd856`

Framework branch:
`swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

Important Framework anchors:

- M2 dependency fix: `4012be3606c300d11e7b34826ee1cb22b0852b93`
- M2 closeout: `a7020e603d6081f1f16f26b5ad1ead5ca17d7756`
- G3-0 freeze: `65a6e68d35cded7b78293b92a253e09c75c5aa36`

Fetch/pull the latest ChatGPT handoff before continuing.

## Required execution

Follow `M2_REVIEW_FIX_BEFORE_M3.md` RF1–RF8.

The minimum semantic requirement is:

> once `(translation key, waiter UID)` is accepted/registered in an active MSHR, retries of that same waiter while the walk remains active must wait without consuming/probing L1/L2 TLB ports or adding new TLB access/miss events.

A new waiter for the same key must still perform its own first lookup before merging.

Do not solve this merely by renaming the existing polluted counters. The resource behavior itself must stop same-waiter polling from occupying TLB lookup bandwidth.

## Required validation emphasis

Before re-closing M2:

- exact same-waiter non-reprobe directed test;
- proof an unrelated translation can use the shared L2 port while the first waiter is pending;
- waiter allocation/merge/wakeup exact-once conservation;
- M1 transparency;
- all G2 directed regressions;
- functional one-kernel/LUD/BFS replay;
- kernel-boundary persistence evidence;
- expanded MSHR observability;
- complete M2 review-pack minimum files;
- controlled fixed-walk-latency sensitivity.

The controlled sensitivity must specifically demonstrate that merely increasing walk latency no longer causes same-waiter retry polling to inflate L2 misses roughly in proportion to wait time.

## Interaction with provisional G3-1

Do not rewrite history.

Implement the M2 review repair on the current Core branch, then rerun the provisional G3-1 backend/no-recursion tests. If the two conflict semantically, STOP and report.

No G3-2 source change is authorized.

## Reporting

Maintain:

`docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`

and:

`docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`

Update/reclose:

`docs/vm_tlb/review_packs/M2_FUNCTIONAL_TRANSLATION/`

Create a dedicated repair evidence section/file or review pack if useful, but the final M2 README must remain the sole review entry.

## STOP boundary

After M2-RF acceptance criteria pass:

- push Core + Framework;
- update reports/progress;
- provide final M2-RF SHAs and review entry;
- **STOP FOR CHATGPT REVIEW**.

Do not continue to G3-2 / real PTE memory integration until ChatGPT accepts the repaired M2 baseline.
