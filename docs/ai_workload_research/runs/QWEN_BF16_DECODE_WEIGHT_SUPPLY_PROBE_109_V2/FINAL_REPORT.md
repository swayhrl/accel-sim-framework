# Qwen BF16 Decode weight supply and Batch reuse diagnostic V2

Final execution status: **GPU_RESOURCE_DEFERRED / STOP**.
Scientific result: **INCONCLUSIVE**. Worker launches=0, model initializations=0, warmups=0, formal samples=0. No delta or ratio is computed, and no hardware candidate is generated.

## Decisive actual result

The only nonblocking campaign-lock attempt succeeded. The repaired observer then completed the actual PRE_MODEL_ADMISSION snapshot before any worker/model was started. It observed:

| PID | NVML category | Reported memory bytes | Ownership classification |
|---|---|---:|---|
| 3246996 | compute | 423624704 | outside this Goal process tree |
| 1760 | graphics | 10248192 | outside this Goal process tree |
| 2035 | graphics | 6758400 | outside this Goal process tree |

All three PIDs were live and memory observations were available; unknown-PID and monitor-gap lists were empty. This is an **external-process STOP**, not a lock conflict, missing data, numeric failure, or recurrence of V1's missing-symbol exception. No desktop/graphics exemptions or other whitelist was applied. Process names, users and scientific activity were not investigated, and none of these PIDs was signaled.

Final observation again recorded external processes and no own GPU context. The supervisor released and closed the lock and shut down NVML after **0.019663329seconds of held wall time**. That is not model-compute time. No wait, lock polling or second attempt occurred. raw/ADMISSION.json preserves the exact original runtime receipt before annotations. The observation establishes only that external processes were present at those two snapshots, not who owned a lock or their state later.

## V1 authority and isolation

Fetched V1 branch hrl/aiarch-bf16-decode-weight-supply-probe-109-v1 matched commit efeb32f7e8f08b58a1518a3bef6227ad5d3f15ee and tree9886d63c04e00e7e5edcdaf0f8bfb279b6ee5abc. V2 is a separate worktree/branch descended from exactly that authority. V1 raw,receipts,contract and original failure remain unchanged; V1_AUTHORITY.json records fixed Git blobs and hashes. V1 worktree was still clean when checked.

V2 uses its own QWEN_BF16_DECODE_WEIGHT_SUPPLY_PROBE_109_V2 output, private inputs, test fixtures, logs and compilation/cache roots, plus an independent tool directory. EXECUTION_BINDING.json binds actual Goal epoch1793780461 and V2 paths; V1's hardcoded START/OUT are not executed. New compile-cache roots would be under V2 .private/PROBE; no worker was admitted and no compilation occurred. Old C16/AWMA/A79/V1 environments,caches,raw and coordination state were not modified.

## CPU requalification and full mock coverage

V1's G0 identities were reused. Only necessary current assets were requalified: all12 local model/tokenizer/license/config files still match their accepted full SHA256; A00/A01 each retain original512-token canonical identity; the historical numeric-reference SHA, installed package versions, model/compilation sources and cache-interface hashes also match. V1 did not record inode/mtime/ctime fingerprints, so a bounded full stream hash of these12 required files was used rather than guessing unchanged bytes. No project-wide historical audit, tokenizer re-selection, download or dependency installation was performed.

The complete snapshot collector,enforcement and supervisor lifecycle are shared between real execution and dependency-injected CPU tests. Final **23 tests PASS**, covering:

- None,uint64 unavailable sentinel,ctypes and valid memory; duplicate compute/graphics entries are counted once, inconsistent observations fail closed.
- Self/child ownership,external processes,invalid/nonlive PID,unknown memory and own-tree observation gaps.
- VRAM,RSS,disk and time boundaries; resource excess before launch and during a simulated live worker.
- Single lock conflict with no NVML init/child; actual-policy external/unknown rejection before spawn; API,child and final-query failures.
- Own-group termination,unlock/close/shutdown and durable error receipts, including simulated unlock or shutdown errors.
- Nonfinite failure-log persistence,installed binding symbol shape,one real lock site,lock-before-NVML ordering and timing endpoint order.

