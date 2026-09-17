# C16 Qwen3-30B-A3B S2 formal capture — node109 V2

## Execution mode

Execute in **GOAL MODE**. This is one autonomous node109 GPU producer Goal.

Base scientific authority:

- S2 target requalification branch: `hrl/c16-qwen3-30b-s2-target-requalification-109-v1`
- accepted HEAD: `c9979aa47961f843db4b5b06cffa488e4ff1a132`
- review pack: `docs/vm_tlb/review_packs/C16_QWEN3_30B_S2_TARGET_REQUALIFICATION_109_V1/`
- accepted S2 semantic/state replay authority: `ee67225edc8fc5868de585d38e0391cbeb755d9f`

Use node109's normal Linux Git workflow. Do not install/configure `gh`. Do not use a Windows mirror.

Use the preserved deployment:

- model: `/data/c16/models/qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/`
- runtime: `/data/c16/env/c16-qwen3-30b-hf451-gpu`

Do not recopy 61 GB, retokenize, upgrade runtime, change precision/backend, force routing, or rerun the entire 48-layer S2 semantic stream if accepted state bundles remain intact.

GPU work must acquire `/data/c16/locks/c16_gpu_campaign.lock` normally. Never kill/bypass another scientific workload.

Global formal rule:

`FORMAL_ADMISSION_CONCURRENCY=1`

Each formal run must be fully closed, transferred, verified, admitted and positively ACKed before the next admission begins.

---

## Scientific objective

Turn the accepted Q30 S2 requalification portfolio into accepted formal C16 raw/catalog evidence.

The three already-clean S2 targets remain unchanged:

1. `S2_PF_ATTENTION_FLASH`
   - S2/T2048 Prefill attention
   - ordinal 46
   - 23 static GLOBAL MREF
2. `S2_PF_EXPERT_GEMM`
   - S2/T2048 Prefill expert compute
   - ordinal 905
   - 20 static GLOBAL MREF
3. `S2_DEC3_ATTENTION_SPLITKV`
   - S2/T2048 Decode step3 attention/KV
   - ordinal 47
   - 57 static GLOBAL MREF

Before any formal capture of the Decode Expert target, repair one identity inconsistency in the accepted requalification pack and freeze a corrected S2 decode-expert semantic target.

The final formal portfolio should remain **four targets total**. Do not add a fifth target merely for redundancy.

---

# Stage 0 — revalidate upstream and repair Decode Expert identity

## 0.1 Revalidate accepted upstream

Verify SHA256SUMS and exact deployment/state authority for:

- `C16_QWEN3_30B_S0_TARGET_QUALIFICATION_109_V1`
- `C16_QWEN3_30B_S2_T2048_STATE_REPLAY_109_V1`
- `C16_QWEN3_30B_S2_TARGET_REQUALIFICATION_109_V1`

Revalidate one ordinary fresh-process replay each for:

- S2 Prefill Layer24/T2048
- S2 Decode step3 Layer24 long-KV

Require accepted source/router/replay identity to remain valid.

If an accepted local state bundle is absent, restore only from accepted node164 provenance with exact SHA/file-set verification. Do not regenerate the full semantic stream solely to recreate an intact archived state.

## 0.2 Explicit Decode Expert inconsistency to resolve

The accepted requalification pack contains two incompatible identities under the label `S2_DEC3_EXPERT_GEMV`:

### semantic/candidate/stability identity

From `S2_SEMANTIC_LAUNCH_MAP.tsv` and `S2_OCCURRENCE_STABILITY.tsv`:

- decode step3 / Layer24
- ordinal 116
- `internal::gemvx` template variant containing `(int)7`
- grid `192x1x1`
- block `32x4x1`

### bounded NCU / delta identity

From `S2_NCU_CHARACTERIZATION.tsv` / `S0_VS_S2_TARGET_DELTA.tsv`:

- decode step3 / Layer24 expert family
- `internal::gemvx` template variant containing `(int)6`
- grid `(1024,1,1)`
- block `(16,4,1)`
- DRAM read `16,801,024`
- 243 static GLOBAL MREF according to the S0-vs-S2 delta

These must **not** be treated as the same occurrence without proof.

Do not start the formal Decode Expert capture while this ambiguity exists.

## 0.3 Bounded semantic requalification of Decode Expert only

Using the already accepted S2 Decode-step3 Layer24 replay, instrument the expert subpath strongly enough to bind actual natural-routing expert semantics.

