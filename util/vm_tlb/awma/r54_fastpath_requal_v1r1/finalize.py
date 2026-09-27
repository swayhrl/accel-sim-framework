#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path('/data/c16/awma/r54_fastpath_requal_v1r1_20260927')
WT = Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r54-fastpath-requal-v1r1')
V1 = Path('/data/c16/awma/r54_checkpoint_lifecycle_20260927')
MODEL = V1 / 'model/Qwen3_5_0_8B_c6046cd1'
SRC = V1 / 'source/transformers-main'
ENV = ROOT / 'env'
RECEIPTS = ROOT / 'receipts'
PROV = ROOT / 'provenance'
REVIEW = WT / 'docs/vm_tlb/review_packs/AWMA_R54_FASTPATH_REQUALIFICATION_V1R1'
REPORT = WT / 'docs/vm_tlb/reports/AWMA_R54_FASTPATH_REQUALIFICATION_V1R1_REPORT.md'


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def tree_manifest(path: Path):
    rows=[]
    for p in sorted(path.rglob('*')):
        if p.is_file():
            rows.append((str(p.relative_to(path)), p.stat().st_size, sha(p)))
    payload=''.join(f'{h}  {rel}\n' for rel,_,h in rows).encode()
    return rows, hashlib.sha256(payload).hexdigest()


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')


RECEIPTS.mkdir(parents=True,exist_ok=True)
PROV.mkdir(parents=True,exist_ok=True)
REVIEW.mkdir(parents=True,exist_ok=True)
REPORT.parent.mkdir(parents=True,exist_ok=True)

# Preserve the Triton runtime artifacts produced during this bounded canary.
triton_src=Path('/home/huangrulin/.triton/cache')
triton_dst=PROV/'triton_runtime_cache'
if triton_dst.exists():
    shutil.rmtree(triton_dst)
triton_dst.mkdir(parents=True)
cutoff=time.time()-2*3600
triton_count=0
for p in sorted(triton_src.rglob('*')):
    if p.is_file() and p.stat().st_mtime >= cutoff:
        rel=p.relative_to(triton_src)
        q=triton_dst/rel
        q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,q)
        triton_count+=1

import torch, transformers, kernels, huggingface_hub, einops
gpu_line=subprocess.check_output([
    'nvidia-smi','--query-gpu=name,compute_cap,driver_version,memory.total', '--format=csv,noheader'
],text=True).strip()
wheel=next((ROOT/'environment').glob('kernels-0.17.0-*.whl'))
source_files={
    'qwen3_5_doc': SRC/'docs/source/en/model_doc/qwen3_5.md',
    'hub_kernels': SRC/'src/transformers/integrations/hub_kernels.py',
    'modeling_qwen3_5': SRC/'src/transformers/models/qwen3_5/modeling_qwen3_5.py',
}
env_receipt={
    'stage':'AWMA_R54_FASTPATH_REQUALIFICATION_V1R1',
    'environment_path':str(ENV),
    'python':sys.version.replace('\n',' '),
    'platform':platform.platform(),
    'torch':torch.__version__,
    'torch_cuda':torch.version.cuda,
    'torch_cxx11_abi':torch.compiled_with_cxx11_abi(),
    'transformers':transformers.__version__,
    'transformers_source_commit':'96331a9f93b72697f160a958d2883d4b49a56739',
    'transformers_source_hashes':{k:sha(v) for k,v in source_files.items()},
    'kernels':kernels.__version__,
    'kernels_wheel':str(wheel),
    'kernels_wheel_sha256':sha(wheel),
    'huggingface_hub':huggingface_hub.__version__,
    'einops':einops.__version__,
    'gpu_identity':gpu_line,
    'system_driver_unchanged':True,
    'system_cuda_unchanged':True,
    'v1_environment_mutated':False,
    'model_redownloaded':False,
    'compatibility_resolution':{
        'inherited_torch_2_5_1_cu124':'no mamba-ssm v3 Hub build variant',
        'selected':'torch 2.14.0+cu130 / CXX11 ABI / x86_64',
        'reason':'exact mamba-ssm revision publishes torch214-cxx11-cu130-x86_64-linux',
    },
    'pip_freeze_sha256':sha(ROOT/'environment/pip_freeze.txt'),
}
write_json(ROOT/'R54_V1R1_ENVIRONMENT_RECEIPT.json',env_receipt)

