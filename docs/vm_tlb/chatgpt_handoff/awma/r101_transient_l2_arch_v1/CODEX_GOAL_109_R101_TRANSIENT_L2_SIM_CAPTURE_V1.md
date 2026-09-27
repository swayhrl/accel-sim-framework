# CODEX GOAL — node109 R101 Transient-L2 Simulator Capture V1

Run on **node109 / RTX4080 / SM89** in the existing Lane F window if convenient.

Suggested execution branch:

`hrl/awma-r101-transient-l2-sim-capture-109-v1`

Coordination authority:

`hrl/awma-r101-transient-l2-architecture-v1-handoff`

Read first:

`docs/vm_tlb/chatgpt_handoff/awma/r101_transient_l2_arch_v1/START_HERE.md`

Accepted Native authorities:

- R101 `cfbe6503585fa1b10d979db5d26fb9be3a80e563`
- R101R1 `422faf4d8fcdb5ac49068dcf19a6e783954a29a8`

Stage:

`AWMA_R101_TRANSIENT_L2_SIM_CAPTURE_109_V1`

## 1. Goal

Produce one **simulator-native**, hash-closed trace input for the accepted R101 L512 three-kernel Newton–Schulz recurrence, including exact transient-region/lifetime metadata for:

- A;
- B;
- X0;
- X1/C.

This Goal is a producer only.

Do not:
- change the algorithm;
- implement a mechanism;
- run Accel-Sim;
- create a new model/workload;
- recapture R101 gradients if the accepted payload is recoverable;
- use synthetic matrices as FORMAL input.

## 2. Reuse exact accepted scientific payload

