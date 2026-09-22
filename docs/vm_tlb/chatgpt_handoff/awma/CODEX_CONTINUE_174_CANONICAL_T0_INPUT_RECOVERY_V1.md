# CODEX CONTINUATION — Recover Canonical V2 T0 Input and Resume Frontend V1

Date: 2026-09-22

Mode:

`GOAL MODE / RECOVER-AND-CONTINUE / BLOCKED STATE REVOKED`

Node:

`174-new`

Scientific stage remains:

`AWMA_TRANSLATION_FRONTEND_PIPELINING_RECALIBRATION_V1`

Read first:

1. `EXECUTION_PRIORITY_POLICY_V5.md`
2. `REVIEW_174_T0_INPUT_BLOCKER_RECOVERY_2026-09-22.md`
3. `CODEX_CONTINUE_174_TRANSLATION_FRONTEND_CLEAN_BUILD_RECOVERY_V1.md`
4. original Frontend Pipelining V1 Goal

## 0. Revoke the prior B1

Do not remain blocked on:

`kernelslist_sha256 =
1611b5389de5a1ca6d8de2d567557537503b5a2996a973eacd56a8dbf7593e2e`

That hash belongs to the earlier SIM_INPUT_0ab4... capture
(`kernel-34-ctx_0x5dd0a1addd30.traceg.xz`).

The current candidate must reproduce the repaired V2/V3R1 T0 authority instead.

Status now:

`ENGINEERING_RECOVERY_IN_PROGRESS`

## 1. Recover canonical T0

Canonical T0 trace member:

`kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz`

Durable accepted bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native-contiguous-prefix_q05-contiguous-prefix_20260918T022749Z_1fea2d955d1c`

Accepted producer receipt authority:

`hrl/awma-q05-prefix-ldc-recovery-109-v1 @
c6733012c13099c6a86f506fd8c61e351791159e`

Verify the node164 durable bundle against:

```text
source_manifest_sha256 =
5dc4f8d3fc802e6af66ab76f33adfeb31b335d44511ec792404c7210ca04d64e

destination verification SHA =
0934cba636bf5f8b9f8835aaa8a96f0f5e53631acd327e25b265e1206fd77b9c
```

Verify member 34 exists and matches the durable manifest.

Run the frozen trace grammar validator.

## 2. Reconstruct only the runner index

In candidate-private staging, create a one-member trace directory or safe
read-only binding to the accepted payload.

Create `kernelslist.g` with exactly these bytes:

```text
kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz\n
```

Expected SHA256:

`a8b4ba1cf33f34be345b38908cb39572c0d14972170fd1972b4b080e81154fd5`

Label:

`DERIVED_RUNNER_INDEX_FROM_ACCEPTED_V2_T0_INPUT`

Do not present this as the historical original list.

Do not modify, recompress, rename, or regenerate the trace payload.

## 3. Cross-check accepted V2 execution

Inspect:

`/root/share/mnt164/huangrulin/awma_minimal_requalified_cross_target_hitpath_v2/runs/T0_ISOLATED_10_80_CONTROL/run.log`

Expected log SHA:

`1e94740ff0edbc60d9faf4416f8f50a354b7f29596d125242309c306e7c8d4d6`

Confirm the accepted V2 run uses the same T0 member/target identity.

If it does not, STOP scientific review.

## 4. Legacy hard reproduction gate

Using the successfully rebuilt candidate-private binary in LEGACY mode and the
recovered canonical V2 T0 input, require exact:

```text
cycles           1,654,548
gpu_sim_insn     368,696,302
CTA              224
unique accesses  3,090,304
translated unique = unique
untranslated     0
unobserved       0
Segment functional activity = 0
```

Also require the repaired VM/runtime authority and effective config remain
unchanged apart from already authorized telemetry-only additions.

Mismatch:

`STOP_SCIENTIFIC_T0_INPUT_REBIND_REPRODUCTION_MISMATCH`

Do not substitute the older SIM_INPUT.

## 5. Resume original Frontend V1

After exact legacy reproduction PASS:

- telemetry neutrality;
- directed pipelining tests;
- candidate qualification;
- T0/T1/T2 candidate 10/80 + 0/80 matrix.

Use maximum safe parallelism after resource/dependency audit.

Do not create a separate scientific stage.

Do not mark BLOCKED for ordinary runner-index/build/path recovery.

## 6. Final publication

Continue the original Frontend Pipelining V1 report/review-pack contract.

Record the T0 input recovery provenance explicitly:

- old SIM_INPUT rejected as noncanonical for this stage;
- canonical V2 member;
- durable producer bundle/manifest;
- derived runner-index SHA;
- exact legacy reproduction.

Then remote-publish and STOP for ChatGPT review.