mamba=ROOT/'hf_home/hub/kernels--kernels-community--mamba-ssm/snapshots/20b2508ad12ae40260291539bf45183000451850/build/torch214-cxx11-cu130-x86_64-linux'
fla=ROOT/'hf_home/hub/kernels--kernels-community--fla/snapshots/6d22ed1d2bb627375b6ca8fc135f7f417863e639/build/torch-cuda'
mamba_rows,mamba_tree=tree_manifest(mamba)
fla_rows,fla_tree=tree_manifest(fla)
triton_rows,triton_tree=tree_manifest(triton_dst)

with (PROV/'MATERIALIZED_ARTIFACTS.tsv').open('w',newline='') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n')
    w.writerow(['artifact_group','relative_path','size_bytes','sha256'])
    for group,rows in [('mamba_ssm_torch214_cu130',mamba_rows),('fla_torch_cuda',fla_rows),('triton_runtime_sm89',triton_rows)]:
        for rel,size,h in rows:w.writerow([group,rel,size,h])

evidence={
 'causal_conv1d_fn':'void causal_conv1d_channellast_fwd_kernel',
 'causal_conv1d_update':'void causal_conv1d_update_kernel',
 'chunk_gated_delta_rule':'chunk_gated_delta_rule_fwd_kernel_h_blockdim64',
 'fused_recurrent_gated_delta_rule':'fused_recurrent_gated_delta_rule_fwd_kernel',
}
rows=[]
for op in evidence:
    is_mamba=op.startswith('causal_conv1d')
    rows.append({
      'operation':op,
      'transformers_mapping_repo':'kernels-community/mamba-ssm' if is_mamba else 'kernels-community/fla',
      'transformers_mapping_version':'3' if is_mamba else '1',
      'resolved_revision':'20b2508ad12ae40260291539bf45183000451850' if is_mamba else '6d22ed1d2bb627375b6ca8fc135f7f417863e639',
      'mapped_layer_name':'recurrent_gated_delta_rule' if op=='fused_recurrent_gated_delta_rule' else op,
      'runtime_build':'torch214-cxx11-cu130-x86_64-linux' if is_mamba else 'torch-cuda + Triton 3.8.0 SM89 JIT',
      'materialized_cache_path':str(mamba if is_mamba else fla),
      'materialized_tree_sha256':mamba_tree if is_mamba else fla_tree,
      'materialized_file_count':len(mamba_rows) if is_mamba else len(fla_rows),
      'device_compatibility':'RTX4080 SM89 qualified by successful execution',
      'runtime_selected':'YES',
      'nsys_evidence_kernel':evidence[op],
      'atlas_sm121_mapping_used':'NO',
    })
