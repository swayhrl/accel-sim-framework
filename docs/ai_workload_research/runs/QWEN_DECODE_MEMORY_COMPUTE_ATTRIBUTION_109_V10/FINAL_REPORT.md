# V10: Decode weight supply, dense paths, and resource-safe attribution

State: **symmetric single-node B1/B2 counters obtained; V9 cost ledger reconciled; local proxies and altered-eager sparse boundaries completed. Global hardware bottleneck causality remains INCONCLUSIVE.**

Fixed authority: V9 b8456ce48d8ac4939a8586bc1450239cf4d344fc, tree c8ea0c16805a0b3631bfa101ed5f79ccf9ffbd3b. V1-V9 raw/contracts/receipts remain read-only. No V9 native curve or V8 software matrix was repeated.

## A. Existing native/trace cost ledger

The V9 native curve remains the performance authority: B1 slopes10.126004/10.124480ms per extra output token, B2 10.447678ms; ratio1.0318448. V10 does not mix new profiled requests into those formal samples.

The CPU ledger reconstructs62 Decode steps and27,904 nodes from the previously retained SQLite. A step kernel hull means first-to-last collected GPU kernel, not complete generate timing or a native latency component. Mean milliseconds per step:

| Collected V9 scope | B1 A00 | B2 |
|---|---:|---:|
| Kernel hull |10.164596|10.489929|
| Kernel union |10.101019|10.454562|
| Dense union |9.527848|9.725634|
| Non-Dense union |0.573171|0.734875|
| Dense/non-Dense intersection |0|0.005947|
| Hull uncovered by kernels |0.063577|0.035367|
| All collected GPU activity union |10.132562|10.457992|

The identity is hull difference = dense + non-Dense - intersection + uncovered gap: 0.325333 =0.197786+0.161704-0.005947-0.028210ms. These are sets on one trace; compute/memory overlap is not split into additive elapsed terms. Original group sums and independent unions are both retained.

Each step has145 Dense nodes. B1 uses GEMV families; B2 uses WMMA/Tensorop GEMM and has72 extra direct_copy kernels per step. Their mean summed duration0.103146ms is already inside Non-Dense. All2232 copies are adjacent to cache-update/Flash splitKV or splitKV-combine/O-projection across36 layers. Installed source does not prove the copy tensor arguments, triggering alignment guard or exact layout conversion. It is premature to call these copies removable.

V9 Nsight Systems2024.6.2 used CUDA13-driver fallback to12.8 tracing libraries and warned that some events might be absent. Ledger coverage is complete for the collected records, not proof of perfect whole-application collection. B1 trace uses A00 only; it is not silently substituted for the native A00/A01 mean denominator.

## B. Comparable low-memory native hardware counters

The actual strong model path is unchanged: Qwen2.5-3B-Instruct fixed revision aa8e72537993ba99e69dfaafa59ed015b17504d1, BF16/TP1/no quantization, vLLM0.30.0, VLLM_COMPILE/inductor/FULL_AND_PIECEWISE, FlashAttentionImpl and UnquantizedLinearMethod, 544/1088/2, frozen A00/A01 each512 tokens, prefix cache off, logprobs=None.

NCU2025.1.1 collected two explicit metrics only: dram__bytes_read.sum and gpu__time_duration.sum. Kernel replay, Graph node, first filtered dense node in first Decode Graph, launch-count1, profile-from-start=no, clock-control=none, cache-control=none, no full set. Each mode used its own fresh serial engine with twoN32 warmups before the profiled request. Profiled generate/event time is not native formal timing.

| Observed selected node | B1 | B2 |
|---|---:|---:|
| DRAM read bytes |10,492,288|10,510,208|
| Duration ns |19,840|23,360|
| Actual replay passes |1|1|
| Grid |640,1,1|8,20,1|
| Block |16,4,1|32,1,1|
| Family |cuBLAS BF16 GEMV|CUTLASS BF16 WMMA GEMM|

