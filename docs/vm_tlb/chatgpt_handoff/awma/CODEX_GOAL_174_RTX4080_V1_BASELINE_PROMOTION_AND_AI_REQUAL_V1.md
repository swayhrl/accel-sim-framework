# CODEX 174 GOAL — RTX4080 V1 Baseline Promotion + AI Requalification V1

Date: 2026-09-23

Mode:

`GOAL MODE / LONG-RUN / SOLVE-AND-CONTINUE / FINAL BASELINE GATE`

Node:

`174-new`

Stage:

`AWMA_RTX4080_V1_BASELINE_PROMOTION_AND_AI_REQUALIFICATION_V1`

Read first, completely:

`docs/vm_tlb/chatgpt_handoff/awma/REVIEW_RTX4080_V1_BASELINE_PROMOTION_CANDIDATE_2026-09-23.md`

This Goal is the last simulator-baseline qualification stage before new TLB/PTW/cache mechanism research.

Do not tune platform parameters.
Do not tune VM/TLB parameters.
Do not redesign V1/V2R1.
Do not start a new mechanism.

---

# 1. Frozen authorities

## RTX4080/Ada platform

Authority:

`RTX4080_ADA_ACCELSIM_BASE_V1`

Config SHA256:

`de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`

Platform qualification authority:

`hrl/awma-174-rtx4080-platform-requal-mechanism-v1 @ 8af2c00e6361c53eaf7b02d5dab3ef9021925774`

Do not modify the platform config.

Paper scope:

`QUALIFIED_FOR_AWMA_MEMORY_TRANSLATION_STUDIES`

Do not broaden this into a universal RTX4080 fidelity claim.

## Translation semantics

V1 authority:

`hrl/awma-174-translation-frontend-pipelining-v1 @ ad6f38878bc1e7c268b17e65fdb3793a3899a84d`

V2R1 authority:

`hrl/awma-174-translation-frontend-ready-application-v2r1 @ dccc11f05aece7ee8ef07ffd0bec7ad83d8eb1f8`

V1 semantic truth:

```text
GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH=1
GPGPUSIM_READY_APPLICATION_V2=0/unset
```

V2R1 is NOT part of the candidate baseline.

V2R1 remains diagnostic evidence only.

## Existing mechanism-sensitive classification

Accepted:

```text
V1_EXTERNAL_SEMANTIC_SUPPORT_PARTIAL
V2R1_ADDS_NO_EXTERNAL_ALIGNMENT_BENEFIT
BASE_CONCURRENCY_MODEL_RESIDUAL
```

Do not reopen mechanism-sensitive microbenchmark design in this Goal.

---

# 2. Accepted AI target identities

The actual target workload family remains:

`Qwen/Qwen2.5-0.5B-Instruct`

revision:

`7ae557604adf67be50417f59c2c2f167def9a775`

workload:

`S2_TEXT / batch1 / prefill2048 / decode32 / FP16 / SDPA`

Targets:

## T0

`Q05_PREFILL_ATTN_FLASH`

Accepted isolated payload:

`kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz`

Durable bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native-contiguous-prefix_q05-contiguous-prefix_20260918T022749Z_1fea2d955d1c`

Producer authority:

`c6733012c13099c6a86f506fd8c61e351791159e`

Derived candidate-private index content:

`kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz\n`

index SHA256:

`a8b4ba1cf33f34be345b38908cb39572c0d14972170fd1972b4b080e81154fd5`

## T1

`PREFILL_GEMM_PRIMARY_OCC0`

Producer authority:

`8f49ba3b9228b5f8a9163e961225ffd415107734`

Durable bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native_prefill-gemm-primary-occ0_20260918T052739Z_01540d931e17`

Accepted Native footprint:

```text
memory instructions = 2,298,240
lane addresses       = 70,352,896
unique 4K regions    = 7,906
unique 64K regions   = 495
```

## T2

`DECODE_GEMV_PRIMARY_STEP16`

Same producer authority:

`8f49ba3b9228b5f8a9163e961225ffd415107734`

