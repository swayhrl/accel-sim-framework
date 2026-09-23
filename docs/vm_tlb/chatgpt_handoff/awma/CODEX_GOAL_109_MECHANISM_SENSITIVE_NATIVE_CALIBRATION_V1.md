# CODEX 109 GOAL — Mechanism-Sensitive Native Calibration + RTX4080 Platform Anchors V1

Date: 2026-09-23

Mode:

`GOAL MODE / LONG-RUN / SOLVE-AND-CONTINUE / BOUNDED INFRASTRUCTURE`

Node:

`109 / RTX4080`

Stage:

`AWMA_MECHANISM_SENSITIVE_NATIVE_CALIBRATION_109_V1`

Read first, completely:

`docs/vm_tlb/chatgpt_handoff/awma/AWMA_PAPER_GRADE_PLATFORM_AND_MECHANISM_CALIBRATION_CONTEXT_2026-09-23.md`

This Goal has two coordinated outputs:

1. an **early, small RTX4080 platform-anchor bundle** for node174 platform qualification;
2. a **new mechanism-sensitive benchmark** whose memory instructions produce multiple coalesced accessq entries.

The second output is the main scientific task.

Do not build a large new GPU characterization suite.

Do not run Accel-Sim on node109.

---

# Phase A — branch and environment authority

Create execution branch:

`hrl/awma-109-mechanism-sensitive-native-calibration-v1`

Record:

- GPU UUID;
- GPU model;
- driver;
- CUDA;
- NVBit/Route-B producer authority;
- accepted Native exact control authority:
  `149af0566cc6720621fdfe88d3cd3ca9b32cba67`

Use the same qualified trace producer family unless a minimum extension is required.

Do not modify accepted `native_tlb_probe_v1`.

---

# Phase B — publish a SMALL RTX4080 platform-anchor bundle early

Purpose:

give node174 enough independent Native evidence to qualify a reasonable RTX4080/Ada Accel-Sim base config.

This is deliberately bounded.

## B1. Prefer existing microbench infrastructure

First search local/upstream Accel-Sim/GPGPU-Sim tuner/microbenchmark infrastructure already present.

Prefer existing, known-working CUDA microbenchmarks over writing new ones.

Do not spend more than one ordinary engineering repair cycle on any single platform anchor.

If a particular official microbench is unavailable/broken, replace it with a simpler independent point.

## B2. Calibration-anchor target dimensions

Obtain at least four usable calibration anchors covering:

```text
P-L1   small working-set / L1-class latency behavior
P-L2   medium working-set / L2-class latency behavior
P-DRAM dependent/global-memory latency behavior
P-BW   streaming global-memory bandwidth behavior
```

Optional, only if trivial:

`P-COMP basic arithmetic throughput`

The exact benchmark names are not important.

What matters is that their semantics are clear and they are independent from AWMA M0–M3 and future mechanism-sensitive workloads.

For each calibration anchor:

- use an explicit command;
- run uninstrumented Native timing >=3 repetitions;
- record median and variation;
- capture one qualified simulator-native SASS trace;
- preserve source/binary hash;
- zero drop/overflow;
- xz/grammar PASS.

Do not use NCU as a required primary measurement.

NCU may be used only if one metric is easy and necessary to identify whether an anchor is actually L1/L2/DRAM dominated.

## B3. Held-out platform validation points

Also publish at least three held-out simple kernels/points, not used to choose/tune platform parameters:

- one cache-friendly memory point;
- one streaming/bandwidth-oriented point;
- one compute or mixed point.

Prefer already-working simple kernels from existing CUDA/Accel-Sim suites.

Do not create a large benchmark set.

For held-out points:

- uninstrumented Native timing >=3 repetitions;
- one qualified trace;
- source/binary/CLI authority.

Mark every point explicitly:

`CALIBRATION`

or:

`HELDOUT_VALIDATION`

## B4. Clock policy

Attempt once to establish a stable/repeatable GPU clock policy if permissions and existing environment make it easy.

If fixed clocks are not available:

- record the default policy;
- record observed clock information if easy;
- use repetition/median;
- proceed.

Do not spend significant time fighting GPU clock locking.

## B5. Early durable publication

Publish this bundle to node164 **before** spending the rest of the Goal on the mechanism-sensitive benchmark.

Bundle receipt identity:

`RTX4080_PLATFORM_ANCHORS_109_V1`

