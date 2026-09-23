# AWMA PROJECT HANDOFF — Native ↔ Simulator Cross-Calibration V1

Date: 2026-09-23  
Node: 174-new  
Purpose: complete the first external/native calibration of the accepted AWMA translation/frontend simulator semantics before any new TLB/PTW/cache mechanism is designed.

---

# 0. Executive state

The simulator-internal frontend investigation has reached semantic closure for the two concrete HOL hypotheses already tested:

1. **Legacy accessq-head-only translation launch serialization is a real simulator amplification.**
2. **READY result application being delayed until the accessq head is NOT the primary source of the remaining T2 sensitivity.**

The next stage must stop tuning the simulator against its own 10→0 sensitivity and instead compare simulator behavior against already-collected Native RTX4080 evidence.

Stage to execute:

`AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1`

This is a **calibration / validation stage**, not a new architecture-mechanism stage.

---

# 1. Hard frozen conclusions — do not reopen

Do not redesign, rerun, or debate these unless a new hard contradiction is discovered.

## 1.1 Accepted Native / producer foundations

Frozen:

- simulator-native producer lifecycle;
- exact Q05 identity;
- contiguous-prefix recovery;
- contextual replay;
- VM per-access coverage repair;
- V3 VM-map audit;
- V3R1 Segment dormancy;
- hit-path attribution;
- accepted Native target identity/Route-B evidence;
- Native calibration V1/V1R1/V1R2 evidence described below.

Do not return to node109 merely because a runner wrapper/index is missing on 174 if the scientific payload already exists on node164 and a deterministic P2/P3 wrapper can be reconstructed.

## 1.2 Accepted V1 frontend result

Authority:

`hrl/awma-174-translation-frontend-pipelining-v1`

HEAD:

`ad6f38878bc1e7c268b17e65fdb3793a3899a84d`

V1 meaning:

- resident accessq entries may launch translation before becoming the head;
- existing one-L1-TLB-port-per-cycle behavior remains authoritative;
- each access still requires its own translation READY before downstream admission;
- downstream accessq order is unchanged;
- no new TLB/PTW/cache mechanism;
- V1 prelaunch is observe-only at READY:
  `consume_ready=false`;
- normal head path remains the READY consumer.

Accepted V1 T0/T1/T2 matrix:

| Target | V1 10/80 | V1 0/80 | residual |
|---|---:|---:|---:|
| T0 | 756,812 | 693,548 | 8.3593% |
| T1 | 1,320,195 | 1,251,826 | 5.1787% |
| T2 | 111,607 | 71,743 | 35.7182% |

Legacy/V3R1 comparison:

| Target | Legacy 10/80 | Legacy 0/80 | legacy sensitivity |
|---|---:|---:|---:|
| T0 | 1,654,548 | 711,464 | 56.9995% |
| T1 | 3,114,834 | 1,252,198 | 59.7989% |
| T2 | 152,777 | 71,654 | 53.0990% |

Accepted project-level V1 classification:

`SERIAL_ACCESSQ_FRONTEND_AMPLIFICATION_PARTIAL`

Interpretation:

- launch serialization explains most of the Legacy 10→0 amplification for T0/T1;
- T2 retains a large residual;
- V1 is still a diagnostic/recalibration candidate, not an accepted hardware-calibrated baseline.

## 1.3 Accepted V2R1 result

Final publication authority:

`hrl/awma-174-translation-frontend-ready-application-v2r1`

HEAD:

`dccc11f05aece7ee8ef07ffd0bec7ad83d8eb1f8`

V2R1 meaning:

- contains accepted V1 launch pipelining;
- when a resident non-head access becomes READY, V2R1 **consumes** the exact controller READY once and applies its PA/outcome to that exact resident `mem_access_t`;
- this still does NOT admit the access downstream early;
- downstream order remains unchanged;
- V1 mode remains observe-only;
- V2R1 mode is consume-and-apply.

