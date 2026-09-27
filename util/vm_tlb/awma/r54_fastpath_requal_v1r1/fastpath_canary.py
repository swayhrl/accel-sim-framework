from __future__ import annotations

import csv
import fcntl
import hashlib
import json
import os
import sys
import traceback
from pathlib import Path

ROOT = Path('/data/c16/awma/r54_fastpath_requal_v1r1_20260927')
MODEL = Path('/data/c16/awma/r54_checkpoint_lifecycle_20260927/model/Qwen3_5_0_8B_c6046cd1')
LOCK = Path('/data/c16/locks/c16_gpu_campaign.lock')
TEXT = 'Exact recurrent checkpoint qualification uses a bounded text-only prefix fixture. ' * 8


def sha_tensor(tensor):
    import torch
    raw = tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()
    return hashlib.sha256(raw).hexdigest()


def describe_runtime(model):
    import transformers.models.qwen3_5.modeling_qwen3_5 as mq
    names = [
        'causal_conv1d_fn',
        'causal_conv1d_update',
        'torch_chunk_gated_delta_rule',
        'torch_recurrent_gated_delta_rule',
    ]
    functions = {}
    for name in names:
        obj = getattr(mq, name)
        functions[name] = {
            'repr': repr(obj),
            'module': getattr(obj, '__module__', ''),
            'qualname': getattr(obj, '__qualname__', ''),
            'wrapped_repr': repr(getattr(obj, '__wrapped__', None)),
        }
    layers = []
    for name, module in model.named_modules():
        if module.__class__.__name__ == 'Qwen3_5GatedDeltaNet':
            layers.append({
                'name': name,
                'class': f'{module.__class__.__module__}.{module.__class__.__qualname__}',
                'kernel_attrs': {k: repr(v) for k, v in module.__dict__.items() if 'kernel' in k.lower()},
            })
    return {'model_use_kernels': bool(getattr(model, '_use_kernels', False)), 'functions': functions, 'gdn_layers': layers}


def run_arm(label, use_kernels, input_ids, tokenizer):
    import torch
    from transformers import KernelConfig, Qwen3_5ForConditionalGeneration

    torch.cuda.empty_cache()
    kernel_config = None
    if use_kernels:
        kernel_config = KernelConfig(
            kernel_mapping={
                'causal_conv1d_fn': (
                    'kernels-community/mamba-ssm:causal_conv1d_fn',
                    {'revision': '20b2508ad12ae40260291539bf45183000451850'},
                ),
                'causal_conv1d_update': (
                    'kernels-community/mamba-ssm:causal_conv1d_update',
                    {'revision': '20b2508ad12ae40260291539bf45183000451850'},
                ),
                'chunk_gated_delta_rule': (
                    'kernels-community/fla:chunk_gated_delta_rule',
                    {'revision': '6d22ed1d2bb627375b6ca8fc135f7f417863e639'},
                ),
                'fused_recurrent_gated_delta_rule': (
                    'kernels-community/fla:recurrent_gated_delta_rule',
                    {'revision': '6d22ed1d2bb627375b6ca8fc135f7f417863e639'},
                ),
            },
            inherit_mapping=False,
        )
    model = Qwen3_5ForConditionalGeneration.from_pretrained(
        MODEL,
        local_files_only=True,
        dtype=torch.bfloat16,
        device_map={'': 'cuda:0'},
        use_kernels=use_kernels,
        kernel_config=kernel_config,
    ).eval()
    runtime = describe_runtime(model)
    ids = input_ids.to('cuda:0')
    tokens = []
    step_top8 = []
    step_top2 = []
    logits0 = None
    cache_type = None
    cache_len = None
    with torch.inference_mode():
        torch.cuda.nvtx.range_push(f'R54_V1R1_{label}=PREFILL64')
        out = model(input_ids=ids, use_cache=True, return_dict=True)
        torch.cuda.nvtx.range_pop()
        torch.cuda.synchronize()
        cache = out.past_key_values
        logits = out.logits[:, -1, :].detach()
        logits0 = logits.cpu()
        cache_type = type(cache).__name__
        cache_len = len(cache) if cache is not None else 0
        for step in range(16):
            top = torch.topk(logits, 8, dim=-1).indices[0].cpu().tolist()
            step_top8.append(top)
            step_top2.append(top[:2])
            next_id = int(top[0])
            tokens.append(next_id)
            if step != 15:
                one = torch.tensor([[next_id]], dtype=torch.long, device='cuda:0')
                torch.cuda.nvtx.range_push(f'R54_V1R1_{label}=DECODE_STEP_{step + 1:02d}')
                out = model(input_ids=one, past_key_values=cache, use_cache=True, return_dict=True)
                torch.cuda.nvtx.range_pop()
                torch.cuda.synchronize()
                cache = out.past_key_values
                logits = out.logits[:, -1, :].detach()
    result = {
        'label': label,
        'use_kernels_requested': use_kernels,
        'runtime': runtime,
        'input_shape': list(input_ids.shape),
        'initial_logits_shape': list(logits0.shape),
        'initial_logits_dtype': str(logits0.dtype),
        'initial_logits_finite': bool(torch.isfinite(logits0).all()),
        'initial_logits_sha256': sha_tensor(logits0),
        'initial_argmax': tokens[0],
        'initial_top8': step_top8[0],
        'initial_top2': step_top2[0],
        'continuation_token_ids': tokens,
        'continuation_text': tokenizer.decode(tokens),
        'step_top8': step_top8,
        'step_top2': step_top2,
        'cache_type': cache_type,
        'cache_len': cache_len,
    }
    del out, cache, logits, model
    torch.cuda.empty_cache()
    return result, logits0