Durable accepted root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101_fixed_ns_intermediate_lifecycle_20260927/`

Use the accepted discovery L512 payload with expected SHA:

`1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234`

Recover/reconstruct only by accepted receipts and deterministic tooling.

If scientific tensor bytes cannot be recovered or deterministically regenerated to this exact hash:

`R101_SIM_CAPTURE_INPUT_NOT_RECOVERABLE`

and STOP.

Do not call a missing wrapper/cache/index scientific input loss.

## 3. Arithmetic source identity

Use exactly:

`tang0389/himuon@af89eda9a0176effed99e1fe19cc1f8a1a2c9588`

Five steps, unchanged:

`XXT -> ba_plus_cAA -> fused_bmm_add -> X/C swap`

Coefficients:

`3.4445, -4.7750, 2.0315`

No Gram NS, Flash-Muon, fused-muon, tile-size change or step-count change.

Prefer the corrected R101R1 arena-style wrapper only when:
- output is bitwise identical to accepted L512 B0;
- arithmetic kernel family/name/grid/block identity matches the accepted R101R1 qualified path;
- it makes A/B region identity deterministic.

Do not reuse any obsolete pre-fix arena attempt.

## 4. Trace producer path

Reuse the already accepted AWMA `SIM_COMPAT_CAPTURE_V1` native tracer path and its current qualified SM89 compatibility fixes.

Do not create a new trace grammar.

Before GPU:
- inventory exact tracer source/binary authority;
- bind CUDA/NVBit/tool versions;
- prepare parser/list/hash checks;
- prepare disk/size guards;
- prepare exact kernel selector/ROI rule.

All CUDA work uses:

`/data/c16/locks/c16_gpu_campaign.lock`

## 5. Capture scope

Preferred formal capture:

the full L512 fixed-map operator invocation, including normalization and all five NS iterations, but no unrelated model work.

If full capture volume is unsafe, the only allowed reduced FORMAL scope is:

`R101_L512_NS_CONTEXT2_V1`

defined as:
- exact full 44-tile L512 batch;
- two **consecutive** complete NS iterations;
- first iteration provides cache/context;
- second iteration is the intended measured simulator ROI;
- kernel launch order and addresses come from the real accepted run;
- no per-tile subsetting;
- no shortened batch;
- no random/synthetic tensor.

The reduced scope must be frozen before mechanism performance is observed.

Prefer tracer launch filtering over changing the application from 5 steps to 2.

If filtering cannot preserve trace semantics, capture all five steps.

## 6. Region/address sidecar

Before FORMAL trace collection, freeze and log exact device regions:

- X0 base/bytes;
- X1/C base/bytes;
- A base/bytes;
- B base/bytes.

Expected per L512 logical buffer bytes from R101:

`23,068,672`

Confirm from actual tensor shape/stride rather than hardcoding.

Each region must have:
- device address base;
- byte length;
- 128B alignment status;
- allocation identity;
- tensor shape/dtype;
- relation to accepted input/output;
- hash/receipt where contents are scientifically meaningful.

Create a lifetime table keyed by exact captured launch sequence.

For each selected NS iteration:

1. current X = LIVE before XXT;
2. XXT writes A -> A LIVE;
3. BA reads A/writes B;
4. after BA completion: A DEAD;
5. BMM-add reads B and current X, writes next X;
6. after BMM completion: B DEAD and old X DEAD;
7. next X remains LIVE into next iteration.

The sidecar states **kernel-boundary region lifetime only**.
It must not encode per-line future last-use.

## 7. Native binding receipt

For the exact capture run record:
- kernel names/order;
- grid/block geometry;
- stream/context;
- device pointers;
- input/output identity;
- finite output;
- output equality against accepted wrapper contract.

A small NSYS canary is allowed only if needed to prove selector/order.

Do not recollect NCU merely for this Goal.

Reference accepted Native traffic from R101/R101R1 by receipt/hash.

## 8. Trace semantics and completeness

FORMAL bundle must include:

- `kernelslist.g`;
- `*.traceg.xz`;
- producer manifest;
- region/lifetime sidecar;
- source/binary/env receipt;
- terminal/completeness receipt;
- SHA256 manifest.

Require:
- COMPLETE;
- drop=0;
- overflow=0;
- all kernelslist members exist;
- actual trace parser/grammar smoke PASS;
- memory access kind/width/address semantics present;
- sync/control semantics preserved;
- repeated hash/read stability.

Do not post-hoc concatenate shards if global ordering is lost.

## 9. Producer identity

Use a new stable input identity:

`SIM_INPUT_R101_L512_TRANSIENT_V1`

or a deterministic derivative if the framework requires a catalog hash.

It must explicitly relate to:

`R101_DISCOVERY_L512_ACCEPTED_PAYLOAD`

as:

`EXACT_SCIENTIFIC_PAYLOAD_NEW_SIM_CAPTURE`.

## 10. Publish

Durable node164 root:

`/root/share/mnt164/huangrulin/c16_ai_workload/provenance/awma/r101_transient_l2_sim_capture_20260927/`

Review pack:

`docs/vm_tlb/review_packs/AWMA_R101_TRANSIENT_L2_SIM_CAPTURE_109_V1/`

Minimum:

- README.md
- EXECUTION_CONTEXT.md
- TRACER_SOURCE_AND_BUILD_RECEIPT.md
- ACCEPTED_INPUT_BINDING.json
- CAPTURE_SCOPE_PREREGISTRATION.json
- BUFFER_REGION_MAP.tsv
- REGION_LIFETIME.tsv
- NATIVE_KERNEL_BINDING.tsv
- SIM_CAPTURE_MANIFEST.json
- TRACE_MEMBER_MANIFEST.tsv
- TERMINAL_AND_COMPLETENESS.md
- TRANSFER_RECEIPT.md
- TEST_AND_REGRESSION_SUMMARY.md
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Final states:

- `R101_TRANSIENT_SIM_CAPTURE_PASS`
- `R101_SIM_CAPTURE_INPUT_NOT_RECOVERABLE`
- `R101_SIM_CAPTURE_TRACER_SEMANTICS_BLOCKED`
- `R101_SIM_CAPTURE_VOLUME_BLOCKED`

On PASS:
push/fetch-back/remote SHA-tree verify/clean worktree/GPU release and STOP.

Do not wait for174 scientific result to publish.