Final T2 result:

```text
T2 V2R1 10/80 = 111,607
T2 V2R1  0/80 =  71,743
residual        = 35.7182%
```

Correctness closure for both points:

```text
gpu_sim_insn          = 43,357,696
CTA                   = 1,216
unique UID            = 411,008
translated_unique     = 411,008
untranslated          = 0
unobserved            = 0
duplicate application = 0

m_lookups             = 0
LOOKUP_READY          = 0
m_mshrs               = 0
m_pwq                 = 0
active_walks          = 0
quiescent_invariants_hold = true
Segment functional activity = 0
```

Accepted classification:

`READY_APPLICATION_HOL_NOT_PRIMARY`

Meaning:

The remaining T2 35.7182% sensitivity is **not** explained by READY results waiting until accessq-head application.

This does **not** identify the remaining 35.7182% source.

Possible remaining components include:

- genuine modeled lookup-latency exposure that cannot be hidden;
- zero-latency retry/order nonlinearity;
- LD/ST pipeline / scoreboard / warp-level coupling;
- other simulator/hardware differences.

Do not infer which one dominates from the V2R1 result alone.

## 1.4 Pre-repair V2 is not scientific final evidence

Pre-repair V2 authority:

`hrl/awma-174-translation-frontend-ready-application-v2 @ 1a5f4dc49273c9640b981fb1b946d146dd15f21b`

Frozen status:

`PRE_REPAIR_READY_RETENTION_INVALID_FOR_FINAL_CLASSIFICATION`

Root cause:

- prelaunch passed `!ready_application_v2`;
- V2 mode therefore used `consume_ready=false`;
- PA/outcome was applied to resident access but controller READY lookup remained;
- access later skipped the head translate path;
- READY lookup became stranded;
- `m_lookups` accumulated;
- host-side lookup cost grew severely.

Engineering evidence after repair:

- repaired T2 10/80 ~808 simulated cycles/s;
- repaired T2 0/80 ~547 simulated cycles/s;
- pre-repair T2 10/80 had degraded to roughly 11 cycles/s in recovered evidence.

Do not use pre-repair V2 as final calibration evidence.

---

# 2. Existing simulator feature switches

The cross-calibration stage must preserve these semantics independently.

## 2.1 Functional switches

### Legacy

```text
GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH=0/unset
GPGPUSIM_READY_APPLICATION_V2=0/unset
```

### V1

```text
GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH=1
GPGPUSIM_READY_APPLICATION_V2=0/unset
```

### V2R1

```text
GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH=1
GPGPUSIM_READY_APPLICATION_V2=1
```

V2R1 requires V1 pipelined launch enabled.

## 2.2 Existing diagnostic switches

```text
GPGPUSIM_READY_APPLICATION_DIAGNOSTICS
GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS
```

These are diagnostic-only.

## 2.3 Mandatory rule for all new code

**Every new simulator feature added in this stage must be opt-in.**

More specifically:

- functional semantics switches and observational/telemetry switches must remain separate;
- default OFF must preserve accepted behavior;
- new cross-calibration telemetry must not alter:
  - simulated cycles;
  - arbitration;
  - queue state;
  - TLB/PTW/cache state;
  - scheduler behavior;
  - memory request timing;
  - random state;
  - downstream order;
- telemetry may increase host wall time only;
- all diagnostic output should use a dedicated `awma_crosscal_` prefix;
- prefer one dedicated helper/module/struct rather than scattering calibration code across unrelated simulator files;
- parse the new diagnostic enable once, not via repeated hot-path `getenv()` calls;
- diagnostics OFF/ON neutrality must be proven before the science matrix is admitted.

Suggested new switch:

`GPGPUSIM_AWMA_CROSSCAL_DIAGNOSTICS=1`

Do not repurpose an existing semantic switch for calibration telemetry.

---

