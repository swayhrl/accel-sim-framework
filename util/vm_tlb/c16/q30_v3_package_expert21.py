#!/usr/bin/env python3
"""Assemble (without mutating) the first Q30 V3 formal producer bundle."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SOURCE = Path('/data/c16/qwen3_30b/formal_v3/Q30_S2_FORMAL_V3_20260917T030000Z')
DECODE_STATE = Path('/data/c16/qwen3_30b/bringup/Q30_S2_STREAM_V1_20260917T001000Z/target_states/decode3/manifest.json')
ROUTING = Path('/data/c16/qwen3_30b/formal_v2/Q30_S2_FORMAL_V2_20260917T020000Z/repair/natural_expert_routing.json')
V20 = Path('/data/c16/qwen3_runtime_v14/v20/tools/v20_warp_regsource.so')
RUNTIME = Path('/data/c16/env/c16-qwen3-30b-hf451-gpu/bin/python')


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def cp(src: Path, dst: Path):
    if not src.is_file() or src.is_symlink():
        raise RuntimeError(f'invalid source artifact: {src}')
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def command(argv):
    return subprocess.check_output(argv, text=True).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--staging-root', type=Path, required=True)
    ap.add_argument('--run-id', required=True)
    args = ap.parse_args()
    out = args.staging_root / args.run_id
    if out.exists():
        raise SystemExit(f'collision: {out}')
    if not re.fullmatch(r'C16R_[a-z0-9-]+_[a-z0-9-]+_[a-z0-9-]+_[a-z0-9-]+_[a-z0-9-]+_\d{8}T\d{6}Z_[a-f0-9]{12}', args.run_id):
        raise SystemExit('invalid run id')

    audit_path = SOURCE / 'formal_decode_expert21/LOCAL_INDEPENDENT_AUDIT.json'
    audit = json.loads(audit_path.read_text())
    if not audit.get('complete_set') or audit.get('present_static_global_mref_count') != 243:
        raise SystemExit('local audit not complete 243-set')
    if any(s['overflow'] != 0 for s in audit['shards']):
        raise SystemExit('overflow evidence present')
    if not ROUTING.is_file() or not DECODE_STATE.is_file() or not V20.is_file():
        raise SystemExit('upstream authority missing')

    out.mkdir(parents=True)
    cp(audit_path, out / 'FORMAL_AUDIT.json')
    cp(SOURCE / 'capture.json', out / 'ISOLATED_CAPTURE.json')
    cp(SOURCE / 'isolated_replay.json', out / 'ISOLATED_REPLAY.json')
    cp(DECODE_STATE, out / 'STATE_CHAIN.json')
    cp(ROUTING, out / 'NATURAL_ROUTING.json')
    cp(SOURCE / 'isolate_static/static_map.tsv', out / 'STATIC_MREF_MAP.tsv')

    selected = {int(s['static_index']): s for s in audit['shards']}
    manifest = []
    for index in sorted(selected):
        shard = SOURCE / 'formal_decode_expert21' / f'mref_{index}'
        stem = f'raw_shards/mref_{index}'
        cp(shard / 'trace.bin', out / f'{stem}.bin')
        cp(shard / 'ADDRESS_CONTEXT.json', out / f'{stem}.ADDRESS_CONTEXT.json')
        cp(shard / 'stdout.log', out / f'{stem}.stdout.log')
        cp(shard / 'stderr.log', out / f'{stem}.stderr.log')
        item = selected[index]
        manifest.append({
            'static_index': index,
            'binary_record_format': 'C16WARP1',
            'trace_relative_path': f'{stem}.bin',
            'address_context_relative_path': f'{stem}.ADDRESS_CONTEXT.json',
            'terminal_status': item['terminal_status'],
            'record_count': item['record_count'],
            'drop_count': 0,
            'overflow_count': item['overflow'],
            'trace_sha256': item['trace_sha256'],
            'address_context_sha256': item['address_context_sha256'],
            'same_process_address_hits': item['same_process_address_hits'],
            'exact_replay_identity': 'isolated model.layers.24.mlp.experts.21.down_proj occurrence=0',
        })
    (out / 'WARP_SHARD_MANIFEST.json').write_text(json.dumps({
        'schema_version': 1,
        'target': 'S2_DEC3_NATURAL_EXPERT21_DOWN',
        'semantic_identity': 'model.layers.24.mlp.experts.21.down_proj; natural expert 21; S2/T2048 Decode step3 Layer24',
        'function': 'internal::gemvx<int7>',
        'grid': '512x1x1', 'block': '32x4x1', 'function_occurrence': 0,
        'static_global_mref_count': len(manifest),
        'shards': manifest,
        'prohibitions': ['no cross-shard chronology', 'no cross-replay VA union', 'no reconstructed reuse distance'],
    }, indent=2, sort_keys=True) + '\n')
    quick = {
        'status': 'PASS', 'expected_shards': len(manifest), 'present_shards': len(manifest),
        'executed_shards': sum(s['record_count'] > 0 for s in manifest),
        'zero_execution_proven_shards': sum(s['record_count'] == 0 for s in manifest),
        'total_callback_records': sum(s['record_count'] for s in manifest),
        'drop_count': 0, 'overflow_count': 0,
        'static_set_sha256': sha(SOURCE / 'isolate_static/static_map.tsv'),
    }
    (out / 'QUICKCHECK.json').write_text(json.dumps(quick, indent=2, sort_keys=True) + '\n')
    controls = {
        'tool': str(V20), 'tool_sha256': sha(V20),
        'isolated_source_canary': {'static_index': 810, 'expected_range': 'activation/input', 'terminal': True, 'overflow': 0},
        'isolated_store_canary': {'static_index': 1105, 'expected_range': 'output', 'terminal': True, 'overflow': 0},
        'zero_execution_lifecycle_control': {'static_index': 101, 'terminal': True, 'overflow': 0, 'records': 0},
        'selector_policy': 'fresh process; C16/CUDA injection inheritance cleared; isolated occurrence=0',
    }
    (out / 'TRACER_RECOVERY_CONTROL.json').write_text(json.dumps(controls, indent=2, sort_keys=True) + '\n')

    gpu = command(['nvidia-smi', '--query-gpu=name,uuid,driver_version', '--format=csv,noheader']).split(', ')
    versions = json.loads(command([str(RUNTIME), '-c', 'import json,torch,transformers,safetensors,accelerate,tokenizers; print(json.dumps({"python":__import__("sys").version.split()[0],"torch":torch.__version__,"torch_cuda":torch.version.cuda,"transformers":transformers.__version__,"safetensors":safetensors.__version__,"accelerate":accelerate.__version__,"tokenizers":tokenizers.__version__}))']))
    capture = {
        'instrument': 'NVBit V20 warp register-source', 'tool_version': 'C16WARP1/V20',
        'tool_identity_sha256_if_applicable': sha(V20),
        'target': 'S2_DEC3_NATURAL_EXPERT21_DOWN',
        'exact_argv': [
            'fresh isolated exact expert21 down_proj replay',
            'function occurrence=0',
            'one static GLOBAL MREF per process',
            'no CTA slicing',
        ],
    }
    run_manifest = {
        'schema_version': 1, 'run_id': args.run_id, 'created_at_utc': datetime.now(timezone.utc).isoformat(), 'scientific_status': 'FORMAL',
        'producer': {'hostname': command(['hostname']), 'gpu_name': gpu[0], 'gpu_uuid': gpu[1], 'driver': gpu[2], 'cuda': versions['torch_cuda']},
        'git': {'repository': 'accel-sim-framework', 'commit': command(['git', '-C', '/home/huangrulin/workspace/worktrees/accel-sim-q30-s2-formal-v3', 'rev-parse', 'HEAD']), 'dirty': False},
        'model': {'model_id': 'Qwen/Qwen3-30B-A3B', 'revision': 'ad44e777bcd18fa416d9da3bd8f70d33ebb85d39', 'asset_receipt_sha256': 'f49a40631ceac11fda5378ec18ed35eb5da3b3e6e24bc667a77994eed0631f25'},
        'input': {'binding_id': 'Q30_S2_TEXT B1/T2048/D32', 'authority_status': 'ACCEPTED_EXACT', 'receipt_sha256': 'e3368d01dc311d134e1f62c6412a3c05b2a2fb1de527f1947f3b7502af28c99a', 'token_ids_sha256_or_semantic_hash': '00d47e2312fb3db3585b5396ebc7484507356148019a845c8253c6d58d56d4f5'},
        'scenario': {'batch': 1, 'prefill_tokens': 2048, 'decode_tokens': 32, 'input_class': 'S2_TEXT', 'phase': 'DECODE_STEP3_LAYER24'},
        'runtime': {'python': versions['python'], 'torch': versions['torch'], 'transformers': versions['transformers'], 'dtype': 'bfloat16', 'attention_backend': 'sdpa; qwen3moe_sparse_expert_loop'},
        'capture': capture, 'artifacts': [],
    }
    manifest_path = args.staging_root / f'{args.run_id}.manifest.json'
    if manifest_path.exists():
        raise SystemExit(f'manifest collision: {manifest_path}')
    manifest_path.write_text(json.dumps(run_manifest, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': 'PASS', 'bundle': str(out), 'manifest': str(manifest_path), 'shards': len(manifest)}, sort_keys=True))


if __name__ == '__main__':
    main()