Record:

- exact natural router top-k expert IDs and weights for the frozen decode-step3 token/state;
- exact selected expert whose operator will become the formal anchor;
- exact projection role: gate/up/down or explicitly typed grouped/fused equivalent;
- exact input/output tensor hashes/shapes/dtypes;
- exact weight object identity/range;
- exact launch ordinal inside the accepted replay;
- exact function/mangled function;
- grid/block;
- code object/module identity;
- repeated-replay stability.

Preferred cross-model-compatible semantic target:

> one naturally selected routed expert's **down projection** under the exact S2 Decode-step3 state,

if the HF Q30 runtime exposes it as a separable operator and its dynamic addresses can be tied to the expert weight/activation objects.

Do **not** force an expert ID.

If the runtime groups/fuses expert work such that a single expert cannot be losslessly attributed, name and qualify the grouped/fused target explicitly instead of pretending it is a single-expert trace.

Use projection-specific NVTX/instrumentation or exact module hooks as needed. A generic `Q30_COMPONENT_EXPERT` range plus kernel-name matching is not enough to distinguish two different GEMV occurrences.

## 0.4 Corrected target requirements

For the corrected S2 Decode Expert target:

1. replay/state equivalence PASS;
2. natural routing receipt frozen;
3. exact semantic projection/expert identity frozen;
4. occurrence stability PASS;
5. fresh SM89 static GLOBAL-MREF map;
6. independent LDGSTS/GLOBAL_TO_SHARED and special address-path audit;
7. one-MREF reachability canary terminal-close PASS;
8. bounded NCU only if needed to confirm the selected semantic occurrence;
9. same-process address-context ranges for expert weight/input/output when feasible.

If the semantic down-projection target is the `1024x1x1`, `16x4x1`, 243-MREF kernel, prove it. Do not assume it from dimension intuition.

If it is instead the `192x1x1` occurrence, prove that and update the portfolio accordingly.

The old S0 Decode Expert entry remains historical/reference evidence only once a clean S2 Decode Expert formal target is established.

## 0.5 Freeze corrected final portfolio

Create a corrected authoritative portfolio before formal capture.

Default intended final portfolio:

- `S2_PF_ATTENTION_FLASH` — 23 MREF
- `S2_PF_EXPERT_GEMM` — 20 MREF
- `S2_DEC3_ATTENTION_SPLITKV` — 57 MREF
- corrected `S2_DEC3_<NATURAL_EXPERT_DOWN_OR_TYPED_EQUIVALENT>` — expected count only after fresh audit

Do not keep both S0 and S2 Decode Expert merely to increase coverage.

If corrected S2 Decode Expert has 243 MREF, total remains 343 shards.

Persist a `PORTFOLIO_CORRECTION_RECEIPT.json` explaining why the old mixed-identity entry was superseded and which artifacts remain historical.

---

# Stage 1 — formal capture discipline for every target

For each selected target independently:

- use exact accepted state/replay authority;
- use exact occurrence selector frozen by qualification;
- freeze complete static address-bearing set before capture;
- fresh output root;
- clear inherited `C16_CTA_BEGIN`, `C16_CTA_END`, and equivalent selectors;
- explicit function/static selectors;
- sufficient capture capacity;
- same-process `ADDRESS_CONTEXT` per shard;
- expected shard count == present shard count;
- every shard terminal-closed;
- drop = 0;
- overflow = 0;
- explicit `EXECUTED_SHARD` vs `ZERO_EXECUTION_PROVEN` partition.

The formal methodology is one static MREF per independently replayed shard.

Do not infer:

- cross-shard chronology;
- global L2 arrival order;
- cross-shard reuse distance;
- cross-replay absolute-VA union.

Per-shard page/line/event statistics are allowed.

For the corrected S2 Decode Expert target, require the semantic object/routing receipt to stay attached to the formal run. Any expert-specific claim requires same-process expert-weight/activation attribution or an equivalently strong typed proof.

---

# Stage 2 — serial formal capture and admission order

Prioritize reaching an accepted S2 natural-MoE anchor while preserving serial admission.

Recommended order:

1. corrected S2 Decode Expert semantic target;
2. S2 Prefill Expert GEMM;
3. S2 Decode Attention SplitKV;
4. S2 Prefill Attention Flash.

For each target:

`capture complete set -> local audit -> package -> transfer node164 -> destination verification -> exactly one admission -> wait positive ACK`

Only after positive ACK may the next target begin admission.