def main():
    import torch
    import transformers
    import kernels
    from transformers import AutoTokenizer

    ROOT.joinpath('raw/fastpath').mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    input_ids = tokenizer(TEXT, return_tensors='pt', add_special_tokens=False)['input_ids'][:, :64].contiguous()
    input_sha = sha_tensor(input_ids)
    receipt = {
        'stage': 'AWMA_R54_FASTPATH_REQUALIFICATION_V1R1',
        'status': 'RUNNING',
        'model': 'Qwen/Qwen3.5-0.8B',
        'model_revision': 'c6046cd1f7e2763bf1abf5a5aef6ad7878e10ccb',
        'model_weight_sha256': '04b1c301231dd422b8860db31311ab2721511346a32cb1e079c4c4e5f1fe4696',
        'input_text': TEXT,
        'input_token_sha256': input_sha,
        'input_token_ids': input_ids[0].tolist(),
        'torch': torch.__version__,
        'torch_cuda': torch.version.cuda,
        'transformers': transformers.__version__,
        'kernels': kernels.__version__,
        'gpu': torch.cuda.get_device_name(0),
        'compute_capability': list(torch.cuda.get_device_capability(0)),
        'arms': {},
    }
    lock = LOCK.open('a+')
    fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        fallback, fallback_logits = run_arm('FALLBACK', False, input_ids, tokenizer)
        receipt['arms']['fallback'] = fallback
        hub, hub_logits = run_arm('HUB', True, input_ids, tokenizer)
        receipt['arms']['hub'] = hub
        diff = (fallback_logits.float() - hub_logits.float()).abs()
        exact_shape = fallback_logits.shape == hub_logits.shape
        exact_dtype = fallback_logits.dtype == hub_logits.dtype
        exact_argmax = fallback['initial_argmax'] == hub['initial_argmax']
        exact_top8_set = set(fallback['initial_top8']) == set(hub['initial_top8'])
        exact_top2_order = fallback['initial_top2'] == hub['initial_top2']
        exact_continuation = fallback['continuation_token_ids'] == hub['continuation_token_ids']
        hub_selected = bool(hub['runtime']['model_use_kernels'])
        semantics = {
            'exact_shape': exact_shape,
            'exact_dtype': exact_dtype,
            'both_finite': fallback['initial_logits_finite'] and hub['initial_logits_finite'],
            'exact_argmax': exact_argmax,
            'exact_top8_set': exact_top8_set,
            'exact_top1_top2_ordering': exact_top2_order,
            'exact_16_token_continuation': exact_continuation,
            'differing_element_count': int(torch.count_nonzero(fallback_logits != hub_logits)),
            'max_abs': float(diff.max()),
            'mean_abs': float(diff.mean()),
            'fallback_output_sha256': fallback['initial_logits_sha256'],
            'hub_output_sha256': hub['initial_logits_sha256'],
        }
        receipt['semantic_equivalence'] = semantics
        receipt['hub_runtime_selected'] = hub_selected
        semantic_pass = all(semantics[k] for k in [
            'exact_shape', 'exact_dtype', 'both_finite', 'exact_argmax', 'exact_top8_set',
            'exact_top1_top2_ordering', 'exact_16_token_continuation'])
        receipt['semantic_gate_pass'] = semantic_pass
        receipt['status'] = 'CANARY_COMPLETE'
    except Exception as exc:
        receipt['status'] = 'CANARY_FAILED'
        receipt['error'] = repr(exc)
        receipt['traceback'] = traceback.format_exc()
        raise
    finally:
        ROOT.joinpath('receipts/R54_V1R1_FASTPATH_RECEIPT.json').write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + '\n'
        )
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()

    row = dict(receipt['semantic_equivalence'])
    row['semantic_gate_pass'] = receipt['semantic_gate_pass']
    with ROOT.joinpath('receipts/R54_V1R1_SEMANTIC_EQUIVALENCE.tsv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(row), delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerow(row)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
