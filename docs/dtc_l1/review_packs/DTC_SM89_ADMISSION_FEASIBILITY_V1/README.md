# DTC SpMV SM89 admission feasibility ? node109 V1

**Decision: NO_GO_FOR_DROP_IN_SM89_ADMISSION; scientific promotion remains HOLD.** Existing AWMA/C16 source artifacts provide reusable parser, coverage and address-observation methods, but their SM89 entries alias the Ampere classifier and their qualification is narrower than this DTC input. The missing dispatcher is not the only blocker: the immutable SpMV trace lacks constant-memory addresses and complete wide/uniform/predicate dependencies. No architecture equivalence or new timing qualification is asserted.

Read [SOURCE_COMPARISON.md](SOURCE_COMPARISON.md), [NEXT_DECISION.md](NEXT_DECISION.md), OPCODE_COVERAGE.tsv, CPU_TEST_RECEIPTS.json and PAIR_DEPENDENCY_WITNESSES.json. `candidate_fail_closed.patch` is a **failure-status-only** review candidate; it does not add SM89 support and is not applied to any dispatcher. README is the sole recommended entry.

## Scope and provenance

CPU-only auxiliary Goal D, not a restart of the completed native producer. Fetched actual documentation branch `hrl/iscas2027-dtc-experiment-registry-v1` at expected `7112a2242c81bc6aed82a1077b3e68abd6771ea3`; default remote HEAD `565381ef5d43286895cefb3c71912c9d896516e9`. Read assigned README/GOAL_D in full and reviewed consumer `e3dbe3dbf2abb49b923244538d2a3d1828024d4f` plus producer `890fb0be7e681a60419c49ca0a7aa85731d8c164` receipts.

Independent branch `hrl/iscas2027-dtc-sm89-admission-109-v1`, worktree `/home/huangrulin/workspace/worktrees/accel-sim-dtc-sm89-admission-109-v1`, CPU build/raw/assets `/data/c16/dtc_sm89_admission_feasibility_109_v1`. Main C16 worktree and previous native worktree remain unchanged. No global LATEST_REPORT, registry44 rows, dispatch state/lock, active binary or platform config is modified. GPU lock was never requested. No native/GPU/simulator job, LayerNorm work, third family, input substitution or toolchain upgrade.

## Verified CPU results

- Scanned194 local worktrees, found5 distinct decoder file variants. Representative bytes match their recorded Git source. Three SM89 forms are a gated numeric alias, an Ada-named alias, and C16's numeric alias; none supplies a separate Ada instruction/resource implementation.
- All4 original compressed SpMV members match producer AND consumer SHA; header89/tracer5 unchanged,36 CTAs and36 warps each.11,708 warp records total,353,256 active-thread instructions.
- Compiled the actual frozen `18a68dcc` trace parser with host g++13.3. It links system C++/zstd libraries, no CUDA runtime/driver library. Parsed every original instruction; independent decoder agrees on PC/mask/opcode/captured registers/memory width/active-lane addresses/immediates. Parser success is not classifier, dependency, timing or simulator admission.
-23 complete opcode spellings/16 roots audited individually.22 spellings overlap the prior C16 full-spelling audit; `FFMA.FTZ` is new to that audit, despite root overlap. See exact data in OPCODE_COVERAGE.tsv.
-64 dynamic examples confirm a missing high-register producer edge: `LDC.64 R16`/`R2` captures only the base destination while following instructions consume R17/R3. Offline nvdisasm12.8 liveness on the original SM89 cubin independently shows paired writes. Constant addresses are absent; frozen frontend forces LDC width4 and does not expand the destination pair. Uniform and predicate dependencies are also omitted, while dynamic masks and sequence remain recorded.
- Four negative record/allowlist fixtures and20 CPU dispatcher-control-flow cases pass. Original unsupported89 returns0 with no execution; failure-only candidate returns1 with explicit rejection. Known-version CPU sentinel behavior remains unchanged. These are literal dispatcher fragments, not a simulator run or full-build qualification.

SpMV remains the original small1138_bus input,36-CTA underfill and warm DRAM read0; a repaired frontend would not turn it into a large pressure workload. No performance result or native DTC speedup was generated. Formal support changes and a future full canary remain A/mainline review responsibilities.

## Validation and handoff

VALIDATION.json passes28 consistency checks; CPU_ARCHIVE_RECEIPT.json verifies all45 raw/source/build files in a separate local109 CPU archive. RAW_LOG_INDEX.md/JSON give exact paths and SHA values. Run `bash util/dtc_l1/sm89_admission_feasibility_v1/run_cpu.sh` in this isolated worktree to reproduce the CPU checks against the original readonly producer files. No full simulator build or canary is part of that script. First independent source/CPU publication is `f0133ebc`; final branch closeout adds archive/validation receipts. A may consume this pack immediately without waiting for the primary44-row campaign.