# 3. Native RTX4080 evidence already collected — do not recollect by default

Native calibration authority V1R1:

`hrl/awma-native-calibration-analysis-109-v1r1 @ 589d0d579e8e9d30922d3842084c3c50f09833d7`

Exact M1/M2 pair authority V1R2:

`hrl/awma-native-calibration-exact-pair-v1r2 @ 1d56c7ff12bd273f0f27c0de24d308a255b50b56`

Native GPU UUID in V1R2:

`GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59`

No direct Native TLB/MMU/GMMU translation counter was admitted by NCU.

Therefore:

- Native evidence is behavioral;
- do not claim Native L1-TLB latency/capacity from these data;
- do not equate Native clock cycles with simulator cycles as absolute values.

## 3.1 Exact AI target Native timing

| Target | mean ns | median ns | CV | status |
|---|---:|---:|---:|---|
| T0 Q05 FlashAttention | 152,717.0 | 152,544 | 4.567% | MEASURED_WITH_VARIABILITY |
| T1 Prefill GEMM | 203,591.2 | 203,873 | 0.286% | STABLE_NATIVE_TIMING_ANCHOR |
| T2 Decode GEMV | 4,422.4 | 4,416 | 1.073% | STABLE_NATIVE_TIMING_ANCHOR |

These are workload anchors only.

Never fit:

`Native ns ↔ simulator cycles`

directly.

## 3.2 Native target footprints

### T0 Q05 FlashAttention

```text
memory instructions   = 1,100,848
effective lane addrs  = 33,693,184
unique 4 KiB regions  = 3,625
unique 64 KiB regions = 228
```

### T1 Prefill GEMM

```text
memory instructions   = 2,298,240
effective lane addrs  = 70,352,896
unique 4 KiB regions  = 7,906
unique 64 KiB regions = 495
```

### T2 Decode GEMV

```text
memory instructions   = 318,592
effective lane addrs  = 9,022,720
unique 4 KiB regions  = 2,132
unique 64 KiB regions = 135
```

The 4 KiB / 64 KiB aggregation is an address-footprint description only.

It does not prove RTX4080 hardware TLB page sizes.

---

# 4. Native controlled microbenchmark evidence

Source family:

`util/vm_tlb/awma/native_tlb_probe_v1`

Native probe V1R2 source SHA256:

`cec9492b3d6dfeedab3cfcc3659523eaa6afebb2c0158499ad8c423b20d70f07`

Native probe V1R2 binary SHA256:

`a9488afa190ba1e27e58f840b07f1db092177c5a097773ce6a8934262e37357f`

The probe uses a dependent pointer/address chain and Native `clock64()`.

The Native quantity is therefore a dependent-chain behavioral latency exposure:

`(clock64_end - clock64_start) / steps`

It includes realized memory-hierarchy behavior and loop/instruction effects.

It is **not** a direct TLB latency counter.

## 4.1 Working-set behavior

For the 4 KiB-spacing, one-warp dependent chain, representative medians from V1R1:

| locations | median cycles/load |
|---:|---:|
| 16 | 52.0 |
| 512 | 52.0 |
| 1024 | 155.5 |
| 2048 | 245.5 |
| 4096 | 282.5 |
| 8192 | 302.0 |
| 16384 | 427.5 |
| 32768 | 644.5 |

There is strong working-set-dependent latency exposure.

Do not call the knee a hardware TLB capacity.

## 4.2 1024-location concurrency behavior

At 1024 locations, one warp → sixteen warps reduced pooled per-chain median across several address spacings:

| spacing | 1 warp | 16 warps | reduction |
|---|---:|---:|---:|
| 4 KiB | 166.0 | 110.0 | 33.73% |
| 64 KiB | 169.5 | 104.0 | 38.64% |
| 256 KiB | 155.0 | 111.0 | 28.39% |
| 2 MiB | 165.5 | 106.0 | 35.95% |

