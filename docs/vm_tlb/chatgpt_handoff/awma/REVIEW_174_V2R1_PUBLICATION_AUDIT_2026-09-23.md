# REVIEW — V2R1 publication audit

Date: 2026-09-23
Owner: ChatGPT
Status: SCIENTIFIC_RUN_PLAUSIBLE / PUBLICATION_NOT_ADMISSIBLE_YET

## Remote authority

Execution branch:
`hrl/awma-174-translation-frontend-ready-application-v2r1`

Remote HEAD:
`42226dbf4a61be3081c976f639c7d2284db58ff5`

## Source repair

The committed `READY_CONSUMPTION_REPAIR.patch` contains the intended V2R1 correction:

- accepted V1 `consume_ready` API is present;
- V1 prelaunch remains observe-only;
- V2R1 prelaunch passes `ready_application_v2`, therefore consumes READY when V2R1 is enabled;
- full-quiescence diagnostics are opt-in via
  `GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS`.

This source direction is consistent with the reviewed semantic repair.

## Publication failure

The remote review pack is not populated correctly.

At remote HEAD, the following required files are zero-byte empty files:

- CONTROLLER_QUIESCENCE.tsv
- DIRECTED_READY_CONSUMPTION_TESTS.tsv
- HOST_TIME_OBSERVATION.tsv
- PRE_REPAIR_V2_DIAGNOSIS.md
- RAW_DATA_INDEX.tsv
- README.md
- RECALIBRATION_DECISION.md
- RUN_RECEIPTS.json
- SOURCE_ANCHORS.md
- T2_REQUALIFICATION.tsv

Their Git blob SHA is the empty-file blob, and `SHA256SUMS` records the empty-file SHA256:

`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

The expected V2R1 report file is also absent from the remote tree.

Therefore the user-facing statement that the report/review pack is published and independently auditable is false at the current remote HEAD.

This is a publication/provenance defect, not a reason to rerun simulation.

## Scientific status

The reported V2R1 result:

- T2 10/80 = 111607
- T2 0/80 = 71743
- residual = 35.7182%
- full quiescence = true

is plausible and consistent with the described repair, but cannot yet be formally admitted because the required evidence tables/receipts are absent from the remote branch.

Do not change the scientific classification or rerun T2 merely because the Git publication failed.

## Required action

Recover the already-produced V2R1 evidence from:

`/root/awma_v2r1_closeout_pending`

and/or the surviving V2R1 worktree/runtime logs.

Deterministically reconstruct the required report/review-pack files, regenerate `SHA256SUMS`, commit, push, fetch-back, and verify that every promised remote file:

1. exists;
2. is non-empty where semantically required;
3. contains the expected T2 values and quiescence fields;
4. hashes to the published SHA256;
5. is visible from the fetched remote HEAD.

No simulator rerun is authorized unless the raw scientific payload itself is actually missing or corrupt.
