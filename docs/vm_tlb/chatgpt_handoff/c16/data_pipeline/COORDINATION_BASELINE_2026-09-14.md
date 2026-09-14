# C16 Data Pipeline — ChatGPT Coordination Baseline

Date: 2026-09-14

This document freezes the coordination model after old174 final handover.

## 1. Long-term roles

```text
109 / RTX4080
  GPU producer / capture execution plane
  native inference, NCU, NVBit, NSYS, runtime maps, bounded GPU canaries

174-new / 2239
  ingest / catalog / CPU analysis plane
  receive, verify, catalog, parse, feature extraction, dataset construction

164
  long-term data plane
  raw, provenance, parsed, features, datasets, reports, quarantine

GitHub
  control plane
  code, schemas, manifests, receipts, catalogs, review packs, handoffs

old174 / 2233
  historical authority source after accepted final handover
  no continuous C16 workflow design role
```

## 2. Current accepted authority anchors

```text
RTX3090 closeout
649af1b9d65a774d4aa8c32a15f9b6f4da0dd4d9

RTX4080 clean R5
b75f26674a09705659e770ab2134351414aa3c93
READY_FOR_MULTIMODEL_REVIEW
R4 remains mechanism-only/non-authoritative

Historical frozen-input recovery
4b5c2bb79b9e2e79bed8bef10365bf34be6f6cdd
HISTORICAL_FROZEN_INPUT_NOT_RECOVERED

Future-use adopted Llama input
494ccc0f5e6be3bba71d35a58c8c61a60b61988a
ADOPTED_INPUT_AUTHORITY_V1_PASS
FUTURE_USE_ADOPTED_INPUT_NOT_HISTORICAL_RECOVERY
```

Historical and future-use authorities must not be merged retroactively.

## 3. 174-new / 164 planned data root

Accepted candidate root from destination admission:

```text
/root/share/mnt164/huangrulin/c16_ai_workload_2239
```

Long-term layout target:

```text
inbox/
raw/
provenance/
parsed/
features/
datasets/
catalog/
reports/
quarantine/
legacy/
tmp/
```

Large raw/model/profiler data stay outside Git.

## 4. Pipeline lifecycle target

```text
109 capture staging
→ 109 finalize/hash/manifest
→ 109 ready
→ transfer to 164 inbox/<RUN_ID>.partial
→ 174-new verify
→ atomic admit to 164 raw/<RUN_ID>
→ TRANSFER_ACK
→ 109 verifies ACK
→ 109 marks transferred
```

No source deletion follows mere rsync success.

## 5. Phase order after old174 closeout

```text
Phase B  174-new / 164 data-root admission and namespace freeze
Phase C  pipeline V1: RUN_ID, manifest, transfer, verify, ACK, catalog using tiny fixture
Phase D  legacy RTX4080 R5 import from 109 /data/c16 into 164/legacy with independent rehash
Phase E  multi-model capture through the new pipeline
Phase F  analysis pipeline: NVBit/NCU/NSYS parse, object join, page/line fingerprints, sampling, cross-model datasets
```

Do not skip Phase C and begin large multi-model capture with ad hoc copy procedures.

## 6. Coordination ownership

ChatGPT owns:

```text
scientific boundaries
phase planning
109 vs 174-new task split
pipeline contracts and schemas
Codex goals
review / PASS / FAIL decisions
next-stage handoffs
```

109 Codex owns producer-side implementation/execution.
174-new Codex owns ingest/archive/catalog/analysis implementation.
old174 Codex is STOP after accepted closeout except for explicitly requested historical archaeology.

## 7. Immediate next gate

The immediate gate is:

```text
C16_OLD174_FINAL_HANDOVER_TO_2239
```

No new pipeline implementation is authorized by this baseline until the old174 handover review pack has been returned and reviewed.