This supports concurrency hiding behavior in that working-set regime.

## 4.3 Exact representative M1/M2 pair

V1R2 froze an exact pair:

```text
stride       = 4096 bytes
locations    = 4096
steps        = 512
samples      = 50 per warp
policy       = default
warmup       = 2
seed         = 102
```

M1:

```text
warps = 1
process medians = 294.0, 294.5, 295.0
median-of-medians = 294.5 cycles/load
```

M2:

```text
warps = 16
process pooled medians = 279.0, 282.0, 281.0
median-of-medians = 281.0 cycles/load
```

Exact Native M1→M2 relative change:

`-4.5840%`

Accepted interpretation:

`NATIVE_CONCURRENCY_HIDING_PARTIAL / WORKING_SET_DEPENDENT`

Important:

The M2 Native value is a pooled distribution of 16 independent warp-local chains.

It is not aggregate throughput.

---

# 5. Qualified simulator-native microtraces already available on node164

Authority:

`AWMA_NATIVE_TRANSLATION_CALIBRATION_ANALYSIS_109_V1R1`

Common Native calibration provenance root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/native_translation_calibration_109_v1_20260922T101218Z`

Common source/destination manifest authority:

`4b3b51c96c05a6f54f88d2414b3aaae59c80886e95b6fc993df29970f57e7053`

All four:

- selector: `chase_occurrence_0`;
- producer: Route-B / NVBit 1.7.7.1;
- zero drop;
- zero overflow;
- xz integrity PASS;
- postprocess trace-format PASS;
- durable hash closed.

## M0_COMPACT

```text
configuration: 4K stride × 16 locations × 1 warp
durable path:
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/native_translation_calibration_109_v1_20260922T101218Z/microtraces/m0_compact

payload SHA256:
b9f87594b0279d8b489aa5181e6fcf37551e04553b154a7848c88fa44fc03e7e

raw records: 6,574
```

## M1_DEPENDENT_LARGE

```text
configuration: 4K stride × 4096 locations × 1 warp
durable path:
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/native_translation_calibration_109_v1_20260922T101218Z/microtraces/m1_dependent_large

payload SHA256:
bea5cf39d41f9807d95be659984fe850c56d910214ecfe85d6379df705cc9ec5

raw records: 6,574
```

## M2_MULTIWARP_HIGH

```text
configuration: 4K stride × 4096 locations × 16 warps
durable path:
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/native_translation_calibration_109_v1_20260922T101218Z/microtraces/m2_multiwarp_high

payload SHA256:
c165749ff06013f7bebc6ceecb2915f5de0b3d88171366a4832001cd6da2642f

raw records: 105,184
```

## M3_STRIDE64K

```text
configuration: 64K stride × 1024 locations × 1 warp
durable path:
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/native_translation_calibration_109_v1_20260922T101218Z/microtraces/m3_stride64k

payload SHA256:
be63c6cd23cb101d626be18bc82766c27a91ff687f1d4427d9ba47cbf26d0799

