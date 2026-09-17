# CODEX NEXT STAGE — 109 Q05 Native Predecessor-Context Characterization V1

## Status

ACTIVE MAINLINE.

Stage:

`AWMA_Q05_NATIVE_CONTEXT_CHARACTERIZATION_109_V1`

Node:

```text
109 / RTX4080
```

This is the highest-priority GPU task. Do not start any side lane while this Goal is active.

## Start point

Read the ChatGPT coordination branch first:

`hrl/awma-q05-context-warmup-handoff-v1`

Mandatory files:

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md
docs/vm_tlb/chatgpt_handoff/awma/Q05_CONTEXT_WARMUP_EXPERIMENT_CONTRACT_V1.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE.md
```

Recommended execution branch/worktree:

```text
parent = c17df93f9c44aa35d2942ae696bc2bd2a30b3643
branch = hrl/awma-q05-native-context-109-v1
```

The parent contains accepted storage/data-plane support and does not modify the frozen simulator-native producer semantics. The Decode Flash `LDC.U8` blocker is deferred and must not be repaired in this Goal.

## Frozen scientific identity

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
scenario   = S2_TEXT
batch      = 1
input      = exact frozen TEXT binding
prefill    = 2048
decode     = 32
dtype      = FP16
backend    = SDPA

target     = Q05_PREFILL_ATTN_FLASH
function occurrence = 0
exact kernel family = pytorch_flash::flash_fwd_kernel<...>
```

Reference accepted full census:

```text
hrl/awma-qwen25-s2-census-109-v1
678d7b491d4788369ca0c22717453b20846ab195
```

Existing Q05 historical global launch numbers may be used as navigation only. Re-close target identity in the exact fresh execution whenever a new observer/profiler run is used.

## Scientific objective

Establish the real native predecessor context of Q05 without claiming that page overlap equals TLB residency.

Answer:

1. Which exact CUDA kernels execute immediately before Q05 in the frozen Prefill run?
2. Which Q05 data pages were already touched by those predecessor kernels in the SAME execution context?
3. How far before Q05 was each overlapping page last touched?
4. Does the observed page-overlap opportunity converge with short nested continuous predecessor windows?
5. Does normal full-application Q05 timing show stable behavior?
6. When supported, does data-cache-sensitive profiling indicate a meaningful difference between preserved-context and profiler-controlled cache conditions?
7. What continuous predecessor windows should be considered for the later expensive simulator warmup study?

This Goal does NOT prove the exact hardware TLB contents at Q05 entry.

---

## D0 — Preflight / authorities / GPU lock

Before using GPU:

- verify branch/worktree clean;
- verify exact model and input receipts;
- verify GPU identity RTX4080 and current driver/runtime;
- check `/data/c16/locks/c16_gpu_campaign.lock` or current formal lock convention;
- do not interrupt another formal campaign;
- verify the accepted S2 full launch inventory on node164 and its hashes;
- verify the accepted Q05 target identity.

If the frozen workload cannot be reconstructed exactly, STOP_FOR_SCIENTIFIC_REVIEW.

---

## D1 — Exact Q05 predecessor launch sequence

First reuse the accepted S2 census if sufficient.

For the exact Q05 occurrence, produce an ordered launch table from the beginning of the relevant Prefill inference range through Q05.

At minimum record:

```text
relative_position_to_Q05
global_launch_navigation
phase
exact kernel function
normalized family
grid
block
duration_ns from accepted census
deterministic occurrence when provable
```

Do not infer Transformer layer, Q/K/V role, or operator semantics from launch order unless existing NVTX/semantic evidence proves them.

If the accepted census cannot unambiguously bind Q05 in a fresh exact run, perform only the minimal lightweight listing needed to re-close it.

Output:

`Q05_PREDECESSOR_SEQUENCE.tsv`

---

## D2 — Same-run lightweight memory/page observer qualification

The key requirement is SAME-RUN address context across the predecessor window and Q05.

