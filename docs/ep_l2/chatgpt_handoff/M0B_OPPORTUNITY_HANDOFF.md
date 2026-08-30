# EP-L2 M0b Opportunity Characterization — Handoff

Status: **AUTHORIZED SPECULATIVE OBSERVATION-ONLY STAGE**

## Objective

Use the reviewed M0a+M1 integrated source to measure whether the next functional EP-L2 mechanisms have real opportunity in production workloads.

M0b answers:

1. RO/pending-state: request-class eligibility and Line-MSHR lifetime decomposition.
2. WAD/TVD: dirty-victim/WAD lifetime and whether the old resident payload is actually held until writeback completion.
3. Shared payload: whether any real production non-resident payload consumer exists today.

M0b is observation/shadow only and may not alter admission, allocation, MSHR lifetime, writeback behavior, or cache policy.

## Exact speculative parent

```text
Core      1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e
Framework d61ffd23c926a25fa463a3e6e955c885b45f0f8a
Base      EP_L2_D512_CALIBRATED + M1_STATIC + M0A
```

Create isolated worktrees:

```text
Framework /workspace/worktrees/accel-sim-ep-l2-m0b/
Core      /workspace/worktrees/gpgpu-sim-ep-l2-m0b/
branch    hrl/ep-l2-m0b-opportunity-v0
results   /workspace/results/ep_l2_m0b/
```

## Mode

Add a separate default-OFF M0b observation switch. Compare:

```text
M0A_ON_M0B_OFF_M1_STATIC
M0A_ON_M0B_ON_M1_STATIC
```

M0a remains ON in both modes for blocked-cycle correlation.

## A. RO / pending-state opportunity

Do not use `!is_write()` alone as a proof of safe read-only treatment.

Produce a conservative source-audited request classification with explicit exclusion/unknown reasons. Only call a class safely eligible if every required ordering/request-type predicate is proven from source; otherwise retain `CANDIDATE` or `UNCERTIFIED`.

Add observation-only instance IDs/timestamps for Line-MSHR entries and measure exact milestones where available:

```text
allocation -> first lower issue
allocation -> last lower issue
allocation -> first fill
allocation -> all required sectors ready
allocation -> final retirement
last lower issue -> final retirement
all-ready -> final retirement
```

Missing exact events must be `NOT_EMITTED`, not inferred.

Post-issue/post-ready intervals are candidate transferable pending-state lifetime, not automatically avoidable MSHR lifetime.

Correlate with M0a any-blocked cycles, stage-primary descriptor/MSHR/per-address reasons, useful admits/responses, and lower-path pressure.

## B. Dirty victim / WAD / TVD opportunity

For dirty-victim events measure the actual timeline:

```text
victim selected
WAD allocated
writeback object created
old payload handle invalidated or still live
payload slot reassigned/reused
writeback issued
true set_done completion
WAD release
```

Answer directly:

```text
Does the old victim payload remain live after writeback creation?
For how many cycles?
Does it prevent new resident use?
Is it already reusable before set_done?
How long is WAD live?
How many M0a blocked cycles overlap WAD full/hazard periods?
```

If the current model already carries dirty data in the writeback object and immediately reuses the resident payload slot, report TVD early-payload-release opportunity as absent in this model.

## C. Shared-payload precondition

Audit actual production payload allocations after M1 and count resident vs real non-resident semantic owners.

Do not create synthetic bypass traffic. If real non-resident payload demand is still zero, report:

```text
NO_REAL_CONSUMER_YET
```

for standalone shared-payload capacity opportunity.

## Workloads

RO focus:

```text
convolutionSeparable
spmv
vectorAdd_4M
scan
sad
```

WAD/TVD focus:

```text
dwt2d
FWT_7_21
scan
cfd_097k
sad
```

A distinct M0b scan may run in its own result root while the old M0a scan continues.

Timing-neutrality controls: `convolutionSeparable`, `dwt2d`, `sad`.

## Deliverables

Create `docs/ep_l2/review_packs/M0B_OPPORTUNITY_r1/` containing at least:

```text
README.md
SOURCE_ANCHORS.md
FIELD_SEMANTICS.md
RO_CLASSIFICATION_CONTRACT.md
RO_PENDING_OPPORTUNITY.csv
MSHR_LIFETIME_SUMMARY.csv
WAD_TVD_LIFETIME_SUMMARY.csv
TVD_PREMISE_AUDIT.md
UNIFIED_PRECONDITION_AUDIT.md
M0B_OPPORTUNITY_MATRIX.md
TIMING_NEUTRALITY.csv
TEMPORAL_CORRELATION.csv
RAW_LOG_INDEX.tsv
VALIDATION_SUMMARY.md
SHA256SUMS
```

Update `docs/ep_l2/codex_handoff/LANE_M0B_LATEST.md`.

Local status may reach `M0B_OPPORTUNITY_LOCAL_COMPLETE`, but maturity remains `SPECULATIVE_PENDING_GATE` until the integrated parent is finally promoted. Stop for ChatGPT review after publishing the measured opportunity matrix.