The first CPU run exposed a cleanup-status bug: final UNKNOWN observation overwrote the already-correct resource STOP. This was corrected before any real lock; the first failed log remains in raw/CPU_TEST_FIRST_FAILURE.txt. The final test log is raw/CPU_TEST_OUTPUT.txt. All successful synthetic cases live only in ignored private CPU fixtures and do not populate FORMAL_SAMPLES.tsv or count as GPU results.

## Scientific contract and engineering differences

The model remains Qwen/Qwen2.5-3B-Instruct@aa8e72537993ba99e69dfaafa59ed015b17504d1, BF16,TP1,no quantization. The intended single engine remains VLLM_COMPILE/inductor/FULL_AND_PIECEWISE,strong FlashAttention/unquantized linear,max_model_len544,max_num_batched_tokens1088,max_num_seqs2. Live engine/backend/Graph support was not exercised because resource admission stopped first.

A00/A01,P1-P6,2warmup/5formal per point,sampling,interleaved order,exact-token requirements and sampled-logprob atol0.05/rtol0.01 are identical to V1. Fullgenerate pre-sync,event-start,generate,event-stop,post-sync,elapsed timing statements and both host boundaries are unchanged. The inherited scientific-field canonical hash is8571824801bf46ae9f1c84c55470274e580fa7d8b9ff5491ded36e87172a5397.

Worker science AST comparison passes after normalizing only OUT,the persistence import and save function. Engineering changes are execution isolation,snapshot factoring,typed NVML normalization and failure-safe lifecycle/persistence. Nonfinite floats are tagged only when saving failure evidence; numeric gates still inspect original values and remain unrelaxed. ENGINEERING_CHANGELOG.json and V1_V2_COMPARISON.json provide explicit differences.

## Scientific interpretation

No truly comparable six-point results were obtained. P1-P6 medians/MAD,deltaA00,deltaA01,deltaB2 and R remain null; FORMAL_SAMPLES.tsv contains only its header. H1 weight supply and H2 compute/scheduling explanations are untested. No executed model mismatch, numeric pairing or Graph descriptor is claimed.

The inherited MODEL_AND_BANDWIDTH_BOUND.json remains a conditional structural model:6.171GB dense matrices,31 no-retention passes about191.31GB and266.90ms at nominal716.8GB/s. It is not newly measured DRAM traffic,achieved bandwidth or a bound proving this signed full-request difference. No timing is available for model comparison.

The inherited SOFTWARE_EXCLUSION.md retains NanoFlow,LLMCompass,DFloat11,ZipServ,Unweight and muShare scope checks. Ordinary batch amortization is existing software capability; this run does not establish any remaining cost or independently falsifiable hardware variable. Successful resource observation alone cannot promote hardware research.

## Resource scope and termination

Real GPU observation contains two snapshots with no observation gaps and own NVML use0MiB. Sampled supervisor-tree RSS peaked37,785,600bytes; CPU asset revalidation separately peaked36,343,808bytes at1-second sampling. Entire Goal metadata preparation,tests and Git publication were not continuously RSS-sampled, so no whole-Goal measured-peak claim is made. New disk snapshots,private logs and Git publication scope are recorded in receipts.

Model/data downloads,dependency installation/upgrades,164 access,Profiler/NCU/NSYS/NVBit,simulator/RTL and other-process interference are0. One GPU owner path was prepared; no GPU worker launched.

V1's engineering failure was repaired and the real observer operated successfully. V2 legitimately stopped on external GPU processes under the unchanged resource rule. This says nothing about whether the six-point scientific hypothesis is true. Any future attempt requires a new explicit bounded resource authorization; no background waiting,retry,batch extension,compression idea,Profiler or other Goal follows publication.