Suggested durable root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/rtx4080_platform_anchors_v1_<timestamp>`

Required early bundle content:

```text
README
GPU_ENVIRONMENT
ANCHOR_ROLE.tsv
COMMAND_AUTHORITY.tsv
NATIVE_TIMING.tsv
TRACE_AUTHORITY.tsv
SOURCE_BINARY_AUTHORITY.tsv
MANIFEST/SHA256SUMS
node164 destination verification
```

After this early publication, continue immediately to the main benchmark.

Do not STOP merely to report the anchor bundle.

---

# Phase C — create a NEW mechanism-sensitive benchmark source family

Create a new source family, for example:

`util/vm_tlb/awma/native_accessq_probe_v1/`

Do NOT modify:

`native_tlb_probe_v1`

Scientific purpose:

one warp memory instruction must generate a controlled number of coalesced memory transactions, therefore controlled accessq cardinality in the simulator.

Use all 32 lanes as active participants.

---

# Phase D — benchmark design contract

Use a grouped-lane address pattern.

Let:

`fanout = K`

where K divides 32.

Partition 32 lanes into K groups.

Lanes in one group access words inside the same aligned 128B line.

Different groups access distinct, widely separated regions.

The target memory instruction is therefore expected to create approximately K coalesced transactions / accessq entries.

Use three main fanouts:

```text
K1  = 1
K8  = 8
K32 = 32
```

K1 is the mechanism-inactive control.

K8 and K32 are mechanism-sensitive candidates.

## D1. Address layout

Use an explicit, deterministic layout.

Recommended starting design:

```text
locations = 256
node_stride = 4096 bytes
group separation >= one 64KiB model region
seed = 102
```

The exact group separation may be larger if needed for safe alignment and per-warp isolation.

For multi-warp configuration, give each warp an independent region to avoid unintended cross-warp data sharing.

Memory footprint must remain safely below GPU capacity.

## D2. Dependent chain behavior

Each lane group should follow the same logical chain index.

At one dependent load instruction:

- all 32 lanes are active;
- lanes in the same group access different words in one 128B line;
- all words in that line encode the same next chain index;
- different groups access separate lines/regions;
- after the load, every group advances deterministically.

This preserves a warp-level dependent sequence while exposing multiple transactions per instruction.

Do not serialize groups in software.

The mechanism-sensitive property must come from one warp LDG with divergent addresses.

## D3. Timing bracket

Use Native `clock64()` around the repeated dependent-load loop.

Lane0 may store the warp timing result after the warp-synchronous loop.

Use `__syncwarp()` only where required for a correct bracket; keep it identical across fanouts.

The primary Native quantity is:

`cycles per dependent warp-load step`

Do not interpret it as direct TLB latency.

---

# Phase E — frozen benchmark configurations

Start with exactly four primary configurations.

Common:

```text
steps = 256
samples = 50
warmup_batches = 2
seed = 102
policy = default
locations = 256
```

Configs:

## A1_CONTROL

```text
fanout = 1
warps = 1
```

## A8

```text
fanout = 8
warps = 1
```

## A32

```text
fanout = 32
warps = 1
```

## A32_W8

```text
fanout = 32
warps = 8
```

Do not add many more fanout/warp points in this Goal.

Only add one surgical configuration if one of these four cannot establish mechanism opportunity for a clear technical reason.

---

# Phase F — source-level / trace-level mechanism-opportunity precheck

Before doing full timing:

1. compile;
2. run one small correctness invocation;
3. capture a short trace;
4. inspect the target dependent LDG:
   - active mask must contain 32 active lanes;
   - address list must contain the intended K groups;
   - unique aligned 128B-line count should equal K or the precisely explained expected transaction grouping.

Publish:

`TRACE_COALESCING_PRECHECK.tsv`

This is only a precheck.

Actual simulator `accessq_entries` will later be measured on node174.

If K8/K32 collapse to one transaction because of compiler/address-layout behavior:

repair benchmark engineering and continue.

If the compiler emits separate scalar instructions instead of one warp memory instruction:

repair source/layout until the intended single-LDG warp event is obtained.

Do not proceed with a benchmark that cannot structurally exercise multiple transactions.

---

# Phase G — Native timing

For A1/A8/A32/A32_W8:

run 3 independent uninstrumented Native processes each.

Record:

- all measurement samples;
- mean;
- median;
- p10;
- p90;
- CV;
- median-of-medians.

The important Native comparisons are relative:

```text
A8 / A1
A32 / A1
A32_W8 / A32
```

Do not infer TLB sizes or direct lookup latency.

---

# Phase H — exact ordered trace-pair capture

For every configuration capture in the same process/context:

```text
target occurrence0 = warmup
→
target occurrence1 = measurement
```

Keep exact ordering.

Expected clock-bracket counts:

## A1/A8/A32, 1 warp

```text
warmup occurrence0 = 2
measurement occurrence1 = 50
```

## A32_W8, 8 warps

```text
warmup occurrence0 = 16
measurement occurrence1 = 400
```

Require:

- zero drop;
- zero overflow;
- xz PASS;
- trace grammar PASS;
- exact target instruction identity;
- same process/context ID;
- source/binary/CLI/GPU authority.

If bracket counts do not close:

STOP:

`MECHANISM_SENSITIVE_MEASUREMENT_TRACE_IDENTITY_FAIL`

---

# Phase I — mechanism opportunity evidence from trace

For every measurement occurrence1:

publish the address-level structural evidence for target dependent LDG.

At minimum:

- active lane count;
- unique 128B lines per dynamic target instruction;
- distribution;
- expected fanout;
- any deviation.

Desired:

```text
A1  ≈ 1 line
A8  ≈ 8 lines
A32 ≈ 32 lines
A32_W8 ≈ 32 lines per warp instruction
```

Do not call this simulator accessq cardinality yet.

Label it:

`TRACE_LEVEL_COALESCING_OPPORTUNITY`

Node174 will later close actual accessq cardinality.

---

# Phase J — durable publication

Publish mechanism-sensitive bundle to node164.

Suggested root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/mechanism_sensitive_accessq_v1_<timestamp>`

