# C16 Pipeline V1 Integration — ChatGPT Review

Status: `ACCEPTED_FOR_FORMAL_CAPTURE_WITH_RECORDED_LIMITATIONS`

Accepted implementation head:

```text
hrl/c16-data-pipeline-v1-integration-174new-r1
3c4847d2da818013dca6422194af36966136ab31
```

## Accepted

- Cross-node synthetic small / 64 MiB / 256 MiB transfer closure.
- Resume with append-verify.
- Independent destination rehash.
- Collision/no-overwrite negative test.
- Corruption -> quarantine and no ACK.
- Catalog + ACK + producer READY -> TRANSFERRED closure.
- SSHFS transport changed from archive metadata preservation to content-oriented copy.
- RTX3090 curated historical minimum set archived copy-not-move with SHA closure.
- No scientific workload rerun.

## Filesystem limitation

On the admitted SSHFS root, directory `renameat2(RENAME_NOREPLACE)` returned EINVAL. The implementation uses checked destination absence + same-mount `os.rename` fallback.

This is accepted for the controlled single-receiver C16 pipeline, but is not a general concurrent atomic no-replace guarantee. Until a stronger reservation/locking primitive is separately qualified:

```text
FORMAL_ADMISSION_CONCURRENCY = 1
```

Do not run concurrent admissions for the same node164 root.

## R5 legacy classification correction

The integration review pack imported the earlier NCU N1 qualification report/CSV, not the actual complete R5 U5/U6/U7/U9 artifact set.

Therefore:

```text
PIPELINE_V1 = PASS
RTX3090_MINIMAL_ARCHIVE = PASS
N1_QUALIFICATION_ARCHIVE = PASS
RTX4080_R5_LEGACY_ARCHIVE = NOT_YET_CLOSED
```

Do not label the imported N1 artifacts themselves as the R5 scientific archive.

The missing U8 manifest remains missing provenance and must not be regenerated.

A future CPU-only reconciliation may inventory existing R5 artifacts on node109 and archive only objects whose path/size/SHA/authority can be closed. No rerun is authorized.

## Authority metadata seed

The final integration review pack does not independently evidence the requested complete seed of:

- Llama frozen R5 model/input authority;
- 21 Qwen historical binding authorities;
- Qwen3-8B / DeepSeek no-historical-binding audit metadata.

Treat this as an analysis-preparation item, not as a pipeline blocker.

## Bounded-large note

The explicit cross-node synthetic bounded-large test used 256 MiB. This is accepted for V1 because all correctness/failure gates passed and future scientific bundles remain independently hash-closed and bounded. The first formal bundle >=1 GiB, if any, must record transfer bytes/duration/throughput and source/destination SHA in its transfer receipt.

## Formal capture gate

Pipeline V1 may now carry formal new captures provided all of the following hold:

```text
one admission writer at a time
RUN_MANIFEST closed on producer
copy-not-move
.partial destination
independent destination rehash
catalog registration
PASS ACK
no source deletion from ACK alone
```