raw records: 6,574
```

Before simulation, verify the durable manifests and recover the **full actual launch arguments** for each trace, especially:

- steps;
- samples;
- warmup;
- seed;
- policy.

Do not silently assume the simulator-native capture used the exact V1R2 timing-run values merely because stride/locations/warps match.

If trace launch arguments differ from Native timing runs, preserve the distinction in evidence class.

---

# 6. Cross-calibration scientific questions

The goal is not to force simulator numbers to equal Native numbers.

The goal is to test whether the **relative behavioral constraints** of the simulator become more or less consistent with Native evidence when moving:

`Legacy → V1 → V2R1`

Primary questions:

## Q1 — Working-set amplification

Native behavior strongly increases from compact M0-like working set to large M1-like working set.

Does each simulator semantic reproduce a qualitatively and quantitatively meaningful M0→M1 increase in a Native-aligned dependent-chain observable?

## Q2 — Exact M1→M2 concurrency behavior

Native exact pair:

```text
M1 1 warp  = 294.5 cycles/load
M2 16 warp = 281.0 cycles/load
relative   = -4.584%
```

For each simulator semantic, what is the exact M1→M2 change in the Native-aligned observable?

Do not compare Native 294.5/281.0 directly to total simulator kernel cycles.

## Q3 — Translation contribution versus generic memory behavior

For each microtrace and semantic, compare:

`10/80` versus `0/80`

This is a **model-relative L1-lookup-latency diagnostic**, not a hardware latency measurement.

Use it to determine whether a semantic change mainly alters translation-latency amplification or generic kernel behavior.

## Q4 — Does V2R1 add any Native-alignment benefit over V1?

V2R1 made no difference to T2 10/80↔0/80 cycles after correctness repair.

Test whether V2R1 also changes or does not change microbenchmark cross-calibration behavior.

## Q5 — Is the remaining T2 35.7182% residual obviously inconsistent with Native behavior?

Do not answer by inventing a hardware TLB latency.

Instead determine whether the controlled microbench behavior under the accepted simulator semantics shows:

- excessive latency amplification;
- excessive concurrency hiding;
- insufficient working-set sensitivity;
- or mixed behavior.

---

# 7. Mandatory Native-aligned simulator observable

Total kernel cycles are secondary.

The primary calibration observable should align as closely as possible with the Native `clock64()` bracket used by the dependent-chain benchmark.

## 7.1 First choice — CLOCK64 bracket observable

Before writing instrumentation:

1. inspect the actual M0/M1 simulator-native SASS trace;
2. identify how CUDA `clock64()` appears in the captured SASS;
3. identify the dependent global-load instruction PC/opcode;
4. prove the dynamic bracket/sample structure is unambiguous.

If the trace contains an identifiable start/end clock-read pattern per sample, instrument simulator cycles at those exact dynamic clock-read events per warp/sample.

Preferred quantity:

`sim_clock_bracket_cycles / dependent_steps`

This is the closest simulator-side semantic analogue of the Native quantity.

The instrumentation must only observe existing instruction flow.

It must not write architectural clock values back into the simulated program or change dependency behavior.

## 7.2 Fallback — dependent chain span

If exact clock-bracket identity cannot be closed from the trace/parser:

use an explicitly defined dependent-chain observable such as:

- first dependent load issue cycle;
- final dependent load dependency-release/completion cycle;
- exact dependent-load count;
- normalized span per dependent load.

Label this:

`DEPENDENT_CHAIN_SPAN_SUPPORTING_ONLY`

Do not describe it as exactly equivalent to Native `clock64()`.

## 7.3 Stop boundary for observable identity

If neither clock-bracket nor dependent-chain identity can be established without changing program semantics, STOP with:

`NATIVE_ALIGNED_OBSERVABLE_IDENTITY_NOT_CLOSED`

Do not invent a metric.

---

# 8. Cross-calibration simulator matrix

Use the accepted latency configurations only.

Do not tune latency toward Native results.

Primary:

`10/80`

Diagnostic control:

`0/80`

No new latency values in V1.

Semantics:

```text
LEGACY
V1_PIPELINED_LAUNCH
V2R1_READY_CONSUME_APPLY
```

Microtraces:

```text
M0
M1
M2
M3
```

Full matrix:

`4 traces × 3 semantics × 2 latency configs = 24 points`

These microtraces are intentionally small; execute with maximum safe parallelism after isolating run directories and immutable inputs.

No matrix point may share mutable output directories.

---

# 9. Telemetry-neutrality gates before the 24-point science matrix

New cross-calibration diagnostics must be proven observational-only.

Create a clean pre-instrumentation candidate and an instrumented candidate.

At minimum prove:

## G1 — build/source identity

- accepted V1/V2R1 semantics reconstructed from accepted authority;
- clean build;
- cross-calibration patch isolated and hashed.

## G2 — diagnostics OFF equivalence

For representative small points, instrumented binary with diagnostics OFF must exactly match clean candidate in:

- terminal simulator cycles;
- instructions;
- CTA;
- translation coverage;
- relevant TLB/cache counters;
- Segment state;
- quiescence.

Run at least one point for each semantic mode.

M0 10/80 is preferred because it is small.

## G3 — diagnostics ON neutrality

For the same representative points:

diagnostics ON versus OFF must exactly match all scientific simulator outputs listed above.

Only the new diagnostic telemetry may differ.

## G4 — observable count sanity

For M0/M1/M2/M3:

- sample/warp count must agree with trace/program authority;
- dependent-load count must agree with trace/program authority;
- no duplicate sample accounting;
- no missing terminal sample unless explicitly explained.

Do not start the full matrix until G1–G4 pass.

---

# 10. Existing AI-target simulator results — reuse, do not rerun

Cross-calibration should include a compact table of already accepted AI-target evidence.

Do not rerun expensive T0/T1/T2 merely for symmetry.

Use:

## Legacy

```text
T0 10/80 = 1,654,548
T0  0/80 =   711,464

