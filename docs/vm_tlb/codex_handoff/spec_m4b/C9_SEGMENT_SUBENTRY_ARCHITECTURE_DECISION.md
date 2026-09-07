# C9：Weight Segment / Sub-entry 架构决策

Goal：`C9_SEGMENT_SUBENTRY_ARCHITECTURE_DECISION`

状态：`READY_TO_EXECUTE / DESIGN_ONLY / SPECULATIVE_CANDIDATE`。

## 1. 目的

C8 已证明当前 speculative implementation 有分析机会，但还不能作为合理、可实现且公平比较的 GPU translation architecture；唯一 C5 gate 为 `ARCHITECTURE_DECISION_REQUIRED`。

C9 不实现代码、不跑 simulator。唯一目标是把 C8 的开放问题收敛成一套足以指导下一受控模型实现轮（未来 C10）的 architecture specification，并明确哪些决定来自论文 `PAPER_SPEC`、哪些是本项目 `MODEL_DECISION`。

## 2. 冻结输入

Framework：
- branch：`hrl/vm-m4b-speculative-v0`
- C8 HEAD：`468fe62ddc1c4d1786133072b540e52e0d8bdc23`

Core frozen implementation：
- repo：`swayhrl/gpgpu-sim`
- branch：`hrl/vm-m4b-speculative-v0`
- SHA：`c21137bcb86010215c008292f272aacefac175d3`

Authoritative evidence：
- `docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C8_HARDWARE_COST_AND_MODEL_RISK_AUDIT/`
- C7/C4/C3/C1 review docs
- `docs/vm_tlb/paper_specs/SEGMENTATION_LLM_2026.md`

External Window-A progress evidence (read-only context only)：
- branch：`hrl/vm-llm-m4b-c3-progress-review-20260907`
- SHA：`73d25ebbdd96833ee1ddb8ea42b9017cefbceb75`

A evidence shows large decode translation headroom and a smaller generic prefill penalty at the checkpoint. It is motivation/context only; do not tune C9 parameters to match A IPC/cycle numbers and do not pool A/C counts.

## 3. Hard boundary

C9 is design-only. Forbidden：
- modifying Core or Framework functional simulator code;
- rebuild;
- simulator/C5 replay;
- trace generation/full trace scan;
- PPA/synthesis heavy run;
- Window A/B process/worktree/scratch access;
- implementing KV segmentation/12K/M5.

Allowed：
- source/spec inspection;
- symbolic bit/port/latency models;
- small scripts/tables;
- architecture state/sequence diagrams;
- deterministic calculation of equal-bit budgets from source/config facts.

If a required field width or implementation fact cannot be recovered, mark `UNKNOWN` and give a bounded formula; do not invent precision.

## 4. Evidence hierarchy

Every architecture statement must be labeled as one of：
- `PAPER_SPEC`
- `EXISTING_MODEL_FACT`
- `USER_APPROVED_DIRECTION`
- `C9_MODEL_DECISION`
- `UNKNOWN`

Important paper facts to preserve：
- weights are read-only and long-lived during inference;
- serving framework places weights in a large virtually contiguous buffer;
- segmentation requires virtual and physical contiguity for complete paging bypass;
- descriptor stores base/limit/offset semantics;
- L1 TLB and Segment lookup may operate in parallel; Segment hit masks/discards conventional result and bypasses paging;
- typical one model needs one weight segment; multiple colocated models use a small descriptor count (paper discusses roughly 2--8);
- baseline uses 64KiB pages, 32-entry L1 TLB, 768-entry 16-way L2 TLB and 16 walkers.

Unknown paper details remain UNKNOWN; do not upgrade them to paper-exact.

## 5. Weight Segment architecture decisions

C9 must resolve W1--W7 from C8 and produce one internally consistent first-version design.

### W-A: real VA->PA mapping form

The current identity-like `ppn=vpn` is forbidden as the architecture mapping.

Preferred first-version architecture：a privileged runtime/driver registers physically contiguous weight extents. A descriptor represents at least：
- valid;
- context/ASID identity;
- VA base and VA limit/size;
- PA base or equivalent signed offset;
- permission/read-only state;
- mapping/page-size class if needed;
- epoch/version for stale protection.

