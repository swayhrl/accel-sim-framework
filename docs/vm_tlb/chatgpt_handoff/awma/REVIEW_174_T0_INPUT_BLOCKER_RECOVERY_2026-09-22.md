# ChatGPT Review — 174 T0 Input Blocker Recovery

Date: 2026-09-22

Status:

`B1_REJECTED_RECOVERABLE_ACCEPTED_INPUT_EXISTS`

Applies to:

`AWMA_TRANSLATION_FRONTEND_PIPELINING_RECALIBRATION_V1`

## 1. Root cause of the apparent blocker

The blocked candidate recovery used the earlier current-model SIM_INPUT
authority:

`SIM_INPUT_0ab4e2fe2195d3b7d7da4ee9df6017cbec5c063fcc8110374e1a753f87177634`

whose one-line `kernelslist.g` SHA is:

`1611b5389de5a1ca6d8de2d567557537503b5a2996a973eacd56a8dbf7593e2e`

and whose trace member was:

`kernel-34-ctx_0x5dd0a1addd30.traceg.xz`

That SIM_INPUT is valid historical evidence, but it is NOT the canonical T0
input authority used by the repaired V2/V3R1 cross-target baseline that the
current candidate must reproduce.

Therefore absence of the old 1611... kernelslist is not a legitimate blocker
for the current stage.

## 2. Canonical current T0 authority

Accepted V2 execution:

`hrl/awma-174-minimal-requalified-cross-target-hitpath-v2 @
f34b53597ab7d9175f8286dde67f4313462aabb5`

Its `TARGET_INPUT_AUTHORITY.tsv` states:

```text
T0  ADMITTED
bundle_or_input = kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz
reason = accepted isolated repaired input
```

This is the T0 input that produced the accepted repaired isolated:

```text
10/80 = 1,654,548 cycles
0/80  =   711,464 cycles
```

and is the T0 anchor inherited by V3R1.

## 3. Durable producer authority

Accepted 109 recovery/capture branch:

`hrl/awma-q05-prefix-ldc-recovery-109-v1 @
c6733012c13099c6a86f506fd8c61e351791159e`

Its transfer receipt gives durable bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native-contiguous-prefix_q05-contiguous-prefix_20260918T022749Z_1fea2d955d1c`

Bundle authority:

```text
source_manifest_sha256 =
5dc4f8d3fc802e6af66ab76f33adfeb31b335d44511ec792404c7210ca04d64e

destination_manifest_or_verification_sha256 =
0934cba636bf5f8b9f8835aaa8a96f0f5e53631acd327e25b265e1206fd77b9c

verification_status = PASS
file_count = 114
total_bytes = 390072942
```

`MEMBER_VALIDATION.tsv` explicitly records:

`member 34 -> kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz -> PASS`

Therefore the accepted T0 trace payload has a durable hash-bound producer
authority independent of the missing earlier SIM_INPUT kernelslist.

## 4. Candidate-private list reconstruction

The Accel-Sim tracer/post-processing source defines a one-kernel
`kernelslist.g` entry as the relative processed trace filename followed by a
newline.

For the accepted V2 isolated T0 member, candidate-private reconstruction is
exactly:

```text
kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz
```

with one trailing LF byte.

Its SHA256 is:

`a8b4ba1cf33f34be345b38908cb39572c0d14972170fd1972b4b080e81154fd5`

Classify this file as:

`DERIVED_RUNNER_INDEX_FROM_ACCEPTED_V2_T0_INPUT`

Do NOT claim it is the historical original kernelslist unless an original hash
is independently found.

The scientific identity is carried by the accepted trace payload/target
authority; the reconstructed one-line list only tells the simulator to replay
that already accepted member in isolation.

## 5. Mandatory recovery verification

Before using the reconstructed list:

1. verify the durable bundle and available manifest/verification files against
   the accepted transfer receipt hashes;
2. verify the exact member
   `kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz` exists;
3. verify its hash against the durable bundle manifest;
4. rerun the frozen grammar validator;
5. inspect accepted V2 T0 run log:
   `/root/share/mnt164/huangrulin/awma_minimal_requalified_cross_target_hitpath_v2/runs/T0_ISOLATED_10_80_CONTROL/run.log`
   SHA:
   `1e94740ff0edbc60d9faf4416f8f50a354b7f29596d125242309c306e7c8d4d6`
   and confirm it processes the same accepted T0 member;
6. use only the candidate-private reconstructed runner index; do not mutate the
   durable bundle.

## 6. Legacy reproduction hard gate

Before candidate science, legacy mode using this recovered V2 T0 input must
reproduce:

```text
cycles          = 1,654,548
gpu_sim_insn    = 368,696,302
CTA             = 224
unique coverage = 3,090,304
untranslated    = 0
unobserved      = 0
Segment activity = 0
```

If this does not reproduce exactly, STOP:

`STOP_SCIENTIFIC_T0_INPUT_REBIND_REPRODUCTION_MISMATCH`

Do not fall back to the older 0x5dd0 SIM_INPUT merely to obtain a runnable T0.

## 7. Decision

The reported B1 is no longer valid.

Resume the existing Frontend Pipelining V1 stage.

This is input-authority correction/recovery, not a new scientific stage and not
a trace substitution.
