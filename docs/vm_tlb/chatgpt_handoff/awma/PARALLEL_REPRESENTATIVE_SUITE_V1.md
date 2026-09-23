# AWMA Post-Lane-A Representative Suite Parallel Handoff V1

Date: 2026-09-23

## Frozen authority

- Lane A accepted authority: `1c26b5c07b8ab4d7a457a84ea9b1327dd7ce8456`
- Lane A tree: `af4697a8da314c02c105fdf40d4eef5939e1cae8`
- Frozen simulator baseline: `AWMA_RTX4080_SIM_BASELINE_V1`
- Baseline authority: `8d1f14a32f5538660d74da86ccb03a2c504c5735`
- Current running Lane B must remain untouched:
  `AWMA_LITERATURE_GUIDED_MECHANISM_EXPLORATION_V1`
- Node109 remains idle unless a later reviewed gap explicitly requires new Native capture.

Do not retune RTX4080 platform, 10/80, V1/V2R1 semantics, producer identity, or Native calibration.

## Execution policy

These four jobs are independent enough to start now in separate worktrees.

Before heavy execution, each window must inspect CPU/RAM/I/O/storage and the current Lane B load.

- Light analysis jobs should start immediately.
- Heavy Accel-Sim jobs may run concurrently only if resource checks show safe headroom.
- If Lane B is consuming the safe heavy-run budget, the ideal-translation window should continue source audit, implementation, tests, and matrix preparation, then launch simulations as soon as resources free; do not stop merely because the heavy slot is temporarily occupied.
- Every job uses an independent branch/worktree/build/runtime/output.
- Read-only assets may be shared.
- Do not modify the Lane B worktree or kill/restart its processes.
- Ordinary engineering issues are solve-and-continue.
- Scientific contract or identity changes require STOP.

---

# Window A — Full kernel census reclassification

Stage:
`AWMA_QWEN25_S2_KERNEL_CENSUS_RECLASSIFICATION_V2`

Goal:

Recompute the frozen Qwen2.5 S2 full-run kernel census from the existing accepted NSYS/SQLite authority without new GPU capture, correcting phase attribution so GPU kernels are associated with the CPU launch context that issued them rather than only wall-time overlap with NVTX ranges.

Primary existing authority:

- branch/commit: `hrl/awma-qwen25-s2-census-109-v1 @ 678d7b491d4788369ca0c22717453b20846ab195`
- durable raw:
  `/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/qwen25_s2_kernel_census_20260917T101100Z/`
- original inventory SHA256:
  `7825697aa23647daee6a38ac4436029c5746fe29a468d303520d3884f2b4abef`

Tasks:

1. Verify the existing durable SQLite/NSYS authority and hashes. Do not recapture.
2. Inspect CUPTI/NSYS correlation fields and derive a source-supported launch-context mapping from CPU runtime launch/API activity to GPU kernel activity, then to PREFILL / DECODE_STEP_n NVTX context.
3. Preserve the original V1 census read-only as historical evidence.
4. Produce a V2 full launch inventory and summaries by:
   - phase;
   - normalized kernel family;
   - exact kernel function;
   - grid/block shape;
   - launch count;
   - accumulated GPU duration;
   - per-step distribution where relevant.
5. Explicitly account for auxiliary work outside model-call ranges such as argmax/sampling helpers; do not silently drop or force them into a phase.
6. Quantify V1→V2 attribution changes, including previously UNKNOWN-phase launches and time.
7. Do not infer Q/K/V, layer, or operator roles without explicit evidence.
8. Publish compact review evidence to GitHub and keep large raw/derived files on node164.

STOP after report/review pack/commit/push/fetch-back verification.

---

# Window B — RTX4080/V1 ideal-translation control

Stage:
`AWMA_RTX4080_V1_IDEAL_TRANSLATION_CONTROL_V1`

Goal:

Create a current-baseline ideal-translation diagnostic and measure T0/T1/T2 on the frozen RTX4080/V1 platform, so the current 10/80→0/80 L1-lookup sensitivity can be compared with the response to removing the complete modeled translation service.

Important historical boundary:

The old R0/I0 study used an SM86 RTX3070-derived research shell and fixed-cycle progress. Its I0 numbers are historical supporting evidence only and must not be reused as current RTX4080 full-kernel results.

Tasks:

1. Audit the old `I0_IDEAL_TRANSLATION` / vm-mode semantics and current RTX4080/V1 source.
2. Define an ideal control that:
   - removes modeled translation lookup/miss/MSHR/PTW/PWC/PTE waiting/service;
   - preserves the same functional virtual→physical mapping used by the comparator;
   - preserves downstream data addresses, cache indexing, memory partition mapping, data accesses, instruction stream, scheduling semantics, and V1 downstream ordering;
   - does not provide future information or alter non-translation memory behavior.
