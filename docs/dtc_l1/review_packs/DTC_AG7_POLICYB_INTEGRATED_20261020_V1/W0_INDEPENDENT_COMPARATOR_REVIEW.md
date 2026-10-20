# W0 independent comparator review

Verdict at intake: **CONDITIONAL_NOT_YET_ACCEPTED; A NARROW NO-EXTRA-BASE PATH IS SOURCE-SUPPORTED, NOT YET QUALIFIED.** The historical 1,071,405-cycle GEMM and 3,278,356-cycle Gaussian observations remain authentic, narrowly scoped AG6 comparators. AG7 does not inherit that acceptance merely by naming c809 or calling telemetry observational. No extra BASE simulator start is authorized here. A Framework-only observer linked to the unchanged original Core library is a materially smaller equivalence bridge than rebuilding Core, and should be evaluated before declaring a new baseline indispensable.

This reviewer fully read the exact AG7 Goal, BB2 contract, feasibility report, CPU qualification and report, BA `BASE_REUSE_DECISION_V2.json`, and the relevant executable preregistration/identity metadata and independent BASE review indexes. Only source and small immutable evidence indexes were read. No model ELF or trace was opened; no compiler, fixture, policy test, simulator, process signal, authority acquisition or production mutation was performed by this reviewer. BA alone decides and records dispatch eligibility after the bridge below is actually closed.

## Historical evidence and its boundary

`BASE_REUSE_DECISION_V2.json` has status `PASS_BOTH_SCOPED_IMPORTED_BASES_FOR_AG6_ONLY_NO_DISPATCH_PERMISSION`. Its two decisions require complete original input/ROI, exact c809 Core, byte-identical runtime/library/loader/cache, equivalent 270 options and only the intended single AE/AD arm bit changing. The GEMM and Gaussian independent reviews expressly exclude rebuilt diagnostic libraries and automatic changed-source/default-OFF equivalence. The old executor limitations remain: AG3 lacks per-resume generation instrumentation; AG4's prelaunch qualification STOP was not reversed. The narrow original import used the run-specific complete strict/event/loader proof joins; it did not recertify those executors.

`AG6_EXECUTABLE_PREREGISTRATION_V2.json` binds the BASE decision hash, input/member/source indexes, original build and runtime manifests, not a generic workload name. Its CPU receipts cover interfaces, lifecycle and exact registered roles. They do not qualify a new simulator producer or automatically establish AG7 scope.

BB2 `CPU_QUALIFICATION.json` records `NOT_EXECUTED_RESOURCE_HOLD`: zero actual unittest methods, zero fixtures and zero simulators. Its source AST/syntax status and expected scenarios cannot be used as W1 CPU PASS. The first resource sample had host IO full avg10 28.90%, cgroup IO 0%; the own relative argv defect was repaired source-only. AG7's explicitly bounded W1 exception changes only the permitted new W1 admission; no old result is back-approved.

## Why existing output is not yet the preferred qualified producer

The c809 `shader_core_ctx::warp_inst_complete()` at `shader.cc:2352–2371` increments `gpu_sim_insn` by `inst.active_count()`. The metric is committed/completed active-lane simulated instructions. `gpu-sim.cc:1553–1571` accumulates into `gpu_tot_sim_insn` and then resets the current count. Their coherent sum, sampled on the simulator thread outside that update, avoids the local reset.

The old `gpu-sim.cc:2562–2590` liveness text prints that sum and flushes stdout, but it requires simulated-cycle sampling, wall-time frequency and `DTRACE(LIVENESS)`. The second cycle path at `:2874–2888` updates time without printing an equivalent completion count. Neither establishes a maximum 30-second record age during parsing or a stalled cycle. Text also lacks the producer identity/epoch/sequence/monotonic contract. BB2's historical sealed stdout proof has no usable semantic progress series. An outer parser cannot manufacture these missing guarantees. Existing output therefore does not presently establish a no-rebuild PASS.

CTA and kernel events are coarser and have distinct hazards: CTA state resets; `set_kernel_done()` is also called by forced stop. They cannot silently replace the committed-instruction metric or prove natural completion.

## Source-supported minimal bridge without an additional BASE start

There is an existing public API surface: c809 `gpu-sim.h:826–828` exposes `gpu_sim_insn` and `gpu_tot_sim_insn`. Frozen Framework `8e43c75a5e2eb60a8466084602b7df8117111e89`, `gpu-simulator/accel-sim.cc:150–171`, runs `cycle()` and `deadlock_check()` serially in `simulate()`. A sample immediately after a returned `cycle()`, on that same thread, can read their coherent sum without changing Core source or injecting a concurrent reader. Framework `gpu-simulator/Makefile` links `-lcudart`; the recorded runtime manifest explicitly resolves the original `combined-final/libcudart.so`. This supports a Framework-only producer linked to the original Core library, rather than rebuilding Core. The stock Makefile also has a `gpgpu-sim` build dependency; a qualified isolated build must avoid inadvertently rebuilding/replacing the frozen Core library.

This is a feasible proof strategy, **not a finding that an implementation already satisfies it**. A completed bridge must bind an exact patch/build and independently establish the following state-projection argument:

1. Project the instrumented execution onto the existing model/config/parser/scheduler/trace state. Every retained modeled transition must be exactly the old transition in the same order. Observer operations may only add stuttering steps to this projection.
2. The producer reads the two completion counters at a coherent same-thread boundary. It writes only observer-owned fixed/bounded records and observer state. Its return value, clock, fd status, sequence, timestamp and failure do not choose or mutate the next modeled transition, random state, input/ROI, stream order, launch window, finite queue/timing service, options or simulated clock. The external guard may stop a run; such a run is consumed and scientifically unaccepted.
3. Review the complete observer call graph, not just the insertion line: initialization/cleanup, allocator use, signals, error paths, descriptors, errno handling and lifetime must introduce no undefined behavior or model alias write. Nonblocking bounded emission and fail-closed loss handling must be real. No wall-clock feedback may alter modeled timing; observer overhead changes wall time and safety survival only. Those effects must remain disclosed and common to all four arms.
4. Counter resets and kernel boundaries must preserve the cumulative metric, and cancellation/limits/errors must not become natural success. Sequence/epoch/source/input/ROI and monotonic time are bound to the proven postfork simulator identity. No unsynchronized `/proc/PID/mem`, debugger injection or pre-admission-parent identity substitution is an equivalent solution.
5. Freeze the changed Framework source, unchanged Core source and original Core library content, exact toolchain/flags, unchanged parser/trace objects, new executable, loader/cache/all dependency closure and the unchanged 270-option/input/ROI tuple. Changes in binary layout or an embed string are not by themselves evidence of modeled change or of equivalence. Actual link/runtime identity and source-to-binary provenance remain necessary.
6. BA must expressly record a newly scoped acceptance of these historical measurements for this exact observational AG7 build. Such a decision may be supported by the independently reviewed non-interference bridge; it cannot be inferred from the historical AG6 decision or from this source-only feasibility opinion. CPU qualification must exercise the producer/receiver/guard protocol and failure paths but does not create a measured BASE or prove AE/AD benefit.

No scientific rule here requires a gratuitous baseline simulation if that bridge can actually be closed. Conversely, a source-diff assertion, synthetic policy PASS, unchanged Core commit string, or lack of observed failure is insufficient. A Core-rebuilding design expands the proof surface: original binary identity is lost, all changed translation units/ABI/build/runtime effects must be covered, and the same independently accepted projected-model equivalence is still required before any fork.

## Gate decision and smallest remedy

At this intake there is **no completed, exact implementation-bound equivalence bridge and no newly scoped BA AG7 BASE acceptance**. Consequently W0 is not yet PASS and cannot authorize a simulator fork. This is a preparation gate, not an assertion that science equivalence is impossible. Continue only with the authorized bounded CPU/static/build qualification sequence while the coordinator independently closes the minimal Framework-only bridge and the heavy resource gate permits it.

If that proof cannot be established, STOP before an AG7 fork. The smallest remaining scientific remedy is explicit comparator authorization for the exact changed build: either an accepted independent non-interference proof with complete runtime binding, or separately authorized complete-input OFF baseline performance starts for GEMM and Gaussian under the same frozen instrumentation/runtime. The current four-start authorization contains only the AE/AD arms and does not grant those additional BASE starts, replacements or a free canary. If resources block qualification first, publish that actual gate and keep the comparator status unaccepted; do not invent a completed proof or claim a speedup.

Until complete 4/4 scientific acceptance, `F=null` and O remains provisional. Old AG6 stays 1/4 consumed, 0 accepted, three UUIDs sealed; BA remains independent 0/32. Existing selection files and original BASE values are preserved.

## Compact source/evidence bindings

| Item | Exact binding |
|---|---|
| AG7 Goal commit | `244eea3d6ccde53bf4ceffdf16da9f25295147cb` |
| Goal SHA256 | `5492e08baed9fc80ebc46a0fbe5c7ec90351fb045bbab6f754959e5866bb0ddc` |
| BA BASE decision SHA256 | `a8e834093bc3da494190798cc87eee6c39edbe34efa04d38a5ab6771cea37f9a` |
| AG6 executable preregistration SHA256 | `45d994d7489880bdfe53a1c902207856f06f77ba7927ba8dd6f52124f7dfe9cc` |
| Original build metadata SHA256 | `0f66fb68264ac061b4800b7c134b82d7a73b10e96d3993dc59fdea552826142a` |
| BB2 progress report SHA256 | `e7dbc4292dec836d0c51b8b7ebeca95769bfba6c724cbf9800aff6ba3c47f12a` |
| Core commit | `c8090115bd57512b1b23fca7d925301fa620c751` |
| Core shader.cc / gpu-sim.cc / gpu-sim.h blobs | `af741064700409363d06aa447d601aa740f6c57f` / `c03efe92e303c1e557319bdc0a9b0c3f8961085e` / `f4ebe35b887ad62d93491dd5493293c7ed8c88e7` |
| Original compiled Framework | `8e43c75a5e2eb60a8466084602b7df8117111e89` |
| Original trace ELF SHA256 (metadata only, not reread) | `38158d03dcaecd847d0d6098603c7bc4bfd2a165c4e46f657930e5dedbd291bd` |
| Original Core library SHA256 (metadata only, not reread) | `aee7c03cf30c2e9c2c9577165e019ce1dde929a668ca84882b5286415989cec2` |

The source inspection targeted exact Git objects and small indexes; it does not assert current filesystem contents or current loaded images equal the historical metadata. The single exact authority/resource snapshot and any new implementation-bound closure belong to the sole BA coordinator.
