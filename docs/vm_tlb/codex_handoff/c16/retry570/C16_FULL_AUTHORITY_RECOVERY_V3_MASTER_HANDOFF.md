# C16 Full-Authority Recovery V3 — Master Handoff

## 0. Purpose

This handoff supersedes the **scope** of the prior post-Llama partial closeout while preserving all of its evidence unchanged.

The objective is to finish the **authoritative C16 model × scenario GPU/native/capture work that is still missing**, copy all required raw/large artifacts back to the local/control host with remote→local SHA closure, and publish a final analysis-ready dataset/index.

This is a **Goal-mode execution plan**. Codex should solve ordinary engineering problems and continue rather than stopping to ask the user after each obstacle.

### Accepted immutable checkpoints

- Active partial closeout commit: `2c52c7aa79e5dc131ffefa29bedf5b0018fcdac3`
- Accepted Llama S0 target-trace checkpoint: `2e955e007bcabcd3ec24a5f9d24768d27caaee27`
- Accepted Llama manifest SHA256: `0d8aeb74729a06e2188359cca2eb18c3884ea5b108723d6966778a161c4aaacc`

Do **not** rewrite or invalidate these commits. Consume them as historical/reference evidence.

---

## 1. Authoritative scope

The recovery-v3 scope is derived from the existing C16 Master / Lane-A / Lane-G contracts, not from the smaller post-Llama roster.

### Wave-1 authoritative deployments

1. Llama-3.2-1B — historical bridge/reference
2. Qwen2.5-0.5B-Instruct
3. Qwen2.5-7B-Instruct **raw**
4. Qwen2.5-7B-Instruct-AWQ

### Wave-2 authoritative deployments

5. Qwen3-8B
6. Qwen3-30B-A3B
7. DeepSeek-V2-Lite

### User-requested extension deployment

8. GLM — exact historical project identity must first be recovered. It is not allowed to guess a ChatGLM/GLM-4/GLM-4.x variant.

The final dataset must clearly distinguish `C16_AUTHORITATIVE` rows from the `USER_EXTENSION` GLM row.

---

## 2. Authoritative scenario matrix

### Dense/smaller deployment scenarios

- `S0`: B1 / T128 / Decode4 — **canary only**
- `S1`: B1 / T256 / Decode16
- `S2`: B1 / T2048 / Decode32
- `S3`: B1 / T8192 / Decode16
- `S4`: B4 / T2048 / Decode16

### MoE / 30B first-round minimum

For Qwen3-30B-A3B and DeepSeek-V2-Lite, required first-round scenarios are:

- `S1`: B1 / T256
- `S2`: B1 / T2048

Additional S0/S3/S4 may be attempted only if the frozen runtime fits and resource safety remains satisfied. Do not silently change batch/context to make the model fit.

### Existing Llama evidence

Llama `S0` is already complete and MUST NOT be rerun merely for symmetry.

Accepted Llama S0 targets:

- Prefill: full `indexSelectLargeIndex`, NVBit 1.7.5 `[101,102)`, `LDG.E.U16`, 8192 address-bearing records.
- Decode: full `indexSelectSmallIndex`, NVBit 1.7.5 `[17,18)`, `LDG.E`, 64 records in each actual Decode2–4 forward; logical Decode1 is prefill-derived and has no separate CUDA forward.

Recovery-v3 must extend Llama to the still-required C16 S1–S4 native/census/capture work without overwriting S0.

---

## 3. Frozen infrastructure

Keep the proven runtime fixed unless a model's authoritative package contract explicitly requires otherwise and such a change is recorded as a separate deployment identity.

Primary proven profile:

```text
GPU                  RTX3090 / SM86
Driver               570.124.04
CUDA                 12.4
PyTorch              2.5.1+cu124
NVBit                 1.7.5
effective loading     EAGER
```

NVBit 1.8 is forbidden for this campaign.

NCU on this instance is already capability-limited (`ERR_NVGPUCTRPERM`). Do not waste campaign time retrying equivalent NCU permission probes. Preserve the existing capability receipt and continue native census + NVBit.

---

## 4. What data must be completed

For each required `deployment × scenario` that fits the frozen scientific contract, recovery-v3 must produce the following layers.

### Layer A — Identity / input / runtime closure

- immutable model ID/revision or exact package/content manifest;
- tokenizer/input identity and actual token count/hash;
- quantization/dtype;
- attention/backend implementation;
- device map/offload/TP/PP/EP behavior;
- config/weight/index hashes;
- runtime/library/tracer hashes.

### Layer B — Native execution and lightweight census

