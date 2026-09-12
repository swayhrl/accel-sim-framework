# C16 Resident-Model Execution Mode

## Purpose

Reduce paid-GPU idle/setup time by loading one deployment exactly once and executing multiple frozen scenarios in the same CUDA/Python process. This is an engineering optimization, not a change to model, inference semantics, precision, backend, or scenario definitions.

Do not replace the currently qualified standalone runner until the equivalence gate below passes.

## Scientific invariant

Resident mode may change only model lifetime. It must not change:

- model/tokenizer revision or local checkpoint bytes;
- frozen input-token receipts;
- scenario batch/context/decode definitions;
- dtype / quantization / attention backend / compile state;
- prefill/decode implementation semantics;
- prefix caching, speculative decoding, continuous batching, TP/PP/EP settings;
- measurement warmup/repeat policy;
- execution-budget accounting.

The resident implementation must reuse the currently validated prefill/decode execution primitive. Do not combine resident-mode work with any rewrite of decode/KV semantics.

## Architecture

Add a separate resident entry point (or an explicit `--resident-plan` mode) rather than silently changing `run_model.py` behavior.

Lifecycle:

1. Validate exact package/model/runtime identity.
2. Acquire/validate the shared execution-budget parent lease.
3. Import runtime and load model once onto the GPU.
4. Record `MODEL_RESIDENCY_RECEIPT.json`: model identity, GPU UUID, code commit, parameter device closure, dtype/backend/quantization, model-only allocated/reserved memory after load.
5. Execute a frozen ordered scenario plan. Each plan row references an immutable scenario and token receipt by exact hash; no raw text retokenization is allowed.
6. Before each scenario:
   - reconstruct the scenario input tensor from its frozen token IDs;
   - reset RNG seeds as applicable;
   - assert there is no retained scenario-specific KV/cache object from the previous scenario;
   - synchronize outside the measured region;
   - record pre-scenario allocated/reserved memory;
   - reset peak-memory statistics;
   - optionally release only unreferenced allocator cache outside measurement (`gc.collect`; `torch.cuda.empty_cache`) if and only if the standalone-vs-resident qualification uses the same reset policy.
7. Run the existing 2 warmups + 3 measured repetitions (bounded to 5 for frozen noise policy). Every scenario gets a separate immutable run UUID and receipt even though the model process is shared.
8. After each scenario:
   - delete input/output/past-KV references owned by the scenario;
   - synchronize outside measurement;
   - collect Python garbage;
   - verify `torch.cuda.memory_allocated()` returns to the qualified model-resident envelope. Cached *reserved* bytes may differ and must be reported rather than mistaken for live KV state.
   - if live allocated bytes remain materially above the model-resident envelope without an explained runtime-global cache, fail resident isolation and stop; do not continue contaminating later scenarios.
9. Keep the model loaded and execute the next frozen scenario.
10. At session end, write a session receipt containing exact scenario order, all run IDs, start/end GPU telemetry, total model-load time, total scenario time, idle/setup time saved, and any reset/isolation findings.

## Measurement ranges

Use nested NVTX names that make scenario boundaries auditable, for example:

- `C16_RESIDENT_SESSION::<deployment_id>`
- `C16_SCENARIO::<scenario_id>::WARMUP::<n>`
- `C16_SCENARIO::<scenario_id>::MEASURE::<n>`
- existing validated phase ranges inside those scenario ranges (e.g. prefill/decode)

Do not include model load, inter-scenario cleanup, export, transfer, or hash work inside scenario measurement ranges.

## Execution-budget rule

One resident session may hold one validated parent operation lease, but every scenario still needs an individual accounting receipt with elapsed GPU operation time and run identity. A standalone invocation without a valid parent lease must continue to acquire its own lease or fail closed. Resident mode must not create a budget bypass.

## Qualification experiment (required before GO)

Use Llama3.2-1B first. Do not use holdout/candidate outcomes to tune the gate.

### Q0 — standalone reference

Run frozen S2 with the currently qualified standalone path:

- same package and code commit;
- same token receipt;
- same dtype/backend/compile state;
- 2 warmups + 3 measures;
- capture output checksum, timing samples, peak allocated/reserved memory;
- one lightweight nsys census if G1 is available.

### Q1 — resident first-scenario

Start a fresh resident process, load the same model once, and run S2 as the first scenario using the exact same reset and measurement policy.

### Q2 — resident after another scenario

Start a fresh resident process, run S1 first, perform the qualified cleanup/isolation boundary, then run S2. Q2 tests the actual contamination risk.

## GO gate

Resident mode may be promoted only if all of the following pass:

1. Exact scientific identity:
   - checkpoint / revision / token receipt / dtype / quantization / backend / compile state / GPU UUID match the intended comparison.
2. Output equivalence:
   - S2 output checksum is identical for standalone, Q1, and Q2.
3. Isolation:
   - no scenario-specific KV/past-cache object from S1 is live when S2 begins;
   - post-cleanup live allocated memory returns to the qualified model-resident envelope, or any persistent runtime-global allocation is separately identified and shown not to contain scenario data.
4. Kernel-structure equivalence after warmup:
   - measured S2 uses the same implementation/backend and the same expected kernel/correlation structure; unexplained kernel-path changes are a FAIL, not a timing optimization.
5. Timing consistency:
   - compare medians and retained samples against observed standalone noise. The engineering screen is `abs(resident_median/standalone_median - 1) <= max(0.03, 2 * standalone_CV, 2 * resident_CV)`.
   - This screen is only a qualification guard; it is not a claim of statistical equivalence or performance speedup.
6. Peak-memory semantics:
   - compare peak *allocated* bytes relative to each scenario's pre-scenario live allocation baseline. Reserved allocator bytes may differ and must be reported separately.
7. No hidden reuse:
   - prefix caching remains disabled;
   - no KV/past state, generated tokens, prompt tensors, or scenario-local object maps are reused across scenarios.

If any item fails, keep standalone mode as the scientific path and record resident mode `NO_GO_WITH_EVIDENCE`.

## After GO

Use resident sessions per deployment, not across different models:

- one Llama session may run S1/S2/S3/S4 in the frozen order;
- one Qwen0.5 session may run its frozen admitted scenarios;
- raw Qwen7 and AWQ are separate deployments and require separate model loads/sessions;
- never keep two scientific models concurrently resident merely to increase utilization.

Formal nsys/NCU/NVBit capture can use resident mode only after each tool-specific wrapper is shown to preserve exact scenario targeting inside the resident process. Until then, it is acceptable to use resident mode for unprofiled native baselines while keeping profiler/capture runs standalone.

## Efficiency accounting

Record separately:

- cold model load time;
- resident session setup time;
- scenario warmup time;
- measured scenario time;
- inter-scenario cleanup time;
- avoided repeated model-load time;
- total paid instance wall-time saved estimate.

The expected benefit is reduced paid setup/idle wall time, not higher within-kernel GPU utilization.
