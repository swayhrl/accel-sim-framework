# Raw Qwen2.5-7B S2 Memory Recovery V2

## Goal

Recover the ~74 MiB S2_TEXT admission shortfall while preserving the raw Qwen2.5-7B FP16/SDPA scientific identity.

Do not quantize, lower context, lower batch, disable KV cache, change attention implementation, or CPU-offload model layers as a shortcut.

## Step 0 — reproduce and measure

Run in a fresh process with no profiler/tracer loaded. Record:

- `nvidia-smi` before launch;
- Torch allocated/reserved/free memory after model load;
- after warmup;
- immediately before the failing operation;
- requested allocation size and full OOM text;
- allocator configuration;
- module loading mode.

Distinguish true capacity shortage from allocator fragmentation.

## Step 1 — allocator recovery, scientific semantics unchanged

Try exact S2_TEXT under:

```text
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

Use a fresh process. Also ensure:

```text
model.eval()
torch.inference_mode()
output_attentions=False
output_hidden_states=False
```

Before the measured/captured phase, release only unused cached blocks:

```text
gc.collect()
torch.cuda.empty_cache()
```

Do not free live model/KV tensors.

Allocator changes may alter virtual addresses but do not change model math. Absolute VA is not compared across runs.

## Step 2 — CUDA module loading

Confirm actual CUDA module loading mode. CUDA 12.x normally uses lazy loading, but record it explicitly.

If not lazy, test:

```text
CUDA_MODULE_LOADING=LAZY
```

Then warm up the exact target kernel before timing/capture so first-use module loading is outside the measured window.

Do not claim performance comparability without warmup.

## Step 3 — avoid unnecessary full-sequence logits

Inspect the installed Transformers Qwen2 forward signature.

If supported, use the official last-token-logit control:

```text
logits_to_keep=1
```

or the version-equivalent `num_logits_to_keep=1`.

This is allowed only after a validation run proves:

1. identical hidden-layer target kernel identities/shapes for the relevant Prefill targets;
2. identical next-token selection/checksum for the frozen input;
3. no change to attention/KV/model-layer execution before the LM head;
4. the formal trace scope excludes any claim that the full-vocabulary LM-head behavior is unchanged.

This optimization is particularly attractive because only the last-token logits are required for generation while full-sequence logits at long context can consume substantial temporary memory.

If the current generation path already uses one-token logits, record `NO_ADDITIONAL_SAVING` and continue.

## Step 4 — capture-process overhead reduction

The native admission process and the formal NVBit process are different memory environments.

For raw7B formal capture:

- do not co-run NSYS/NCU;
- use the V2 sharded tracer with the smallest qualified channel/buffer;
- keep only required target data structures resident;
- avoid debug tensors/logit retention;
- stream trace data rather than accumulating it on device.

These are tooling changes, not model changes.

## Step 5 — Prefill-equivalent harness, only if necessary

If the full S2 generation harness still fails but the research target is a Prefill kernel, an exact-input Prefill-only harness may be used only after equivalence is demonstrated.

Requirements:

- identical model revision, dtype, SDPA backend, batch and 2048-token frozen input;
- `use_cache=True` so normal KV construction occurs;
- target Prefill kernel function/grid/block/static-MREF identity exactly matches the full generation path on a reference deployment where both paths fit;
- target output hidden state/checksum matches at the boundary used by the target;
- evidence class is named `S2_PREFILL_EQUIVALENT_HARNESS`, not full S2 generation.

No Decode claim may be made from this harness.

## Forbidden shortcuts

Do not use as formal raw7B equivalence:

- moving one or more transformer layers to CPU;
- moving KV cache to CPU;
- reducing sequence length from 2048;
- changing batch;
- FP16 -> INT8/INT4/BF16 purely to fit;
- SDPA -> another attention backend;
- `use_cache=False`;
- dropping model blocks.

## Admission decision

Classify each attempt as:

- `RAW7B_S2_ADMITTED_EXACT`
- `RAW7B_S2_ADMITTED_ALLOCATOR_RECOVERY`
- `RAW7B_PREFILL_EQUIVALENT_HARNESS_PASS`
- `RAW7B_NOT_ADMITTED_TRUE_CAPACITY`

The first two may support full S2 formal targets. The third supports Prefill-only targets with explicit scope. The fourth is a legitimate final defer and must not block Qwen0/AWQ.
