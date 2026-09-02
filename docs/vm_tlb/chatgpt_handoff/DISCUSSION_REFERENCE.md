# Discussion reference

## Research objective

Build a reusable, research-grade GPU virtual-memory substrate on a clean Accel-Sim/GPGPU-Sim baseline, validate it in a single-GPU setting, reproduce `Towards Segmentation-Based Address Translation for LLM Inference`, and only then use the infrastructure for new AI-workload TLB research.

## Why the clean dev baseline is the root

S1-R0 established that the current TLS branch contains useful MCM/cache infrastructure but no usable timing TLB/PTW implementation. The legacy `dev-uvm` branch has older TLB/GMMU/UVM code but is heavily diverged. Therefore:

- TLS/MCM code is a future adapter/reference, not the VM root.
- `dev-uvm` is a behavior/interface reference only; do not wholesale cherry-pick it.
- M1-M3 start from the frozen clean Core and Framework baselines.

## Why SimVA / SimPA are explicit simulator contracts

Current trace parsing carries raw 64-bit addresses without a VA/PA type. We therefore define the trace memory address as `SimVA` for the simulator model, while explicitly avoiding a claim that this proves the exact internal NVIDIA hardware VA stage observed by NVBit.

The first mapper is identity-like (`SimPPN = SimVPN`) so the data address reaching cache/DRAM remains numerically unchanged. This isolates translation effects from changes in cache set mapping, DRAM partition mapping, or memory locality.

The strongest transparency checks are:

1. VM disabled == frozen baseline.
2. VM enabled + ideal translation + identity mapping == frozen baseline for all non-VM architectural outcomes.

Failure of either blocks later stages.

## Why translation is inserted after coalescing

The existing trace-driven path first creates coalesced 32/64/128B memory transactions and then sends them toward L1D. M1-M3 therefore model translation per approved coalesced transaction rather than per lane. Codex must prove whether any transaction can cross the base-page boundary and add splitting only if evidence requires it.

## Why page faults are excluded from M1-M3

The immediate research question is TLB/PTW/MSHR behavior, not residency management. Adding page fault service, migration, UVM oversubscription, PCIe/NVLink transfer, and shootdown behavior now would couple multiple phenomena and make correctness and causality harder to establish. These remain future extensions for CLAP/UVM work.

## Why M1-M3 are one macro track

M1, M2, and M3 have a strict dependency chain but can be executed continuously in Codex target mode because each stage has deterministic internal gates:

- M1: semantic substrate + transparency.
- M2: functional TLB/MSHR/fixed-PTW/stall-replay pipeline.
- M3: timing-realistic PTE memory path + PWC + page sizes + characterization readiness.

Codex may advance automatically only after the current stage's acceptance criteria pass. A failed invariant is a macro-task STOP, not an invitation to weaken the test.

## Why M4A can run in parallel

LLM trace and metadata preparation is mostly independent of the VM implementation. It can proceed concurrently to reduce schedule risk, provided it does not alter the M1-M3 Core semantics.

M4A must establish:

- whether an exact public paper artifact/trace exists;
- a reproducible Llama-3.2 1B workload/capture path if not;
- allocation/tensor metadata sufficient to classify WEIGHT/KV_CACHE/ACTIVATION/WORKSPACE;
- a credible path to the paper's contiguous-weight layout;
- trace/config compatibility with the frozen simulator.

M4A is preparation only. It must STOP before implementing segmentation or synthetic-KV performance behavior.

## Target-paper facts that matter

The paper evaluates Llama-3.2 1B using a TP-equivalent 1/4 partition on a downscaled RTX3070-like configuration, batch size 8, base input sequence length 64, and 3 generated tokens. It focuses on prefill and the first decoding phase, and emulates longer contexts by injecting synthetic KV translation requests rather than fully simulating a 12K-token execution.

The scheme requires model weights to be virtually and physically contiguous, uses a small segment descriptor containing base/limit/offset, bypasses page-based translation for matching weight accesses, and leaves KV/activation on conventional paging.

Exact parameters and unresolved paper details are maintained in `docs/vm_tlb/paper_specs/SEGMENTATION_LLM_2026.md`.

## Rejected shortcuts

Do not:

- build single-GPU TLB research on top of the full TLS implementation;
- treat the old `dev-uvm` implementation as authoritative;
- infer tensor type from address patterns without metadata evidence;
- call an approximation `PAPER_EXACT`;
- represent translation-MSHR merge as a TLB hit;
- model realistic PTW as a single fixed penalty once M3 requires real PTE traffic;
- run paper performance figures before correctness invariants are closed.
