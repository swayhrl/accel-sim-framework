# CODEX GOAL — 174 Native ↔ Simulator Cross-Calibration V1

Date: 2026-09-23

Mode:

`GOAL MODE / LONG-RUN / SOLVE-AND-CONTINUE`

Node:

`174-new`

Stage:

`AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1`

This is one continuous Goal. Do not stop after ordinary setup/build/runner problems.

Read first, completely:

`docs/vm_tlb/chatgpt_handoff/awma/AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_CONTEXT_2026-09-23.md`

Then execute the following phases in order.

---

# Phase A — establish execution authority

## A1. Verify handoff authority

Record:

- handoff branch and HEAD;
- V2R1 final publication authority:
  `dccc11f05aece7ee8ef07ffd0bec7ad83d8eb1f8`;
- V1 authority:
  `ad6f38878bc1e7c268b17e65fdb3793a3899a84d`;
- Native V1R1 authority:
  `589d0d579e8e9d30922d3842084c3c50f09833d7`;
- Native V1R2 exact-pair authority:
  `1d56c7ff12bd273f0f27c0de24d308a255b50b56`.

Create a fresh execution branch:

`hrl/awma-174-native-simulator-cross-calibration-v1`

Create an isolated worktree/staging root.

Do not modify accepted V1/V2R1 branches.

## A2. Reconstruct one unified accepted simulator candidate

The cross-calibration binary must support, by runtime switches:

- Legacy;
- V1;
- V2R1.

Do not maintain three separately reimplemented source trees if one accepted source can reproduce all modes.

Recover the strongest accepted source authority in this order:

1. byte-verified surviving V2R1 source/worktree;
2. archived V2R1 source evidence:
   `/root/awma_v2r1_closeout_pending`;
3. published V2R1 `READY_CONSUMPTION_REPAIR.patch`;
4. accepted V1 source authority.

Important:

The V2R1 Git publication branch is evidence authority. Do not assume the repo-root simulator source already contains the runtime patch.

Record:

- base source commit;
- imported patch SHA;
- reconstructed source tree hash or relevant source-file hashes;
- resulting simulator binary SHA.

Build cleanly.

Run the already-accepted controller regressions.

## A3. Verify semantic truth table

Prove in source/config:

```text
LEGACY:
pipelined_launch = OFF
ready_application = OFF

V1:
pipelined_launch = ON
ready_application = OFF
V1 prelaunch READY observe-only
consume_ready = false

V2R1:
pipelined_launch = ON
ready_application = ON
V2R1 prelaunch READY consume-and-apply
consume_ready = true
```

Do not change those semantics in this Goal.

---

# Phase B — bind the four simulator-native traces

Use node164 durable evidence.

For each:

- M0_COMPACT
- M1_DEPENDENT_LARGE
- M2_MULTIWARP_HIGH
- M3_STRIDE64K

verify:

- durable directory exists;
- exact payload file is identified;
- payload SHA256 matches accepted receipt;
- source/destination manifest authority matches;
- xz integrity PASS;
- selector identity is `chase_occurrence_0`;
- zero drop/overflow provenance is present.

Accepted payload SHA256:

```text
M0 b9f87594b0279d8b489aa5181e6fcf37551e04553b154a7848c88fa44fc03e7e
M1 bea5cf39d41f9807d95be659984fe850c56d910214ecfe85d6379df705cc9ec5
M2 c165749ff06013f7bebc6ceecb2915f5de0b3d88171366a4832001cd6da2642f
M3 be63c6cd23cb101d626be18bc82766c27a91ff687f1d4427d9ba47cbf26d0799
```

Recover exact launch arguments from durable manifest/receipts:

- stride;
- locations;
- warps;
- steps;
- samples;
- seed;
- policy;
- warmup;
- other relevant flags.

Do not infer missing values from labels.

If a runner index is missing, reconstruct it deterministically as a P2 artifact from the accepted payload path and label it derived.

Create early:

- `TRACE_AUTHORITY.tsv`
- `TRACE_LAUNCH_ARGUMENTS.tsv`

If a P1 trace payload is actually missing/corrupt and cannot be recovered from node164, STOP.