T1 10/80 = 3,114,834
T1  0/80 = 1,252,198

T2 10/80 =   152,777
T2  0/80 =    71,654
```

## V1

```text
T0 10/80 =   756,812
T0  0/80 =   693,548

T1 10/80 = 1,320,195
T1  0/80 = 1,251,826

T2 10/80 =   111,607
T2  0/80 =    71,743
```

## V2R1

Only scientifically admitted T2 pair:

```text
T2 10/80 = 111,607
T2  0/80 =  71,743
```

Do not fabricate T0/T1 V2R1 terminal results.

---

# 11. Analysis rules

## 11.1 Never use these invalid equalities

Do NOT equate:

- Native ns with simulator cycles;
- Native `clock64` cycles/load with total simulator kernel cycles;
- NCU L2 bytes with simulator L2 accesses;
- 4 KiB / 64 KiB region aggregation with hardware TLB page size;
- simulator 10-cycle lookup with RTX4080 hardware TLB latency;
- Native cache behavior with simulator TLB behavior.

## 11.2 Primary normalized comparisons

For each semantic at 10/80:

### Working-set ratio

`M1 / M0`

using the Native-aligned observable.

### Exact concurrency change

`(M2 - M1) / M1`

Native exact reference:

`-4.5840%`

### Translation-latency diagnostic

For each Mx:

`(metric_10_80 - metric_0_80) / metric_10_80`

This remains simulator-model-relative.

## 11.3 Secondary outputs

Also report:

- total kernel cycles;
- simulator instructions;
- CTA;
- L1 TLB hit/miss;
- L2 TLB hit/miss if available;
- walk activity;
- MSHR/PWQ activity;
- translation coverage;
- cache/DRAM counters already available;
- terminal quiescence.

Use these to explain, not redefine, the primary Native-aligned metric.

---

# 12. Predeclared interpretation classes

Do not tune simulator code or latency parameters to obtain any expected label.

Allowed final scientific classifications:

- `V1_NATIVE_ALIGNMENT_SUPPORTED`
- `V1_NATIVE_ALIGNMENT_PARTIAL`
- `V1_NATIVE_ALIGNMENT_NOT_SUPPORTED`
- `V2R1_ADDS_NATIVE_ALIGNMENT_BENEFIT`
- `V2R1_ADDS_NO_NATIVE_ALIGNMENT_BENEFIT`
- `MIXED_NATIVE_SIMULATOR_ALIGNMENT`
- `NATIVE_ALIGNED_OBSERVABLE_INSUFFICIENT`

Additionally state whether:

`LEGACY_FRONTEND_AMPLIFICATION_EXTERNALLY_SUPPORTED`

is supported, partial, or not supported by the controlled Native comparison.

Do not promote a new simulator baseline automatically.

At most classify:

`BASELINE_PROMOTION_CANDIDATE`

and STOP for ChatGPT review.

---

# 13. Source reconstruction / worktree guidance

A fresh Codex window must not assume the accepted runtime candidate still exists in-place.

Execution must:

1. create a new isolated worktree/staging area;
2. preserve the handoff branch;
3. recover accepted V1/V2R1 source from the strongest surviving authority.

Preferred order:

1. surviving accepted V1/V2R1 source/worktree if byte-identical and authority can be proven;
2. V2R1 archived source evidence under:
   `/root/awma_v2r1_closeout_pending`;
3. published V2R1 repair patch at:
   `docs/vm_tlb/review_packs/AWMA_TRANSLATION_FRONTEND_READY_APPLICATION_RECALIBRATION_V2R1/READY_CONSUMPTION_REPAIR.patch`;
4. accepted V1 source/repair authority.

Do not silently reimplement V1/V2R1 from prose.

After reconstruction:

- build;
- run accepted controller regressions;
- prove functional switch truth table;
- hash the reconstructed source/binary;
- record exact provenance.

The V2R1 publication branch is an evidence authority; do not assume its repository-root simulator source already contains the runtime patch.

---

# 14. Resource / execution policy

Use maximum safe parallelism after inputs and outputs are isolated.

Allowed to parallelize:

- trace inspection;
- source reconstruction verification;
- build-independent parsing;
- 24 matrix points with isolated run directories;
- post-processing.

Do not parallelize processes that share mutable simulator output state.

Ordinary engineering failures:

`solve-and-continue`

Examples:

- derived runner index missing;
- wrapper/manifest path issue;
- build include/signature error;
- stale temporary directory;
- parser path;
- publication transport.

Do not upgrade P2/P3 wrapper loss into scientific input loss if deterministic reconstruction from accepted authority is possible.

Stop only for:

- P1 scientific payload missing/corrupt with no accepted recovery path;
- target/trace identity change;
- Native observable identity cannot be closed;
- source semantic contract must change;
- evidence/claim boundary must change.

---

# 15. Publication contract

Suggested execution branch:

`hrl/awma-174-native-simulator-cross-calibration-v1`

Final report:

`docs/vm_tlb/codex_handoff/awma/NATIVE_SIMULATOR_CROSS_CALIBRATION_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1/`

At minimum include:

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

Before commit:

- no promised file may be an accidental zero-byte placeholder;
- all TSV/JSON files parse;
- all matrix rows bind exact trace SHA + semantic mode + latency config + binary SHA;
- all scientific rows identify evidence class.

Publication close:

```text
report/review pack
→ SHA256SUMS
→ commit
→ push
→ fetch-back
→ remote HEAD == local HEAD
→ remote tree contains every promised file
→ all required files non-empty
→ sha256sum -c on fetched remote tree
→ clean worktree
→ STOP
```

Do not start any new TLB/PTW/cache mechanism in this Goal.

---

# 16. Expected end state

At the end of this stage we should be able to answer, with external/native evidence:

1. Did Legacy accessq-head serialization exaggerate translation-latency sensitivity relative to controlled Native behavior?
2. Does V1 move the simulator in the correct behavioral direction?
3. Does V2R1 add anything beyond V1?
4. Does the simulator reproduce:
   - strong M0→M1 working-set exposure;
   - weak/modest exact M1→M2 hiding at 4096 locations;
   - sensible 10/80→0/80 model-relative translation contribution?
5. Is V1/V2R1 credible enough to become a **baseline promotion candidate**, or is another simulator-model discrepancy still externally visible?

Only after this cross-calibration should the project decide whether to:

- promote a recalibrated baseline;
- further repair simulator semantics based on a specific Native mismatch;
- or begin a new TLB/PTW/cache mechanism.

