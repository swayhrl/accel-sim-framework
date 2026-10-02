# R27 varied-batch capacity stability review

Date: 2026-10-03 (Asia/Shanghai)

Execution: [`4dca1cd713df8315b9e04f702d7f3b990c8f4b88`](https://github.com/swayhrl/accel-sim-framework/commit/4dca1cd713df8315b9e04f702d7f3b990c8f4b88), tree `03debf7395f51062c133ad4d534791f2b5fc1770`. The execution commit is the single direct child of the exact R27 handoff `5144bde8f9d7b399a596395e0c88ee89025b3a6f`, tree `605f0360debb3f62a1923452c91552ca1f2acaa9`. Remote branch `hrl/awma-r27-varied-batch-capacity-109-v1` points to the execution commit.

Stage: `AWMA_R27_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1`.

## Review decision

Accept the frozen classification:

`R27_INPUT_OR_SOURCE_NOT_QUALIFIED`

This is a **qualified source/input availability STOP**, not a varied-input capacity negative, not a numerical negative, and not evidence against the R26 one-batch repeated-sequence observation. Gate A passed; Gate B stopped before tokenization, source freeze, CUDA/JIT, GPU-lock acquisition or any capacity observation. Gates C and D were not run.

Accordingly, R27 answers no new scientific question about varied-text capacity. The intended question—whether the R26 C1/S2 same-B distinction survives a fixed diverse text stream and 32-step/resume checks—remains unresolved.

## Gate A — accepted

I independently read the Git execution pack, the exact handoff Goal/contract and the R26 readback summary.

The readback reports and cross-indexes:

- R26 archive SHA256 `c8319694dc33858bb0760f97f80f4a509e07e9ce7eadb6b10b28a7823f0696c3`.
- R26 manifest SHA256 `8e0e30a90856f152cf1221c6a660ce6ceeeca84c402ed59cd8a6956f1e371159`, with 207/207 remote manifest entries verified.
- R26 common checkpoint SHA256 `09e293774ac9dcb535e1a3d47d72878ff68f3831476175060b1016bce8a28b55`; BF16 W, FP32 m/v, logical step 1 and recorded RNG/identity fields are present and finite/CPU-bound as required.
- Frozen R26 component/runner/search source hashes match their authority values.
- Four endpoint groups are present at 3/3: C1 B70 PASS, C1 B71 OOM, S2 B71 PASS and S2 B72 OOM.
- The 12 endpoint receipts plus 12 logs have matching Git-index, manifest and readback size/SHA records in `selected_file_evidence`.
- B71 input binding is fixed; S2 B71 completes five steps. Each C1 B71 confirmation completes two steps, then fails in the third-step `BACKBONE_COMPACT_LOOKUP_BACKWARD` with an explicit CUDA OOM request of 142.00 MiB and recorded free/allocated/reserved fields.
- The readback itself explicitly limits interpretation: it verifies the R26 five-step witness and does not assert an allocator cause.

The initial Gate-A script attempts contained four incorrectly transcribed expected SHA constants caused by wrapped-line duplication. The execution corrected only those expected constants from the already-frozen `PARENT_AUTHORITY.json`, retained the failed attempts, and then reran the read-only audit. Evidence bytes and scientific identities were not changed. This is an ordinary pre-freeze engineering correction permitted by the Goal and does not invalidate Gate A.

I did not directly SSH/read node164 bytes in this ChatGPT review environment. The 207-item remote byte audit is therefore an execution-side primary-evidence readback whose detailed per-file cross-check is preserved in the Git review pack, not a second reviewer-side node164 attestation.

## Gate B — accepted STOP

The Goal permits exactly one new source: Salesforce `wikitext@8aaa8b27d493dba10b8553290236799e6dc57829`, `wikitext-2-raw-v1/train-00000-of-00001.parquet`, expected size 6,357,543 bytes and SHA256 `e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7`. The Goal explicitly requires `R27_INPUT_OR_SOURCE_NOT_QUALIFIED` and STOP if that exact payload is unavailable.

The acquisition receipt records:

- node109 exact URL: timeout, zero bytes;
- local execution environment: three bounded timeouts, zero bytes;
- node164 storage host: three bounded timeouts, zero bytes;
- controlled web access: no exportable payload;
- bounded exact-size searches in the listed node109/node164 cache roots: zero candidates;
- alternate source/corpus/split/tokenizer/proxy: not used;
- bytes acquired: 0;
- tokenization started: false;
- GPU lock acquisitions: 0;
- CUDA/JIT operations: 0.

Therefore the execution followed the frozen STOP rule rather than substituting a convenient input. No `IMPLEMENTATION_FREEZE`, capacity search, numerical trajectory, timing campaign or GPU result should be inferred from this run.

## Gates C / D

Both are `NOT_RUN`. There is no R27 observation of:

- varied-input natural capacity boundaries;
- C1-OOM/S2-PASS same-B witness under the new stream;
- B1 varied-stream numerical qualification;
- 32-step trajectories;
- fresh-process resume;
- allocator diagnostics;
- formal timing.

Do not use the absence of these results as evidence for or against S2.

## Publication and closure

The execution branch/ref, parent relation and result tree were independently checked through GitHub. The commit changes only R27 result/report/support files plus the review-pack index; it does not rewrite the frozen handoff/contract or R26 scientific implementation.

The Git review pack contains the expected decision, gate, source/input, R26-readback, raw-index, lock, node164-publication and validation records. I independently recomputed the SHA256 of the committed `SHA256SUMS` file as:

`dffbae1f68239420104a691fd3869213475fd4307a9dc68d45965ca490bac3f6`

matching the execution report, and spot-checked the committed SHA entries for `FINAL_DECISION.json`, `GATE_STATUS.json` and `RESOURCE_LOCK_RECEIPTS.json`.

The node164 publication receipt reports 103/103 manifest items verified, archive SHA256 `32d71192bd435f592e7b6bc384d47bc218942a5e1e7b82d1d6e935a2e288c542` and manifest SHA256 `d9344074e2a6ded85188cba6f9285e05c4233a33216c86c4bece1be0bf8772ce`. These remain execution-side node164 receipts in this review environment.

Resource closure is consistent with an input-gate stop: zero CUDA/JIT operations, zero GPU-lock acquisitions, no recorded campaign GPU processes and no final lock owner. The execution report states push/fetch-back and clean worktree; the remote execution branch currently points to the exact result commit/tree.

## Scientific status after R27

R26 remains accepted, with its original narrow scope: repeated copies of one sequence, tied-W-only training, C1 B70/B71 versus S2 B71/B72 five-step capacity boundary, one physical-batch extension, B70 S2 whole-step peak slightly higher and timing MIXED.

R27 adds **no varied-input capacity evidence**. It only closes two evidence questions:

1. the previously unreviewed node164 R26 endpoint/raw authority was successfully read back and parsed by the R27 execution; and
2. the exact new WikiText-2 payload was unavailable through the authorized execution paths, so the scientific experiment correctly stopped before observation.

A future continuation must be a new reviewed contract after the exact byte-identical parquet is made available and admitted. This execution must not be implicitly resumed. No new GPU work, production/default change, node174/Accel-Sim, hardware/PPA or second corpus/model follows from this review.