3. If an existing mode cannot satisfy those conditions exactly, implement a new opt-in diagnostic-only ideal-translation mode. Default OFF must reproduce frozen V1 exactly.
4. Directed tests and OFF/ON correctness:
   - exact target identity;
   - instructions/CTA;
   - UID/translation coverage;
   - untranslated/unobserved = 0;
   - duplicate-free;
   - terminal quiescence;
   - OFF scientific signature identical to accepted V1.
5. Reuse accepted T0/T1/T2 10/80 and 0/80 results where identity/config/source are exact.
6. Run only the three ideal full-kernel points initially:
   - T0 ideal
   - T1 ideal
   - T2 ideal
7. Report, for each target:
   - normal 10/80 cycles;
   - 0/80 cycles;
   - ideal cycles;
   - `S_L1=(C10_80-C0_80)/C10_80`;
   - `S_ALL=(C10_80-Cideal)/C10_80`.
8. Do not interpret `S_ALL-S_L1` as a literal PTW time fraction without a separate causal decomposition.
9. Do not retune baseline parameters and do not start a mechanism.

This is the only new heavy-simulation lane in this parallel stage. Respect resource availability with Lane B.

STOP after current-baseline ideal control and T0–T2 matrix are closed.

---

# Window C — Existing simulator-native trace asset audit

Stage:
`AWMA_EXISTING_AI_SIM_TRACE_COVERAGE_AUDIT_V1`

Goal:

Determine how much of a future representative kernel suite can be built by reusing already accepted simulator-native assets, before asking node109 to capture anything new.

Tasks:

1. Search GitHub authority plus node164 accepted provenance for existing simulator-native traces, runner indexes, target-selection records, and exact target identities related to the frozen Qwen2.5 S2 workload.
2. Map each reusable asset to:
   - phase;
   - normalized family;
   - exact function;
   - grid/block;
   - occurrence/step;
   - payload SHA;
   - runner/index SHA;
   - simulator qualification status;
   - whether it has accepted RTX4080/V1 replay evidence.
3. Include at least the existing T0/T1/T2 authorities and historical candidate/capture lines for:
   - Prefill Flash;
   - Prefill GEMM;
   - Decode GEMV;
   - Decode Flash splitkv;
   - Decode Flash combine.
4. Do not infer that a Native MREF/NVBit trace is losslessly convertible into a simulator-native trace.
5. Produce:
   - REUSABLE_NOW;
   - REQUIRES_REQUALIFICATION;
   - NATIVE_ONLY;
   - MISSING_SIM_TRACE
   classifications.
6. Link current Native census time/share evidence where available, but mark weights provisional until Window A V2 reclassification closes.
7. Produce a prioritized missing-asset list. Do not launch node109 or capture anything.

STOP after inventory/review pack/commit/push/fetch-back verification.

---

# Window D — Representative-suite methodology and selector

Stage:
`AWMA_AI_TRANSLATION_REPRESENTATIVE_SUITE_DESIGN_V1`

Goal:

Build the deterministic methodology and selector for a paper-defensible representative kernel suite, without prematurely fixing the final members before Window A/C results arrive.

Tasks:

1. Consume the accepted V1 census and target-selection history as provisional inputs.
2. Define strata using source-supported fields, at minimum:
   - Prefill vs Decode;
   - normalized family;
   - exact implementation;
   - launch shape;
   - decode-step behavior where relevant.
3. Preserve semantic/operator fields only when explicitly supported; UNKNOWN is valid.
4. Selector must account for both:
   - accumulated native GPU-duration mass;
   - within-family diversity/shape variants.
5. Add certainty/forced-inclusion rules for:
   - high-time subfamilies;
   - rare but structurally distinct memory/translation behaviors;
   - known major variants such as long Decode GEMV and splitkv vs combine.
6. Do not assume one representative is sufficient merely because function names match.
7. Reserve independent validation samples not used to choose/tune the selector.
8. Produce a script/tool that can consume Window A's corrected V2 inventory later without redesign.
9. Generate a PROVISIONAL suite from current evidence, clearly marked pre-gate.
10. Define the final outputs expected after reconciliation:
    - selected representative target list;
    - coverage by phase and accumulated native GPU time;
    - uncovered/low-confidence strata;
    - proposed holdouts;
    - mapping to existing simulator-native assets from Window C.
11. Do not request new capture and do not run mechanisms.

STOP after methodology, selector code, provisional result, and review pack are published.

---

# Merge/review boundary

Do not auto-merge these four branches.

After all four reports and Lane B return to ChatGPT/user, review them jointly.

Expected next decision:

1. reconcile corrected Native time weights;
2. finalize the representative suite;
3. reuse existing simulator-native inputs wherever possible;
4. authorize only the minimum missing captures on node109;
5. extend 10/80 vs 0/80 vs ideal measurements to the final suite;
6. evaluate Lane B survivors across the same representative suite and held-out targets;
7. only then decide whether broader models/scenarios are needed.