B2/B1 reads=1.0017079; duration=1.1774194. The runtime module weight is[2560,2048] BF16, stride[2048,1], weight model10,485,760bytes. Cached compiled contracts, Graph descriptor token counts1/2, launch order and grid support layer0 packed-QKV correspondence. Raw kernel argument dimensions were not captured: this remains source/shape/order-consistent attribution.

NCU's actual one-pass audit and logs are preserved. The tool omits its backup-byte statistic in these one-pass reports. Its value remains null/NOT_EMITTED. Installed official guide says single-pass profiling does not perform save/restore; this documented behavior plus actual one-pass evidence is the basis for the no-backup interpretation. Missing fields were never filled with0. The explicit DRAM read0 in the small hot proxy pilot is a real returned counter, a different field.

The native B1 read count differs slightly from V9's seven-pass10,505,728bytes; neither is rewritten. V10's near-equal byte counts support weight reuse for this node, while its duration changes with the dense path. This does not causally identify SM limitations: clocks were not locked, caches were not forced, each mode has one measured node, and SM/tensor utilization was deliberately not added. Node read-bytes/time528.85/449.92GB/s is not application bandwidth.

Application replay was investigated as a fallback: file buffers, strict grid matching, per-pass initialization and actual worker identity would need explicit accounting. It was unnecessary after the one-pass scheme worked; no application replay or parallel GPU processes were used.

## C. Local compute/data-supply proxy

Eight independent synthetic BF16 F.linear configurations used QKV(K2048,N2560) and gate/up(K2048,N22016), B1/B2, one versus eight distinct weights, eight Dense operations per CUDA Graph, two warmups and five interleaved formal observations per point. The input tensor lifetime is retained for every captured graph. No bias is fused; actual kernel names were not captured for this timing matrix, so it is a dimensional proxy, not an exact native operator reproduction.

Median microseconds per Dense operation:

| Shape / Batch | HOT one weight | STREAM eight weights |
|---|---:|---:|
| QKV B1 |17.280|10.880|
| QKV B2 |11.500|18.160|
| gate/up B1 |136.320|128.256|
| gate/up B2 |137.600|137.600|

All56 warmup/formal observations and their roles are retained;40 are formal. QKV B1 STREAM contains three10.88us and twoapproximately16.99us values, despite median MAD0. These address-reuse controls do not produce a uniform monotonic cache story. No samples were filtered and no synthetic DRAM-byte estimate is substituted. The separate hot QKV pilot returned DRAM reads0 and approximately9us, showing that the same dimensional workload can have a very different measured DRAM state from the native node; it does not explain every proxy timing above.

Thus local behavior is OBSERVED; a general memory-versus-compute limit from this matrix is INCONCLUSIVE. Working-set labels do not prove L2 residency, and proxy timing does not replace vLLM performance.

## D. Independent model qualification

NOT_AVAILABLE. The bounded accepted-asset inventory contains the existing Qwen BF16 model and its AWQ variant. No independent accepted Dense decoder plus valid independent natural-input identity was available. No model/data download or broad filesystem search was performed.

## E. Sparse numerical boundaries

Six B1/B2 matched comparisons were collected in a separately labeled altered eager/NONE/NONE path at embedding, decoder0/17/35 and final norm, keeping hidden/residual distinct. Nine private tensor captures are SHA-indexed. All generated tokens match.

All selected embedding rows are bitwise equal. Layer0 returned hidden is the first differing among the sampled boundaries. Prefill A00 has1037/2048 differing elements, maxabs0.00390625; A01 has1016/2048, maxabs0.0078125. Layer0 residual is equal in those prefill pairs. N1 versus N2 same-mode prefill boundary captures are bitwise identical. N2 Decode observations use the matched preceding sampled token and retain position/request mapping evidence.

This demonstrates model-path numerical differences before logprob return in this altered path. It does not locate the earliest primitive inside layer0, prove a native compiled earliest layer, or attribute the V7 sampled-logprob discrepancy to a BF16 kernel/sampler. Full position/input tensors were not captured; row selection and consumption identity are supported by source/assertions plus returned prompt/sample IDs, with that limitation recorded. Logprobs are UNOBSERVED and no old numerical FAIL becomes PASS.