Prefer an already accepted Native/memory-only observer that can capture a contiguous dynamic-kernel range while preserving per-kernel identity. Audit existing C16/NVBit infrastructure before writing a new tool.

The observer is for structural address/page evidence only; it is NOT simulator-native instruction trace input.

Minimum required information per memory event where available:

```text
kernel launch identity
kernel-relative or static PC when available
access class/opcode when available
active mask when available
address(es)
access width when proven
```

For the context study, exact addresses and launch identity are mandatory; width/opcode may be UNKNOWN only if the structural page-set computation is unaffected and this limitation is documented.

The observer must not fabricate address/width fields and must not change application semantics.

If no existing observer can capture a bounded contiguous range in one process, a minimal read-only observer may be implemented, but it must first pass a small canary against an already-known target and must remain structurally scoped. Do not modify the accepted Route-B simulator-native producer for this purpose.

---

## D3 — Capture the bounded native predecessor context

Determine Q05's actual number of predecessors inside the explicit Prefill inference range.

Preferred policy:

```text
if predecessor_count <= 64:
    observe the entire contiguous Prefill prefix through Q05
else:
    observe Q05 + the immediate last 64 predecessor launches
    keep the full older launch sequence from census metadata
```

Do not selectively omit interior kernels based on whether they appear useful.

The page-observer capture must include Q05 itself in the same process/context so that predecessor/Q05 address overlap is meaningful.

Large raw belongs on node164 under a new durable mainline namespace with manifest + SHA closure. Do not store it only on 109.

---

## D4 — Page-set and temporal-context analysis

Compute both 64KiB and 4KiB page views when exact addresses permit.

For each launch in the captured prefix:

```text
unique_64K_pages
unique_4K_pages
memory_event_count in the observer's proven unit
```

For Q05, for every page determine:

```text
was_touched_before_Q05
closest_predecessor_launch
kernel_distance_to_Q05
number_of_intervening_unique_pages when computable
number_of_predecessor_launches_touching_this_page
```

Aggregate for nested continuous prefixes:

```text
P1
P2
P4
P8
P16
P32 if available
PFULL = all captured predecessors from the relevant Prefill start
```

For each prefix report:

```text
Q05 64KiB page overlap count/fraction
Q05 4KiB page overlap count/fraction
last-touch distance distribution
```

Important wording:

- call this `PREDECESSOR_PAGE_OVERLAP_OPPORTUNITY`;
- do NOT call it TLB hit rate;
- do NOT claim that a prior page touch survives to Q05.

Output:

```text
Q05_PAGE_SET_SUMMARY.tsv
Q05_PREDECESSOR_PAGE_OVERLAP.tsv
Q05_PAGE_LAST_TOUCH.tsv
PREFIX_OVERLAP_CONVERGENCE.tsv
```

---

## D5 — Normal-context timing stability

Use the exact frozen full application and measure Q05 occurrence 0 in normal program context across independent repetitions.

Prefer the least intrusive existing timing method. Reuse the accepted NSYS methodology if it can reliably identify Q05 without changing workload semantics.

Suggested minimum:

```text
3 warmup application runs when appropriate
5 measured independent runs
```

Report:

```text
Q05 duration per run
mean
median
min/max
coefficient of variation
```

If repeated full profiling is too intrusive, use the best available exact method and document the limitation rather than changing workload identity.

Output:

`Q05_NATIVE_CONTEXT_TIMING.tsv`

---

## D6 — Optional targeted data-cache sensitivity on real GPU

This subsection is SECONDARY to D3/D4 and may run only if the current installed NCU can deterministically target Q05 occurrence 0.

Purpose:

> test whether profiler-controlled data-cache initial-state handling materially changes Q05 hardware timing/traffic.

It is NOT a TLB experiment.

If supported, compare a minimal metric set under application replay with:

```text
cache-control none
vs
profiler default / all
```

Use only metrics actually available on the RTX4080, preferably a small set covering:

```text
kernel duration
L1/TEX traffic
L2 traffic
DRAM bytes/traffic
```

