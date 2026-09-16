# CONTINUE node109 — AWMA terminal recovery V2 after official NVBit 1.7.7.1 canary

## Operator-reported checkpoint to verify locally

The user reports the following progress from the active V2 work on node109. Treat these as a continuation checkpoint, but verify exact local source/build/binary hashes and paths before using them as formal evidence:

```text
- isolated NVBit 1.7.7 and 1.7.7.1 downloaded and SHA-closed
- NVBit 1.7.7.1 repaired the CUDA 12.8 official CUDA_ERROR_INVALID_SOURCE path
- official NVBit 1.7.7.1 mem_trace explicit tool-kernel path terminal-closed twice on RTX4080 vectoradd and emitted real memory records
- explicit load/find/launch plus managed ChannelDev/tool-pthread lifecycle were minimally migrated into the Accel-Sim tracer while preserving the existing payload/grammar
- custom Accel-Sim tracer tiny vectoradd still stalls in the terminal path
- no COMPLETE was fabricated; no Q05 capture was resumed; GPU lock was released
```

This checkpoint is strong evidence that:

```text
RTX4080 / SM89 itself is not the remaining blocker
NVBit 1.7.7.1 explicit tool-kernel launch is viable on this host
Qwen workload identity is not the active problem
remaining blocker is inside the custom Accel-Sim tracer receiver/channel lifecycle
```

Do not declare these conclusions FORMAL until the local receipts/hashes/tests are added to the V2 review pack.

## Scope of the continuation

Stay in the same V2 scientific stage. Do not create a V3 scientific identity and do not change the Q05 target.

The next engineering objective is narrowly:

```text
complete the receiver/channel lifecycle migration
-> tiny vectoradd terminal closure
-> tiny trace grammar/semantics regression
-> repeatability
-> exact Q05 kernel-35 canary
-> formal Q05 producer bundle
```

Do not rerun the 81 MB Q05 capture before the tiny closure gate passes.

## Required receiver-state migration

Compare the current custom tracer against the verified official NVBit 1.7.7.1 `mem_trace` receiver implementation and the newer Accel-Sim per-context tool patterns.

Migrate the complete semantics-preserving receiver lifecycle required by the verified official path, not just isolated pieces such as:

```text
explicit tool-kernel launch
managed ChannelDev allocation
nvbit_set_tool_pthread registration
```

The migration must also close the thread lifecycle/state protocol, including the equivalent of:

```text
receiver initialized and WORKING
per-kernel receive state armed
payload records consumed
terminal sentinel observed by receiver
per-kernel receive completion acknowledged
context/tool shutdown requests STOP
receiver drains/exits safely
receiver publishes FINISHED
host joins/destroys channel only after FINISHED
```

Use the actual official 1.7.7.1 source semantics as authority for implementation details. The names `WORKING`, `STOP`, `FINISHED` are descriptive requirements here; preserve the official behavior even if exact symbol names differ.

Do not copy unrelated official `mem_trace` features and do not alter the Accel-Sim trace payload/grammar unless required by a separately justified compatibility change.

## Concurrency and state requirements

The old V1 global protocol was built around global receiver flags and a global channel. The V2 continuation must explicitly audit whether the verified official lifecycle requires per-context state for correctness.

At minimum verify:

```text
- no stale per-kernel completion flag can satisfy a later kernel
- terminal state is reset before each traced kernel
- receiver cannot exit before consuming the terminal sentinel
- context teardown cannot race with receiver/channel access
- tool-kernel callback re-entry remains suppressed without hiding legitimate target events
- channel destruction occurs only after receiver termination is proven
- xz/file close happens only after per-kernel terminal acknowledgement
```

If per-context state is required, migrate the minimum necessary per-context receiver/channel state. Do not retain global state merely to minimize diff size if it is the demonstrated source of the deadlock.

## Tiny acceptance gate — mandatory before Q05

Use a tiny vectoradd or equivalent micro-canary that exercises the exact custom Accel-Sim channel, writer, terminal and close path.

Required PASS evidence for one run:

```text
1. custom tracer injects and emits real instruction/memory records
2. explicit flush tool kernel launches and completes
3. receiver positively observes the terminal sentinel
4. per-kernel receive completion transitions through the intended state machine
5. writer/xz pipe closes normally
6. process exits without watchdog/forced kill
7. kernelslist + trace member are readable
8. actual Accel-Sim trace parser/grammar smoke passes
9. payload fields/ordering remain compatible with the previously qualified grammar
10. no host-fabricated COMPLETE
```

Then repeat the same tiny test at least twice from a fresh process. The terminal closure must be reproducible, not a one-off success.

A timeout or forced receiver stop is DIAGNOSTIC and does not satisfy this gate.

## Trace-semantics regression

Because the channel/thread lifecycle is changing, compare the successful tiny custom trace against the expected Accel-Sim grammar and, where useful, against the official-canary evidence.

Freeze evidence for:

```text
PC/opcode
register src/dst fields
memory width and memory records
warp/CTA identity
active mask
addresses
instruction ordering
sync/control records required by the consumer
kernel/list closure
terminal provenance
```

The purpose is not byte-equality with official `mem_trace`; the purpose is to prove that the custom tracer still emits the existing simulator-native Accel-Sim grammar with unchanged scientific semantics.

## Q05 resume gate

Only after the tiny gate is PASS and repeated should GPU work resume on the frozen current-model target:

```text
Qwen/Qwen2.5-0.5B-Instruct
revision = 7ae557604adf67be50417f59c2c2f167def9a775
scenario = S2_TEXT
phase = PREFILL
B1 / T2048 / Decode32
FP16 / SDPA
TARGET_ID = Q05_PREFILL_ATTN_FLASH
occurrence = 0
previously observed diagnostic kernel ID = 35
```

Re-resolve the semantic/function binding in the new process. Do not assume numeric kernel ID 35 without checking; the frozen authority is the workload/target/function/occurrence relation, not the number by itself.

Run one bounded Q05 target canary first. Require genuine terminal closure and parser/readability before the formal run.

If the target canary succeeds, proceed directly to the formal Q05 producer capture in the same Goal. Do not stop merely to report that the canary works.

## Formal producer PASS remains unchanged

The required final state is still:

```text
SIM_COMPAT_CAPTURE_V1_PRODUCER_PASS
TERMINAL_PROTOCOL_SM89_RECOVERED_V2
```

PASS still requires:

```text
exact workload/input/target identity
simulator-native ordered trace
actual parser/grammar smoke
terminal marker observed through the real channel protocol
COMPLETE
source/build/binary/version closure
all kernelslist members present
stable trace/member/sidecar/bundle hashes
zero-drop/overflow evidence or exact source-backed native equivalents
READY publication through the accepted 109 -> 174/node164 pipeline
```

No `SIM_INPUT_ID` is generated on 109. No 10k Accel-Sim replay or mechanism experiment is run on 109.

## V2 evidence updates

Update the existing V2 review pack rather than creating a new scientific stage:

```text
docs/vm_tlb/review_packs/AWMA_SIM_COMPAT_TERMINAL_RECOVERY_109_V2/
```

Ensure it now includes exact evidence for:

```text
NVBit 1.7.7 archive/source/build identities
NVBit 1.7.7.1 archive/source/build identities
official 1.7.7.1 mem_trace two-run terminal closure
CUDA_ERROR_INVALID_SOURCE comparison/repair evidence
custom tracer explicit-tool-kernel migration diff
receiver state-machine migration diff
custom tiny canary repeated closure matrix
tiny parser/grammar regression
Q05 target canary
formal terminal/completeness evidence
```

Continue the same V2 report:

```text
docs/vm_tlb/codex_handoff/awma/SIM_COMPAT_TERMINAL_RECOVERY_109_V2_REPORT.md
```

## Fail-closed rule

Never declare success from:

```text
host timeout
forced receiver shutdown
manual completion-flag clear
successful xz bytes without terminal acknowledgement
process exit alone
absence of an observed crash
```

If the full official receiver lifecycle is migrated and the tiny custom tracer still cannot terminal-close, preserve the full observability trace and classify the next exact blocker before considering any further architecture change.
