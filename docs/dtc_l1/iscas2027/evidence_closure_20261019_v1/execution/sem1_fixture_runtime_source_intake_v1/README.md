# SEM1 ten-case CPU fixture runtime contract: source preparation

**PREPARED_NOT_TESTED. Configure1 / fresh ABI build0 / fixture0 / simulator dispatch0.** Core1fcf5113 and the existing bounded build controller are unchanged. No configure, build, fixture, resource sampling, classifier import or test ran for this preparation.

The current fixture accepts all ten modes, one mode per process. Its source uses real LDST issue/cycle/fill and actual OO physical storage, collect quota and WB completion. The loop is bounded at140 component cycles; it does not launch a kernel, GPU, trace reader, simulator runtime thread or gpgpu_sim::cycle. Source review therefore supports preparing one finite sequential ten-process CPU cohort after a matching ABI build. It does **not** establish that the unbuilt fixture compiles or that any case passes.

There is currently no authorized ten-case cohort entry. Parent f7246c5d's manager has fixed Python build/COV phases, requires successful controller receipts and checks a Python executable during cleanup. Its readonly external role provider recognizes only three earlier roles. Registering fixture JSON rows alone cannot create a valid runtime launch path or accept intended nonzero exits. The parent must bind a new runtime role and actual direct-Popen launcher in published source before releasing it. This pack supplies that next registration's fixed contract and pure output classifier; it introduces no process-launch API.

## Exact launch and evidence contract

FIXTURE_RUNTIME_CONTRACT.json supplies all ten absolute argv arrays, environment maps, case cwd/output paths and fixed order. Each argv is exactly the future build's dtc_l1_sem1_values_ldst ELF, the pinned original SM7_QV100 config, and one mode. No shell, CTest, timeout command, environment setup script, simulator CLI, build controller reuse or argument discovery is allowed. Runtime attempt1/case directories must be created exclusively and retained; existence means stop, not overwrite. Manager creates each own tmp directory before the launch.

The proposed parent entry is finite: concurrency1, maximum10 roots, no retry,900s total including admission/cleanup,60s per case,30/31s soft/hard CPU,2GiB hard virtual address space,1GiB sampled RSS stop, core dumps0. Each stdout/stderr file has a512KiB hard size limit,1MiB combined case logs,10MiB cohort logs and32MiB sampled own output bound. The latter is not a filesystem quota. Proposed disk start is2GiB floor +32MiB output +128MiB safety. These are preparation bounds for parent review, not resource admission or an amended global policy.

Parent must freeze the successful fresh build receipt, ELF and libcudart.so hashes, static loader/DT_NEEDED/RPATH and dependency closure, assertion-enabled compiler recipes and pinned config before publishing any runtime release. Build is still0, so binary/library SHA fields are intentionally null. The existing configured link recipe names build/libcudart.so and an absolute build RPATH; actual postbuild dynamic identity remains unverified. Do not execute ldd or use an ELF as a metadata-discovery helper. The retained configure, Cache and compile_commands identities remain fixed; do not reconfigure.

Before the first root the parent needs a fresh complete paired host+cgroup R2 admission under its unchanged policy. Every later launch needs its required still-valid admission and current resource/role checks. A resource failure ends this finite attempt without hidden polling. All-project pressure/OOM, own process and output monitoring continue throughout. A timeout, OOM/resource event, log bound, identity mismatch, unexpected descendant or unresolved cleanup overrides every nominal expected exit.

Only the parent's retained direct Popen/pidfd establishes ownership. Record actual boot/PID/start ticks/TGID/PGID/SID, argv/exe/cwd/source/ABI identities, monotonic birth and terminal wait. No identity may be adopted from process discovery. While its direct child is unreaped, the parent's frozen cleanup can stop that exact owned instance/group. After reap, inspect/report leftovers without signalling a remembered numeric PID/PGID. Unknown descendants or leftovers mean CLEANUP_UNRESOLVED and no next case. If a fast root exits before live observer sampling, preserve actual Popen/wait evidence and mark unavailable live attributes honestly; the parent must explicitly bind this observation policy before execution.

