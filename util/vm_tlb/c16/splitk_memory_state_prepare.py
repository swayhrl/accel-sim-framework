#!/usr/bin/env python3
"""CPU-only authority and pre-execution manifest freeze for split-K memory state V1."""
import datetime
import hashlib
import json
import os
import platform
import secrets
import subprocess
from pathlib import Path

ROOT = Path("/data/c16/splitk_memory_state_interaction_v1")
REPO = Path("/home/huangrulin/workspace/worktrees/accel-sim-c16-splitk-memory-state-interaction-109-v1")
PACK = REPO / "docs/vm_tlb/review_packs/C16_SPLITK_MEMORY_STATE_INTERACTION_109_V1"
MODEL = Path("/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641")
AUTH = Path("/data/c16/e1_clean_baseline_v1/capture_a")
A_BINARY = Path("/data/c16/env/c16-awq-v6/lib/python3.10/site-packages/awq_ext.cpython-310-x86_64-linux-gnu.so")
B_BINARY = Path("/data/c16/e1_lowbit_splitk_native_ab_v1/build/lib/awq_split1_ext.cpython-310-x86_64-linux-gnu.so")
EXPECTED_A = "9e8d38a04c28770338fcef8ae0f9a90a984b7a8f95bcb98a407738594e1c08d7"
EXPECTED_B = "1aa8db13f5fd10651aa4241f58200e3a7075214d34cca4d70fbcbe7cbbc07887"


def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()


def atomic_json(path,value):
    tmp=path.with_name(path.name+'.tmp')
    with tmp.open('x') as f:
        json.dump(value,f,indent=2,sort_keys=True); f.write('\n'); f.flush(); os.fsync(f.fileno())
    tmp.replace(path)


