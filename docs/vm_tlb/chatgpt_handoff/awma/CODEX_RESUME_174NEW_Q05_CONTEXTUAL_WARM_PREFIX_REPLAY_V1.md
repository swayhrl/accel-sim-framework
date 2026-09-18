# CODEX RESUME — 174-new Q05 Contextual Warm-Prefix Replay V1

Status: ACTIVE MAINLINE.

Stage:

`AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1`

Node:

`174-new / port 2239`

## Start point

Read coordination branch:

`hrl/awma-q05-contextual-replay-handoff-v1`

Then read:

- `docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md`
- `docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md`
- `docs/vm_tlb/chatgpt_handoff/awma/Q05_CONTIGUOUS_PREFIX_CAPTURE_CONTRACT_V1.md`
- this resume file.

Execution parent:

```text
hrl/awma-q05-warm-prefix-replay-174new-v1
5b9d708087e8ff485f03fd561a15e08baea8ad3a
```

Recommended execution branch:

`hrl/awma-q05-contextual-warm-prefix-replay-174new-v1`

## Newly available formal context bundle

Producer/recovery authority:

```text
hrl/awma-q05-prefix-ldc-recovery-109-v1
c6733012c13099c6a86f506fd8c61e351791159e
```

Run ID:

`C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native-contiguous-prefix_q05-contiguous-prefix_20260918T022749Z_1fea2d955d1c`

Durable authority:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native-contiguous-prefix_q05-contiguous-prefix_20260918T022749Z_1fea2d955d1c`

Producer receipt:

```text
file_count      = 114
total_bytes     = 390072942
manifest_sha256 = 5dc4f8d3fc802e6af66ab76f33adfeb31b335d44511ec792404c7210ca04d64e
same context    = ctx_0x5b5ba0bd1a60
members         = 35 / launches 0..34
```

Producer-side destination ACK is PASS, but 174 must independently verify the durable object before scientific replay.

## D0 — Independent consumer admission

From 174-new:

1. verify node164 path exists and is readable;
2. verify manifest SHA256 exactly;
3. verify file count and total bytes;
4. rehash all formal member artifacts or verify the manifest's complete per-file hash ledger independently;
5. verify exactly 35 ordered raw/traceg members, launches 0..34, same CUDA context;
6. verify no missing/duplicate/interior member;
7. verify all terminal receipts are COMPLETE, drop=0, overflow=0;
8. verify the exact repaired-validator source identity used for LDC acceptance.

Do not trust only the producer ACK.

Because the 174 parent branch predates the LDC validator patch, bring forward only the narrow validator/test semantic change from:

`a62f5f778f97c388187b4d674b120ea131be7999`

Prefer a clean cherry-pick if conflict-free, or reproduce the exact two-file source delta with hash/diff evidence. Do not merge unrelated 109 producer/review-pack history into the simulator branch merely to obtain the validator change.

Run the compiled fixtures/full consumer tests on 174.

Output:

- `CONTEXT_BUNDLE_CONSUMER_RECEIPT.json`
- `LDC_VALIDATOR_CONSUMER_RECEIPT.md`

## D1 — Fold the waiting-state F0 semantic cleanup into this real resume

Do not create a separate cleanup stage.

Close the effective F0 kernel-boundary state using actual accepted config + core source.

Required matrix rows, separately:

### L1 data cache

Accepted F0 explicitly sets:

`-gpgpu_flush_l1_cache 1`

Classify as kernel-completion flush/reset under accepted source semantics.

### L2 data cache

Accepted F0 does not override `-gpgpu_flush_l2_cache`.

Accepted core default is:

`-gpgpu_flush_l2_cache = 0`

Therefore effective F0 does **not** flush L2 data cache at kernel completion. Resident/replacement state may persist across dispatch.

### L2 TLB

Direct self-warm runtime evidence:

```text
Q05 #2 L2 TLB = 2922 access / 2922 hit / 0 miss
new walks = 0
```

Classify as persistence demonstrated by self-warm diagnostic under unchanged F0.

### L1 TLB

Do not inherit the L2 dynamic proof as if it directly dumped L1 state.

Use source lifetime/normal-boundary flush audit. If no direct runtime resident dump exists, use:

`PERSISTS_BY_SOURCE_NOT_DIRECTLY_RUNTIME_DUMPED`

### PWC

If source audit confirms persistent translation-controller ownership and no normal kernel-boundary flush, use:

`PERSISTS_BY_SOURCE_PENDING_DIRECT_RUNTIME_OBSERVABILITY`

Do not call it measured residency.

### Translation in-flight state

MSHR/PWQ/walkers must be quiescent/drained at clean kernel completion before the next member is dispatched.

Output:

- `F0_KERNEL_BOUNDARY_STATE_MATRIX_FINAL.tsv`
- `SELF_WARM_INTERPRETATION_FINAL.md`

Self-warm 885681 -> 821426 cycles remains a **combined modeled warm-context effect**, not a translation-only gain, because L2 data-cache state also persists.

## D2 — Recompute translation-relevant page overlap

The producer review pack reports broad same-run trace page overlap:

```text
4 KiB Q05 coverage:
P1  24.724%
P2  49.448%
P4  49.448%
P8  98.896%
P16 99.227%
P34 99.338%

