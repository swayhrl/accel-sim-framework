# M4A — LLM Trace, Metadata, and Paper-Input Preparation

## Objective

In parallel with M1-M3, prepare all external/workload inputs needed for a credible reproduction of `Towards Segmentation-Based Address Translation for LLM Inference`.

M4A is **not** the Segmentation implementation stage. It must not alter the M1-M3 Core VM semantics.

## Primary outputs

By M4A closeout, establish as much of the following as evidence allows:

1. exact public paper artifact/code/trace availability status;
2. exact or best-supported Llama-3.2 1B workload setup;
3. a reproducible short-context trace-acquisition procedure compatible with the frozen simulator;
4. allocation/tensor metadata sidecar design and generation path;
5. a credible method for the paper's contiguous-weight virtual layout and corresponding simulated physical contiguity input;
6. trace/config compatibility validation;
7. an explicit list of paper details that remain unavailable and would require later approved approximation.

## M4A.0 — Paper/artifact/source audit

Use the extracted paper spec:
`docs/vm_tlb/paper_specs/SEGMENTATION_LLM_2026.md`.

Search authoritative/public sources for:

- author/project GitHub repositories;
- supplemental material/artifacts;
- Accel-Sim patches;
- trace archives;
- scripts/configs for the paper;
- detailed L2-TLB sub-entry model;
- synthetic KV translation-injection implementation/parameters;
- exact page-table/PTW model inherited from cited work;
- any author-provided workload modifications for contiguous weight allocation.

Record URLs, repository commit SHAs/tags, publication/artifact identities, access date, and license/redistribution constraints.

If an exact public trace/artifact is not found after a reasonable targeted search, record `PAPER_DETAIL_UNAVAILABLE`; do not keep searching indefinitely and do not fabricate an exact implementation.

The copyrighted IEEE PDF must not be committed to this public repository. A local copy may be indexed in a local-only path if useful, with `.gitignore` protection.

## M4A.1 — Local hardware/software inventory

Without modifying the VM Core, inspect the server for:

- available NVIDIA GPUs and compute capability;
- CUDA driver/toolkit versions;
- NVBit/tracer compatibility;
- Python/PyTorch/vLLM/Transformers versions if installed;
- disk capacity for traces/model cache;
- whether Llama-3.2 1B weights are already available locally;
- current Accel-Sim trace-format/tracer version compatible with the frozen Framework/Core.

Classify a viable capture route as one of:

- `LOCAL_EXACT_OR_COMPATIBLE`
- `LOCAL_APPROX_CAPTURE`
- `EXTERNAL_SM86_GPU_REQUIRED`
- `PAPER_ARTIFACT_AVAILABLE`
- `BLOCKED_OTHER`

Do not install/upgrade a major CUDA/PyTorch stack in-place if it risks breaking existing simulator experiments. Prefer an isolated environment/container/venv and document it.

## M4A.2 — Workload reproduction contract

Prepare a versioned workload specification containing at minimum:

- model: Llama-3.2 1B;
- effective tensor-parallel scaling: factor 4, one partition to be simulated;
- batch size 8;
- base input sequence length 64;
- 3 output tokens;
- phases of interest: prefill + first decoding phase, with any extra short decode iterations only for validation;
- model dtype/quantization if established from paper/artifact, otherwise `UNKNOWN`;
- exact framework/model revision when self-captured.

The paper's TP-equivalent 1/4 partition must not be silently replaced by a full-model trace. If exact TP capture is infeasible, document candidate approaches and STOP before declaring one `PAPER_EXACT`.

## M4A.3 — Contiguous-weight preparation

The paper changes model loading so weights occupy a single virtually contiguous region rather than many layer-sized allocations.

Establish a reproducible approach for the trace/workload path. Preferred evidence hierarchy:

1. author artifact implementation;
2. faithful framework-level single-buffer allocation with tensor views;
3. explicitly documented trace-level relocation/emulation, only if later approved.

M4A may prototype framework/workload-side scripts in its own Framework branch, but must not modify the Core VM implementation.

Required validation for any prepared contiguous-weight layout:

- weight range start/size known;
- no unintended overlap with KV/activation/workspace regions;
- per-weight tensor offset mapping reproducible;
- addresses stable across kernels used in the captured execution;
- original/non-contiguous and proposed/contiguous layout identities clearly distinguished.

## M4A.4 — Allocation/tensor metadata sidecar

Design and, where capture is feasible, generate a versioned metadata sidecar separate from the instruction trace.

Minimum semantic fields:

- schema version;
- address-space label (`SimVA` input range);
- allocation ID;
- VA start;
- size;
- object kind: `WEIGHT`, `KV_CACHE`, `ACTIVATION`, `WORKSPACE`, `UNKNOWN`;
- model ID;
- optional layer/tensor name or ID;
- lifetime start/end event or kernel where known;
- provenance/source of classification.

Synthetic KV is not a real allocation-trace class in M4A; reserve `SYNTHETIC_KV` for the later injection stage.

Required metadata checks:

- no overlapping active ranges unless explicitly justified;
- every classified trace address lies inside its range;
- unknown addresses remain `UNKNOWN`, never guessed as activation;
- report address-coverage fraction by object type;
- cross-kernel range identity/stability report.

## M4A.5 — Trace acquisition / feasibility

First check whether an exact public trace exists. If not, self-capture is the expected path.

Target a short-context trace only; do not attempt a full 12K-context instruction trace merely to reproduce the paper. The paper uses synthetic translation pressure for long-context emulation.

Where hardware/environment permits, collect the smallest trace set that can support later reproduction:

- initialization only as needed to establish allocations;
- prefill at base input length 64;
- first decode phase/token(s);
- enough repeated decode behavior to verify weight-address reuse if practical.

Record:

- GPU model/compute capability;
- tracer version/commit;
- CUDA/runtime/framework/model revisions;
- exact command;
- trace format and total size;
- kernel count;
- trace SHA(s) or manifest checksums;
- whether the trace is exact-paper, paper-compatible self-capture, or an approximation.

Do not commit large trace payloads or model weights. Commit manifests and local paths/checksums only.

If capture requires external hardware, produce a ready-to-run capture package/script and a precise hardware requirement instead of blocking indefinitely.

## M4A.6 — Simulator compatibility validation

For any captured/downloaded trace proposed for later use:

- validate parser compatibility with the frozen Framework/Core;
- run a minimal smoke if feasible;
- confirm ISA/config compatibility rather than assuming that any Ampere trace matches RTX3070;
- record whether the simulation configuration is the paper's downscaled RTX3070 configuration or merely a tracer hardware source;
- confirm the trace preserves the address identities needed by the metadata sidecar.

Do not alter the M1-M3 simulator to make an incompatible trace appear compatible without explicit authorization.

## Paper-details ledger

At closeout classify every required later-reproduction item as:

- `PAPER_EXACT_AVAILABLE`
- `PAPER_EXACT_INFERABLE_WITH_EVIDENCE`
- `PAPER_DETAIL_UNAVAILABLE`
- `NOT_YET_NEEDED`

At minimum include:

- exact L1/L2 TLB organization;
- exact TLB lookup latency/throughput if available;
- exact sub-entry organization/fill/replacement;
- exact PTW/page-table model;
- exact synthetic-KV request-generation distribution/rate/reuse;
- exact TP-partition workload/capture method;
- contiguous-weight software implementation;
- trace/artifact availability.

## Acceptance criteria

M4A PASS means **reproduction-input readiness**, not paper-result reproduction. It requires:

1. targeted artifact/trace audit completed with provenance;
2. local/external capture feasibility explicitly determined;
3. workload contract versioned;
4. metadata schema and classifier path implemented/tested or, if capture hardware is unavailable, fully specified with a ready capture package;
5. contiguous-weight strategy established to the strongest available evidence level;
6. at least one parser/simulator compatibility smoke for the proposed trace path if a trace is available;
7. paper-details ledger completed;
8. no M1-M3 Core VM semantics modified;
9. no copyrighted paper PDF, large trace, or model weights committed;
10. review evidence and git provenance complete.

M4A may be `CONDITIONAL_PASS` if the only remaining blocker is external compatible GPU access or unavailable author artifact, provided the capture package and exact missing information are clearly documented.

## Deliverables

Review pack:
`docs/vm_tlb/review_packs/M4A_LLM_TRACE_METADATA_PREP/`

Also create stable project documents/scripts as appropriate, for example:

- `docs/vm_tlb/llm/WORKLOAD_CONTRACT.md`
- `docs/vm_tlb/llm/TRACE_ACQUISITION.md`
- `docs/vm_tlb/llm/METADATA_SCHEMA.md`
- `docs/vm_tlb/llm/PAPER_DETAIL_LEDGER.md`
- lightweight capture/validation scripts under a clearly named project utility directory.

After M4A closeout, STOP before Segmentation implementation or synthetic-KV simulator injection.
