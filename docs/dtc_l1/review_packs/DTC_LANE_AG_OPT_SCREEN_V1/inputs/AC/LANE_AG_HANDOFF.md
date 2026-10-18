# Immutable Core handoff to Lane AG

OPT-COLLECT sole production implementer: Lane AC, original174/root.

**Pin exactly `83aca449135703c176cfab29ae43e1245d00a557` from swayhrl/gpgpu-sim.**
Branch: `hrl/iscas2027-dtc-lane-ac-collect-pipeline-core-174-v1`.
Baseline: `e32afdcf44be3374ff36d22568ed01a075459b6f`, direct child of c0a5e2c3.
Do not replace the immutable commit with a later branch HEAD.

Review branch: `hrl/iscas2027-dtc-lane-ac-collect-pipeline-174-v1`.
Pack: `docs/dtc_l1/review_packs/DTC_LANE_AC_COLLECT_PIPELINE_V1/`.

Opt-in `-gpgpu_dtc_l1_collect_wb_pipeline 1` requires PAPER_OO+finiteV1+L1D;
omitted/0 preserves the serial source path. K1 is independent and unchanged.
There is at most one collecting owner and one WB result. No new sector/retire
quota or relaxed cycle comparison exists. Refs release only on successful WB/
original retirement. Conservative raw-sector buffer cost is **160KiB additional
per SM** at640 lines (two80KiB banks), no free PIB payload or equal-area claim.
Do not silently substitute a compact output buffer or unlimited result cache.

Publication includes real production-LDST CPU qualification,75 positive processes
+5 expected mode/config rejections,17 OFF typed-state triples/51 normal boundaries,
16 parser negatives,7 original CTests+new full-bank resource CTest. These are
bounded CPU timing/ownership witnesses. No full GPU/native/ISA/value/coherence/
PPA/performance acceptance is asserted. Test-specific zero initialization of the
unchanged unused DRAM refresh counter and controlled lower packets are explicit.

Lane AG should independently verify fixed source/patch/config/parser/ELF/library
identities, resource charge, stage ownership, finite quotas, K1 Ref conservation
and normal cumulative snapshot parsing. Preserve each earlier Lane's accepted
scope and all AA5/X2/raw/locks. This handoff does not authorize full/canary/native/
GPU execution or claim AG has accepted it. Scientific contract changes require
STOP/review; ordinary test/engineering findings remain scoped to the appropriate
independent Lane. The handoff is published through this immutable Git review pack;
no claim of delivery through an unavailable private Lane mailbox is made.