Hit translation is equivalent to：
`PA = PA_base + (VA - VA_base)`
or a mathematically identical base+offset representation.

If a model allocation is not one physically contiguous extent, split it into multiple descriptors; do not silently fall back to identity mapping.

C9 must decide exact descriptor semantics and symbolic bit formula.

### W-B: trustworthy classification / installation provenance

Hardware must not infer `OBJECT_WEIGHT` from simulator metadata.

Preferred contract：
- serving runtime requests Weight-region registration;
- privileged driver validates the allocation/mapping/context;
- driver installs context-bound descriptor(s);
- simulator object map remains telemetry/classification evidence only.

C9 must define install/remove authority, permission checks, error/fallback behavior, and what happens when descriptor capacity is exceeded.

### W-C: placement, capacity and lookup topology

The current software vector is not a hardware topology.

C9 must compare and select one first-version placement among at least：
- per-translation-cluster replicated small table;
- shared banked table;
- hierarchical/indexed table.

Working preference is a small table local to each translation/L1-TLB cluster so each cluster can sustain its local translation ingress without a central bottleneck. Paper's typical descriptor count is small; C9 must explicitly evaluate N=1/4/8/16/64 and choose one nominal first-version capacity (8 or 16 should be considered, not assumed).

For the selected design specify：
- descriptor storage formula;
- comparator/index topology;
- requests accepted per cycle per cluster/table;
- replication/broadcast/update cost proxy;
- queue/bank conflicts, if any;
- latency decomposition or parameterization.

No fake area/power number is allowed.

### W-D: parallel L1/Segment completion policy

Current wait-both behavior may penalize L1 hits if Segment becomes slower or queues.

C9 must choose and specify an exact policy. Preferred policy to analyze is `HIT_FIRST / MISS_JOIN`：
1. L1 and Segment launch in parallel.
2. Segment hit may complete translation immediately and suppress conventional lower translation/fills.
3. L1 hit may complete immediately without waiting for a slower Segment lookup; a late Segment result must not mutate the completed request.
4. If L1 misses while Segment is unresolved, wait for Segment before launching conventional L2 so a valid Segment hit is not lost.
5. If Segment misses while L1 is unresolved, wait for L1.
6. Only after both miss does conventional L2/PTW proceed.
7. If both produce a mapping for the same request, mappings must be consistent; define assertion/error behavior.

If C9 rejects this policy, it must show why and provide an alternative that does not add unjustified serial latency to ordinary L1 hits.

### W-E: throughput and latency model

Do not treat 10 cycles as a hardware fact.

C9 must specify：
- throughput contract, preferably at least 1 lookup/cycle per selected local cluster interface unless a queue model is explicitly chosen;
- parameterized lookup latency;
- nominal reproduction point and sensitivity points (e.g. 5/10/20 cycles or a justified alternative);
- how compare, permission/epoch, PA add, routing and queue delay compose.

The future model must expose queue/backpressure if the chosen topology cannot accept every local request.

### W-F: lifecycle / context / migration

Preferred first-version contract is a pinned immutable inference epoch：
- model load / allocation;
- driver pins or otherwise guarantees descriptor mapping stability;
- descriptors installed before the inference epoch;
- active descriptors immutable during that epoch;
- migration/remap/free/context teardown requires descriptor invalidate/revoke before mapping changes;
- context/ASID + epoch/version prevents stale reuse;
- completion/barrier semantics defined for install/remove.

C9 must spell out context switch, ASID reuse, model unload and failure/fallback behavior. Full arbitrary dynamic remapping need not be supported in v1 if the restriction is explicit and correct.

### W-G: multi-model scalability

Using selected descriptor capacity/topology, instantiate storage/comparator/port scaling for N=1/4/8/16/64 and distinguish：
- active-context capacity;
- per-cluster replication;
- update broadcast;
- overflow fallback to conventional paging.

## 6. Sub-entry architecture decisions

### S-A: fair bit budget

The current 768-group reference model must not be used as a same-cost performance baseline against 768 exact entries.

C9 must recover or symbolically define the hardware-relevant state bits for：
- baseline exact L2 TLB entry/tag/PPN/context/page-size/valid/replacement;
- one sub-entry group tag/context;
- 16 leaf valid bits and translation payload/state;
- replacement metadata;
- any actual hardware state required by lookup/fill/invalidation.