Durable bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_decode-gemv-primary-step16_20260918T074437Z_b0dfb1af1ae1`

Accepted simulator identity from V2R1:

```text
gpu_sim_insn      = 43,357,696
CTA               = 1,216
unique logical UID= 411,008
```

For T0/T1, recover the accepted expected simulator identity fields from existing accepted receipts before launching.

Do not invent missing expected values.

---

# 3. Fresh branch / unified candidate

Create execution branch:

`hrl/awma-174-rtx4080-v1-baseline-promotion-v1`

Use an isolated worktree/runtime root.

Reconstruct one unified simulator binary that supports:

```text
LEGACY
V1
```

through runtime switches.

Do not maintain separate divergent implementations.

The source must contain the accepted V1 semantics and the already-qualified RTX4080 platform support.

Record:

- source authority;
- binary SHA256;
- platform config SHA256;
- trace config SHA256;
- VM overlay authority.

Run the existing controller regressions before AI replay.

---

# 4. VM configurations

Use only the frozen model-relative VM configurations.

Primary:

`10/80`

Diagnostic:

`0/80`

No new latency values.

No tuning.

Continue to state:

`10/80 IS NOT CLAIMED AS RTX4080 HARDWARE TLB LATENCY`

It is the project's model-relative research configuration.

---

# 5. Pre-bind AI matrix identity

Before launching, create:

`AI_MATRIX_CONFIG_AUTHORITY.tsv`

For each point bind:

- target T0/T1/T2;
- exact trace payload SHA;
- runner/index SHA;
- platform config SHA;
- binary SHA;
- semantic;
- functional switches;
- VM config;
- output directory;
- expected instructions / CTA / UID or other accepted identity fields.

If a runner/index/manifest wrapper is absent but deterministically reconstructible from accepted authority:

reconstruct as P2/P3 and continue.

Do not escalate that to P1 input loss.

---

# 6. Final AI promotion matrix

Run:

`3 targets × 2 semantics × 2 VM configs = 12 points`

Matrix:

```text
T0 Legacy 10/80
T0 Legacy 0/80
T0 V1     10/80
T0 V1     0/80

T1 Legacy 10/80
T1 Legacy 0/80
T1 V1     10/80
T1 V1     0/80