64 KiB Q05 coverage:
P1  24.670%
P2  49.339%
P4  49.339%
P8  98.678%
P16 99.119%
P34 99.559%
```

These numbers are useful but are **not yet accepted as translation-relevant overlap**, because the predecessor-distance table contains low address pages such as `0x0`, indicating that the offline extraction scope may include shared or other non-VM address spaces.

Recompute from the admitted context bundle using the accepted simulator's actual VM entry semantics.

Source authority:

`ldst_unit::memory_cycle()` applies VM translation only when instruction space is one of:

```text
global_space
local_space
param_space_local
```

Exclude:

```text
shared_space
const_space
texture/surface paths that do not enter this VM path
addressless controls
implicit LDC records
```

For generic LD/ST, mimic the accepted trace-driven memory-space resolution using each kernel's shmem/local base headers rather than classifying by opcode prefix alone.

Produce:

- `TRANSLATION_RELEVANT_PAGE_OVERLAP_4K.tsv`
- `TRANSLATION_RELEVANT_PAGE_OVERLAP_64K.tsv`
- `TRANSLATION_RELEVANT_Q05_PAGE_DISTANCE.tsv`
- `PAGE_OVERLAP_SCOPE_AUDIT.md`

Preserve the producer's original overlap tables as broad trace-address evidence; do not rewrite them.

Do not force the historical 228 offline-64KiB-VPN and 240 simulator-key domains into a 1:1 mapping.

## D3 — Context input identities

Create a new immutable context-bundle consumer identity distinct from the old isolated Q05 SIM_INPUT.

For each row define the exact suffix:

```text
P1  = member 33 -> 34
P2  = members 32..34
P4  = members 30..34
P8  = members 26..34
P16 = members 18..34
P34 = members 0..34
```

Each row identity must hash/reference:

- producer bundle manifest SHA;
- exact ordered member list;
- framework/core SHAs;
- accepted F0 config SHA/content;
- address-context policy;
- measurement-boundary contract;
- validator semantic receipt.

Do not modify or supersede historical isolated-Q05 SIM_INPUT/SIM_BASELINE/SIM_RUN/SIM_EVIDENCE.

## D4 — Replay execution contract

Each row starts from a fresh simulator process/state.

Within a row:

```text
fresh simulator
-> execute exact predecessor suffix in order
-> clean kernel completion boundaries under unchanged F0
-> snapshot monotonic counters immediately before member 34/Q05
-> run Q05
-> snapshot immediately after Q05
-> Q05 metric = after - before
```

No reset/flush API may be called merely to mark Q05 entry.

Do not change F0's L1/L2 cache policy or translation behavior.

Run rows serially to avoid host-load interference with engineering observability:

```text
P1
P2
P4
P8
P16
P34
```

The accepted isolated Q05 natural run is the comparison anchor and does not need to be regenerated unless a neutrality/control gate requires it.

If a row fails because an interior member exposes a simulator semantic/parser incompatibility, solve ordinary parser/driver issues only when semantics are source-backed. Stop if continuing requires inventing trace semantics or changing accepted F0 functionality.

## D5 — Q05-only metrics

For every contextual row report Q05-only deltas for at least:

- cycles;
- completed active thread-instructions;
- issued/completed CTA where source-supported;
- L1 TLB accesses/hits/misses;
- L2 TLB accesses/hits/misses;
- translation MSHR allocations/merges/full/HWM;
- walk starts/completions;
- PWC accesses/hits/misses;
- PTE requests/responses;
- PTE L2-only vs DRAM responses;
- requester latency total + L1 queue/service + L2 queue/service + MSHR wait;
- L2 data-cache accesses/hits/misses or closest accepted source-defined counters;
- DRAM request/traffic counters in source-defined units.

Do not use raw REQUEST invocation counts as independent translation-request counts.

## D6 — First-key translation outcome, if source-safe

Because the main scientific question is whether predecessor history removes Q05 first-touch translation work, add read-only target-boundary telemetry only if it can be done timing-neutrally and disabled by default.

Preferred per-key unit:

`{asid, vpn, page_size}`

For each Q05 key, record the first Q05 outcome when directly observable:

- L1 hit;
- L2 hit;
- new miss/walk;
- merged with existing in-flight state if such a state can legally exist at Q05 entry;
- UNKNOWN if source telemetry cannot separate it safely.

Any new instrumentation requires isolated-Q05 neutrality against accepted scientific counters before use.

Do not block the main replay matrix solely because resident-key dumping is unavailable; aggregate TLB/walk deltas remain mandatory.

## D7 — Scientific comparison

Create one summary table with isolated + all contextual rows.

Directly answer:

1. How much does real contiguous predecessor history change Q05 cycles?
2. How do L1/L2 TLB miss counts and walk counts change from isolated -> P1 -> P2 -> P4 -> P8 -> P16 -> P34?
3. Does translation behavior converge by P2/P8, or do longer non-overlapping/polluting predecessors change it again?
4. Does the page-overlap jump near P8 correspond to a drop in simulated first-touch walks/misses?
5. How much of the total cycle change tracks translation counters versus L2 data-cache counters?
6. Is isolated Q05 still representative enough for future TLB/PTW mechanism studies?
7. If not, which shortest contiguous prefix is sufficient as a future contextual baseline?

Important: P4 can differ from P2 even if page overlap is identical, because intervening non-overlapping kernels may evict/perturb warm state. Likewise P16/P34 test pollution/history after page coverage already saturates. Do not drop these rows solely because overlap does not increase.

No new mechanism experiment starts automatically.

## Durable output

Large simulation raw belongs on node164, not 174 local disk.

Use a new durable analysis root, e.g.:

`/root/share/mnt164/huangrulin/awma_q05_contextual_warm_prefix_replay_v1/`

174 local holds source/worktree/small scratch only.

## Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1/`

