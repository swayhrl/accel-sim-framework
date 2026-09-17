# GPU queue addendum for node109 V29

This addendum supersedes any interpretation that a busy C16 GPU campaign lock is a scientific blocker.

The node109 RTX4080 is currently allowed to be occupied by another accepted C16 Goal (for example DeepSeek V27). V29 may be started in a separate Codex window while that Goal is running, but it MUST behave as a queued campaign.

## Queue semantics

Before any CUDA execution, profiler launch, native MXFP4 model load onto GPU, heavy runtime validation that allocates GPU memory, formal capture, or Pipeline admission:

1. inspect `/data/c16/locks/c16_gpu_campaign.lock` and `nvidia-smi`;
2. if the campaign lock is held by another legitimate C16 Goal, classify local state as `WAITING_FOR_C16_GPU_CAMPAIGN_LOCK`, not as a blocker;
3. do not kill, preempt, bypass, replace, or steal the lock;
4. do not start any CUDA/profiler/model process while waiting;
5. wait/poll non-busily until the existing owner releases the lock;
6. after the lock becomes available, acquire it normally and then re-check `nvidia-smi`, stale profiler processes, and GPU baseline before continuing automatically.

A held lock must NOT cause V29 to emit a final BLOCKED decision or terminate the Goal.

## What is allowed while waiting

Only lightweight, non-interfering preparation is allowed before V29 owns the GPU lock:

- fetch/verify coordination and implementation branches;
- create a fresh isolated Git worktree;
- read V28 review/producer authority;
- verify node164 canonical asset receipts/manifests read-only;
- inspect existing local runtime/tool files without running CUDA;
- prepare scripts/configuration/review-pack skeletons;
- resolve exact non-GPU provenance information.

## What must wait for lock ownership

Defer all heavy/shared-resource work until V29 owns the GPU lock:

- any CUDA import/probe that initializes a context when avoidable;
- native MXFP4 model execution or capacity test;
- Nsight/NVBit profiling;
- formal trace capture;
- Pipeline formal admission;
- large model transfer/copy from node164 to node109 unless the exact required subset is already present and verification is lightweight;
- large runtime provisioning/build that could materially interfere with the active producer campaign.

The intent is queueing convenience, not resource overlap.

## Formal admission serialization

`FORMAL_ADMISSION_CONCURRENCY=1` remains mandatory.

V29 must not begin formal admission while another C16 formal admission is in flight. Because the preceding producer Goal is expected to hold the campaign lock through its scientific closure, normal queue order should serialize this automatically; nevertheless, re-check before V29 admission.

## Worktree isolation

Use a fresh V29 worktree/branch. Do not modify or checkout the active V27 worktree, active producer output roots, fixed shared temporary paths, or its review pack.

## Automatic continuation

Once the prior campaign releases the GPU lock and V29 successfully acquires it, continue the full V29 Goal automatically:

`GPU baseline check -> native MXFP4 runtime/capacity precheck -> Harmony S2 freeze -> natural routing -> target qualification -> formal capture -> serial admission/ACK -> review pack -> Git closure -> cleanup -> STOP`

Do not ask the user to return merely to say that the lock became free.