T2 Legacy 10/80
T2 Legacy 0/80
T2 V1     10/80
T2 V1     0/80
```

Do NOT run V2R1 unless required by a concrete correctness contradiction.

Use maximum safe parallelism after host-resource audit.

All output directories must be isolated.

Do not allow high parallelism to cause memory pressure / I/O contention that changes completion behavior.

---

# 7. Required correctness gates for every point

Require:

- terminal completion;
- exact target/kernel identity;
- expected instructions;
- expected CTA;
- expected logical UID / translation coverage where that authority exists;
- untranslated = 0;
- unobserved = 0;
- Segment functional activity = 0 where applicable;
- no duplicate translation/data side effects;
- MSHR/PWQ/walkers drained;
- full controller quiescence diagnostics when available.

For T2 require the frozen:

```text
gpu_sim_insn = 43,357,696
CTA          = 1,216
unique UID   = 411,008
```

For T0/T1 bind accepted expected fields from prior receipts and publish them.

Any identity mismatch is scientific STOP.

Ordinary runner/build/path issues solve-and-continue.

---

# 8. AI semantic analysis

For each target compute:

## Legacy sensitivity

`(Legacy_10 - Legacy_0) / Legacy_10`

## V1 sensitivity

`(V1_10 - V1_0) / V1_10`

## V1 semantic reduction

Report:

- Legacy 10/80 cycles;
- V1 10/80 cycles;
- relative Legacy→V1 improvement;
- Legacy sensitivity;
- V1 sensitivity.

## Zero-latency sanity

Compare:

`Legacy_0 vs V1_0`

V1 is allowed to have minor ordering effects, but a large difference in the zero-L1-latency control requires explanation.

Predeclared materiality flag:

if:

`abs(V1_0 - Legacy_0) / Legacy_0 > 2%`

mark:

`ZERO_LATENCY_SEMANTIC_DIVERGENCE_REQUIRES_REVIEW`

Do not auto-fail purely because of the flag; inspect cause and only STOP if it changes semantic interpretation.

## Promotion expectation

A healthy promotion result should show:

- V1 does not introduce correctness regressions;
- V1 materially reduces modeled lookup-latency amplification on the real AI targets;
- V1 does not create a material pathological zero-latency regression;
- the direction is consistent with mechanism-sensitive external evidence.

Do not tune to meet this expectation.

---

# 9. Known limitation — fold into this publication, do not create another task

The baseline publication must explicitly carry:

`BASE_CONCURRENCY_MODEL_RESIDUAL`

Evidence:

even under V1 0/80, A32_W8/A32 remains far above Native.

This is a known base-simulator multi-warp/concurrency limitation, not a reason to modify V1 or platform parameters now.

Also fold in these scope clarifications:

1. A1_CONTROL:
   - trace-level = one 128B line opportunity;
   - simulator coalescing = four 32B sector accessq entries.

2. RTX4080 platform:
   - qualified for AWMA memory/translation studies;
   - H_STREAM/H_COMPUTE matched-scale held-outs are small/launch-dominated;
   - do not claim universal RTX4080 cycle fidelity.

These are documentation/claim-boundary fixes only.

Do not open separate repair Goals for them.

If other similarly small publication/documentation issues are found and the correct fix is unambiguous, repair them in this same Goal.

Do not stop for them.

---

# 10. Baseline promotion gate

If all 12 points pass correctness and the evidence supports V1 as the better semantic baseline, formally promote:

`AWMA_RTX4080_SIM_BASELINE_V1`

Definition must include:

## Hardware platform

`RTX4080_ADA_ACCELSIM_BASE_V1`

config SHA:

`de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`

## VM research model

primary `10/80` VM overlay.

Keep `0/80` as the frozen diagnostic companion.

## Translation frontend

V1:

```text
GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH=1
GPGPUSIM_READY_APPLICATION_V2=0
```

## Explicit exclusions

- V2R1 is NOT baseline;
- Segment F0 remains dormant;
- 10/80 is not hardware-latency truth;
- Legacy remains available as historical/control mode.

Important:

Do NOT change the simulator source default to force V1 ON globally.

Promotion must be represented by:

- named baseline config/manifest;
- runner/env authority;
- documentation.

Preserve runtime switchability.

---

# 11. Baseline regression bundle

If promoted, create a durable baseline authority that future experiments can consume without re-deriving semantics.

At minimum publish:

```text
AWMA_RTX4080_SIM_BASELINE_V1.json
baseline.env
platform config SHA
trace config SHA
VM 10/80 overlay SHA
VM 0/80 diagnostic overlay SHA
simulator binary SHA
V1 source authority
controller regression receipt
AI 12-point promotion matrix
known limitations
```

Future mechanism Goals should import this exact baseline authority.

---

# 12. Promotion classifications

Allowed final decisions:

- `AWMA_RTX4080_SIM_BASELINE_V1_PROMOTED`
- `AWMA_RTX4080_SIM_BASELINE_V1_PROMOTED_WITH_SCOPE`
- `V1_BASELINE_PROMOTION_BLOCKED`

A scoped promotion is acceptable if:

- correctness is clean;
- V1 is directionally and materially better than Legacy;
- remaining mismatch is already identified as base concurrency/platform scope rather than V1 semantic error.

Do not demand perfect Native alignment.

---

# 13. Paper-oriented output

The report must separate:

## A. Platform validation

already frozen.

## B. Mechanism-sensitive external semantic evidence

already frozen.

## C. New AI workload regression

the 12 points from this Goal.

## D. Baseline decision

why V1 is chosen over Legacy and V2R1.

## E. Known limitations

especially:

`BASE_CONCURRENCY_MODEL_RESIDUAL`

Do not hide residual mismatch.

---

# 14. Required publication

Report:

`docs/vm_tlb/codex_handoff/awma/RTX4080_V1_BASELINE_PROMOTION_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/`

Required:

```text
README.md
SOURCE_ANCHORS.md
BASELINE_DEFINITION.md
AWMA_RTX4080_SIM_BASELINE_V1.json
baseline.env
AI_TRACE_AUTHORITY.tsv
AI_MATRIX_CONFIG_AUTHORITY.tsv
AI_PROMOTION_MATRIX.tsv
AI_SEMANTIC_ANALYSIS.tsv
AI_CORRECTNESS_GATES.tsv
CONTROLLER_REGRESSION.tsv
KNOWN_LIMITATIONS.md
PAPER_EVIDENCE_SUMMARY.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

No accidental zero-byte placeholders.

If promotion is blocked, publish the evidence honestly and omit fake promoted-baseline files rather than creating empty placeholders.

---

# 15. Publication contract

Close exactly:

```text
AI matrix closure
→ baseline decision
→ report/review pack
→ SHA256SUMS
→ commit
→ push
→ fetch-back
→ remote HEAD == local HEAD
→ fetched remote tree verification
→ all required files non-empty
→ sha256sum -c
→ clean worktree
→ STOP
```

Do not begin a new TLB/PTW/cache mechanism in this Goal.

---

# 16. Solve-and-continue policy

Ordinary engineering:

`solve-and-continue`

Also solve-and-continue for small, unambiguous non-scientific issues discovered during execution.

Do NOT stop for:

- wording;
- filename cleanup;
- deterministic wrapper reconstruction;
- obvious report/table correction;
- benign provenance bookkeeping that can be repaired from accepted authority.

STOP only for:

- target scientific payload missing/corrupt without recovery;
- AI target identity changes;
- V1 semantic contract must change;
- frozen RTX4080 platform/VM parameter would need tuning;
- correctness/coverage cannot close;
- evidence requires changing the baseline claim materially.