At minimum:

- README.md
- SOURCE_ANCHORS.md
- CONTEXT_BUNDLE_CONSUMER_RECEIPT.json
- LDC_VALIDATOR_CONSUMER_RECEIPT.md
- F0_KERNEL_BOUNDARY_STATE_MATRIX_FINAL.tsv
- SELF_WARM_INTERPRETATION_FINAL.md
- PAGE_OVERLAP_SCOPE_AUDIT.md
- TRANSLATION_RELEVANT_PAGE_OVERLAP_4K.tsv
- TRANSLATION_RELEVANT_PAGE_OVERLAP_64K.tsv
- TRANSLATION_RELEVANT_Q05_PAGE_DISTANCE.tsv
- CONTEXT_INPUT_IDENTITIES.json
- WARM_PREFIX_RESULTS.tsv
- Q05_TRANSLATION_RESULTS.tsv
- Q05_DATA_CACHE_RESULTS.tsv
- Q05_FIRST_KEY_OUTCOMES.tsv if source-safe
- NATIVE_OVERLAP_VS_SIM_TRANSLATION.tsv
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Success marker:

`AWMA_Q05_CONTEXTUAL_WARM_PREFIX_REPLAY_174NEW_V1_COMPLETE_WITH_SCOPE`

Then report -> review pack -> hashes -> commit -> push -> remote verify -> clean worktree -> STOP.
