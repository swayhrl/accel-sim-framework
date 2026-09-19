# CODEX SIDE GOAL OVERRIDE — 109 V2.1 Mid-Campaign Checkpoint 1

Date: 2026-09-19

Status: IMMEDIATE CHECKPOINT REQUEST — CONTINUE CAMPAIGN AFTER REMOTE VERIFY.

Applies to:

`AWMA_109_TEN_HOUR_CAPTURE_AND_NATIVE_RECON_V2`

This does **not** close the campaign and does **not** reset the active 10-hour timer.

## 0. Trigger

The campaign has already produced high-value evidence needed by the active AWMA research program:

- RTX4080 native TLB reconnaissance:
  - core working-set/stride surface;
  - warm-repeat vs intervening-thrash;
  - `cg` load-policy variant;
  - 1/2/4/8/16-warp concurrency;
  - three-process repeatability;
- Decode Flash temporal coverage:
  - Primary-1 step4/8/16/24/32 formal + node164 ACK;
  - Primary-2 step4/8/16/24/32 formal + node164 ACK;
- Decode Flash 2D:
  - Primary-1 all 15 newly requested cells accepted;
  - Primary-2 partially completed and continuing;
- validator-only evidence recovery:
  - old validator rejected real `LDC.U8`;
  - isolated validator built from the already accepted source-backed implicit-constant-load rule;
  - positive/negative regression and real-trace validation passed;
  - P1 Step4 promoted only through validator/evidence recovery;
  - original failed attempt remains preserved.

These results are sufficiently valuable to checkpoint now rather than waiting for campaign finalization.

## 1. Do not interrupt current GPU target

If a GPU target is currently active:

- let it reach its normal target-safe terminal boundary;
- finish validator/postprocess/transfer/node164 ACK for that target if it qualifies;
- if it fails target-locally, quarantine normally;
- do not terminate it just to checkpoint.

At the next safe boundary:

- do not start the next GPU target yet;
- enter `MIDCAMPAIGN_CHECKPOINT_1`.

## 2. Checkpoint scope

Commit only evidence that is already scientifically closed at checkpoint time.

Do not fabricate status for incomplete targets.

Snapshot at least:

### Native TLB reconnaissance

- device/toolchain receipt;
- exact benchmark source and binary SHA;
- raw-data index/path receipts;
- summary surface;
- candidate knees;
- warm/thrash comparison;
- load-policy comparison;
- concurrency comparison;
- cross-process repeatability;
- limitations/claim boundary.

Keep classification:

`RECONNAISSANCE_ONLY`

Do not convert candidate plateaus/knees into pure TLB latency claims.

### Decode Flash temporal

For both Primary-1 and Primary-2:

```text
step1 existing accepted anchor
step4
step8
step16
step24
step32
```

Create a temporal summary with:

- exact function identity;
- grid/block;
- dynamic records;
- memory instructions;
- effective lane addresses;
- 4KiB/64KiB translation-relevant page counts;
- opcode digest;
- immutable run ID;
- node164 ACK.

### Decode Flash 2D partial snapshot

Record every cell already ACKed.

For every planned but incomplete cell, use:

```text
PENDING_AFTER_CHECKPOINT
```

not SKIPPED and not inferred.

### Validator recovery

Record explicitly:

- accepted historical implicit-constant-load semantic rule source anchor;
- validator-only delta;
- positive/negative tests;
- real `LDC.U8` evidence;
- no producer/raw/parser/simulator semantic weakening;
- original failed attempt retained;
- which targets were admitted using the repaired isolated validator.

## 3. Checkpoint artifacts

Create a dedicated review pack:

`docs/vm_tlb/review_packs/AWMA_109_TEN_HOUR_SIDELANE_V2_CHECKPOINT_1/`

At minimum:

```text
README.md
SOURCE_ANCHORS.md
ACTIVE_WINDOW_RECEIPT.json
GPU_LOCK_WAIT_RECEIPT.tsv
CHECKPOINT_TARGET_STATUS.tsv
NATIVE_TLB_RECON_DEVICE_RECEIPT.json
NATIVE_TLB_RECON_SUMMARY.tsv
NATIVE_TLB_RECON_KNEE_CANDIDATES.md
NATIVE_TLB_RECON_REPEATABILITY.tsv
NATIVE_TLB_RECON_LIMITATIONS.md
DECODE_FLASH_TEMPORAL_MATRIX.tsv
DECODE_FLASH_TIME_DEPTH_PARTIAL_MATRIX.tsv
VALIDATOR_LDC_U8_RECOVERY.md
TRANSFER_ACK_INDEX.tsv
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Create checkpoint report:

`docs/vm_tlb/codex_handoff/awma/TEN_HOUR_SIDELANE_109_V2_CHECKPOINT_1_REPORT.md`

Use checkpoint marker:

`AWMA_109_TEN_HOUR_SIDELANE_V2_CHECKPOINT_1_REMOTE_VERIFIED`

Do **not** emit the campaign COMPLETE marker.

## 4. Git behavior

At the safe boundary:

1. ensure no completed target has unrecorded node164 ACK;
2. materialize checkpoint report/review pack;
3. hash checkpoint pack;
4. commit all already-closed campaign evidence that should be durable in Git;
5. push the existing execution branch;
6. verify the remote branch resolves to the exact checkpoint commit;
7. make the worktree clean at the checkpoint commit.

The checkpoint commit message should clearly identify it, for example:

`awma: checkpoint 109 V2 native TLB and Decode Flash results`

Do not create a second campaign branch if the existing execution branch is healthy.

## 5. Resume automatically

After remote verification:

- continue the **same V2/V2.1 campaign**;
- preserve the original `ACTIVE_START_UTC`;
- checkpoint/push time counts normally inside the active 10h budget;
- resume with the next unfinished high-value queue item;
- do not rerun already ACKed targets;
- do not reset aggregate-storage accounting;
- do not mark pending cells complete merely because the checkpoint exists.

If normal GPU-lock policy requires reacquisition after the checkpoint, reacquire through the standard lock. Never bypass another owner.

## 6. Mainline independence

Node174 remains independent.

The checkpoint exists so ChatGPT can review closed 109 evidence early.

Do not wait for ChatGPT review before continuing the remaining 109 queue unless a new explicit stop/preemption instruction arrives.

## 7. Campaign finalization remains unchanged

The final campaign still closes later under the existing V2.1 wallclock/finalization rules.

Checkpoint 1 is an intermediate immutable scientific snapshot only.
