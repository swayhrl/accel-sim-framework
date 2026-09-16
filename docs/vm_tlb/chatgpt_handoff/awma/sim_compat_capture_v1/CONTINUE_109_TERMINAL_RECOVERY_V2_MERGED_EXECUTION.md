# CONTINUE node109 — AWMA terminal recovery V2 merged execution directive

## Purpose

Continue the existing V2 terminal-recovery work as **one continuous Goal**. Do not split engineering milestones into separate Codex rounds when the next action is already determined and does not change scientific identity or claim boundaries.

Current operator-reported checkpoint to verify locally and then accept into the V2 evidence pack:

```text
- NVBit 1.7.7 / 1.7.7.1 archive, source, build and binary SHA closure exists
- official NVBit 1.7.7.1 mem_trace terminal-closed twice on RTX4080 vectoradd
- CUDA 12.8 CUDA_ERROR_INVALID_SOURCE was eliminated by the 1.7.7.1 device-assert hotfix
- custom Accel-Sim tracer has migrated explicit load/find/launch, managed ChannelDev, and ChannelHost-owned receiver registration
- custom tiny tracer still stalls before terminal acknowledgement
- registration-only migration is therefore insufficient
- Q05 has not been resumed
- GPU lock is free
```

## Efficiency rule

The following are **one merged engineering sequence**, not separate reporting stages:

```text
per-context/per-kernel receive-state ownership
-> tiny custom tracer closure
-> fresh-process repeat closure
-> tiny parser/grammar/semantic regression
-> exact Q05 target canary
-> formal Q05 capture
-> producer completeness/hash closure
-> accepted pipeline READY publication
-> final V2 review pack/report/commit/push
```

Do not stop after any intermediate PASS merely to report progress if the next step is already authorized by this handoff.

Examples of milestones that must continue inline when they pass:

```text
receiver state-machine compiles          -> run tiny canary
tiny canary passes once                  -> repeat from fresh process
repeated tiny closure passes             -> run parser/semantic regression
regression passes                        -> reacquire GPU lock and run Q05 canary
Q05 canary terminal-closes               -> run formal Q05 capture
formal capture closes                    -> validate/parser/hash/publish READY
READY publishes                          -> finish review pack/report/commit/push
```

Only pause/STOP if a new issue changes scientific identity, trace semantics, accepted grammar, formal completeness meaning, or proves a bounded external blocker.

## Active engineering objective

Do not keep modifying a single global completion flag. Complete **true receive-state ownership** using the verified official NVBit 1.7.7.1 receiver/channel semantics and the newer per-context Accel-Sim tool pattern as engineering references.

The implementation must correctly own at least:

```text
context receiver lifecycle
channel lifetime
per-kernel receive/completion state
kernel-by-kernel state reset
terminal sentinel acknowledgement
receiver STOP request
receiver FINISHED acknowledgement
thread join / ChannelHost destruction ordering
trace/xz writer close ordering
callback re-entry suppression
```

A reasonable architecture is per-context receiver/channel state containing a per-kernel completion state, rather than V1's global receiver flags. Use the minimum semantics-preserving design justified by the verified source; do not copy unrelated features.

Required properties:

```text
1. receiver is WORKING before traced kernel traffic can arrive
2. each traced kernel arms a fresh incomplete receive state
3. payload records are drained by the receiver
4. only the real device/channel terminal sentinel marks that kernel complete
5. stale completion from kernel N cannot satisfy kernel N+1
6. writer/xz close occurs only after terminal acknowledgement
7. context teardown requests STOP only after no traced kernel remains pending
8. receiver publishes FINISHED before join/destroy completes
9. ChannelHost / ChannelDev cannot be destroyed while receiver may access them
10. timeout/watchdog is diagnostic failure only, never COMPLETE
```

## Tiny gate — run and continue inline

Use the custom Accel-Sim tracer with a tiny vectoradd/equivalent workload exercising the actual writer + channel + terminal path.

PASS requires:

```text
real traced records
explicit flush tool kernel launch and completion
real terminal sentinel observed by receiver
per-kernel state reaches complete through the intended state machine
normal writer/xz close
normal process exit
readable kernelslist + trace
actual Accel-Sim parser/grammar smoke
trace semantics preserved
no host-fabricated COMPLETE
```

After the first PASS, immediately repeat from fresh processes until at least **two independent successful closures** are recorded. Do not create a separate round between repetitions.

Then immediately run the tiny grammar/semantic regression and freeze its hashes/evidence. If that passes, proceed to Q05 in the same Goal.

## Q05 resume — same Goal

Reacquire `/data/c16/locks/c16_gpu_campaign.lock` only when the tiny gate and parser/semantic regression have passed.

Frozen scientific identity remains:

```text
Qwen/Qwen2.5-0.5B-Instruct
revision 7ae557604adf67be50417f59c2c2f167def9a775
S2_TEXT
PREFILL
B1 / T2048 / Decode32
FP16 / SDPA
TARGET_ID = Q05_PREFILL_ATTN_FLASH
occurrence = 0
```

Re-resolve function/occurrence binding in the fresh execution. Kernel ID 35 is prior diagnostic evidence, not the authority by itself.

Run one bounded Q05 canary. If it terminal-closes, parser/readability/identity gates pass, and size/headroom remains safe, **continue immediately to formal capture**. Do not stop just because the canary succeeded.

## Formal producer closure — same Goal

For the formal Q05 run, close all existing producer requirements:

```text
terminal observed through real channel protocol
COMPLETE
zero-drop/overflow evidence or exact source-backed native equivalent
kernelslist/member closure
actual traceg parser smoke
full read/decompression
source/archive/build/binary/environment hashes
trace/member/sidecar/bundle hash roots
address/context fields
READY publication through accepted 109 -> 174/node164 pipeline
```

Then update the existing V2 pack and report:

```text
docs/vm_tlb/review_packs/AWMA_SIM_COMPAT_TERMINAL_RECOVERY_109_V2/
docs/vm_tlb/codex_handoff/awma/SIM_COMPAT_TERMINAL_RECOVERY_109_V2_REPORT.md
```

Commit, push, confirm clean status, and STOP only at:

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
TERMINAL_PROTOCOL_SM89_RECOVERED_V2
```

or at an exact fail-closed blocker after bounded recovery.

## What not to redo

Do not repeat already-closed work unless needed for a regression after source changes:

```text
model/input authority archaeology
Q05 scientific target selection
174-new consumer preparation
NEW_SIM_BASELINE qualification
NVBit 1.7.7/1.7.7.1 archive acquisition
initial official mem_trace proof
Native C16WARP1 work
```

Reuse accepted receipts and hashes; only rerun the minimum tests required to prove the modified custom tracer remains correct.

## Downstream boundary

Even after producer PASS, do not generate `SIM_INPUT_ID`, run the 10k Accel-Sim replay, or start TLB/PTW/Cache mechanism sweeps on node109. Those resume on 174-new after independent consumer admission.