---

# Phase C — close Native-aligned observable identity

This phase must finish before the science matrix.

## C1. Inspect actual SASS trace

Inspect M0 and M1 first.

Determine:

- exact SASS instruction implementing the dependent global load;
- exact PC/opcode;
- how CUDA `clock64()` is represented in the captured SASS;
- whether start/end clock-read groups can be paired unambiguously per warp/sample;
- actual dependent-load count per sample;
- sample count per warp;
- whether trace dynamic structure agrees with the recovered command authority.

Do not assume source-level `clock64()` maps to one SASS instruction.

## C2. Preferred observable

If exact start/end clock-read groups are unambiguous:

define:

`CLOCK64_BRACKET_SIM_CYCLES_PER_DEPENDENT_STEP`

For each warp/sample:

1. observe simulator cycle at the defined start clock-read event;
2. observe simulator cycle at the corresponding end clock-read event;
3. subtract;
4. divide by exact dependent-step count.

Use a simulator event point that best corresponds to architectural execution/issue of the clock-read instruction.

Document the chosen event semantics.

Do not emulate or overwrite clock register values.

Do not change dependencies.

## C3. Fallback observable

If exact clock-read pairing is not possible but dependent-chain dynamic identity is unambiguous:

define:

`DEPENDENT_CHAIN_SPAN_CYCLES_PER_LOAD`

using a rigorously documented first-load to final dependency-release/completion span.

Label:

`DEPENDENT_CHAIN_SPAN_SUPPORTING_ONLY`

Do not call it Native-clock64-equivalent.

## C4. Identity stop gate

If neither clock bracket nor chain span can be defined without semantic invention:

STOP:

`NATIVE_ALIGNED_OBSERVABLE_IDENTITY_NOT_CLOSED`

Do not fall back to total kernel cycles as though it were equivalent.

---

# Phase D — implement opt-in cross-calibration diagnostics

All new simulator code in this stage must be opt-in.

Use a new observational switch:

`GPGPUSIM_AWMA_CROSSCAL_DIAGNOSTICS=1`

Default OFF.

## D1. Code organization

Prefer:

- one dedicated helper/module/struct for cross-calibration state;
- tiny read-only hooks at the required instruction/memory event points;
- one centralized enable/config parse;
- output prefix `awma_crosscal_`.

Avoid scattering repeated `getenv()` checks through hot paths.

Do not fold the new diagnostics into the V1/V2R1 semantic switches.

## D2. Hard neutrality rules

Diagnostics must never modify:

- scheduler choices;
- instruction readiness;
- scoreboard;
- memory requests;
- accessq;
- TLB state;
- PTW state;
- cache state;
- cycle timing;
- retry behavior;
- random state;
- downstream order.

Only observe existing state and write host-side counters/records.

## D3. Required output

At minimum produce, per selected warp/sample as applicable:

- kernel identity;
- warp identity;
- sample index;
- start cycle;
- end cycle;
- dependent-step/load count;
- normalized cycles/step;
- observable mode;
- validity/status.

Also produce aggregate summary:

- count;
- mean;
- median;
- p10;
- p90;
- CV or robust dispersion.

For M2 preserve per-warp information and separately compute the pooled distribution.

Do not confuse pooled per-warp latency with throughput.

---

# Phase E — telemetry neutrality qualification

Do not start the full science matrix until this passes.

Maintain:

- a clean reconstructed accepted candidate C0;
- an instrumented candidate C1.

## E1. Diagnostics-OFF equivalence

For M0 10/80 under each semantic:

- Legacy;
- V1;
- V2R1;

run:

```text
C0 clean
vs
C1 diagnostics OFF
```

Require exact equality in:

- terminal simulator cycles;
- instructions;
- CTA;
- translation unique/coverage;
- untranslated/unobserved;
- TLB/cache counters used later;
- Segment state;
- controller quiescence.

If a semantic does not expose a field, document that rather than fabricate it.

## E2. Diagnostics ON/OFF neutrality

For the same three M0 points:

```text
C1 diagnostics OFF
vs
C1 diagnostics ON
```

Require exact equality in all scientific outputs.

