# Downstream NVBit capture-scope decision

Decision: **adjust the formal C16 contract before broad Qwen/DeepSeek/GLM
capture.**  Retain Route A as a low-cost case-study tier, make Route B the
normal first formal tier for representative kernels, and reserve a bounded
Route C validation slice for claims that need workload-level coverage.

| Route | Answers | Does not answer | Relative raw/capture cost | TLB/Cache value |
|---|---|---|---|---|
| A: selected representative target PCs | Parser compatibility; a narrowly defined spatial/locality case study; cross-step set overlap if the *same* PC is captured at each step | Whole-kernel/model footprint, operator coverage, temporal cache behavior | Lowest | Useful screening only; object map optional for address shape but required for semantic attribution |
| B: all explicit global-memory instructions in representative kernels | Per-kernel line/page footprint; instruction mix; kernel-level hot sets and set overlaps | ROI-wide coverage; global L2 arrival/reuse without a qualified order producer | Moderate | Recommended formal default for structural TLB/Cache questions; needs C16 object-map snapshot for semantic rows |
| C: bounded ROI-wide address capture | Phase/ROI coverage audit; contribution of kernels excluded by B; evidence for workload-level structural statements | Hardware TLB misses/PA locality/global L2 MRC unless separately measured/proven | Highest; enforce C16 4GiB/20min window and 64GiB wave caps | Required validation tier before calling an issue whole-inference or formal mechanism evidence |

The present selected-target stream only supports Route-A conclusions.  It
demonstrates that a small Decode target can have a compact, concentrated
observed set while the prefill target has a larger one, but it cannot establish
that this is the model's TLB or cache behavior.

For formal Decode2/3/4 overlap, freeze one identical full mangled target plus
static PC/range across all steps, record one hash-bound entry per step, and
keep the resulting metric `SET_ONLY`.  Do not synthesize missing steps from
batch/context scaling.  For Route B/C, retain active mask, per-lane VA, width,
explicit memory-space evidence, access kind, full target identity, terminal
state, raw SHA, producer receipt, and a receipt-bound runtime object-map
snapshot/cutoff.  Strict global time order is not required for set overlap; it
is required before any global cache reuse/MRC claim.