A rejected/diagnostic capture must not be promoted into accepted raw/catalog.

If one later target fails after earlier targets are accepted, preserve accepted earlier targets and emit a typed partial decision rather than deleting them.

---

# Stage 3 — local independent close gate before each admission

Before each admission decode the new traces and verify at least:

- exact function/occurrence identity;
- static-set completeness;
- executed/zero partition;
- active-lane event totals;
- CTA coverage appropriate to the exact launch;
- per-shard 4K/64K/2M pages;
- per-shard 128B lines;
- address min/max;
- terminal/drop/overflow conditions;
- same-process object membership where the semantic claim requires it.

For attention targets, keep claim scope kernel/layer-local unless object ranges allow stronger typed attribution.

For the corrected Decode Expert target, report separately:

- expert-weight events;
- expert activation/input events;
- output events where provable;
- neither/unknown events.

Fail closed on a false single-expert attribution.

---

# Stage 4 — bounded NCU / existing NCU

Do not launch a broad profiling campaign.

Reuse accepted bounded NCU qualification evidence where exact target identity is unchanged.

For the corrected Decode Expert target, preserve a new bounded NCU report only if the semantic correction changed the exact occurrence or if needed to bind the target.

Report numeric metrics only when explicit values and units are available. Preserve cache-control warnings and do not infer cache/TLB causality.

---

# Stage 5 — review pack

Create:

`docs/vm_tlb/review_packs/C16_QWEN3_30B_S2_FORMAL_CAPTURE_109_V2/`

Include at minimum:

- `UPSTREAM_AUTHORITY.tsv`
- `PORTFOLIO_CORRECTION_RECEIPT.json`
- `CORRECTED_FORMAL_CAPTURE_PORTFOLIO.tsv`
- `S2_DECODE_EXPERT_NATURAL_ROUTING.json`
- `S2_DECODE_EXPERT_TARGET_QUALIFICATION.json`
- `S2_DECODE_EXPERT_STATIC_PATH_AUDIT.json`
- per-target formal summary JSON
- per-target shard fingerprint/summary artifacts
- per-target admission/ACK receipts
- `NCU_TYPED_EVIDENCE.json`
- `FORMAL_CAPTURE_TOTAL_SUMMARY.json`
- `SCIENTIFIC_SCOPE.md`
- `NEXT_STEP_AUTHORIZATION.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

A full PASS requires all four corrected targets to receive positive ACK.

Suggested full decision:

`C16_QWEN3_30B_S2_FORMAL_CAPTURE_109_V2_PASS`

The next-step authorization should state whether the accepted Q30 S2 Decode Expert anchor is suitable for independent cross-model MoE comparison with the accepted DeepSeek-V2-Lite S2 natural routed-expert anchor.

Do not perform the cross-model comparison inside this producer Goal.

---

# Stage 6 — Git and cleanup

Suggested implementation branch:

`hrl/c16-qwen3-30b-s2-formal-capture-109-v2`

Use node109's existing Git transport/authentication; do not install `gh`.

After Goal-owned artifacts are complete:

- commit;
- push actual HEAD;
- verify canonical repository identity `swayhrl/accel-sim-framework`;
- verify nonempty canonical `git ls-remote` branch SHA;
- require local HEAD == remote SHA;
- require clean worktree.

Then:

- release `/data/c16/locks/c16_gpu_campaign.lock`;
- verify no profiler/Q30 CUDA process remains;
- verify GPU returns to expected baseline.

Report:

- implementation branch/final HEAD;
- corrected Decode Expert semantic identity, expert ID/routing/projection/function/grid/block/static count;
- corrected final portfolio;
- all four formal run IDs;
- executed/zero/event counts per target;
- ACK status per target;
- total actual elapsed time;
- next-step authorization.

STOP.

---

# Stop conditions

Fail closed only for real blockers, including:

- accepted S2 state/replay authority corrupted;
- Decode Expert ambiguity cannot be resolved to a stable semantic target;
- natural routing cannot be preserved;
- selected expert/projection replay mismatch;
- static/address-path closure failure;
- false expert-specific attribution;
- drop/overflow;
- terminal incomplete formal run;
- Pipeline rejection/negative ACK;
- artifact corruption.

Do not stop merely because the old S0-vs-S2 deduplication choice must be superseded; repairing that choice is part of this Goal.

Do not stop after Stage 0 if a corrected portfolio is frozen and downstream formal capture remains executable.
