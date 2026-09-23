# CODEX 109 GOAL — RTX4080 Held-Out Scale-Match Repair V1

Date: 2026-09-23

Mode:

`GOAL MODE / SHORT SCIENTIFIC REPAIR / SOLVE-AND-CONTINUE`

Node:

`109 / RTX4080`

Stage:

`AWMA_RTX4080_HELDOUT_SCALE_MATCH_REPAIR_109_V1`

Read first:

`docs/vm_tlb/chatgpt_handoff/awma/REVIEW_RTX4080_PLATFORM_V1_AND_MECHANISM_NATIVE_V1_2026-09-23.md`

Accepted platform-anchor source authority:

`hrl/awma-109-mechanism-sensitive-native-calibration-v1 @ 6b75a3da3e3fedea6a359cd3657bf3e3fa2655d7`

Purpose:

repair only the Native held-out timing scale mismatch.

Do NOT recapture platform traces.

Do NOT modify held-out source semantics.

Do NOT touch the mechanism-sensitive benchmark.

---

# 1. Recover exact existing held-out trace launch identity

From the accepted node164 platform-anchor bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/rtx4080_platform_anchors_v1_20260923T115000Z`

recover the exact trace-side kernel launch configuration for:

- H_CACHE;
- H_STREAM;
- H_COMPUTE.

Expected from accepted V1 publication:

```text
H_CACHE   trace elements = 1024
H_STREAM  trace elements = 4096
H_COMPUTE trace elements = 1024
```

Verify source/binary SHA and kernel launch dimensions from accepted trace receipts.

Do not infer if the durable receipt differs.

---

# 2. Run matched-scale uninstrumented Native timing

Use the same accepted `heldout_probe.cu` source and binary identity as the trace producer when possible.

For each of:

```text
H_CACHE
H_STREAM
H_COMPUTE
```

run the exact same per-kernel problem size as the trace.

The host repetition count is NOT part of the kernel scientific identity.

Use enough repetitions to obtain a stable per-launch CUDA-event timing:

- start with >=100;
- increase to 1000 only if required for stable timing;
- do not alter the kernel/problem size.

Run 5 independent processes each if cheap; minimum 3.

For each process record:

- total CUDA-event elapsed time;
- host repetitions;
- derived us/launch;
- median/mean/CV across repetitions/processes.

No profiler is required.

Do not use host wall-clock timing as the primary metric.

---

# 3. Identity requirements

For each matched point prove:

```text
Native kernel source == trace kernel source
Native binary/source authority closed
Native problem size == trace problem size
Native kernel launch geometry == trace launch geometry
```

The host repetition count may differ because comparison is per launch.

Publish a clear row:

`MATCHED_PER_LAUNCH_COMPARISON_VALID`

for each of the three held-out points.

If a kernel launch geometry differs at the same problem size because the binary/source path changed, rebuild/recover the accepted source and retry.

Do not change the benchmark algorithm.

---

# 4. Do not reinterpret calibration data

Do not rerun or modify:

- P_L1;
- P_L2;
- P_DRAM;
- P_BW calibration;
- M0–M3;
- A1/A8/A32/A32_W8.

This Goal only supplies corrected held-out Native timing.

---

# 5. Durable publication

Publish to node164 under a new immutable bundle, e.g.:

`rtx4080_heldout_scale_match_v1_<timestamp>`

Required:

```text
README
SOURCE_BINARY_AUTHORITY
TRACE_BINDING.tsv
COMMAND_AUTHORITY.tsv
NATIVE_TIMING_RAW/
NATIVE_TIMING_SUMMARY.tsv
MATCH_VALIDITY.tsv
SHA256SUMS
destination verification ACK
```

Evidence class:

`RTX4080_HELDOUT_MATCHED_NATIVE_TIMING_V1`

---

# 6. Git publication

Suggested branch:

`hrl/awma-109-rtx4080-heldout-scale-match-v1`

Report:

`docs/vm_tlb/codex_handoff/awma/RTX4080_HELDOUT_SCALE_MATCH_109_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_RTX4080_HELDOUT_SCALE_MATCH_109_V1/`

Required files:

```text
README.md
SOURCE_ANCHORS.md
TRACE_BINDING.tsv
COMMAND_AUTHORITY.tsv
NATIVE_TIMING_SUMMARY.tsv
MATCH_VALIDITY.tsv
RAW_DATA_INDEX.tsv
DURABLE_PUBLICATION_ACK.md
SHA256SUMS
```

Close with commit/push/fetch-back/remote-tree/hash/clean-worktree verification.

STOP after publication.

No Accel-Sim on node109.