## Source-bound expected results

| Case | Exit | Required interpretation |
|---|---:|---|
| shared | 0 | Three consumers, bytes0..3 all match,4 accepted packets. |
| masked | 0 | Three consumers, synthetic requested bytes31/32 all match across two sectors. |
| with-e | 0 | Four consumers,8 accepted packets; later consumer byte0=153 after fixture publication and selected E. |
| ae | 0 | Three matching consumers under hash-bankrow1. |
| ad | 0 | Ten matching consumers under progressive-wakeup1. |
| no-e | 0 | Exactly one stale byte: later consumer byte0 got0/expected153; explicit countermodel marker;4 packets. |
| wrong-byte | 1 | Exactly three mismatches, each consumer byte0 got1/expected0;12 total byte records; no RESULT. |
| missing-sector | 2 | Exact incomplete-return marker; no final byte/RESULT records; source asserts live Ref. |
| wrong-generation | 1 | Actual sem1_accept_sector identity/sector assertion and SIGABRT crash-handler evidence. |
| early-release | 1 | Actual oo_frontend::release combined allocation/generation/Tag/Ref assertion and SIGABRT evidence. |

Normally completed cases must report exactly the own frozen libcudart.so path through dladdr. Positive cases report exact consumers/packet population plus actual_ldst=1, kernels=0, GPU_cycle_calls=0 and architectural/native UNPROVEN. Their source asserts full consumer retirement, collected sector counts, no active Ref/inflight entry, exact retire count, nonzero real RF-blocked WB cycles and an empty scoreboard. wrong-byte reaches these completion assertions before its deliberate return1. No assertion negative is credited with reaching final completion.

The existing gpu-sim.cc crash handler catches SIGABRT and calls _exit(1). The two assertion negatives therefore require exit1 **and the exact assertion site/expression plus SIGABRT**, not exit-6 or arbitrary nonzero. Buffered SEM1_LIBRARY stdout can be absent on _exit; record per-case dladdr evidence UNAVAILABLE in that event. Static ABI/source binding remains mandatory but cannot be described as observed per-negative loaded-library stdout. Return64, return71, SIGSEGV, timeout and resource/cleanup failure are never expected rejection success.

evaluate_fixture_output.py contains a pure, source-bound classifier for these records. It has no CLI, launch, signal, wait, reference-memory or injection API and is PREPARED_NOT_TESTED: it has not been imported or executed. Its hash is in the contract. Its output checks do not authenticate launch or loaded mappings; the parent must first join actual resource/ownership/ABI/cleanup receipts. The parent must review/integrate it through its separately bound finite entry. Arbitrary logs or a caller-provided library path cannot establish runtime provenance.

## Semantic limits and remaining blockers

A successful future cohort would yield **five conditional sector-value cases, one conditional countermodel and four targeted rejection cases**. It would not be ten positive value tests. Explicit packet bytes traverse actual accepted generation-scoped physical storage and actual collection/WB hooks; reference arrays are separate fixture state. These are diagnostic bytes, not native application data or architectural register values.

The no-E/with-E pair executes no store. Its external publication and selected source-E invocation are explicit fixture assumptions; application object lifetime/publication-to-E proof and coherence remain unresolved. masked starts from a supplied coalesced mask, so upstream coalescing/lane gather is unproved. ad exercises the actual progressive-ready path but adds no independent per-notification timing assertion. early-release fails a compound guard with live Tag and Ref; it does not isolate the Ref predicate. missing-sector observes withheld response, active Ref and no final output protocol, without independently enumerating every internal collected vector.

Pending steps belong to the parent: complete/freeze the matching ABI build, bind the new runtime role/launcher/classifier and exact observation/cleanup schema, publish a separate runtime release, then obtain fresh full R2 admission. Native/full architectural/application values remain UNPROVEN. No new K0/candidate policy, functional ISA, simulation, performance claim or AG4/AG5 retry is introduced.