Telemetry-only object attribution bits must be excluded from architecture cost.

Compute or derive：
`G_equal_bit = max G such that B_subentry(G) <= B_exact_baseline`.

If concrete widths are available, publish a concrete G. Otherwise publish a bounded formula and list the only unresolved widths.

### S-B: baseline comparison policy

Freeze the following comparison classes：
1. paper/baseline exact 64KiB L2 TLB;
2. expanded exact L2 TLB under the same bit budget as the candidate;
3. sub-entry with `G_equal_bit` groups;
4. leaf-capacity-matched exact TLB diagnostic (not equal-cost);
5. PWC expansion under an explicitly comparable total translation-state budget;
6. 2MiB page diagnostic/alternative with explicit allocator/page-policy caveat;
7. Weight Segment;
8. equal-bit Sub-entry + Weight Segment combined design, with Segment storage charged rather than free.

No result may call the old 768-group configuration equal-cost.

### S-C: lookup/fill/invalidation semantics

Specify：
- base-tag compare and leaf select;
- hit critical path/latency parameterization;
- existing-group leaf fill;
- group replacement;
- leaf/group invalidation;
- ASID/context and shootdown;
- racing fill/update rules;
- interaction with 2MiB pages.

For v1 it is acceptable to keep sub-entry 64KiB-only if 2MiB is retained as an explicit alternative baseline rather than silently excluded from comparison.

## 7. A checkpoint implications for architecture design

C9 must include a short section interpreting A only as motivation：
- decode generic/paper show large translation overhead relative to ideal/disabled;
- paper having fewer misses but worse cycles than generic demonstrates that hit-rate-only optimization is insufficient;
- future C model/reporting must retain queue/backpressure/latency/stall observables, not just miss rate;
- prefill-paper was nonterminal at A checkpoint, so no final paper-vs-generic prefill statement is allowed.

Do not calibrate Segment latency or Sub-entry capacity to reproduce A's observed ratios.

## 8. Output

Create：
`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C9_SEGMENT_SUBENTRY_ARCHITECTURE_DECISION/`

At minimum：
- `README.md`
- `INPUT_PROVENANCE.tsv`
- `ARCHITECTURE_DECISION_RECORD.md`
- `WEIGHT_SEGMENT_ARCHITECTURE_SPEC.md`
- `SEGMENT_DESCRIPTOR_AND_LIFECYCLE.md`
- `SEGMENT_LOOKUP_ORDERING_AND_THROUGHPUT.md`
- `SUBENTRY_EQUAL_BIT_BUDGET.md`
- `FAIR_BASELINE_POLICY.md`
- `A_CHECKPOINT_IMPLICATIONS.md`
- `C10_IMPLEMENTATION_REQUIREMENTS.md`
- `FINAL_REPORT.md`

Small scripts/tables used for symbolic bit math are allowed; no functional implementation changes.

## 9. C10 implementation requirements preview

C9 must produce a bounded future implementation delta, including：
- which current C3/C2 shortcuts must be replaced;
- config/interface changes;
- new state/queues if selected architecture requires them;
- directed tests for mapping, context, lifecycle, first-hit/miss-join ordering, queue conflicts and equal-bit sub-entry;
- standard-mode regression invariants;
- how C4/C7 old evidence will be retained as historical evidence but not reused as post-C10 performance result.

Do not implement any of this in C9.

## 10. Final status

C9 must choose exactly one：
- `ARCHITECTURE_READY_FOR_MODEL_IMPLEMENTATION`
- `ARCHITECTURE_DECISION_STILL_OPEN`

`ARCHITECTURE_READY_FOR_MODEL_IMPLEMENTATION` requires real PA mapping, trusted registration, table topology/capacity, ordering/throughput, lifecycle and equal-bit sub-entry policy all closed with no unresolved issue that would materially change C5 performance.

Commit/push and STOP. Do not auto-start C10 or C5.

Keep labels `REFERENCE_APPROX_SUBENTRY_16` and `SPECULATIVE_CANDIDATE` for historical C1--C8 evidence; C9 architecture spec is a new design decision, not paper-exact evidence.