# C16 Data Pipeline Acceptance Matrix V1

Ownership: ChatGPT

## Gate G0 — old174 handover

Authority:

```text
674e834d25ab4f5be914bcebe021ce685eb51e54
OLD174_HANDOVER_COMPLETE
```

Status: PASS.

## Gate G1 — 174-new / 164 data root

Required:

```text
mount identity recorded
accepted root frozen
namespace created
small read/write/hash PASS
64 MiB bounded write/read/hash PASS
same-root promotion/rename behavior classified
no-overwrite behavior classified
directory fsync behavior classified
free-space and inode visibility recorded
cleanup fixture PASS
catalog namespace seed PASS
```

Decision enum:

```text
DATA_ROOT_ADMISSION_PASS
DATA_ROOT_ADMISSION_PASS_WITH_FILESYSTEM_LIMITATIONS
DATA_ROOT_ADMISSION_BLOCKED
```

Only first two permit Pipeline V1 integration.

## Gate G2 — 109 producer prep

Required:

```text
schema implementation PASS
10k RUN_ID uniqueness PASS
finalize valid fixture PASS
missing/mutated/symlink/collision failures PASS
deterministic manifest PASS
publish dry-run PASS
ACK validator positive/negative tests PASS
ready->transferred synthetic transition PASS
no source deletion PASS
no remote mutation PASS
```

Decision:

```text
PRODUCER_PREP_PASS
PRODUCER_PREP_BLOCKED
```

## Gate G3 — end-to-end transport

Required:

```text
small cross-node PASS
64 MiB PASS
1 GiB or documented >=256 MiB bounded PASS
resume PASS
collision/no-overwrite PASS
corruption -> no ACK PASS
independent destination rehash PASS
catalog entry PASS
ACK round trip PASS
109 ready->transferred PASS
```

Decision:

```text
PIPELINE_V1_END_TO_END_PASS
PIPELINE_V1_END_TO_END_PASS_WITH_FILESYSTEM_LIMITATIONS
PIPELINE_V1_BLOCKED
```

## Gate G4 — real legacy seed

### R5

Acceptable decisions:

```text
R5_LEGACY_IMPORT_PASS
R5_LEGACY_IMPORT_PARTIAL_MISSING_PROVENANCE
```

Not acceptable:

```text
rerunning R5 merely to fill archive gaps
regenerating missing raw
promoting R4 quantitative artifacts
```

### RTX3090

Required:

```text
curated set only
copy-not-move
source/destination SHA+size exact
historical scientific identity preserved
34/36 + two CUTLASS fail-closed boundary preserved
```

Decision:

```text
RTX3090_MINIMAL_ARCHIVE_PASS
```

## Gate G5 — infrastructure closeout

Infrastructure becomes default path for all future runs only when:

```text
G1 PASS
G2 PASS
G3 PASS
catalog seed exists
real R5/RTX3090 imports are recorded
```

Decision:

```text
C16_DATA_PLANE_V1_QUALIFIED
```

## Gate G6 — first multi-model wave

Models initially eligible for existing frozen authority:

```text
Qwen2.5-0.5B-Instruct
Qwen2.5-7B-Instruct raw
Qwen2.5-7B-Instruct-AWQ
```

Each model/scenario must have:

```text
exact model revision
exact input binding
resource admission
runtime/backend identity
output/checksum closure or explicit equivalent correctness gate
capture manifest
pipeline transfer closure
catalog admission
```

Qwen3-8B and DeepSeek-V2-Lite are not eligible until a new prospective input authority is explicitly frozen.

## Gate G7 — analysis wave

For each admitted run:

```text
raw immutable
parser version/commit bound
parse receipt
feature extraction receipt
page 4K/64K summaries
128B line summary
object attribution where available
NCU metrics normalization where available
scientific-status propagation
```

Cross-model claims are not permitted until at least the required lineages/scenarios for the claim are present.

## Fail-closed principle

A later gate may proceed around a missing optional artifact only when the missing item is explicitly classified and does not invalidate the gate's scientific claim. Missing authority is never replaced by inference.