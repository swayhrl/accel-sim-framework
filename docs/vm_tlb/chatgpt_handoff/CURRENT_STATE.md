# Current state

## Stage

`S1_B0_BOOTSTRAP` reviewed by ChatGPT: **ACCEPTED WITH RESOLVED REMOTE BLOCKER**.

Next authorized work is a two-track macro execution:

- **Track A:** `M1 -> M2 -> M3` single-GPU VM/TLB/PTW substrate.
- **Track B:** `M4A-P` LLM **pre-capture** preparation only.

Real rented-GPU trace collection has been split into a separate prepared stage, `M4A-C`, and is **not authorized yet**. Track B must finish the capture package/runbook and STOP before external capture so the user can select/provision the rental GPU deliberately.

Track B may run in parallel with Track A, but it must not change M1-M3 VM semantics or Core simulator source.

## Frozen source anchors

- Core/GPGPU-Sim baseline: `73774727e25fadf89df6f30ef5cf014091115db7`
- Framework/Accel-Sim baseline: `3016c658f810bdae9a14bf4534ee99e9945eedae`
- Bootstrap Framework branch: `hrl/vm-core-v0`
- Bootstrap Core branch: `hrl/vm-core-v0`

## Writable repositories

- Framework: `swayhrl/accel-sim-framework`
- Core: `swayhrl/gpgpu-sim`

Writable Core repository access and project branches are available. Codex must configure/verify a writable local Core remote (recommended name `research`) before modifying Core source. Do not push to the official Accel-Sim/GPGPU-Sim upstream.

Project branches:

- `swayhrl/gpgpu-sim:hrl/vm-core-v0`
- `swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`
- `swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`
- `swayhrl/accel-sim-framework:hrl/llm-trace-prep-v0`

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

## LLM capture execution split

### Authorized now: M4A-P

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_PRECAPTURE_PREP.md`

M4A-P must recover/review previous rented-server trace scripts, freeze workload/hardware contracts, prepare metadata and contiguous-weight support as far as possible without the rental GPU, and deliver a ready capture package/runbook.

### Prepared, not authorized: M4A-C

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_EXTERNAL_CAPTURE.md`

M4A-C starts only after the user selects/provisions a rented GPU and ChatGPT explicitly authorizes it.

For current paper reproduction, prefer SM86-compatible capture hardware. For future Accel-Sim 2.0 work, tracer support and simulator-target support must be treated separately; RTX5090/Blackwell instrumentation capability does not by itself make RTX5090 a validated H100/H200 simulation input.

## Parallel reporting

Because two Codex windows will run on separate branches, active reports are track-specific:

- Track A: `docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`
- Track B: `docs/vm_tlb/codex_handoff/m4a/LATEST_REPORT.md`

The root `codex_handoff/LATEST_REPORT.md` is retained as bootstrap/historical state rather than a shared parallel-writer target.

## STOP boundary

M1 may proceed to M2 only after M1 acceptance criteria pass. M2 may proceed to M3 only after M2 acceptance criteria pass. M4A-P may proceed independently through its approved pre-capture tasks.

Codex must STOP before:

- any unresolved correctness failure;
- converting a required `PAPER_EXACT` detail to an approximation without authorization;
- Track B starting real external GPU capture (`M4A-C`) before explicit authorization;
- implementing the Segmentation mechanism itself;
- synthetic-KV performance experiments;
- any new AI-aware TLB research mechanism beyond the reproduction inputs.
