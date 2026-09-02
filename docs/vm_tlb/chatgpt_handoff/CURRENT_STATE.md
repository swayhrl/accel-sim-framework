# Current state

## Stage

`S1_B0_BOOTSTRAP` reviewed by ChatGPT: **ACCEPTED WITH RESOLVED REMOTE BLOCKER**.

Next authorized work is a two-track macro execution:

- **Track A:** `M1 -> M2 -> M3` single-GPU VM/TLB/PTW substrate.
- **Track B:** `M4A` LLM trace / allocation metadata / paper-input preparation.

Track B may run in parallel with Track A, but it must not change the M1-M3 VM semantics or Core simulator source.

## Frozen source anchors

- Core/GPGPU-Sim baseline: `73774727e25fadf89df6f30ef5cf014091115db7`
- Framework/Accel-Sim baseline: `3016c658f810bdae9a14bf4534ee99e9945eedae`
- Bootstrap Framework branch: `hrl/vm-core-v0`
- Bootstrap Core branch: `hrl/vm-core-v0`

## Writable repositories

- Framework: `swayhrl/accel-sim-framework`
- Core: `swayhrl/gpgpu-sim`

ChatGPT independently verified that `swayhrl/gpgpu-sim` is writable and contains the frozen Core baseline. Remote branches have been created:

- `swayhrl/gpgpu-sim:hrl/vm-core-v0`
- `swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`
- `swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`
- `swayhrl/accel-sim-framework:hrl/llm-trace-prep-v0`

Codex must configure a local writable Core remote (recommended name: `research`) before modifying Core source. Do not push to the official Accel-Sim/GPGPU-Sim upstream.

## Verified bootstrap evidence

`VERIFIED_RUN` from S1-B0:

- clean baseline build: PASS;
- Rodinia LUD-64 / QV100 smoke: PASS;
- same trace with unchanged SM86 RTX3070 config: PASS;
- no simulator behavior/config/trace-parser/VM-TLB functionality modified during bootstrap.

Review entry:
`docs/vm_tlb/review_packs/S1_B0_BOOTSTRAP/README.md`

## Frozen modeling decisions for M1-M3

- Trace memory address is named `SimVA` by simulator contract; this is not a claim about the exact NVIDIA internal address stage captured by NVBit.
- Translation produces `SimPA`; preserve both SimVA and SimPA for observability.
- Initial mapper is identity-like at page granularity: `SimPPN = SimVPN`, so data `SimPA == SimVA`.
- Translation operates on coalesced memory transactions before the real L1D/data-cache access unless directed evidence requires a different split.
- M1-M3 model address translation only: all application pages resident; no GPU page fault, migration, UVM oversubscription, or CPU fault service.
- TLB state persists across ordinary kernels in one simulated context unless explicitly invalidated/reset.
- PTE requests are physical and must never recursively translate.

## Target-paper state

Primary reproduction target:
`Towards Segmentation-Based Address Translation for LLM Inference`, IEEE Computer Architecture Letters, 2026, DOI `10.1109/LCA.2026.3693796`.

The copyrighted PDF is not committed to this public repository. Extracted reproduction specifications are stored in:
`docs/vm_tlb/paper_specs/SEGMENTATION_LLM_2026.md`.

## STOP boundary

M1 may proceed to M2 only after M1 acceptance criteria pass. M2 may proceed to M3 only after M2 acceptance criteria pass. M4A may proceed independently through its approved preparation stages. Codex must STOP before:

- any unresolved correctness failure;
- converting a required `PAPER_EXACT` detail to an approximation without authorization;
- implementing the Segmentation mechanism itself;
- synthetic-KV performance experiments;
- any new AI-aware TLB research mechanism beyond the reproduction inputs.