def main():
    if ROOT.exists(): raise SystemExit(f'refusing existing root: {ROOT}')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
    if head!='0e88faa28c9066b48e394dce657d7a16e6332a32': raise RuntimeError(f'BASE_HEAD_FAIL {head}')
    if sha(A_BINARY)!=EXPECTED_A or sha(B_BINARY)!=EXPECTED_B: raise RuntimeError('ACCEPTED_BINARY_IDENTITY_FAIL')
    run_id='C16R_splitk-memory-state-interaction-v1_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+secrets.token_hex(6)
    run=ROOT/run_id; raw=run/'raw'; raw.mkdir(parents=True)
    (ROOT/'ACTIVE_RUN_ID').write_text(run_id+'\n')
    source_names=['splitk_memory_state_prepare.py','splitk_memory_state_runner.py','splitk_memory_state_validate_launch.py','splitk_memory_state_analyze.py','splitk_memory_state_reseal.py','run_splitk_memory_state_locked.sh']
    source_rows=[]
    for name in source_names:
        path=REPO/'util/vm_tlb/c16'/name
        if not path.is_file(): raise RuntimeError(f'MISSING_SOURCE {path}')
        source_rows.append({'path':str(path.relative_to(REPO)),'sha256':sha(path),'bytes':path.stat().st_size})
    input_files=[]
    for role in ('up_proj','down_proj'):
        path=AUTH/f'{role}_M256_input.pt'
        input_files.append({'operator':role,'path':str(path),'file_sha256':sha(path),'file_bytes':path.stat().st_size,'semantic_tensor_sha256':'eeae491edfdbee761de47aa6c4ea35b293bb2796227927778fa51c9e58ef1b41' if role=='up_proj' else 'a1f158a113f56314f4ee5f4a5f10ee41ac9afe732a4f1735b88a1c01b25b9aff'})
    cells=[]
    for role in ('up_proj','down_proj'):
        for cell in ('A_W','B_W','A_E','B_E'):
            arm,state=cell.split('_'); cells.append({'operator':role,'cell':cell,'arm':'ACCEPTED_SPLIT8' if arm=='A' else 'ACCEPTED_SPLIT1_DIRECT_OUTPUT','state':'WARM_SAME_ARM' if state=='W' else 'EVICT_CONDITIONED'})
    manifest={
        'status':'PREEXECUTION_SOURCE_AND_PARAMETERS_FROZEN', 'goal':'C16_SPLITK_MEMORY_STATE_INTERACTION_109_V1', 'run_id':run_id,
        'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'producer_base':head,
        'coordination_head':'17dd9482245d8bdac8e89ff53be5a567048016f1', 'branch':'hrl/c16-splitk-memory-state-interaction-109-v1',
        'original_ab_producer':'0e88faa28c9066b48e394dce657d7a16e6332a32',
        'model':{'id':'Qwen/Qwen2.5-7B-Instruct-AWQ','revision':'b25037543e9394b818fdfca67ab2a00ecc7dd641','path':str(MODEL),'layer':'model.layers.0','loaded_assets_only':['mlp.up_proj qweight/qzeros/scales','mlp.down_proj qweight/qzeros/scales']},
        'accepted_binaries':{'A':{'path':str(A_BINARY),'sha256':sha(A_BINARY)},'B':{'path':str(B_BINARY),'sha256':sha(B_BINARY)}},
        'input_files':input_files,
        'weight_semantic_sha256':{
          'up_proj':{'qweight':'b07a8dec390cec4f664bfd2384acf080c4676e1c6d29386bfaf225e4e68d181a','qzeros':'fa29c34518732c98417613df87bbb46dcf3cd825bd681700a5daa0a49b24205b','scales':'84e59277679d49510b3449687598d47cbe8f9ce356c73f07b2abc60019b0a175'},
          'down_proj':{'qweight':'d5e856f6cb2709c28092e74f3434faaf7bad371c8342a4b0553d148bf5d200cb','qzeros':'06122002c48390245c77e071e2352ebabbc20eedc8dfd555aa222148844be8a80','scales':'031c2f9b22f16ef4538004e3563e03e41ce3b1a015d7476420642d2772fe9cc1d'}},
        'cells':cells,
        'conditioner':{'expected_l2_bytes':67108864,'buffer_multiple':4,'buffer_bytes':268435456,'dtype':'torch.int32','elements':67108864,'operation':'in-place add_(1) full-buffer read-modify-write','stride_elements':1,'same_live_buffer_all_cells':True,'no_allocator_empty_cache':True,'no_persisting_hint':True,'qualification':'lock-time device property exact check required'},
        'timing':{'global_warmups_per_operator_arm':10,'sample_preparation_same_arm_warmups':2,'blocks':25,'mirror_order':['A_W','B_W','A_E','B_E','B_E','A_E','B_W','A_W'],'samples_per_cell':50,'target_clock':'CUDA event','conditioner_outside_event':True,'bootstrap':{'seed':20260928,'permutations':1000,'unit':'complete mirror block','quantiles':[0.05,0.5,0.95]}},
        'ncu':{'profiles':8,'operators':['up_proj','down_proj'],'cells':['A_W','B_W','A_E','B_E'],'nvtx_target_only':True,'replay_mode':'application','cache_control':'none','metrics':['l1tex__t_bytes.sum','lts__t_bytes.sum','dram__bytes.sum'],'preparation_outside_nvtx':True,'ncu':'2025.1.1.0'},
        'launch_contract':{'up_proj':{'A_gemm_grid':18944,'B_gemm_grid':2368,'A_reduction_grid':9472},'down_proj':{'A_gemm_grid':3584,'B_gemm_grid':448,'A_reduction_grid':1792},'gemm_block':[32,2,1],'reduction_block':[32,4,1],'A_reduction':True,'B_reduction':False},
        'sources':source_rows,'gpu_lock':'/data/c16/locks/c16_gpu_campaign.lock','one_outer_gpu_campaign':True,
        'prohibitions':{'extra_split':False,'M1':False,'q_proj':False,'extra_model_backend_quantization':False,'Lane4_partial_accessed':False,'timing_or_cache_causality_claim':False},
    }
    PACK.mkdir(parents=True)
    atomic_json(raw/'SOURCE_AND_RUN_MANIFEST.pre_gpu.json',manifest)
    atomic_json(PACK/'SOURCE_AND_RUN_MANIFEST.json',manifest)
    print(json.dumps({'status':manifest['status'],'run_id':run_id,'run':str(run)}))


if __name__=='__main__': main()
