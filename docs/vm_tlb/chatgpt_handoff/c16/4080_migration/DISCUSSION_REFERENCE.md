# C16 RTX4080 Discussion Reference

## Why this handoff exists

The C16 RTX4080 lane has moved from host bootstrap into userspace scientific qualification. The next decisions must preserve exact scientific identity while avoiding unnecessary host/root work.

The project already uses `accel-sim-framework` as the source, script, receipt, and provenance repository. The correct coordination pattern is therefore a scoped handoff inside the same repository, not a new repository. Splitting C16 RTX4080 coordination into a separate repository would separate executable code from the receipts and source anchors that validate it.

## Why U4 should use the transferred local asset

The required gated model already exists on the CPU server with a source-side receipt that binds:

`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

The payload has been rsynced to the RTX4080 host and post-transfer payload hashes were manually observed to match. Therefore Hugging Face authentication is no longer the preferred path for U4.

However, the scientific claim is stronger than "the directory name contains the revision". U4 must bind the transferred bytes to an authoritative source receipt or equivalent payload manifest. If the exact source receipt is not currently present on the RTX4080 host, Codex should first search committed/project evidence for an equivalent exact payload authority. If no such authority exists locally, the correct action is to request the small source receipt/provenance file from the CPU server while continuing independent U8.5 repair work. It must not fabricate provenance from the path name.

## Why U8 is a partial pass rather than a platform failure

NVBit 1.7.5 successfully:

- matched the known-good archive/core hashes;
- built for SM89;
- ran the official vectoradd fixture;
- ran official `instr_count_bb` and counted instructions;
- injected into PyTorch elementwise workloads;
- injected into PyTorch GEMM and observed a live GEMM kernel.

Therefore there is direct evidence that NVBit 1.7.5 can operate on RTX4080/SM89 with driver 580.178.04 for those paths. No driver downgrade is justified by current evidence.

The only unresolved U8 item is the custom C16 no-match/no-trace tool lifecycle: the fixture exited normally and produced zero traces, but the expected READY marker was absent. This is a custom-tool closure problem. It must be repaired because the formal model tracer depends on a trustworthy prewarm/READY/arm protocol, but it is not evidence that the platform or driver is unusable.

## Dependency boundary

U5-U7 depend on U4 but not on U8.5:

- U5: exact Llama native baseline;
- U6: RTX4080-local kernel census;
- U7: NCU model capture.

U9 depends on both:

- U4 exact model closure;
- repaired custom NVBit tool lifecycle from U8.5;
- U5/U6 runtime and target evidence.

Thus U8.5 repair should proceed in parallel with U4/U5-U7 where possible, but U9 is fail-closed until it passes.

## Scientific invariants

- No CPU offload.
- No model/revision/dtype/context/batch substitution.
- No reuse of RTX3090 launch IDs, static instruction ranges, or target maps on RTX4080.
- NCU and NVBit formal model captures remain separate processes/windows.
- Raw `.ncu-rep`, traces, weights, wheel payloads, and build artifacts remain outside Git.
- Git records scripts, manifests, hashes, receipts, derived analysis, and immutable identities.
- Any unknown remains `UNKNOWN`; no retrospective invention of historical build commands.

## Root policy rationale

The RTX4080 host now has ordinary-user NCU permission, a complete userspace CPython/runtime closure, CUDA toolchain access, and a userspace NVBit build path. Therefore ordinary scientific work should continue as `huangrulin`. Root is reserved only for proven unavoidable host mutations, not ordinary installation/build tasks.

## Coordination structure

For this scoped lane:

- ChatGPT-owned state/specification: `docs/vm_tlb/chatgpt_handoff/c16/4080_migration/`
- Codex-owned latest execution report: `docs/vm_tlb/codex_handoff/c16/4080_migration/LATEST_REPORT.md`
- Detailed review evidence: `docs/vm_tlb/review_packs/C16_4080_U4_U9_R1/`

Codex must not rewrite the ChatGPT-owned files while executing the stage. It should report execution results through `LATEST_REPORT.md` and the review pack.
