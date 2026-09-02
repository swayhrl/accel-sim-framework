# Discussion reference

## Why the clean dev baseline is retained

The project deliberately starts from the clean Core/Framework baselines rather than TLS/MCM or legacy UVM code. The current TLS branch has no usable timing TLB/PTW pipeline and carries substantial MCM/cache-specific semantics. The old `dev-uvm` branch contains useful historical implementation ideas but is heavily diverged and is reference-only.

Frozen bases:

- Core/GPGPU-Sim: `73774727e25fadf89df6f30ef5cf014091115db7`
- Framework/Accel-Sim: `3016c658f810bdae9a14bf4534ee99e9945eedae`

## Bootstrap outcome

S1-B0 established isolated worktrees and produced the first clean `VERIFIED_RUN` evidence. The only original condition was lack of a writable Core project remote. ChatGPT review subsequently verified `swayhrl/gpgpu-sim` as writable, verified that it contains the frozen Core commit, and created `hrl/vm-core-v0` there from that exact commit.

Codex still needs to configure/verify the local Core worktree remote before the first Core source modification. Official upstream must remain read-only.

## VM modeling decisions to preserve into M1

These are modeling contracts, not claims about undocumented NVIDIA internals:

1. The raw trace memory address becomes simulator input address `SimVA`.
2. VM translation produces `SimPA`; preserve both identities for observability.
3. Initial mapping is identity-like (`SimPPN = SimVPN`) so enabling ideal translation does not silently alter cache/DRAM locality.
4. Translation is expected to operate on coalesced memory transactions before real data-cache access, not as one TLB lookup per lane by default.
5. M1–M3 model resident memory only: no page faults, migration, UVM oversubscription, or CPU fault service.
6. TLB state should persist across normal kernels in the same simulated context unless an explicit invalidation/remapping event is modeled.
7. PTE memory traffic must never recursively enter normal translation.

The exact state-machine details, queue semantics, page-size representation, and statistical definitions remain to be frozen by M1 specifications.

## Why M4 can proceed in parallel

LLM input preparation has a separable critical path: paper/artifact audit, trace availability, trace acquisition planning, allocation/tensor metadata design, and local paper-reference extraction can proceed while M1–M3 implement the generic VM substrate.

M4 parallel work must not modify Core VM semantics or assume unapproved TLB/PTW behavior. It should produce inputs/specifications that M1–M3 can consume later.

The target paper uses Llama-3.2 1B with a scaled partition and short real simulation, then injects synthetic KV translation pressure for long-context emulation. Therefore an exact public 12K-context instruction trace is not required. However, an exact public paper trace/artifact has not yet been established; absence of such an artifact must not be silently replaced by an approximation.

## Paper handling

The uploaded IEEE paper may be copied to a local server-only reference directory if useful, but should not be committed to the public repository. Commit bibliographic metadata, extracted reproduction parameters, and provenance notes instead.

## Research boundary

M1–M3 close out the generic single-GPU translation substrate. Segmentation-specific behavior, tensor-aware policies, and new AI-aware mechanisms must not be used to simplify or bias the generic baseline.