Only `awma_crosscal_*` telemetry and host wall time may differ.

Add at least one M1 neutrality point because the long dependent chain exercises the diagnostic path more heavily.

## E3. Observable-count gate

For M0/M1/M2/M3 require:

- expected warp count;
- expected sample count;
- expected dependent-step/load count;
- no duplicate sample;
- no missing completed sample;
- no malformed pairing.

Publish:

`TELEMETRY_NEUTRALITY.tsv`

If diagnostics alter simulated behavior, repair diagnostics only.

Do not change V1/V2R1 semantics.

---

# Phase F — freeze matrix configuration

Use accepted model-relative latency configurations only.

Primary:

`10/80`

Control:

`0/80`

Do not add or tune intermediate latency values.

Construct a single `MATRIX_CONFIG_AUTHORITY.tsv` binding each point to:

- trace ID;
- payload SHA;
- derived runner-index SHA;
- semantic mode;
- exact functional switches;
- diagnostics switch;
- latency config;
- reconstructed binary SHA;
- output directory.

Full matrix:

```text
M0 × Legacy × 10/80
M0 × Legacy × 0/80
M0 × V1     × 10/80
M0 × V1     × 0/80
M0 × V2R1   × 10/80
M0 × V2R1   × 0/80

M1 × same six
M2 × same six
M3 × same six
```

Total:

`24 points`

All run directories must be isolated.

---

# Phase G — execute 24-point microtrace matrix

Use maximum safe parallelism based on CPU/memory audit.

Do not allow output collision.

For every point require:

- terminal completion;
- expected kernel/CTA/instruction identity;
- no malformed trace;
- full translation coverage;
- untranslated = 0;
- unobserved = 0;
- Segment state as expected;
- no duplicate READY/application for V2R1;
- terminal translation-controller quiescence when diagnostics are enabled;
- Native-aligned observable valid;
- total kernel cycles captured;
- TLB/PTW/cache context counters captured.

If one point has an ordinary runner/index/config problem:

solve-and-continue.

Do not invalidate other independent points.

If a scientific payload identity changes, STOP.

---

# Phase H — build Native reference matrix

Do not contact 109 or recollect Native data.

Consume accepted Git evidence.

Create:

`NATIVE_REFERENCE_MATRIX.tsv`

At minimum include:

## M0

Evidence class:

`NATIVE_V1R1_SWEEP_SUPPORTING`

Expected configuration:

`4 KiB × 16 locations × 1 warp`

Representative median:

`52.0 cycles/load`

## M1 exact

Evidence class:

`NATIVE_V1R2_EXACT_PAIR`

`294.5 cycles/load median-of-medians`

## M2 exact

Evidence class:

`NATIVE_V1R2_EXACT_PAIR`

`281.0 cycles/load median-of-medians`

M1→M2:

`-4.5840%`

## M3

Evidence class:

`NATIVE_V1R1_SWEEP_SUPPORTING`

Bind the exact 64 KiB × 1024-location one-warp summary from the accepted V1R1 table.

Do not silently substitute another warm/thrash/cache-policy row.

Also create:

`AI_TARGET_EXISTING_ANCHORS.tsv`

using the frozen Native and simulator AI-target evidence from the context document.

No expensive AI rerun.

---

# Phase I — analyze cross-calibration

Create:

- `MICROTRACE_MATRIX.tsv`
- `NATIVE_ALIGNED_OBSERVABLE.tsv`
- `TRANSLATION_DIAGNOSTIC_MATRIX.tsv`
- `CROSS_CALIBRATION_ANALYSIS.md`

## I1. Primary 10/80 working-set comparison

For each semantic compute:

`M1 / M0`

using the Native-aligned observable.

Compare with Native behavior as a shape constraint.

Do not require absolute equality.

## I2. Primary exact concurrency comparison

For each semantic:

`(M2 - M1) / M1`

Compare with Native:

`-4.5840%`

Also show per-warp distributions.

Do not turn M2 pooled latency into aggregate throughput.

## I3. 10/80 vs 0/80 model-relative diagnostic

For each M0–M3 and semantic:

`(metric_10_80 - metric_0_80) / metric_10_80`