with (ROOT/'HUB_KERNEL_PROVENANCE.tsv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

# Promote generated receipts to the durable root.
for src,name in [
 (RECEIPTS/'R54_V1R1_FASTPATH_RECEIPT.json','R54_V1R1_FASTPATH_RECEIPT.json'),
 (RECEIPTS/'R54_V1R1_KERNEL_STRATA.tsv','R54_V1R1_KERNEL_STRATA.tsv'),
 (RECEIPTS/'R54_V1R1_SEMANTIC_EQUIVALENCE.tsv','R54_V1R1_SEMANTIC_EQUIVALENCE.tsv'),
 (RECEIPTS/'R54_V1R1_NSYS_SUMMARY.json','R54_V1R1_NSYS_SUMMARY.json'),
]:
    if src.suffix == '.tsv':
        (ROOT/name).write_bytes(src.read_bytes().replace(b'\r\n', b'\n'))
    else:
        shutil.copy2(src,ROOT/name)

v1_inheritance='''# V1 inheritance\n\n- Accepted V1 commit: `40f51deacee491d7e1b57f09db533d43d84d7ad5`.\n- Accepted V1 state remains `R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1` for the attempted local `causal_conv1d` / FLA package path.\n- V1 evidence was not rewritten or deleted.\n- V1R1 reuses the hash-closed Qwen/Qwen3.5-0.8B model and exact Transformers commit.\n- V1R1 tests only the newly authorized Hub generic function mappings.\n'''
(ROOT/'V1_INHERITANCE.md').write_text(v1_inheritance)

decision='''# R54 V1R1 decision\n\nFinal state: `R54_V1R1_HUB_KERNEL_SEMANTICS_NOT_QUALIFIED`.\n\nThe exact Hub generic function path is technically available on RTX4080/SM89. NSYS records all four required optimized strata, while the fallback arm records none of those signatures. The SM121-only `Atlas-Inference/gdn` whole-layer mapping was not used.\n\nThe frozen semantic contract failed without adding a tolerance: fallback initial top-2 IDs were `[5533, 13]`, while Hub initial top-2 IDs were `[5533, 369]`. Initial argmax, initial top-8 set, finite outputs, shape/dtype, and the complete fixed 16-token greedy continuation all matched, but exact top1/top2 ordering is mandatory.\n\nTherefore V1R1 does not resume checkpoint lifecycle timing, state-schema work, P0/P1/P2, D512/D2048, restore, amortization, holdout, or NCU. No fourth runtime/backend is attempted. Current-platform R54 remains not scientifically qualified.\n'''
(ROOT/'R54_V1R1_DECISION.md').write_text(decision)
(ROOT/'FINAL_DECISION.md').write_text(decision)

readme='''# AWMA R54 Fast-Path Requalification V1R1\n\nThis authority tests the official Transformers Hub generic CUDA mappings omitted by R54 V1. The mappings execute on SM89, but the frozen exact top1/top2 ordering gate fails. Final state: `R54_V1R1_HUB_KERNEL_SEMANTICS_NOT_QUALIFIED`.\n\nLarge raw NSYS/SQLite, Hub artifacts, and hashes are retained in this durable authority. Git contains the compact review pack and reproduction utilities.\n'''
(ROOT/'README.md').write_text(readme)
(ROOT/'REPORT.md').write_text(readme+'\n'+decision)

final_receipt={
 'stage':'AWMA_R54_FASTPATH_REQUALIFICATION_V1R1',
 'final_state':'R54_V1R1_HUB_KERNEL_SEMANTICS_NOT_QUALIFIED',
 'hub_fastpath_available':True,
 'semantic_gate_pass':False,
 'full_r54_resumed':False,
 'ncu_run':False,
 'node174_used':False,
 'accel_sim_run':False,
 'atlas_sm121_mapping_used':False,
 'gpu_lock_released_at_closure':True,
 'mamba_artifact_tree_sha256':mamba_tree,
 'fla_artifact_tree_sha256':fla_tree,
 'triton_runtime_tree_sha256':triton_tree,
 'triton_runtime_file_count':triton_count,
}
write_json(ROOT/'FINAL_RECEIPT.json',final_receipt)

# Compact review pack.
compact=[
 'README.md','V1_INHERITANCE.md','R54_V1R1_ENVIRONMENT_RECEIPT.json','HUB_KERNEL_PROVENANCE.tsv',
 'R54_V1R1_FASTPATH_RECEIPT.json','R54_V1R1_KERNEL_STRATA.tsv','R54_V1R1_NSYS_SUMMARY.json',
 'R54_V1R1_SEMANTIC_EQUIVALENCE.tsv','R54_V1R1_DECISION.md','FINAL_DECISION.md','FINAL_RECEIPT.json'
]
for name in compact:shutil.copy2(ROOT/name,REVIEW/name)
REPORT.write_text((ROOT/'REPORT.md').read_text())

# Index everything except the 5.5 GiB reconstructible venv. Hash symlink targets.
def included(p:Path):
    rel=p.relative_to(ROOT)
    return rel.parts[0] != 'env' and rel.name not in {'RAW_DATA_INDEX.tsv','SHA256SUMS'} and p.is_file()

index=[]
for p in sorted(ROOT.rglob('*')):
    if included(p):index.append((str(p.relative_to(ROOT)),p.stat().st_size,sha(p)))
with (ROOT/'RAW_DATA_INDEX.tsv').open('w',newline='') as f:
    w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['relative_path','size_bytes','sha256']);w.writerows(index)
shas=[]
for p in sorted(ROOT.rglob('*')):
    if p.is_file() and p.relative_to(ROOT).parts[0]!='env' and p.name!='SHA256SUMS':
        shas.append(f'{sha(p)}  {p.relative_to(ROOT)}')
(ROOT/'SHA256SUMS').write_text('\n'.join(shas)+'\n')
shutil.copy2(ROOT/'RAW_DATA_INDEX.tsv',REVIEW/'RAW_DATA_INDEX.tsv')
review_shas=[]
for p in sorted(REVIEW.iterdir()):
    if p.is_file() and p.name!='SHA256SUMS':
        review_shas.append(f'{sha(p)}  {p.name}')
(REVIEW/'SHA256SUMS').write_text('\n'.join(review_shas)+'\n')

print(json.dumps(final_receipt,indent=2,sort_keys=True))
