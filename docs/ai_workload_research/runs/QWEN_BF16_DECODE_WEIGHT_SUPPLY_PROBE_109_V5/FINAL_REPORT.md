# Qwen BF16 Decode weight supply and Batch reuse V5

Final execution status: **NUMERIC_OR_RUNTIME_NO_GO**.
Scientific performance conclusion: **INCONCLUSIVE**.

V5 accepted the independently reviewed shared-resident resource contract, acquired the common lock once, initialized one real strong compiled BF16 engine, and issued five requests from the first planned warmup round. P3 failed the frozen B1/B2 sampled-logprob gate. Formal samples=0; all requested medians/MAD and deltaA00,deltaA01,deltaB2,R remain null. No further GPU run or hardware candidate follows.

## Decisive numerical evidence

The first warmup order remained P1,P4,P2,P5,P3,P6. P1,P4,P2,P5 completed their gates; P3 stopped on its first completion, A00:

| Comparison | Value |
|---|---:|
| P1 B1 A00 selected first-token logprob | -0.9105782508850098 |
| P3 B2 A00 selected first-token logprob | -1.0132758617401123 |
| Absolute difference | 0.10269761085510254 |
| Frozen allowance:0.05+0.01*abs(P1 reference) | 0.0591057825088501 |
| Excess over allowance | 0.04359182834625244 |

The token identity was exact and the preserved returned logprobs were finite. Independent CPU recomputation from the original private output arrays reproduces the failure and public output hashes. No tolerance,precision,input,backend or sample order was changed. P4 A00 output32 independently matches the historical32-token reference exactly,including sampled logprobs (maximum difference0).

P3 returned two completions,but the worker raised during the first A00 numeric check before persisting the second A01 completion. That second completion is unavailable;it was neither reconstructed from B1 nor regenerated. P3's final per-request compiled/Graph counter snapshot was also not reached. PRIVATE_RAW_INDEX.json and NUMERIC_AND_IDENTITY.json disclose these limitations.

WARMUP_SAMPLES.tsv preserves all five actual request measurements and captured output identities. FORMAL_SAMPLES.tsv has only its header. Warmup times include first-use effects and are not used to calculate the requested performance contrasts. P6 and every formal round remained unexecuted.

## Independent Image-Lab resource review

The reviewed production build is761ab4f22690f6305b7f903e15a99cc685382a1b;the exact private audit commit is4bcee3fe8d0f82a891d67818cd02d8c580dbe6fb. The audit tree and individual blob identities are recorded in IMAGE_LAB_RESOURCE_REVIEW.json. Twenty audit payloads match both SHA256SUMS and their committed Git bytes. The canonical LIVE_RECEIPT SHA256 is a93bc74d3f68a328cf6a7099b256db6a95c834a739ebb7e3e8f41b50469e1e5d.

The review rehashed972 deployed source files and all16 entry bindings,including the fixed external orchestrators. Eighteen live loaded-function hashes and691 loaded-module hashes matched the acceptance witness. A randomized challenge returned from the actual process with Cache-Control:no-store. PID3518111,UID1004,start_ticks442348560,boot ID,actual executable,build and run nonce matched independent /proc observations. The active0600 profile hash matched the accepted witness.

All16 paths have reviewed gate or disabled-profile coverage:startup/plugin initialization;queue/worker lifecycle;custom prompt validators;model/cache cleanup;metrics CUDA calls;ordinary queued generation/video/restoration;orchestrators;TTS child execution;H3/Writer routes;Ollama translation;daemon/standalone entrypoints;HTTP/schema caching;maintenance;unknown code/producer rejection;dynamic VRAM/offload/compiler fences;and the authorized canary. This is source/deployed/runtime binding coverage,not a claim that16 GPU workflows were rerun.

Two original GPU histories independently show parent/child CUDA results512,child synchronization and drain,plus the expected exception after child drain. Real external-lock evidence preserves pending1/running0,inflight0,unchanged completed scopes and blocked-attempt growth4to9;reverse EX denial was recorded. The /free empty-body harness interruption was preserved and supplemented without repeating CUDA matrix tasks. GPU sync-failure RECOVERY remains supported by CPU fault injection;no deliberate driver fault was introduced.

This approval is scoped to the reviewed cooperative restricted-v2 deployment. It is not an OS sandbox against malicious same-UID CUDA commands. Image-Lab's original candidate/strict_live_admission flags and old receipts were not rewritten.

## Explicit V5 resource policy and actual interval

V5 explicitly adds **VERIFIED_GATED_RESIDENT_CONTEXT**. ComfyUI may retain CUDA memory while the reviewed loaded gate prevents GPU execution. It is not treated as a desktop process or admitted solely by PID,empty queue,low VRAM or an IDLE file.

A credential-authenticated reservation bound the actual supervisor PID,UID,start ticks,boot and executable. It paused new Image-Lab execution while preserving queued work;the response explicitly granted no ownership. The sole nonblocking common flock attempt then acquired /data/c16/locks/c16_gpu_campaign.lock. Both sides' live inode remained dev66306/inode8269816,and actual kernel holders matched the reservation claimant.