Interpret as model-relative lookup-latency sensitivity only.

Do not call it RTX4080 TLB sensitivity.

## I4. Legacy → V1 → V2R1

Determine whether:

- V1 reduces an externally implausible Legacy amplification;
- V1 preserves Native working-set behavior;
- V1 produces a concurrency trend closer to Native behavioral constraints;
- V2R1 adds any further alignment beyond V1.

Do not tune code after seeing the results.

## I5. M3 supporting analysis

Use M3 as a supporting spacing/working-set point.

Do not infer hardware page size.

If there is no matched 4KiB × 1024 one-warp simulator trace, do not present M3 as an isolated 4K-vs-64K experiment.

---

# Phase J — final scientific decision

Allowed labels:

```text
V1_NATIVE_ALIGNMENT_SUPPORTED
V1_NATIVE_ALIGNMENT_PARTIAL
V1_NATIVE_ALIGNMENT_NOT_SUPPORTED

V2R1_ADDS_NATIVE_ALIGNMENT_BENEFIT
V2R1_ADDS_NO_NATIVE_ALIGNMENT_BENEFIT

MIXED_NATIVE_SIMULATOR_ALIGNMENT
NATIVE_ALIGNED_OBSERVABLE_INSUFFICIENT
```

Also explicitly classify:

`LEGACY_FRONTEND_AMPLIFICATION_EXTERNALLY_SUPPORTED`

as:

- SUPPORTED;
- PARTIAL;
- NOT_SUPPORTED.

Do not automatically make V1 or V2R1 the project baseline.

If evidence supports promotion, state only:

`BASELINE_PROMOTION_CANDIDATE`

and STOP for ChatGPT.

Do not design any new TLB/PTW/cache mechanism.

---

# Phase K — report and review pack

Report:

`docs/vm_tlb/codex_handoff/awma/NATIVE_SIMULATOR_CROSS_CALIBRATION_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1/`

Required files:

```text
README.md
SOURCE_ANCHORS.md
TRACE_AUTHORITY.tsv
TRACE_LAUNCH_ARGUMENTS.tsv
RECONSTRUCTED_SIMULATOR_AUTHORITY.json
CROSSCAL_DIAGNOSTIC_CONTRACT.md
CROSSCAL_DIAGNOSTIC.patch
OBSERVABLE_IDENTITY.md
TELEMETRY_NEUTRALITY.tsv
MATRIX_CONFIG_AUTHORITY.tsv
MICROTRACE_MATRIX.tsv
NATIVE_ALIGNED_OBSERVABLE.tsv
TRANSLATION_DIAGNOSTIC_MATRIX.tsv
AI_TARGET_EXISTING_ANCHORS.tsv
NATIVE_REFERENCE_MATRIX.tsv
CROSS_CALIBRATION_ANALYSIS.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

No accidental zero-byte placeholders.

Before commit:

- parse JSON;
- validate TSV row widths;
- verify all required files non-empty;
- recompute all derived percentages from raw rows;
- regenerate SHA256SUMS last.

---

# Phase L — remote publication contract

Close exactly:

```text
science closure
→ report/review pack
→ SHA256SUMS
→ commit
→ push
→ fetch-back
→ remote HEAD == local HEAD
→ inspect fetched remote tree
→ every promised file exists
→ every semantically-required file is non-empty
→ sha256sum -c against fetched remote contents
→ worktree clean
→ STOP
```

Publication failure is engineering/provenance only.

Do not rerun scientific simulations just because Git publication failed.

---

# Global stop / continue policy

Ordinary engineering problems:

`solve-and-continue`

Examples:

- index wrapper missing;
- path mismatch;
- build integration;
- parser bug;
- stale temp file;
- output-directory collision;
- Git transport;
- deterministic manifest reconstruction.

STOP only if:

1. accepted microtrace scientific payload is missing/corrupt with no recovery path;
2. microtrace target identity must change;
3. V1/V2R1 semantic contract must change;
4. Native-aligned observable cannot be closed without changing simulator/program semantics;
5. claim/evidence boundary must change materially.

Do not ask for review between normal phases.

Run the Goal continuously to final publication or a real scientific STOP.

