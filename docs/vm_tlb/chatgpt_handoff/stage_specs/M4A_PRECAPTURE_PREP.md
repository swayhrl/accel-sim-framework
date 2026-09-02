# M4A-P — Pre-capture Preparation for LLM Trace / Metadata

## Status

**AUTHORIZED NOW.**

This stage is intentionally separated from real trace capture on a rented GPU server. It must finish with a ready-to-run, provenance-preserving capture package and a precise rental-hardware requirement. It does **not** require the current development server to have a suitable GPU.

STOP before `M4A-C_EXTERNAL_CAPTURE.md` unless a later ChatGPT-owned handoff explicitly authorizes the rental-server capture stage.

## Objective

Prepare everything that can and should be done before renting external GPU time for the reproduction of `Towards Segmentation-Based Address Translation for LLM Inference`:

1. audit paper/artifact/trace availability;
2. recover and review the user's previous AutoDL/rented-server trace-collection scripts before writing new infrastructure;
3. freeze the paper workload contract and capture-hardware compatibility policy;
4. prepare a reproducible, one-command rental-server capture package;
5. prepare contiguous-weight workload support to the strongest evidence level possible without the target GPU;
6. define and implement versioned allocation/tensor metadata schemas and collection hooks where possible;
7. produce an exact external-capture runbook and validation checklist.

M4A-P is preparation, not simulator mechanism implementation and not formal trace collection.

## A. Mandatory legacy trace-capture asset audit

Before creating a new capture framework, search existing local repositories, branches, worktrees, scripts, docs, and Git history for trace-collection infrastructure previously written for rented GPU servers / AutoDL.

Search scope should include, where present:

- `/workspace/repos/accel-sim-framework`
- `/workspace/worktrees/*accel*`
- relevant archived/project worktrees
- all relevant Git refs (`git log --all`, `git ls-tree`, etc.) without scanning giant trace/result payloads unnecessarily

Search terms / likely clues include at least:

- `AutoDL`, `autodl`
- `run_hw_trace.py`
- `install_nvbit.sh`
- `trace_b200.sh`
- `trace collector`, `trace_collect`, `capture`
- `tar.zst`, `tar.gz`
- `gpu-workloads`, `gpgpu-workloads`
- scripts that install/configure CUDA/NVBit, build workloads, capture traces, checksum/package results, or generate manifests

For every candidate, report:

- exact file path;
- repository / branch / commit provenance if tracked;
- whether it is tracked or only local/untracked;
- intended GPU/CUDA/NVBit versions;
- supported workloads;
- environment/bootstrap behavior;
- output layout and packaging format;
- whether it can be reused unchanged, adapted, or should be retired;
- any known prior successful run evidence.

Do **not** rewrite the collector until this audit is complete. Prefer adapting proven infrastructure.

## B. Paper/artifact/source audit

Use `docs/vm_tlb/paper_specs/SEGMENTATION_LLM_2026.md` and perform the targeted public-source audit already required by the parent M4A spec.

Record whether any author-provided artifact exists for:

- Accel-Sim patch;
- Llama-3.2 1B trace;
- sub-entry implementation;
- synthetic-KV injection;
- contiguous-weight loader;
- exact TP=4 single-partition workflow.

Use `PAPER_DETAIL_UNAVAILABLE` rather than inventing an implementation when evidence is absent.

## C. Capture-hardware compatibility policy

### C.1 Paper-reproduction route (Accel-Sim 1.x / GPGPU-Sim 4.2)

The simulated target is the paper's downscaled RTX3070-class configuration. The trace source should therefore be **SM86-compatible** unless stronger artifact evidence says otherwise.

Preferred rented capture GPUs are SM86 devices such as RTX 3070 / RTX 3090 / RTX 3080 Ti (or another verified SM86 device). A different physical GPU model may be used as a capture source only after recording compute capability, library/kernel-selection implications, and classification as `PAPER_EXACT`, `PAPER_COMPATIBLE_SELF_CAPTURE`, or `DOCUMENTED_APPROX`.

Do not capture on V100/SM70, A100/A800/SM80, Ada/SM89, Hopper/SM90, or Blackwell/SM120 and then silently replay that SASS as RTX3070/SM86.

### C.2 Future modern AI-TLB route (Accel-Sim 2.0)

This is **not** the current paper-reproduction trace, but M4A-P should record a future capture option.

As of 2026-09-02:

- Accel-Sim 2.0 formally emphasizes validated Hopper H100/H200 simulation;
- its release notes still describe Blackwell B200 / RTX5090 simulation support as roadmap/experimental-future work;
- NVBit 1.8 itself supports modern Blackwell instrumentation, so the tracer may run on RTX5090 even when the simulator is not yet a validated RTX5090 target.

Therefore:

- an RTX5090 may be used for **capture-tool / metadata smoke testing** if useful;
- do **not** designate an RTX5090 SASS trace as a formal Accel-Sim-2.0 H100/H200 simulation input;
- if H100 is unavailable, an available Hopper H800 may be evaluated later as an SM90-compatible capture source, explicitly labeled as not identical to H100 hardware;
- A100/A800 may support a separate Ampere modern-workload line, but not Hopper-specific kernel behavior.

M4A-P must produce a short hardware-choice table for the user before rental.

## D. Freeze the workload contract

Prepare/version the exact known paper workload contract:

- Llama-3.2 1B;
- tensor-parallel scale factor 4, one partition evaluated;
- batch size 8;
- base input sequence 64;
- 3 generated output tokens;
- prefill + first decode phase as primary real trace;
- extra short decode iterations only if needed to validate weight reuse;
- no full 12K instruction trace; long-context pressure belongs to later synthetic-KV work.

Keep the exact TP=4 partition-generation method and dtype/quantization as `UNKNOWN` until evidence resolves them. Do not silently substitute a full-model trace.

## E. Prepare the rental-server capture package

Produce a lightweight directory/package that can be copied/cloned onto a fresh AutoDL-like server and run with minimal manual steps.

The package should include, as applicable:

- preflight/inventory script;
- isolated environment/bootstrap script (avoid destructive system-wide upgrades);
- frozen repo/commit checkout logic;
- NVBit/tracer build/install step;
- workload/model setup step;
- capture driver;
- metadata sidecar collector/hook;
- trace post-processing;
- manifest/checksum generation;
- archive packaging (`tar.zst` preferred when available, documented fallback allowed);
- disk-space preflight and projected trace-size guard;
- clear failure/STOP behavior;
- detailed logs.

The capture package must pin or record all versions necessary for provenance rather than implicitly using "latest".

Do not commit model weights, trace payloads, credentials, tokens, or large generated artifacts.

## F. Contiguous-weight preparation

Use the evidence hierarchy from the parent M4A spec:

1. author artifact;
2. faithful framework-level one-buffer allocation with tensor views;
3. trace-level relocation only if later explicitly approved.

Before real GPU capture, M4A-P should implement/prototype as much as possible and provide static/unit validation for:

- deterministic tensor ordering;
- total byte size / alignment accounting;
- tensor-to-offset mapping;
- no overlap in the planned flat buffer;
- reproducible metadata export.

Runtime GPU VA contiguity is verified in M4A-C, not guessed in M4A-P.

## G. Metadata schema / hooks

Prepare a versioned sidecar schema separate from the SASS trace. Minimum semantics:

- schema version;
- run/model identity;
- allocation ID;
- SimVA/input address range start + size;
- object kind: `WEIGHT`, `KV_CACHE`, `ACTIVATION`, `WORKSPACE`, `UNKNOWN`;
- model/layer/tensor identity where known;
- lifetime/event boundaries where known;
- classification provenance;
- kernel/phase mapping for `MODEL_LOAD`, `PREFILL`, and `DECODE`.

Unknown addresses must remain `UNKNOWN`.

Synthetic KV is not collected here and must remain separate from real allocations.

Implement schema validation and non-GPU unit tests where possible. Any GPU-dependent address/range validation is deferred to M4A-C.

## H. External-capture runbook

Create a precise runbook for M4A-C that begins from a fresh rented instance and lists:

1. required GPU architecture / minimum VRAM;
2. acceptable fallback GPUs and exact evidence label consequence;
3. expected disk requirement / safety margin calculation;
4. environment setup command(s);
5. tiny tracer smoke before LLM capture;
6. Llama workload smoke before tracing;
7. contiguous-weight validation;
8. metadata validation;
9. short-context paper trace capture;
10. post-processing/checksum/package commands;
11. artifact-copy-back checklist;
12. cleanup/release conditions for the rental instance.

The goal is that the user can rent the machine, clone/copy the prepared package, and execute it without redesigning the workflow interactively.

## Required deliverables

At minimum create/update stable docs/scripts such as:

- `docs/vm_tlb/llm/WORKLOAD_CONTRACT.md`
- `docs/vm_tlb/llm/CAPTURE_HARDWARE_MATRIX.md`
- `docs/vm_tlb/llm/TRACE_ACQUISITION.md`
- `docs/vm_tlb/llm/METADATA_SCHEMA.md`
- `docs/vm_tlb/llm/LEGACY_CAPTURE_ASSET_AUDIT.md`
- `docs/vm_tlb/llm/PAPER_DETAIL_LEDGER.md`
- a clearly named lightweight capture utility/package

Review pack:

`docs/vm_tlb/review_packs/M4A_PRECAPTURE_PREP/`

## Acceptance criteria

M4A-P PASS requires:

1. legacy AutoDL/rented-server capture scripts have been exhaustively audited within the declared search scope and reusable assets identified;
2. paper artifact/trace audit is complete enough to stop blind searching;
3. paper workload contract is versioned and unresolved exactness is explicit;
4. capture hardware matrix clearly distinguishes SM86 paper reproduction, Hopper future research, and unsupported/mismatched SASS routes;
5. a fresh-rental ready capture package/runbook exists;
6. metadata schema + validation tooling exist to the extent possible without the rented GPU;
7. contiguous-weight preparation is implemented/prototyped to the strongest non-GPU-verifiable level;
8. no Core VM semantics are modified;
9. no real paper trace is falsely claimed collected;
10. provenance / review pack / git checks pass.

`CONDITIONAL_PASS` is allowed only for items that genuinely require the external rented GPU or unavailable author artifact.

## STOP boundary

After M4A-P closeout:

- update Track-B report;
- push the M4A preparation branch;
- provide the exact rental hardware recommendation and one-command/runbook entry;
- **STOP BEFORE RENTING/CAPTURING ON EXTERNAL GPU**.

Do not begin `M4A-C_EXTERNAL_CAPTURE.md` until explicitly authorized after the user has selected/provisioned the rented GPU.
