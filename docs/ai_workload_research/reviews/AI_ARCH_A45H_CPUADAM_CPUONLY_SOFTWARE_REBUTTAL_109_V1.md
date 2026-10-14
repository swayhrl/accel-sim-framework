# Round A45H | CPU-only original CPUAdam software counterfactual / STOP

Executor: Codex Lane M / node109, current window reused under explicit user instruction. Independent branch `hrl/aiarch-a45h-cpuadam-cpu-only-109-v1`; fixed start `7b59349979dc77ec0a671c0ca96d7ebaadf3d8dd`. No coordinator merge. This is synthetic CPU component evidence, not another Rubble training run.

## Verdict and gates

**CPU_SOFTWARE_SENSITIVITY_OBSERVED / STOP.** Unchanged original CPU functions show substantial descriptive thread-policy sensitivity under the frozen synthetic conditions. OMP8 is faster than OMP16 for both optimizer shapes here. This provides software counterevidence to treating the OMP16 historical branch cost as established hardware headroom; it does not quantify recoverable training time or qualify a hardware mechanism.

| Gate | Actual result | Evidence class |
|---|---|---|
| G0 | PASS: old M STOP and clean; new worktree/output; host capacity safe | CPU_COMPONENT_NATIVE / A44_HISTORICAL_NATIVE |
| G1 | PASS: frozen module/source, effective OMP limit, exact scan/count outputs, finite FP32 weight/moments/forward errors all 0 <= 1e-5 | CPU_COMPONENT_NATIVE |
| G2 | PASS: nine fresh processes including gate-order recovery: formal36 conditions x7 measurements; preliminary168 measurements and all180 warmup values also retained | CPU_COMPONENT_NATIVE |
| G3 | Software signal observed; CPU-only scope closed; no further task authorized | CPU_COMPONENT_NATIVE + SOURCE + UNKNOWN |

Qualification checks occur in every warmup and measured call. Initial scan timing preceded global Adam qualification and is preserved as **PREQUALIFICATION_ONLY**. Gate-order audit repaired the wrapper pipeline: after all original Adam/forward numerical fixtures passed, scan1/8/16 fresh processes were repeated with identical preregistered input hashes. Formal scan values below come only from these post-qualification processes; preliminary values remain in JSON and were not silently discarded. The seven formal optimizer measurements per condition were not repeated; their own three numeric-qualified warmups precede them. No scientific input, source math or tolerance changed.

## Frozen identity and method

Author source `SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932`; unchanged module SHA256 `c451fda99327e5969da9f0476ef3f4915815dc9ff314c22cce002e5551379a55`. `cpu_adam.cpp` SHA256 `f3f32bc04f61749baf57d1bd877b24379597e50cf4a94d04fdde80a11c19ce9f`, matched frozen source manifest and blob `f1b40eb4283cfd95c9b26b01448d7275f5aa0958`. Original source/module/environment and referenced historical evidence hashes plus mtimes unchanged; old worktree HEAD stays `cf80f6ec07a31eccdaff264c3bce64e0511179f8`, clean.

Existing isolated Python3.10.12, Torch2.2.0+cu121 and IPEX2.2.0+cpu only. The historical publisher IPEX2.2 yanked-security warning remains disclosed; no installation, recompilation or environment modification. Bytecode writes disabled; HOME/cache/tmp redirected to independent output. CUDA_VISIBLE_DEVICES=-1, no device API; Torch CUDA initialization flag false before/after every process, lazy initialization additionally guarded. No GPU lock read or operation.

Intel i7-13700,24 logical CPUs, default affinity0-23, one NUMA node. Torch intra/inter-op and BLAS=1; OMP_THREAD_LIMIT1/8/16, dynamic=false. Author hardcoded `omp_set_num_threads(64)` unchanged; it is a requested count constrained by the actual limit, not evidence that 64 threads ran. Nine processes, including scan qualification recovery, run serially to avoid benchmark contention.

All choices frozen in preregistration before component measurements: seed42, FP32, N200000/6684932; unique sorted random valid IDs1%/10%. Counter=0 except every97th row=15. Output U is the union of visible IDs and counter15 rows, not the specified visible fraction and not natural late-training U. Observed U=4035/21867 for200k and135036/730492 for6684932. Int32 IDs for scan/deferred, int64 IDs for forwarding preserve original ABI. Exact ID union and counter increment/reset references pass for every call.

Finite optimizer fixtures200k x48 and predeclared400k x48, synthetic U=N, counter0, step10, lr.001, beta1.9, beta2.999, eps1e-15. Each measured call resets mutable arrays outside timing; forward evaluates step+1 and verifies original weight/moments remain unchanged. References use the same previously qualified FP32 equations/rounding and1e-5 max-absolute tolerance. All weights, first/second moments and forward outputs finite and max error0. Nonzero deferred counters and real late optimizer state were not qualified here.

Allocation plan allowed2GiB runtime plus20 live FP32 tensors at largest shape (~3.43GiB total), below6GiB; no6.7million x48 complete optimizer allocation. Reused arrays, three warmups, no cache flush; initialization, reset, reference evaluation and hashing excluded from timing. All raw times, exact fixture hashes and resource samples are in the JSON. A5ms parent budget guardian ran in every arm; its impact on very short calls is not separately calibrated. Seven values within one fresh process are descriptive samples, not independent-replicate significance.

## Actual component medians

