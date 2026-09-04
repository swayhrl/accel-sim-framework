# M4A-PF — Pre-capture Fixup Before Renting GPU

## Status

**AUTHORIZED NOW.**

M4A-P was reviewed by ChatGPT as an acceptable `CONDITIONAL_PASS`, but external capture is **not yet authorized**. One preparation gap remains: the current capture driver requires a user-supplied executable LLM workload command, while the exact paper TP=4 single-partition method is unavailable. The current recommendation of a single RTX3090 is therefore not yet sufficient to define the formal workload path.

This fixup must close the operational/workload ambiguity before rental money is spent.

## Objective

Produce a concrete, pinned, executable workload candidate (or a small set of explicit candidates) and a hardware decision matrix that makes the TP=4 / one-partition issue unambiguous.

Do not collect the formal trace. Do not start M4A-C.

## PF1 — Resolve feasible TP=4 capture strategies

Investigate and document the implementation feasibility of these routes for Llama-3.2 1B, batch 8, input 64, output 3:

### Route E — real TP=4 execution, trace one rank

- 4 x SM86 GPUs if available on a single rented node;
- actual framework tensor parallelism;
- identify whether NVBit can capture only rank0/device0 cleanly with the frozen tracer;
- identify NCCL/collective kernels and whether they should be retained or excluded from the simulated single-partition trace;
- classify fidelity relative to the paper.

### Route A — single-GPU one-rank TP emulation

- construct only the local operator shapes/weights corresponding to one TP rank;
- no claim of exactness unless artifact evidence appears;
- identify required local QKV/MLP partition shapes and any row-parallel dependency placeholders;
- ensure the produced instruction stream is a local partition trace, not a full-model trace.

### Rejected default

A full Llama-3.2 1B single-GPU trace may be useful as a diagnostic workload but must not be the paper reproduction workload and must not be relabeled as the TP=4 partition.

For each route report:

- required GPU count and VRAM;
- software/framework choice and pinned versions;
- expected tracing complexity;
- expected simulator compatibility;
- fidelity label (`PAPER_COMPATIBLE_SELF_CAPTURE`, `DOCUMENTED_APPROX`, or rejected);
- cost/operational risk.

If Route E is feasible and reasonably available, prefer it for the formal paper-capture candidate. If not, do not silently choose Route A; present the tradeoff for user/ChatGPT approval.

## PF2 — Create executable workload wrapper candidate(s)

The capture package must no longer depend on an unspecified external `/mnt/.../llama_workload.sh` with no repository template.

Create one or more versioned templates/scripts under the project utility directory that:

- pin or record model/framework/tokenizer/runtime versions;
- enforce batch 8, input length 64, output 3;
- use deterministic token IDs / prompt inputs;
- explicitly encode the selected TP route;
- honor `M4A_PHASE`, `M4A_RUN_DIR`, and `M4A_METADATA_PATH`;
- generate the required metadata sidecar;
- fail rather than silently falling back to full-model or different TP behavior;
- emit an environment/workload manifest.

Secrets/Hugging Face tokens must remain external environment inputs and never enter Git.

A wrapper may remain unexecuted on the current no-GPU server, but syntax/static/unit validation must pass.

## PF3 — Contiguous-weight runtime hook candidate

The existing static planner is not a runtime contiguous allocator. Prepare the strongest practical workload-side runtime implementation or hook for the chosen candidate framework.

At minimum it must define how to:

- compute the flat weight-buffer size/alignment;
- allocate one backing device buffer;
- map tensor views/parameters into deterministic offsets;
- export base/size/offset metadata;
- avoid untracked post-load copies that would invalidate the range;
- fail or report if a framework operation breaks the one-buffer assumption.

If a fully faithful runtime implementation cannot be prepared without GPU execution, provide the executable hook plus explicit M4A-C runtime assertions; do not claim contiguity from the static planner alone.

## PF4 — Metadata runtime production path

Connect the workload wrapper/hook to `m4a-allocation-sidecar-v1` rather than leaving metadata generation as an unspecified responsibility of the user-supplied command.

Before rental, unit/static tests should cover:

- required fields;
- stable object-kind labels;
- weight tensor offsets/ranges;
- no synthetic-KV entries;
- deterministic phase tags;
- failure on missing required runtime observations.

GPU VA and actual trace-address coverage remain M4A-C checks.

## PF5 — Revise rental recommendation

Do not automatically recommend `1 x RTX3090` until the TP strategy is selected.

Produce a decision table such as:

- `4 x SM86` node — real TP=4 rank0 capture candidate;
- `1 x RTX3090/SM86` — single-rank emulation candidate only if later approved;
- lower-VRAM SM86 — only if measured workload/tracer headroom is sufficient.

The 500 GiB disk gate may remain conservative, but make clear it will be recalibrated after the tiny trace smoke.

## Required deliverables

Update/create:

- `docs/vm_tlb/llm/WORKLOAD_CONTRACT.md`
- `docs/vm_tlb/llm/CAPTURE_HARDWARE_MATRIX.md`
- `docs/vm_tlb/llm/TRACE_ACQUISITION.md`
- `docs/vm_tlb/llm/PAPER_DETAIL_LEDGER.md`
- workload wrapper/template(s)
- runtime contiguous-weight/metadata hook candidate(s)
- static/unit validation scripts

Review pack:

`docs/vm_tlb/review_packs/M4A_PRECAPTURE_FIXUP/`

Track-B report:

`docs/vm_tlb/codex_handoff/m4a/LATEST_REPORT.md`

## Acceptance criteria

PASS requires:

1. real TP=4 rank0 vs single-GPU one-rank emulation feasibility is explicitly analyzed;
2. no full-model single-GPU trace is proposed as the formal TP=4 paper trace;
3. at least one concrete executable workload wrapper candidate exists;
4. the wrapper has pinned/recorded versions and deterministic workload inputs;
5. metadata production is integrated into the wrapper/hook path rather than left unspecified;
6. contiguous-weight runtime strategy/hook exists to the strongest pre-GPU-verifiable level;
7. rental hardware recommendation is conditional on the selected TP route;
8. static/syntax/unit checks pass;
9. no external trace is captured and no Core VM semantics are modified.

If the preferred formal route requires 4 x SM86 and availability/cost is unknown, close as `CONDITIONAL_PASS` with the exact node requirement; do not downgrade automatically to a single-GPU approximation.

## STOP boundary

After closeout, push/report and STOP. M4A-C remains unauthorized until the user/ChatGPT selects the capture route and rental hardware.
