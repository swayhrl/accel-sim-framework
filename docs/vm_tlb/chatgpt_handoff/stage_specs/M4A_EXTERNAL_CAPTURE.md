# M4A-C — External Rented-GPU Capture and Import Validation

## Status

**PREPARED BUT NOT AUTHORIZED.**

This specification is the second half of M4A. It begins only after M4A-P has closed out and the user/ChatGPT explicitly authorizes a selected rented GPU instance.

## Objective

Execute the prebuilt capture package on a rented GPU server, collect the minimum real LLM trace/metadata required for later Segmentation-paper reproduction, safely package/copy the artifacts back, and validate them against the frozen simulator/parser without modifying M1-M3 VM semantics.

## Entry prerequisites

Before starting, require:

- M4A-P review status PASS or acceptable CONDITIONAL_PASS;
- selected rental GPU recorded with model, compute capability, VRAM, driver, CUDA availability, and evidence classification;
- disk-space estimate and safety margin;
- capture package commit/SHA frozen;
- exact model/workload revision frozen;
- no unresolved question that would make the chosen GPU's SASS incompatible with the intended simulator target.

For paper-reproduction trace capture, default target is SM86-compatible hardware. Do not substitute SM80/SM89/SM90/SM120 and later replay it as RTX3070/SM86 without explicit approval.

## C1 — Fresh-instance preflight

On the rented server, record before installation/modification:

- `nvidia-smi -L` and full `nvidia-smi`;
- GPU model / UUID if appropriate / compute capability;
- driver version;
- CUDA toolkit/runtime availability;
- CPU/RAM;
- filesystem/free disk;
- OS/container image;
- network/model-download feasibility.

Run the prepared preflight script. Prefer isolated env/container/venv. Do not make unnecessary destructive system-wide changes.

If the GPU architecture differs from the approved route, STOP before trace capture.

## C2 — Reuse proven generic trace infrastructure first

Use the legacy/proven capture components identified in `LEGACY_CAPTURE_ASSET_AUDIT.md` wherever compatible.

Before LLM tracing, run one tiny known-good CUDA/general-purpose workload through the actual NVBit capture + postprocess + archive path. This proves the rental environment, tracer, filesystem, and packaging chain independently of vLLM/PyTorch complexity.

Required evidence:

- command;
- exit status;
- tracer output;
- post-processing status;
- produced trace manifest/checksum;
- archive test/listing;
- wall-clock.

Failure here blocks LLM capture until understood.

## C3 — LLM workload bring-up without tracing

Run the frozen Llama workload normally first.

Validate:

- exact model revision;
- batch 8;
- base input length 64;
- 3 output tokens;
- intended TP=4 / one-partition interpretation or approved approximation;
- deterministic/frozen input tokens;
- dtype/quantization recorded;
- successful inference/output sanity;
- phase identification for prefill and decode.

Do not enable expensive tracing until the workload is stable.

## C4 — Contiguous-weight runtime validation

Enable the prepared one-buffer weight layout or strongest approved equivalent.

Record/validate on the real GPU:

- flat weight-buffer base VA;
- total bytes and alignment;
- tensor offset table;
- all weight tensor addresses fall inside the planned range;
- no unintended weight copies/reallocations invalidate the range during the traced phase;
- weight range does not overlap KV/activation/workspace ranges;
- addresses are stable across the kernels/iterations used for capture.

Do not claim real hardware physical contiguity unless directly evidenced. The reproduction's simulated physical contiguity is a later VM-mapping input.

## C5 — Metadata sidecar validation

Generate allocation/tensor/phase metadata and validate:

- no unjustified active-range overlap;
- weight-address classification target: 100% of known weight accesses/ranges;
- KV ranges identified where supported;
- activation/workspace only classified when evidence exists;
- unknowns remain `UNKNOWN`;
- object-type address coverage reported;
- cross-kernel stability reported;
- sidecar schema/version/provenance recorded.

If the required metadata cannot be observed with the prepared hooks and fixing it would require simulator/Core semantic changes, STOP and report rather than improvising.

## C6 — Tiny LLM trace smoke

Before the paper-sized short trace, capture the smallest practical LLM region (for example one selected layer/phase or a reduced smoke invocation) to validate:

- NVBit instrumentation stability;
- trace growth rate;
- post-processing;
- address preservation;
- parser compatibility path;
- estimated bytes per relevant kernel/instruction and projected formal trace size.

Recompute disk requirement using measured data. Do not start the formal trace if the safety margin is inadequate.

## C7 — Paper short-context trace capture

Capture only what is required for later reproduction:

- required initialization/allocation context;
- seq-64 prefill;
- first decode phase/token(s);
- a small number of additional decode iterations only if needed to validate repeated weight accesses.

Do **not** attempt a full 12K-context instruction trace. The paper emulates long-context translation pressure synthetically in the later mechanism stage.

Record exact:

- capture package SHA;
- model/framework/tracer revisions;
- command line;
- GPU identity/compute capability;
- kernel count;
- trace format;
- total bytes;
- checksums;
- wall-clock;
- metadata bundle checksums.

## C8 — Package and copy-back

Package traces and sidecars with manifests/checksums. Large trace/model payloads remain outside Git.

The archive must be integrity-testable before rental release.

Record:

- archive path/name;
- byte size;
- SHA256;
- included manifest;
- destination on the main project server after copy-back;
- copy verification result.

Do not release/delete the rental instance until archive integrity and copy-back are confirmed when operationally practical.

## C9 — Frozen simulator/parser compatibility

After import to the main project server, validate the proposed trace against the frozen paper-reproduction parser/config path.

At minimum:

- trace parser accepts the files;
- ISA/config compatibility is explicitly checked;
- a minimal simulator smoke starts/completes when feasible;
- trace address identities correspond to sidecar ranges as expected;
- no M1-M3 simulator modification is made merely to accept an incompatible trace.

Classify the resulting trace as one of:

- `PAPER_ARTIFACT_EXACT`
- `PAPER_COMPATIBLE_SELF_CAPTURE`
- `DOCUMENTED_APPROX_CAPTURE`

Never call a self-captured trace the authors' exact trace.

## Required deliverables

Review pack:

`docs/vm_tlb/review_packs/M4A_EXTERNAL_CAPTURE/`

Stable docs/manifests should include:

- rental hardware/environment provenance;
- exact capture command/runbook version;
- trace manifest/checksums;
- metadata validation;
- contiguous-weight validation;
- parser/simulator smoke;
- paper-exactness classification;
- raw artifact index/local paths.

Large raw traces/model weights remain out of Git.

## Acceptance criteria

M4A-C PASS requires:

1. approved architecture-compatible rented GPU used;
2. generic tracer smoke PASS;
3. frozen LLM workload runs correctly before tracing;
4. contiguous-weight runtime range and tensor offsets validated;
5. metadata sidecar generated and coverage/unknowns quantified;
6. tiny trace smoke PASS and disk projection safe;
7. required short paper trace captured without attempting full 12K execution;
8. package/copy-back checksum integrity PASS;
9. frozen parser/config compatibility validated or any residual incompatibility explicitly blocks later reproduction;
10. provenance/exactness classification complete;
11. no Core VM semantic changes; no synthetic-KV/Segmentation implementation started.

## STOP boundary

After closeout, push report/review evidence and STOP before:

- paper L2-TLB sub-entry implementation;
- Segment Table implementation;
- synthetic-KV simulator injection;
- M4B/M5 performance reproduction.
