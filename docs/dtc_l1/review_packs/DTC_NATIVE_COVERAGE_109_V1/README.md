# DTC native behavior and workload coverage ? node109 V1

R0 CPU inventory published first; R1 native pilot completed independently of174. R2 bounded trace capture follows. Entry point for independent node174 consumption. This work does not run any simulator or change a platform authority.

## Source and isolation

Fetched origin and queried actual heads on 2026-10-16. Handoff branch `hrl/iscas2027-dtc-paper-evidence-closure-v1` is exactly `b0fdcc5760107d1efbab38599510dc96f3b4a133`; remote default HEAD is `565381ef5d43286895cefb3c71912c9d896516e9`. Execution branch `hrl/iscas2027-dtc-native-coverage-109-v1`, isolated worktree `/home/huangrulin/workspace/worktrees/accel-sim-dtc-native-coverage-109-v1`. Main C16 worktree stays at `bd988aeb570708e5a41bab45433e9e49eac53c9a`. No reset or other task termination.

Read both assigned handoffs in full. Root AGENTS.md declares VM/TLB scope; DTC task follows the explicit DTC handoff. No subordinate AGENTS.md was found under docs. Explicit-path staging and provenance discipline retained.

## R0 inventory and path audit

`R0_FIXED_COHORT.tsv` and `R0_SUMMARY.json` are machine-readable. All 12 fixed trace roots are unavailable locally on109. Manifest declares 629 ordered members / 9,162,136,500 bytes; Gaussian+LUD contribute604. Recorded SHA values are not fresh payload validation. Input dimensions, dtype, captured binary/SM, launch resources, opcodes, CTA/steady coverage and actual L2/DRAM behavior remain UNKNOWN until producer bytes are obtained. No NO_ARGS/filename inference. NN is nearest neighbor; PolyBench names establish no modern Tensor-Core/DNN implementation.

Bounded read-only discovery through configured `hrl174new` (`root@10.208.130.174:2239`) found the current164 durable mount `/root/share/mnt164/huangrulin/`. No exact fixed payload/source roots were located in the inspected top-level migration/container namespaces. This is an availability gap, not a claim of irreversible loss. An initial direct109?10.156.120.164 probe timed out; the supported route is109?hrl174new?mounted164. Current jobs were inspected; none was stopped or restarted. No simulator results are required for our independent native delivery.

109 has RTX4080/SM89, driver580.178.04, CUDA12.8 compiler and proven PyTorch2.5.1+cu124 environment `/data/c16/env/c16-py310`. Nsight Compute2025.1.1 executable is its `target/linux-desktop-glibc_2_11_3-x64/ncu`; the top-level wrapper does not forward every query as expected. Existing Accel-Sim SASS tracer is available in the separate `accel-sim-awma-simcompat-v1` worktree, not assumed qualified for DTC before canary. C16 warp-event assets are not Accel-Sim SASS traces.

Raw execution root: `/data/c16/dtc_native_coverage_109_v1` (new DTC-only directory; /data itself is not user writable). `raw/preflight.txt` records jobs/worktrees/locks/GPU/resources. Shared cooperative lock `/data/c16/locks/c16_gpu_campaign.lock` was free at inventory. GPU has only desktop graphics processes. Timing/profiling will acquire this lock nonblocking and reject any compute process; no clock/power/cache-authority setting changes.

## Preregistered bounded scope

R1: exactly12 named conditions, four families ?3. Seven independent process timing batches, ten timed launches each, three unprofiled warm-ups; CUDA-event timing is separate from profiler time. Fixed total logical loads per condition. SASS and launch/occupancy changes must accompany interpretation. Hardware set indices unknown; no PIB/MSHR sizes inferred. Profiles use application replay, cache-control none, clock-control none; three exact predecessor warm-ups precede ROI. Measured cache/DRAM traffic determines the regime; array size alone does not.

R2: only SpMV and native LayerNorm. Existing local/inspected remote Parboil source/input unavailable; bounded recovery uses the already documented `palmer-dabbelt/parboil@4e0fc54866546efa44fe93af57c9cef62f6c8eb9`, not a replacement family. Input is fixed to the repository's primary small SpMV dataset if materialized and verified; source inspection will record exact identity before timing. LayerNorm fixed to installed `torch.nn.functional.layer_norm`, FP32, normalized width1024, affine weight=1/bias=0, seed109; primary(1024,1024), single contrast(8192,1024), epsilon1e-5. Entire operator kernel set retained; no artificial rewrite or full model. Admission is based on numerical/trace/feasibility checks, never DTC speedup.

Native observations describe baseline behavior only, with no hardware DTC speedup/cost claims. No pooled GM14. Failures/neutral/low-exposure results remain. Original FAST64/TC80/SG0/SG3/logical80 and AWMA/C16 authorities are not reopened.

## Native receipt

[NATIVE_FINDINGS.md](NATIVE_FINDINGS.md), TIMING_SUMMARY.tsv, TIMING_SAMPLES.json, PROFILE_METRICS.tsv, ORDERED_OPERATOR_KERNELS.json and binary/input/SASS/lock receipts contain the first independent native delivery. All failures/coverage limits remain explicit.