Record exact NCU version, exact command, replay mode, cache-control mode, metrics, and repetitions.

Never describe this as flushing/preserving the TLB unless the tool explicitly proves that behavior.

If exact filtering/replay cannot be made scientifically clean, set:

`NCU_CONTEXT_SENSITIVITY_UNAVAILABLE`

and continue. NCU failure does not block the primary page-context study.

---

## D7 — Prefix recommendation for the next simulator stage

Use the exact continuous sequence and overlap curves to recommend a SMALL set of future warmup-prefix candidates.

Do not automatically choose only overlapping kernels. Candidate prefixes must remain contiguous.

Preferred final set contains at most 4 windows, for example:

```text
ISOLATED_Q05
SHORT_PREFIX
MEDIUM_PREFIX
FULL_AVAILABLE_PREFIX
```

Choose window boundaries from observed convergence/structure, not arbitrary aesthetics.

For each recommended prefix provide:

```text
ordered launch list
kernel count
Q05 64K overlap opportunity
Q05 4K overlap opportunity
estimated capture complexity
known unsupported-opcode risks if visible from existing evidence
```

Output:

`PREFIX_SELECTION_FOR_SIMULATION.md`

Do NOT capture simulator-native predecessor traces in this V1 Goal.

---

## D8 — Required scientific interpretation

The report must distinguish at least:

```text
NO_PREDECESSOR_PAGE_OVERLAP
LIMITED_OVERLAP
SUBSTANTIAL_OVERLAP
STRONGLY_CONTEXT_EXPOSED
```

These are structural context labels only, not direct TLB-residency labels.

Directly answer:

1. How many Q05 64KiB pages were touched before Q05 in the same run?
2. How many were touched by the last 1/2/4/8/16/... predecessor kernels?
3. Are the overlaps dominated by a few immediate predecessors or spread across a long prefix?
4. Is Q05 normal-context duration stable across full-application runs?
5. Does any hardware data-cache sensitivity experiment materially alter duration/traffic?
6. Which continuous prefixes should be taken into simulator-native capture next?

---

## Deliverables

Report:

```text
docs/vm_tlb/codex_handoff/awma/
Q05_NATIVE_CONTEXT_CHARACTERIZATION_109_V1_REPORT.md
```

Review pack:

```text
docs/vm_tlb/review_packs/
AWMA_Q05_NATIVE_CONTEXT_CHARACTERIZATION_109_V1/
```

At minimum:

```text
README.md
SOURCE_ANCHORS.md
WORKLOAD_IDENTITY.json
Q05_PREDECESSOR_SEQUENCE.tsv
OBSERVER_SEMANTICS.md
Q05_PAGE_SET_SUMMARY.tsv
Q05_PREDECESSOR_PAGE_OVERLAP.tsv
Q05_PAGE_LAST_TOUCH.tsv
PREFIX_OVERLAP_CONVERGENCE.tsv
Q05_NATIVE_CONTEXT_TIMING.tsv
NCU_CONTEXT_SENSITIVITY.md   # PASS or UNAVAILABLE with reason
PREFIX_SELECTION_FOR_SIMULATION.md
RAW_DATA_INDEX.tsv
RUN_RECEIPTS.json
SHA256SUMS
```

Large raw stays on node164.

## STOP conditions

STOP_FOR_SCIENTIFIC_REVIEW if continuing would require:

- changing frozen workload/input/model identity;
- guessing Q05 target identity;
- stitching different-process absolute addresses as if same-run context;
- modifying accepted simulator-native trace grammar/producer semantics;
- fabricating memory widths/addresses;
- treating page overlap as proven TLB residency;
- starting a full predecessor simulator-native capture campaign;
- colliding with another formal GPU campaign.

Routine observer/parser/storage problems are solve-and-continue.

## Completion

Expected marker:

`AWMA_Q05_NATIVE_CONTEXT_CHARACTERIZATION_109_V1_COMPLETE_WITH_SCOPE`

Then review pack -> report -> hashes -> commit -> push -> remote verify -> clean worktree -> STOP.