- no-profile baseline / terminal checksum evidence;
- lightweight kernel catalog with phase attribution;
- runtime implementation audit;
- semantic/shape/dtype coverage where directly supported;
- explicit UNKNOWN rows rather than guessed semantics.

### Layer C — Frozen memory-target plan

Before NVBit formal capture for a deployment/scenario, freeze a versioned plan.

Preferred source order:

1. valid existing `NVBIT_TARGET_PLAN.tsv` / C-lane plan matching the current deployment/scenario;
2. otherwise generate a **recovery-v3 deterministic target plan** from the frozen native census using C16 sampling rules, then freeze its SHA before capture.

A recovery-generated plan must be labeled `RECOVERY_V3_TARGET_PLAN`, never falsely called a C-lane final plan.

At minimum, the target plan must preserve phase and semantic diversity. Do not force the same kernel/range across prefill and decode.

### Layer D — NVBit qualification and formal memory capture

For every selected target class:

- full function identity;
- launch identity/phase/step;
- NVBit 1.7.5 static range;
- opcode/memory space;
- address-bearing proof;
- narrow canary;
- independent-process reproducibility;
- complete selected occurrences over the frozen ROI/scenario;
- structural-zero proof only when kernel census proves the target did not launch.

### Layer E — Copyback and integrity

Every required raw trace / large census payload must be:

```text
remote SHA256
 -> copied to local/control host
 -> local SHA256
 -> equality PASS
```

Raw traces remain outside Git.

After local SHA closure and durable local indexing, remote raw copies may be deleted to reclaim GPU-server disk. Never delete the only verified copy.

---

## 5. Asset acquisition and transfer policy

The AutoDL/GPU host currently has limited or unavailable outbound network access. That is an engineering condition, not a scientific blocker.

### Required resolution order

1. recover exact identity/revision from repo/history/manifests/retained receipts;
2. search bounded local/control-host and GPU-host asset roots;
3. if missing, download the **exact immutable revision** on the network-capable local/control host;
4. build per-file size/SHA manifest there;
5. rsync/scp the package to the GPU host using the existing two-host workflow;
6. rehash on GPU host and require equality before model execution.

Do not stop a model merely because the GPU host cannot reach Hugging Face directly.

Do not use approximate mirrors/substitute models. An alternate official distribution is acceptable only when the exact identity/content can be proved equivalent by revision/content hashes and config/weight manifests.

---

## 6. Known identities already recovered

### Qwen2.5-0.5B-Instruct

```text
model:    Qwen/Qwen2.5-0.5B-Instruct
revision: 7ae557604adf67be50417f59c2c2f167def9a775
```

Prior package metadata also recorded expected model bytes and immutable package manifests. Reuse those receipts rather than rediscovering the identity.

### Qwen2.5-7B-Instruct-AWQ

```text
model:    Qwen/Qwen2.5-7B-Instruct-AWQ
revision: b25037543e9394b818fdfca67ab2a00ecc7dd641
```

Do not replace AWQ with raw/BF16/GPTQ/GGUF.

### DeepSeek-V2-Lite

The C16 authoritative family is DeepSeek-V2-Lite. A retained C15 static candidate is:

```text
deepseek-ai/DeepSeek-V2-Lite
revision candidate: 604d5664dddd88a0433dbae533b7fe9472482de0
```

Recovery-v3 must verify whether this immutable revision is the correct runnable C16 target by reconstructing tokenizer/input/runtime package evidence. Do not relabel the static candidate as runnable until that closure is complete.

### Qwen2.5-7B raw, Qwen3-8B, Qwen3-30B-A3B, GLM

Exact revisions/content manifests must be recovered from authoritative C16/C15 repo history, package manifests, local asset receipts, or authoritative upstream metadata before execution. Model-name guessing is forbidden.

---

## 7. Engineering recovery policy — solve problems, do not stop early

For ordinary failures, Codex must attempt recovery and continue.

### Network unavailable on GPU host

Use local/control-host download + manifest + rsync. Do not classify as final asset blocker merely because the GPU host has no egress.

### Package/environment issue

Repair in isolated/frozen environment; preserve package versions and hashes. Re-run only the smallest failed gate.

### `nvdisasm`/PATH issue

Use the already-hardened child-PATH contract; do not reopen the historical investigation.

### NVBit startup issue

Verify NVBit 1.7.5 and known-good preflight. Do not switch to 1.8.

### OOM / model fit

First attempt only identity-preserving remedies:

- inference/no-grad mode;
- release unrelated GPU allocations/processes;
- allocator/cache cleanup between independent runs;
- avoid duplicate model copies;
- package/runtime options already part of the frozen deployment;
- exact local loading rather than duplicate download/cache copies.

Do **not** silently use CPU offload, smaller batch/context, different dtype, different quantization, or another model to fake success.

If the authoritative contract truly cannot fit the RTX3090 after bounded identity-preserving recovery, record `SKIPPED_RESOURCE` for that deployment/scenario and continue every other row. This does not stop the campaign.

### Trace size / disk pressure

Use canary-based size estimation, rolling copyback, local SHA closure, then safe remote deletion. Do not wait until the disk is nearly full.

### Target zero records

Run phase/kernel census. If target absent, classify `STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED` and select the correct phase-specific target if the scientific plan requires one. Never infer “no memory traffic” from a zero target trace.

### Tool bug

Patch with focused tests, document the code anchor, rerun the smallest affected gate, and continue.

---

## 8. When user intervention is truly allowed

Do not interrupt the Goal for ordinary engineering issues.

A model may require user action only when **all technically safe recovery paths have been exhausted** and one of these remains:

1. gated/licensed model access requires credentials not available to Codex;
2. authoritative exact identity cannot be reconstructed from project history, retained evidence, or official metadata;
3. the scientific workload physically cannot fit the available GPU without changing frozen identity;
4. a required external service/host is unavailable and there is no existing alternate transfer path.

Even then, continue every independent model/scenario first. Put unresolved user actions in the final report with the exact command/file/credential/action needed; do not stop the whole campaign at the first such row.

---

## 9. Required execution stages

Recovery-v3 uses stages R0–R9. Detailed acceptance criteria are in `C16_FULL_AUTHORITY_RECOVERY_V3_STAGE_ACCEPTANCE.md`.

```text
R0 Authority / matrix reconciliation
R1 Exact identity + asset recovery
R2 Package transfer + runtime preflight
R3 Native baseline + lightweight census
R4 Target-plan freeze
R5 NVBit map + canary + reproducibility
R6 Formal bounded capture
R7 Immediate local copyback + SHA closure
R8 Per-deployment/scenario publication
R9 Cross-model final dataset / integrity closeout
```

A row advances only when its current stage acceptance criteria pass or the authoritative contract explicitly permits a resource skip.

---

## 10. Execution order

Prioritize Wave-1 completion before Wave-2, but pipeline asset download/copyback in parallel with CPU-only metadata work when safe.

Recommended order:

```text
1. Reconcile accepted Llama S0 and prepare Llama S1-S4
2. Qwen2.5-0.5B
3. Qwen2.5-7B raw
4. Qwen2.5-7B AWQ
5. Publish Wave-1 checkpoint
6. Qwen3-8B
7. Qwen3-30B-A3B
8. DeepSeek-V2-Lite
9. GLM user extension
10. Final R9 dataset closeout
```

Do not wait idly for a large asset transfer: while one transfer runs, perform metadata-only recovery, local parsing, tests, or publication work for another row.

---

## 11. Capture budget / storage discipline

Keep C16's bounded-capture discipline:

- one GPU capture process at a time;
- each selected capture window: max 4 GiB or 20 minutes, whichever first;
- use target canaries to estimate size before formal capture;
- staged/rolling copyback is mandatory;
- first-wave simultaneous remote raw storage should remain conservative; do not accumulate already-SHA-closed raw files on the GPU host unnecessarily.

If a capture hits the bound, retain `BOUNDED_PARTIAL`, copy it back, and continue other plan rows unless the plan specifically requires retry under a smaller but scientifically equivalent window.

---

## 12. Final completion condition

The Goal is complete only when:

- every authoritative model row has been attempted under its required scenarios;
- Llama S0 is preserved and S1–S4 coverage is closed or explicitly resource-limited;
- all Wave-1 deployments are COMPLETE or have a real, evidence-backed nonrecoverable exception;
- Wave-2 minimum scenarios are COMPLETE or resource-limited per authoritative contract;
- GLM extension has a complete capture or a precise identity/access exception after exhaustive recovery;
- every successful raw trace/large payload is copied back locally and SHA closed;
- native/census/target/capture provenance is complete;
- final local dataset index and Git review pack are validated;
- GPU/diagnostic process counts are zero;
- `MEASUREMENT_ACTIVE` is absent;
- active branch is committed and pushed.

Preferred terminal status:

```text
C16_FULL_AUTHORITY_RECOVERY_V3_DATASET_COMPLETE
```

A partial terminal status is acceptable only for truly nonrecoverable per-row constraints, never for an ordinary fixable engineering problem.