Three pre-model activity samples completed in1.5433seconds with GPU utilization0%,0%,0%. Unknown/ordinary external compute remained forbidden and combined external memory stayed below512MiB. Every runtime snapshot revalidated the resident incarnation,nonce,loaded code,live profile monitor,actual lock holder,claimant reservation,quiescence and child drain.

Thirty-five snapshots record Image-Lab completed scopes fixed at9 and inflight fixed at0. No Image-Lab GPU task or additional canary was triggered by AI-ARCH. Only this Goal's reservation POST/DELETE was used;no queue,maintenance,recovery or process-control action was issued.

The execution condition is **VERIFIED_GATED_RESIDENT_CO_RESIDENT_NATIVE_OBSERVATION**. Per-process desktop utilization telemetry had an observation gap,which was explicitly pre-frozen as a reason to retain INCONCLUSIVE performance interpretation. Basic PID/memory observation or Image-Lab gate/lock/code/quiescence failures remain immediate STOP conditions. Low MAD would not establish freedom from interference.

## Actual engine identity and science contract

Scientific-field SHA is unchanged:
8571824801bf46ae9f1c84c55470274e580fa7d8b9ff5491ded36e87172a5397.

Actual runtime reported vLLM0.30.0,torch2.13.0+cu130,BF16,TP1,no quantization,capacity544/1088/2,VLLM_COMPILE/inductor/FULL_AND_PIECEWISE,FlashAttentionImpl and UnquantizedLinearMethod. Required source hashes matched A79/V4. All cache roots were V5-private and the new compilation identity is recorded explicitly. Initialization/compilation/capture took61.7314seconds,inside the GPU budget.

The compiled Qwen2Model was observed active for P1,P4,P2,P5. P4 and P5 each recorded31 full Graph replays. Single-output prefill requests need not have full Graph replay. The early P3 numeric failure prevented its final Graph snapshot,so no complete B2 Graph qualification is claimed.

A00/A01 remain the accepted natural512-token IDs. Original sampling,interleaved order,maximum2warmup/5formal per point,numeric thresholds and fullgenerate CUDA-event/host timing boundaries are unchanged. Twelve required assets retained their V2/V4-qualified inode,size,mtime,ctime fingerprints;no new full-model streaming hash or data download was performed. Current source/package/cache interfaces and reference/input digests were checked.

The engine log includes a skip_tokenizer_init chat-template warmup warning and first-use sampler JIT warnings. Generation used the frozen token-ID requests. The numerical STOP is independently reproduced from the captured P1/P3 logprobs;the warnings are not assigned as its cause.

## Cleanup,resources and engineering provenance

The lock was held69.9185seconds. Sampled own NVML peak was14314MiB;tree RSS peak2,984,415,232bytes;new disk sample peak151,237,415bytes. All observed values were within the unchanged1500second GPU,3600second Goal,15400MiB own VRAM,16GiB RSS and3GiB new-disk caps. These are sampled GPU-phase peaks;whole-Goal continuous RSS/disk high-water was not measured.

The worker exited with its numeric STOP. Own GPU contexts cleared,the common lock released,and this Goal's reservation was removed. Post-release live status returned Image-Lab IDLE,inflight0,completed scopes9,queue[0,0],no reservation or kernel holder,and only its original resident compute process. No other process was signaled.

Forty-four CPU tests passed before GPU admission. Post-STOP review found a monitoring exception-selection defect:a persistent earlier attribution-gap flag could mask a later explicit high-activity MonitorStop. A CPU-only repair now catches only the specific missing-attribution error. The executed original source is preserved at raw/EXECUTED_SUPERVISOR.py.txt and matches the frozen pre-GPU SHA;the final corrected source has a separate hash. Forty-seven final CPU tests pass,including three targeted regressions. No GPU revalidation was performed. Actual desktop per-process activity records were unavailable,so this run cannot resolve that interference dimension.

The numerical capture gap was preserved,not repaired by another experiment. Worker source and numerical conditions for the executed run remain unchanged. All post-STOP actions are CPU analysis,documentation,validation and publication.

## Scientific decision and V1-V5 distinction

V1 stopped on a pre-model NVML binding defect. V2 stopped on its strict external-process rule. V3 and V4 stopped on the ungated ordinary Image-Lab compute context. V5 achieved the reviewed shared-context admission and actual model execution,then failed numerical pairing. The earlier resource STOPs are not performance negatives.

H1 weight streaming and H2 compute/scheduling still have no qualified six-point timing contrast. H3 now has an observed numerical qualification failure under the requested one-engine batch comparison;its underlying kernel/rounding cause is not identified. Matching tokens alone does not satisfy the frozen logprob contract. This run does not classify model quality or assign a software defect.

The inherited conditional dense-weight model and strong-software exclusion table remain applicable only within their stated assumptions. Estimated bytes are not measured DRAM traffic. Ordinary batch weight sharing is existing software capability,and no specific remaining hardware cost was established. No hardware candidate or new GPU task is generated.

Private output arrays remain local with hashes and the capture limitation indexed. Public artifacts contain anonymous hashes,numeric diagnostics and resource evidence,not generated text or prompt arrays. V1-V4 and Image-Lab production source/receipts/caches remain unchanged. No model/data download,dependency upgrade,164 access,Profiler/NCU/NSYS/NVBit,simulator or RTL was used. After exact Git publication/readback this Goal STOPs.
