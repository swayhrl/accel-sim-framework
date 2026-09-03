# Current state — M4 integration authorization

## Track A

`M1_M3_VM_BASELINE_CLOSEOUT`: **PASS / ACCEPTED / FROZEN**.

Final accepted Core/GPGPU-Sim:

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

Accepted M1-M3 Framework evidence:

`47dde5767af8d30b892c7d63d932455644b7cf3a`

The reusable baseline preserves raw/coalesced SimVA, separate SimPA,
identity-like resident mapping, configurable VA width, 64KB default paging,
32-entry fully-associative per-SM L1 TLB, 768-entry/16-way shared L2 TLB,
32 MSHR/PWQ entries, 16 walkers, real physical/non-recursive PTE L2/DRAM
traffic, FINITE-128 intermediate PWC, and generic 10/80-cycle L1/L2 lookup
service. 2MB and 49-bit directed configurations remain available. Generic
radix/PWC/timing choices are modeling/reference choices, not target-paper exact
facts.

## Track B

`M4A_MERGE_PREP`: **PASS / ACCEPTED FOR INTEGRATION**.

Accepted Framework:

`e21ffebce280e6b932fb4556ef75c609ff54c326`

Accepted integration manifest:

`docs/vm_tlb/review_packs/M4A_MERGE_PREP/INTEGRATION_MANIFEST.md`

Git blob SHA:

`291d749e7b96cc858f09335b052c6e37e5966b98`

Frozen capture executable Framework:

`c79f4469c6a2befa59e4c4efcd3c885dc2259a81`

Model/revision:

`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

Formal semantic kernel counts:

- prefill: 692 COMPUTE + 32 NCCL = 724;
- decode1: 740 COMPUTE + 32 NCCL = 772;
- no semantic MEMCPY/UNKNOWN entries;
- observed NCCL family: one AllReduce BF16 TREE family.

The old filename-only `0 NCCL` classification is superseded.

## Formal address-domain result

Both complete formal ROIs were decoded at active-lane granularity with zero
decoder invariant failures.

- prefill max SimVA `0x7fddf3808007`, required width 47;
- decode1 max SimVA `0x7f81ecb88007`, required width 47;
- both have zero addresses `>=2^49` and zero `>=2^56`.

Therefore paper-facing 49-bit VA mode is authorized for these immutable traces
without masking/truncation/canonicalization. Generic 56-bit mode remains a
reference/diagnostic mode.

## Object-coverage integration recheck

B reported exact-conserving runtime-range Weight/KV/UNKNOWN totals and 64KB/2MB
page footprints. Independent code review identified one safety issue that must
be resolved before object-specific M4 claims: the historical analyzer merges
ranges by object class while its binary-search index assumes globally sorted
starts.

This does **not** invalidate capture integrity, semantic kernel classification,
or the full VA-domain result. The authorized M4 integration begins with
`M4I-RF0`:

- inspect actual formal sidecars;
- prove whether historical B merged range starts were already monotonic;
- globally sort the integration analyzer's merged ranges and assert monotonicity;
- test KV-below-Weight and KV-above-Weight layouts;
- bind resumable partial identity to analyzer/schema + ROI range-map identity;
- reuse B object totals if actual historical ordering was already valid;
- otherwise recompute only the object-specific coverage offline from immutable
  traces before M4C.

No GPU recapture is authorized or needed.

## Current authorization

**M4 integration Goal is AUTHORIZED.**

Entry file:

`docs/vm_tlb/chatgpt_handoff/M4_INTEGRATION_GOAL_START.md`

Evidence-driven overrides:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4_INTEGRATION_AUTHORIZED_ADDENDUM.md`

Prepared detailed contracts are now active under that authorization:

- `M4_INTEGRATION_TO_SEGMENTATION_MASTER.md`
- `M4I_AB_INTEGRATION_AND_REPLAY.md`
- `M4C_LLM_BASELINE_CHARACTERIZATION.md`
- `M4B_SEGMENTATION_REPRODUCTION.md`

Continuous target:

`M4I -> M4R -> M4C -> M4B-P -> M4B-S -> M4B-CLOSEOUT -> STOP before M5`.

Create fresh integration branches/worktrees:

- Framework `hrl/vm-llm-m4b-v0` from the exact Track-A authorization HEAD named
  by the startup command;
- Core `hrl/vm-llm-m4b-v0` exactly from
  `5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`.

Do not wholesale-merge Track B. Use path-scoped import with a manifest.

## Frozen M4 policy decisions

- paper-facing VA width: 49 bits for the accepted formal traces;
- primary paper-facing trace policy: `COMPUTE_ONLY_TP_PARTITION`;
- `FULL_RANK0`: required self-capture sensitivity/provenance path;
- no trace policy is author-exact;
- no synthetic KV in M4C/M4B;
- paper L2-TLB sub-entry details must be audited first; if still unavailable,
  the pre-authorized `REFERENCE_APPROX_SUBENTRY_16` fallback may be used only
  with `PAPER_PAGING_BASELINE_APPROX` labeling;
- Weight Segmentation uses the frozen real contiguous Weight sidecar range;
- Segment and L1 lookup run in parallel; default Segment latency equals accepted
  L1 lookup latency as a modeling decision;
- Segment hit suppresses conventional L2-TLB/MSHR/PWQ/walker/PWC/PTE work and
  does not fill Weight translations into the conventional TLBs;
- Segment miss reuses the already completed L1 result and never re-probes L1.

## Scope boundary

This Goal stops before:

- synthetic long-context / 12K KV pressure;
- KV segmentation;
- new AI-aware mechanisms beyond target Segmentation;
- page fault/migration/UVM;
- MCM/chiplet behavior;
- multi-ASID study.
