# CODEX_NEXT_STAGE — 174-new Q05 full translation behavior V1

Status: **ACTIVE**

Task:

```text
AWMA_Q05_FULL_KERNEL_TRANSLATION_BEHAVIOR_V1
```

Node:

```text
174-new
ssh root@10.208.130.174 -p 2239
repo = /root/workspace/accel-sim-framework
```

## Objective

Using the already accepted complete Q05 simulator-native trace, determine:

1. where 10k and 50k simulation windows lie inside the complete Q05 kernel;
2. complete-kernel 64 KiB VPN footprint and reuse structure;
3. first-touch versus revisit behavior;
4. translation-fill-before/after behavior;
5. same-page outstanding-translation fanout and waiter depth;
6. whether the current 0% L2-TLB hit observation is better explained by cold start, streaming, pre-fill repeated lookup/fanout, persistent reuse, or a mixture.

This is diagnostic characterization only. Do not implement a new TLB/PTW mechanism.

## Required read order

Fetch:

```text
hrl/awma-q05-representativeness-handoff-v1
```

Read:

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE.md
this file
```

Also inspect the accepted characterization report/review pack at commit:

```text
bb92e5a1559dd7e2b2520e9a7a4937262664512c
```

Create a fresh execution branch/worktree from the coordination branch, recommended:

```text
hrl/awma-q05-full-translation-174new-v1
```

Do not modify the frozen accepted characterization worktree.

## Frozen identities

Do not change:

```text
SIM_INPUT_0ab4e2fe2195d3b7d7da4ee9df6017cbec5c063fcc8110374e1a753f87177634
SIM_BASELINE_6305c065f2c4913448b0cb61a85d5003030c5917cd37d6a346fd3f42939d5964
SIM_RUN_92a553b0d69a9f41c5e20a8650366c53f7fed31c29c7462947d3af03c6f136f1
SIM_EVIDENCE_c8b4175d33f8bed7def2984489eadbdbcdfaffbfcb6a7daef33c8beb18e80959
```

Target:

```text
Qwen/Qwen2.5-0.5B-Instruct
revision 7ae557604adf67be50417f59c2c2f167def9a775
B1 / TEXT / Prefill2048 / Decode32 / FP16 / SDPA
Q05_PREFILL_ATTN_FLASH
function occurrence 0
pytorch_flash::flash_fwd_kernel<...>
```

Do not recapture the workload.

## D0 — authority and trace preflight

Verify:

- branch/worktree/remote state;
- accepted source hashes and review pack;
- complete SIM_INPUT location and node164 durable raw source;
- whole-Q05 completion provenance;
- full CTA count;
- full warp-instruction record count using the actual trace format;
- full memory-reference record count using the actual trace format;
- full unique 64 KiB VPN count.

Determine whether the raw trace file's physical record order is a valid global execution-time order. If this cannot be proven, mark it:

```text
STRUCTURAL_TRACE_ORDER_ONLY
```

and never present offline file order as a cycle timeline.

## D1 — complete-Q05 offline structure

Scan the complete trace without changing simulator behavior.

At minimum derive:

```text
full CTA count
full warp-instruction records
full memory-reference records
full unique 64 KiB translation pages
per-page reference count
per-page CTA count
per-page warp count
per-CTA unique pages
per-warp unique pages
page-popularity distribution
single/low-reuse page fractions
hot-page concentration
```

Keep distinct units distinct. If the trace contains a warp instruction with multiple lane addresses, do not conflate:

- instruction records;
- memory requests/transactions;
- lane-address events.

Required compact outputs:

```text
Q05_FULL_TRACE_STRUCTURE.json
VPN_OFFLINE_FOOTPRINT.tsv
VPN_POPULARITY.tsv
TRACE_ORDER_SEMANTICS.md
```

Large tables may live on node164 with a Git index/hash.

## D2 — cycle-ordered translation telemetry audit

Inspect existing simulator telemetry and source semantics.

The desired cycle-ordered event association is at least:

```text
sim_cycle
translation key
VPN/page size
requester identity at a provable simulator granularity
L1 lookup/result
L2 lookup/result
translation-MSHR allocate or merge
walk start
walk completion
translation fill
requester completion
```

Use the simulator's real translation key. If it includes ASID/epoch/page size, preserve those fields. Only simplify to VPN after proving this workload is single-ASID/single-epoch for the relevant interval.

If current telemetry is insufficient, diagnostic-only logging/counters may be added.

They must not alter:

```text
TLB lookup/arbitration/replacement
latencies
translation-MSHR semantics
PWQ/walker/PWC behavior
page-table semantics
PTE memory traffic
scheduler
cache or memory timing
```

Any rebuilt instrumentation binary must be labeled:

```text
DIAGNOSTIC_INSTRUMENTED_BINARY
```

with its own SHA.

## D3 — timing-neutrality/equivalence gate

If instrumentation changes are made, first replay R0 10k and compare against accepted R0.

At minimum compare:

```text
gpu_sim_cycle
gpu_sim_insn
gpu_tot_issued_cta
translation lookup count
L1 access/hit/miss
L2 access/hit/miss
L2 port denial
translation-MSHR alloc/merge/full/HWM
walk start/complete
PWC counters
PTE request/response
requester latency decomposition
```

Scientific execution results must remain identical. New diagnostic output and wall-clock runtime differences are allowed.

If timing or execution order changes:

```text
STOP_FOR_SCIENTIFIC_REVIEW
```

Do not silently redefine the experiment.

## D4 — 10k and 50k coverage framework

For R0, calculate comparable coverage metrics against the complete Q05 denominator:

```text
CTA issued coverage
CTA completed coverage
warp-instruction trace coverage
memory-reference trace coverage
unique 64 KiB page coverage
```

Do not use:

```text
gpu_sim_insn / raw trace record count
```

as a coverage ratio unless source audit proves identical units; currently it is not accepted as such.

Required output:

```text
Q05_WINDOW_COVERAGE.tsv
```

with rows for at least 10k and 50k; add `full` after successful natural completion.

## D5 — per-translation behavior

For every observed translation key, derive where possible:

```text
first_request_cycle
first_miss_cycle
translation_allocate_cycle
walk_start_cycle
walk_complete_cycle
translation_fill_cycle
request_count_total
requests_before_fill
requests_after_fill
mshr_merge_count
max_waiter_depth
post_fill_L1_hits
post_fill_L2_hits
post_fill_misses
first_post_fill_revisit_cycle
last_request_cycle
```

Also derive distributions for:

```text
first-touch time
unique-page growth
pre-fill fanout
waiter depth
translation lifetime
post-fill reuse
page revisit interval
post-fill TLB outcome
```

## D6 — complete Q05 R0 natural-completion replay

After any instrumentation equivalence gate passes, attempt exactly one R0 replay to natural Q05 kernel completion.

Do not run I0/P2/M8 again merely for symmetry.

The purpose is to close complete-kernel coverage and behavior, not to start a mechanism study.

On successful natural completion, populate:

```text
full cycle count
full CTA issued/completed
full warp-inst denominator/coverage
full memory-reference denominator/coverage
full unique-page denominator/coverage
```

If full simulation cannot finish within reasonable existing project resources, do not fabricate full timing. Complete the full offline trace analysis and the 10k/50k ordered analysis, record the exact blocker, and classify:

```text
FULL_TRACE_ANALYZED_FULL_SIM_INCOMPLETE
```

This is a scoped result, not an automatic scientific failure.

## D7 — classification

Use evidence to classify behavior as one or more of:

```text
COLD_FIRST_TOUCH_DOMINANT
STREAMING_LOW_REUSE
BURST_FANOUT_DOMINANT
PERSISTENT_POST_FILL_REUSE
MIXED
INCONCLUSIVE
```

Do not infer streaming merely from `L2 hits = 0`.

The report must explicitly answer:

1. how many 10k L1 misses are first-touch requests;
2. how many corresponding L2 misses occur before translation fill;
3. whether the same pages receive substantial post-fill accesses;
4. whether post-fill accesses predominantly hit L1/L2 TLB or miss again;
5. how unique-page coverage grows at 10k, 50k and through the full kernel/available prefix;
6. how fanout/waiter depth behaves outside the first 10k window;
7. whether current evidence supports a capacity, cold, streaming, fanout, or mixed interpretation.

## Storage

Place large raw timelines/logs under a dedicated node164 directory, recommended logical name:

```text
awma_q05_full_kernel_translation_analysis_v1
```

Use the actual mounted durable root discovered from existing contracts; do not invent a new storage root.

Git contains compact summaries, schemas, source anchors, hashes and indexes only.

## Deliverables

Report:

```text
docs/vm_tlb/codex_handoff/awma/
Q05_FULL_KERNEL_TRANSLATION_BEHAVIOR_174NEW_V1_REPORT.md
```

Review pack:

```text
docs/vm_tlb/review_packs/
AWMA_Q05_FULL_KERNEL_TRANSLATION_BEHAVIOR_174NEW_V1/
```

At minimum include:

```text
README.md
SOURCE_ANCHORS.md
COUNTER_DEFINITIONS.tsv
TRACE_ORDER_SEMANTICS.md
Q05_FULL_TRACE_STRUCTURE.json
Q05_WINDOW_COVERAGE.tsv
VPN_BEHAVIOR_SUMMARY.tsv
FIRST_TOUCH_REVISIT.tsv
TRANSLATION_FANOUT.tsv
WARM_AFTER_FILL.tsv
COLD_STREAMING_DECISION.md
RAW_DATA_INDEX.tsv
RUN_RECEIPTS.json
SHA256SUMS
```

## Execution policy

Routine engineering problems are solve-and-continue.

Stop only for scientific-contract changes, identity changes, translation semantic changes, non-neutral instrumentation, or unresolvable provenance ambiguity.

## STOP boundary

Success marker:

```text
AWMA_Q05_FULL_KERNEL_TRANSLATION_BEHAVIOR_V1_COMPLETE_WITH_SCOPE
```

Then:

```text
review pack
report
hashes
commit
push
remote verify
clean worktree
STOP
```

Do not begin L2-TLB latency, PTW fixed-latency, capacity, walker, page-size, Segment or new-mechanism experiments.