| 原函数 / synthetic shape | OMP1 中位 ms | OMP8 中位 ms | OMP16 中位 ms |
|---|---:|---:|---:|
| calculate_update_ids N=200000 valid=1% | 0.090517 | 0.046221 | 0.029665 |
| calculate_update_ids N=200000 valid=10% | 0.239338 | 0.072465 | 0.049932 |
| calculate_update_ids N=6684932 valid=1% | 3.215151 | 1.192913 | 0.703853 |
| calculate_update_ids N=6684932 valid=10% | 8.477011 | 1.989878 | 1.882571 |
| update_counter N=200000 valid=1% | 0.005260 | 0.003752 | 0.004981 |
| update_counter N=200000 valid=10% | 0.007374 | 0.004585 | 0.005110 |
| update_counter N=6684932 valid=1% | 0.283709 | 0.243031 | 0.143816 |
| update_counter N=6684932 valid=10% | 0.350938 | 0.255349 | 0.171445 |
| adam_deferred_update 200000x48 U=N counter=0 | 28.092335 | 4.552133 | 5.883670 |
| adam_deferred_update 400000x48 U=N counter=0 | 56.162813 | 9.416856 | 12.412171 |
| adam_for_next_with_counter 200000x48 U=N counter=0 | 27.995451 | 4.020479 | 5.972884 |
| adam_for_next_with_counter 400000x48 U=N counter=0 | 55.965470 | 8.004318 | 12.130994 |

At fixed1% visible fraction, single-thread calculate_update_ids scales35.52x while N scales33.42x; at10% it scales35.42x. These two finite sizes are consistent with the source's global scans, not an asymptotic timing proof. SOURCE: calculate_update_ids performs three full-N passes (bitmap, reduction, collection) plus visible-ID marking and output copy, i.e. O(N+U); update_counter increments all N then resets U. Both functions remain unmodified. Per-thread reserve(total_num/5) and allocation/copy costs are included in the native call boundary; this is not a pure DRAM scan benchmark.

For200k x48 deferred update, OMP1/8/16 medians28.092/4.552/5.884ms; OMP8 is1.293x faster than16 in this fixture. Forward200k x48 is27.996/4.021/5.973ms, OMP8 is1.486x faster than16.400k results preserve this non-monotonic policy response. Scan at late-N10% is faster at16 than8 in the qualified repeat. Negative/noisy evidence is retained: preliminary update_counter late-N10% OMP8 ranged0.0641-0.2455ms(CV~0.311); qualified repeat ranges0.2551-0.2576ms(CV0.003). Increasing threads does not universally improve every component. No timing outliers were removed.

## What software evidence changes, and what remains unknown

| Factor | Supported observation / boundary | Class |
|---|---|---|
| Full-N index/count work | Original source full scans; two-size synthetic timings respond to N and visible-ID fraction | SOURCE + CPU_COMPONENT_NATIVE |
| Thread-supply policy | Original functions react to1/8/16; eight beats sixteen for these Adam fixtures | CPU_COMPONENT_NATIVE |
| Historical late CPUAdam/forward | A44 corrected calls57.746/64.779ms and41.855/45.489ms with CPU/GPU concurrency; no local replay | A44_HISTORICAL_NATIVE |
| Historical waits | A44 main-thread union14.084/14.746ms; previous30-32ms cross-thread union is not recoverable headroom | A44_HISTORICAL_NATIVE |
| Author64-thread performance | Untested; cannot extrapolate from a16-thread cap | UNKNOWN |
| Natural U, caches, NUMA/placement and full state | No saved full15k optimizer state/natural U; default hybrid-core scheduling/frequency not isolated | UNKNOWN |
| D2H, GPU critical path, PCIe and training wall | No device execution or transfers measured in this Goal | UNKNOWN |
| CLM and GS-Scale software | Already address asynchronous CPUAdam, camera reuse and parameter forwarding; must be treated as strong neighbors | SOURCE |
| Hardware mechanism novelty/speedup | Not established by synthetic CPU sensitivity | UNKNOWN |

Minimum future Strong-Software-Native proposal ONLY: separately authorize one fixed natural late-state provenance path and identical scene/schedule/precision/quality gates; contrast actual1/8/16 host policy under sequential, contention-controlled runs, keep author deferred/forward math, account preparation/reset/metadata and full uninstrumented wall plus correctly separated host-thread intervals. Record natural visible/update counts and complete live optimizer bytes. Only if an unexplained full-path residual remains should physical-resource attribution be proposed. No15k replay, GPU-only late run, CLM algorithm/batch substitution or new mechanism is started by this report.

## Resources and archive

Process-tree sampled peak RSS 1639477248 bytes (1.527GiB); child rusage peak 1622007808 bytes. Peak running threads 22 including the supervisor (transient import observed); effective original-function OMP limit<=16, peak resident threads23. Components plus imports, including recovery, took 50.055s; creation-through-final component qualification 617.707s, below1200s. Download/install=0; CUDA/GPU/lock operations=0; no training/model/profiler/simulator calls.

Measurements JSON SHA256 `c691a4f45151ca26687db3b672a64545ace78b23e3dacd677663686ccc51b846`; preregistration SHA256 `444dc83c8b9568737731e6aed8a0426890a46518cd79dd55aa7e6ae44b8e84f7`. Module/source hashes above; script hashes and raw process logs included in measurements. The final weight hash label is corrected to `weight_after_forward_reset_equals_input_sha256`: it was captured after resetting state for forward, whereas actual update max-error comparisons ran before that reset. No failed numeric result or raw timing was discarded.

Closeout before Git publication: independent full checkout+output allocated bytes 3231744 (3.082MiB), below50MiB. Elapsed through final report generation 707.670s. Only this branch is published; commit/tree and all four new blob/SHA identities are fetched back. Final ref is enclosing Git HEAD. STOP follows verified readback.

[Raw measurements and resource receipts](AI_ARCH_A45H_CPUADAM_CPUONLY_SOFTWARE_REBUTTAL_109_V1.measurements.json).
