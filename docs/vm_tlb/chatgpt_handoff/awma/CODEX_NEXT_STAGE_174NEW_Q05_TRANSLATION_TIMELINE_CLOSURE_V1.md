# CODEX NEXT STAGE — 174-new Q05 Translation Timeline Closure V1

## Status

ACTIVE after reading the coordination handoff.

Stage:

```text
AWMA_Q05_TRANSLATION_TIMELINE_CLOSURE_V1
```

Node:

```text
174-new / port 2239
```

This is diagnostic characterization only. It is not a mechanism experiment.

## Start point

Previous accepted 174-new result:

```text
branch = hrl/awma-q05-full-translation-174new-v1
HEAD   = 6415d3f1
```

Create a fresh branch/worktree from `6415d3f1`:

```text
hrl/awma-q05-translation-timeline-174new-v1
```

Do not modify the frozen accepted characterization or previous-stage worktrees.

## Frozen scientific identity

Keep unchanged:

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
batch      = 1
prefill    = 2048
decode     = 32
dtype      = FP16
backend    = SDPA

Q05_PREFILL_ATTN_FLASH
function occurrence = 0
```

Frozen SIM_INPUT:

```text
SIM_INPUT_0ab4e2fe2195d3b7d7da4ee9df6017cbec5c063fcc8110374e1a753f87177634
```

Accepted base characterization anchor:

```text
bb92e5a1559dd7e2b2520e9a7a4937262664512c
```

Accepted core/runtime semantics remain those already documented in `CURRENT_STATE.md`.

## Scientific objective

Close the unresolved dynamic questions:

1. What fraction of translation requests are first touches?
2. For each translation key, how many requesters arrive before translation resolution/fill?
3. After fill, how often is the same key revisited?
4. Are post-fill revisits L1 hits, L2 hits, or misses?
5. How does the unique translated-page set grow with simulator cycle?
6. Where do the existing 10k and 50k windows sit by same-unit warp-instruction, memory-instruction and translated-page coverage?
7. Is the Q05 behavior primarily cold/front-loaded, streaming/low-reuse, pre-fill burst fanout, persistent post-fill reuse, or MIXED?

Do not answer these by structural file order.

## D0 — Source audit before implementation

Read the actual VM/TLB source at the frozen core semantics and identify:

- the real translation key/tag type used at L1/L2 TLB and translation-MSHR lookup;
- whether ASID, page size, epoch or other fields are part of the key;
- the exact program points for:
  - translation request entry;
  - L1 lookup result;
  - L2 lookup result;
  - translation-MSHR allocate;
  - translation-MSHR merge;
  - walker start;
  - walker completion / translation resolution;
  - TLB fill/insertion;
  - requester completion;
- the exact point where one warp-instruction record can be counted in a unit that closes against the full trace denominator;
- the exact point where one memory-instruction record can be counted in a unit that closes against the full trace denominator.

Write:

```text
SOURCE_AUDIT_TRANSLATION_TIMELINE.md
```

If a requested event cannot be identified unambiguously from source, preserve that uncertainty instead of inventing a semantic.

## D1 — Diagnostic-only instrumentation design

Add telemetry that is:

```text
disabled by default
read-only with respect to simulated state
no scheduling changes
no latency changes
no queue changes
no replacement changes
no TLB/MSHR/walker/page-table changes
```

Prefer one explicit diagnostic enable flag or environment-controlled output path.

The instrumented binary must have a new SHA and must be labeled:

```text
DIAGNOSTIC_INSTRUMENTED_BINARY
```

Do not replace the accepted qualified-binary identity.

### Minimum translation event schema

For each event, record only fields actually available/proven by source. Target schema:

```text
sim_cycle
event_type
translation_key
page_size
vpn_or_internal_tag
request_id if available
shader/core id if available
warp/requester id if available
result/status
waiter_depth if available
```

Required event types where source semantics permit:

```text
REQUEST
L1_HIT
L1_MISS
L2_HIT
L2_MISS
MSHR_ALLOC
MSHR_MERGE
WALK_START
WALK_COMPLETE
TRANSLATION_RESOLVED_OR_FILL
REQUEST_COMPLETE
```

If the implementation has separate L1/L2 fill events, record them distinctly rather than collapsing them.

The scientific analysis must use the simulator's real translation key, not guessed VPN-only grouping.

### Coverage counters

Add diagnostic counters only at source locations where the unit can be proven:

```text
completed_or_consumed_warp_instruction_records
completed_or_consumed_memory_instruction_records
unique_translation_keys_touched
```

The full natural run must close the warp/memory counters against the already accepted structural denominators before 10k/50k coverage percentages are reported.

Accepted structural denominators:

```text
warp-instruction records   = 13,361,600
memory-instruction records = 971,824
unique offline 64KiB VPN   = 228  # cross-check only; not automatically the simulator-key denominator
```

If the cycle-keyed simulator translation-key set differs from the offline 228-page set due to scope/key semantics, explain the difference and use a scientifically consistent full-run denominator.

## D2 — Strict neutrality gate

Before using any new telemetry scientifically, run instrumented R0 for exactly 10,000 cycles.

Compare against the accepted R0 10k result.

At minimum compare exactly:

```text
gpu_sim_cycle
gpu_sim_insn
gpu_tot_issued_cta
translation lookup requests
L1 access/hit/miss
L2 access/hit/miss
L2 port-denial events
translation MSHR alloc/merge/full/HWM
walk start/complete
PTE request/response
PWC counters
requester latency total and components
max waiter depth
```

Expected core baseline includes:

```text
gpu_sim_cycle = 10000
gpu_sim_insn  = 1084480
issued CTA    = 70
L1            = 930 / 805 / 125
L2            = 125 / 0 / 125
MSHR          = 19 alloc / 106 merge / 0 full
walks         = 19 / 19
max waiter    = 35
```

Scientific counters and progress must be bit-identical unless the existing review pack documents a formatting-only difference.

Wall-clock execution time may change.

If simulated scientific results change:

```text
STOP_FOR_SCIENTIFIC_REVIEW
```

Do not continue to 50k/full and do not modify the scientific contract to make the gate pass.

Output:

```text
INSTRUMENTATION_NEUTRALITY.tsv
INSTRUMENTATION_NEUTRALITY.md
```

## D3 — Cycle-keyed 10k replay

After neutrality PASS, analyze the 10k event stream.

For each translation key derive:

```text
first_request_cycle
first_miss_cycle
first_mshr_alloc_cycle
first_walk_start_cycle
walk_complete_cycle if applicable
translation_resolution/fill_cycle
request_count_total
requests_before_resolution
requests_after_resolution
merge_count
max_waiter_depth
first_post_fill_request_cycle
post_fill_L1_hits
post_fill_L2_hits
post_fill_misses
last_request_cycle
```

Answer explicitly:

```text
How many of the 125 miss requesters are first-touch requesters?
How many are repeated same-key requests before resolution?
How many requests to those keys occur after fill?
What happens to those post-fill requests?
```

Do not assume all 106 merges are identical to all possible pre-fill repeated accesses unless event-key/cycle evidence proves it.

## D4 — 50k replay

Run the same diagnostic R0 at 50,000 cycles.

Report:

- unique translation keys seen by 10k and 50k;
- unique-page/key growth;
- first-touch fraction;
- pre-fill versus post-fill request fractions;
- fanout distribution;
- translation lifetime distribution;
- post-fill hit distribution;
- coverage counters if same-unit closure is proven.

Do not compare 10k and 50k as if they execute identical work prefixes under other variants. This track is R0-only.

## D5 — Natural-completion diagnostic replay

Run one diagnostic R0 to natural Q05 completion if the 10k neutrality gate passed.

Previous uninstrumented natural completion:

```text
885,681 cycles
224 issued CTA
368,696,302 completed active thread-instructions
```

The instrumented natural completion must preserve the same simulation result. If not:

```text
STOP_FOR_SCIENTIFIC_REVIEW
```

Use the complete run to establish full-run denominators and complete translation-key statistics.

For valid same-unit coverage, require closure such as:

```text
full diagnostic warp-record counter == 13,361,600
full diagnostic memory-record counter == 971,824
```

If exact equality is not semantically appropriate, do not force it; document the source-level reason and leave that coverage dimension unavailable.

## D6 — Required scientific products

Generate at least:

```text
Q05_CYCLE_KEYED_COVERAGE.tsv
TRANSLATION_KEY_SUMMARY.tsv
TRANSLATION_EVENT_SCHEMA.md
FIRST_TOUCH_BY_WINDOW.tsv
PREFILL_FANOUT_BY_KEY.tsv
POST_FILL_REUSE.tsv
UNIQUE_PAGE_GROWTH.tsv
TRANSLATION_LIFETIME.tsv
Q05_TRANSLATION_BEHAVIOR_DECISION.md
```

Large event logs must stay on node164 with path/size/SHA index.

### `Q05_CYCLE_KEYED_COVERAGE.tsv`

At minimum:

```text
window  cycles  issued_cta  warp_record_coverage  memory_record_coverage  unique_key_coverage
10k
50k
full
```

Unavailable fields are acceptable only with a concrete source-semantic reason.

### `Q05_TRANSLATION_BEHAVIOR_DECISION.md`

Allowed classifications:

```text
COLD_FRONT_LOADED
STREAMING_LOW_REUSE
PREFILL_BURST_FANOUT
PERSISTENT_POST_FILL_REUSE
MIXED
INCONCLUSIVE
```

Multiple traits may be reported.

The document must answer:

1. Is the 10k 0%-L2-hit observation mainly a pre-fill phenomenon?
2. Once a key resolves, is it substantially reused?
3. Are new pages/keys still entering materially after 10k/50k?
4. Is TLB capacity pressure evidenced by actual eviction/reuse behavior, or still unsupported?
5. Does outstanding-translation fanout remain the dominant structural signal over the full kernel or mainly the front of execution?

## D7 — No mechanism experiments

Explicitly forbidden:

```text
L2-TLB latency changes
TLB capacity changes
TLB port changes
PTW mode changes
walker changes
MSHR capacity changes
page-size changes
Segment
early coalescing/outstanding-detection implementation
cache changes
```

Do not run I0/P2/M8 unless required only as an existing-result cross-check. No new scientific variant matrix is authorized.

## Deliverables

Report:

```text
docs/vm_tlb/codex_handoff/awma/
Q05_TRANSLATION_TIMELINE_CLOSURE_174NEW_V1_REPORT.md
```

Review pack:

```text
docs/vm_tlb/review_packs/
AWMA_Q05_TRANSLATION_TIMELINE_CLOSURE_174NEW_V1/
```

Large raw root:

```text
/root/share/mnt164/huangrulin/awma_q05_translation_timeline_closure_v1/
```

or an equivalent existing AWMA durable namespace, recorded exactly in `RAW_DATA_INDEX.tsv`.

Review pack must include at least:

```text
README.md
SOURCE_ANCHORS.md
SOURCE_AUDIT_TRANSLATION_TIMELINE.md
TRANSLATION_EVENT_SCHEMA.md
INSTRUMENTATION_NEUTRALITY.tsv
INSTRUMENTATION_NEUTRALITY.md
Q05_CYCLE_KEYED_COVERAGE.tsv
TRANSLATION_KEY_SUMMARY.tsv
FIRST_TOUCH_BY_WINDOW.tsv
PREFILL_FANOUT_BY_KEY.tsv
POST_FILL_REUSE.tsv
UNIQUE_PAGE_GROWTH.tsv
TRANSLATION_LIFETIME.tsv
Q05_TRANSLATION_BEHAVIOR_DECISION.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

## Execution policy

Routine instrumentation/build/parser/log-volume issues are solve-and-continue.

Stop only if:

- instrumentation changes simulated scientific behavior;
- the actual translation-key semantics cannot be established;
- producing the required timeline would require changing TLB/PTW functionality or timing;
- frozen Q05/SIM_INPUT identity cannot be preserved;
- another explicit scientific boundary is reached.

## Completion

Expected marker:

```text
AWMA_Q05_TRANSLATION_TIMELINE_CLOSURE_V1_COMPLETE_WITH_SCOPE
```

Then:

```text
review pack
→ report
→ hashes
→ commit
→ push
→ remote verify
→ clean worktree
→ STOP
```

Do not start the next mechanism experiment.
