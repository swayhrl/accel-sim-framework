# R27R1 varied-batch capacity continuation review

Date: 2026-10-03 (Asia/Shanghai)

Execution: `254d66f69ec81bf932add705f721f36255feef2c`, tree `ebefec69e9ba153adfaf5d1f7860a956964d09cb`.

Exact handoff: `ad361be589de85787c3f724582ae1862cb3c3539`, tree `aa0acb61acd0e1a2fa16fedd75cf8d69d314f06e`.

Execution branch: `hrl/awma-r27r1-varied-batch-capacity-109-v1`.

## Review decision

Accept:

`R27R1_INPUT_OR_SOURCE_NOT_QUALIFIED`

This is an exact-input availability STOP before tokenization or GPU work. It is not a varied-input capacity negative, numerical negative, partial capacity result, or evidence against R26.

The execution commit is the single direct child of the exact R27R1 handoff; the remote execution branch points to the exact result commit/tree. The closed R27 execution was not amended or resumed.

## Gate A — PASS

The bounded identity recheck follows the R27R1 contract and correctly avoids repeating the full R27 207-item historical audit.

The execution rechecks:

- closed R27 commit/tree and its 14-entry review pack;
- accepted R27 status `R27_PARENT_RAW_QUALIFIED`;
- R26 common checkpoint: 2,626,691,315 bytes, SHA256 `09e293774ac9dcb535e1a3d47d72878ff68f3831476175060b1016bce8a28b55`, logical step 1;
- BF16 W and FP32 m/v hashes, CPU/CUDA RNG identities and CPU-only tensor state;
- frozen R26 component, runner and capacity-search source;
- three frozen CCE source files;
- all six accepted Llama payloads, total 2,480,783,094 bytes.

The recheck reports no errors and `full_207_item_audit_rerun=false`, as required. Accept `R27R1_PARENT_AUTHORITY_QUALIFIED`.

## Gate B0 — accepted STOP

The only legal payload remains:

`wikitext-2-raw-v1/train-00000-of-00001.parquet`

Expected:

- bytes: 6,357,543
- SHA256: `e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7`

R27R1 records new official-current-main acquisition attempts from node109, local execution environment and node164, all ending before any bytes were received. Browser transport produced no file and the workspace exact-size search found no candidate.

The frozen receipt reports:

- `bytes_acquired=0`;
- `local_size_sha_admission=false`;
- `node164_input_admission_started=false`;
- `tokenization_started=false`;
- `CUDA_JIT_operations=0`;
- `GPU_lock_acquisitions=0`;
- no alternate payload used.

Therefore B1, implementation freeze, C and D were correctly not run.

## Public source status versus execution availability

Independent public metadata still records the target payload. The original Salesforce/wikitext commit `8aaa8b27d493dba10b8553290236799e6dc57829` records the train parquet as a Git-LFS object of 6,357,543 bytes with the exact required SHA256. The current official main file page also reports the same SHA256.

This means the scientific payload is not known to be lost; the blocker is byte transport into the available execution/storage environments.

A ChatGPT-side attempt also could not materialize the payload: the web layer can read the official file metadata and resolve the download redirect, but the local container cannot resolve `huggingface.co`. Therefore this review does not claim an independently downloaded byte copy.

## Publication / resource closure

The R27R1 result branch and tree were independently checked through GitHub.

The review pack has 14 files. The committed `SHA256SUMS` content hashes to:

`6fb62aae13c35d75fd27183d737d18f1e19cd1f54185df0b4e522936404c7a91`

matching the execution report. Key decision, gate, input, parent-identity, lock and node164-publication records are internally consistent.

The node164 publication receipt reports:

- 11/11 remote manifest items verified;
- archive SHA256 `d19c44fb6bb2906c38f4a2ecc0be1991ce4f50fa73baae76658bfb37b9b1de9e`;
- manifest SHA256 `04b10752001f76143fef8ad21f17407d488e6dbcf496e454ce9bd772079f88cb`;
- exact input not admitted.

These are execution-side node164 receipts; this review environment did not independently SSH-read node164 bytes.

Resource closure is consistent: zero CUDA/JIT operations, zero GPU lock acquisitions and no campaign process.

## Scientific status

R26 remains the latest accepted capacity observation, with its repeated-sequence tied-W scope.

R27 and R27R1 add no varied-input capacity evidence. Together they establish that:

1. the R26 raw/parent evidence and consumed identities are qualified; and
2. the exact new scientific input has repeatedly failed to enter the execution environment despite the public source metadata still identifying it.

Do not launch another network-retry-only R27 continuation. The next useful action is to seed one exact byte-identical copy through an external route that can actually obtain the public file, verify size/SHA locally, and transfer it into the C16/AWMA authority path. Only after that byte admission exists should a new reviewed continuation resume at exact-input admission / Gate B1.

No GPU task is authorized by this review.