## F. Hypotheses and hardware relevance

H_MEM is MODEL_CONSISTENT at the selected node and in the inherited native slope. Whole-application measured DRAM bytes are still absent; the conditional191.313GB/31-step weight model remains a hypothesis.

H_SM remains globally INCONCLUSIVE. Batch changes actual Dense family, and a selected node takes17.7% longer for approximatelyequal measured bytes, but this is not a controlled SM-supply experiment or an application-wide result.

H_OTHER is PARTIALLY_ATTRIBUTED within the V9 collected trace: Non-Dense increases, attention-adjacent copies are real, and overlap is accounted for. Exact copy semantics/removability and native counterfactual speedup are unresolved.

| Strong-software baseline | Already present / exclusion | Remaining question |
|---|---|---|
| vLLM compiled + FULL/PIECEWISE Graph | Real accepted path; launch reduction already exploited | Control cost inside/overlapping GPU work |
| Existing Batch execution | Weight amortization already exposed | Ordinary sharing is SOFTWARE_ABSORBED, not a new hardware idea |
| cuBLAS GEMV / CUTLASS WMMA | Real B1/B2 dispatch families | Shape/layout/dispatch efficiency before hardware proposal |
| FlashAttention and cache kernels | Existing strong attention path | Identify copy arguments and software elimination feasibility |
| Prefix-cache / logprob controls | V8 authority retained, no matrix repetition | Do not confuse software state with weight bandwidth |

No global claim reaches CAUSALLY_SUPPORTED. No new microarchitecture/RTL candidate is promoted. NEXT_QUESTIONS.md records falsifiers, not an automatically started next Goal.

## Engineering, resources, and evidence limits

V10 used three serial supervision windows, all successful nonblocking acquisitions of the same flock; there were no lock conflicts, no waiting after a failed acquire, and at most one GPU owner at any time. The initially intended single window ended conservatively because one-pass CSV omitted a backup column. Its original skips remain. The second window completed B1 but stopped on WORKER_NOT_HEALTHY during normal terminal transition; its STOP receipt remains unchanged. Independent CPU review binds marker/nonce/task/supervisor/identity/source and shows no unknown PID or cap breach. The third window ran only pending B2 after a separately frozen <=6s terminal-drain phase fix, preserving every existing GPU identity, RSS/cgroup, shared-gate and deadline check.

CPU evidence includes85 regression tests,4 schema cases and9 terminal-marker cases. The schema fix leaves absent counters null; the terminal phase only stops requiring a successfully completed worker to remain healthy while its same-identity context drains. Unknown PID, PID reuse, AccessDenied, missing process identity, invalid marker, independent monitoring gaps and resource limits remain failures. No active execution source was changed in-place; all three frozen source sets and contracts are retained.

Cumulative GPU hold209.2138seconds (<1800). Observed maxima: own NVML14,888MiB (<15,400), sampled live-tree RSS4,563,410,944bytes, session charged-memory5,860,982,784bytes (<16GiB), conservative worktree disk237,958,440bytes during GPU execution (<3GiB). The cgroup kernel high-water supplements sampled live RSS; censored exited-child RSS is never fabricated as0 and no complete process-tree RSS peak is claimed.

The accepted Image-Lab resident identity, loaded gate, reservation, common lock inode and quiescence were checked again per window. Final all six actual workers are absent, no own NVML compute context remains, reservations/locks are released and Image-Lab is IDLE. Desktop per-process activity telemetry has its inherited gap; these are gated-resident shared measurements, not fully exclusive GPU results.

No model/data downloads, installs/upgrades, driver/profiler-permission changes, clocks/power changes,164, simulator orRTL. No further GPU task follows the final B2 release. All returned12 model generate calls/17 completions are independently source/hash/length checked before interpretation. Synthetic proxy calls are separately labeled and never counted as model completions.

Raw journals/resource snapshots and large CPU ledgers use exact lossless archives; authoritative NCU binaries, sparse tensors and full token arrays stay privately indexed on109. Final Git publication verifies exact commit/tree/all blobs and clean worktree. No V11 starts.