Evidence classes:

Native timing:

`NATIVE_MECHANISM_SENSITIVE_TIMING_V1`

Trace pair:

`SIMULATOR_NATIVE_MECHANISM_SENSITIVE_CONTEXT_PAIR_V1`

Trace opportunity:

`TRACE_LEVEL_COALESCING_OPPORTUNITY_V1`

Do not merge these classes.

---

# Phase K — final Git review pack

Report:

`docs/vm_tlb/codex_handoff/awma/MECHANISM_SENSITIVE_NATIVE_CALIBRATION_109_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_MECHANISM_SENSITIVE_NATIVE_CALIBRATION_109_V1/`

Required:

```text
README.md
SOURCE_ANCHORS.md
GPU_ENVIRONMENT.md

PLATFORM_ANCHOR_PUBLICATION_ACK.md
PLATFORM_ANCHOR_INDEX.tsv

BENCHMARK_DESIGN_CONTRACT.md
BENCHMARK_SOURCE.patch
BENCHMARK_SOURCE_BINARY_AUTHORITY.tsv
COMMAND_AUTHORITY.tsv
TRACE_COALESCING_PRECHECK.tsv
NATIVE_TIMING_SUMMARY.tsv
NATIVE_RELATIVE_COMPARISONS.tsv
TRACE_PAIR_AUTHORITY.tsv
TRACE_BRACKET_COUNTS.tsv
TRACE_COALESCING_OPPORTUNITY.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
DURABLE_PUBLICATION_ACK.md
SHA256SUMS
```

No accidental zero-byte placeholders.

---

# Phase L — publication close

Close exactly:

```text
early platform-anchor node164 publication
→ mechanism-sensitive science closure
→ final node164 publication
→ Git report/review pack
→ SHA256SUMS
→ commit/push
→ fetch-back
→ remote HEAD/tree verify
→ files non-empty
→ sha256sum -c
→ clean worktree
→ STOP
```

Do not run Accel-Sim on node109.

Do not design or evaluate a new TLB/PTW/cache mechanism.

---

# Global solve-and-continue policy

Ordinary engineering issues:

`solve-and-continue`

Examples:

- benchmark compile;
- NVBit selector extension;
- CLI parsing;
- trace postprocess;
- node164 transport;
- simple microbench substitution;
- clock-lock permission failure.

Do not stop over a platform anchor that can be replaced by an equivalent small independent anchor.

STOP only for:

- the mechanism-sensitive benchmark cannot produce one warp LDG with >1 transaction opportunity without fundamentally changing the scientific contract;
- exact warmup→measurement trace identity cannot be closed;
- P1 trace/timing payload is corrupt with no recovery;
- benchmark semantics would need to change materially.

Main priority:

**get a clean mechanism-sensitive calibration workload and traces, not a perfect platform characterization suite.**
