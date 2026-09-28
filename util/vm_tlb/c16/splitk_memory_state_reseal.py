#!/usr/bin/env python3
"""Archive the failed pre-timing qualification and refreeze corrected source identity."""
import datetime
import csv
import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT=Path('/data/c16/splitk_memory_state_interaction_v1')
REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-c16-splitk-memory-state-interaction-109-v1')
PACK=REPO/'docs/vm_tlb/review_packs/C16_SPLITK_MEMORY_STATE_INTERACTION_109_V1'

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def atomic_json(path,value):
 tmp=path.with_name(path.name+'.tmp')
 with tmp.open('x') as f:
  json.dump(value,f,indent=2,sort_keys=True); f.write('\n'); f.flush(); os.fsync(f.fileno())
 tmp.replace(path)

def main():
 run_id=(ROOT/'ACTIVE_RUN_ID').read_text().strip(); raw=ROOT/run_id/'raw'
 manifest=json.loads((raw/'SOURCE_AND_RUN_MANIFEST.pre_gpu.json').read_text())
 attempts=manifest.get('engineering_preflight_attempts',[]); attempt=len(attempts)+1
 archive=raw/f'preflight_attempt{attempt}_authority_binding_fix'; archive.mkdir()
 for name in ('GPU_IDENTITY.txt','GPU_LOCK_START_UTC.txt','NVIDIA_SMI_PRE.txt','qualification.log'):
  src=raw/name
  if src.is_file(): src.rename(archive/name)
 shutil.copy2(raw/'SOURCE_AND_RUN_MANIFEST.pre_gpu.json',archive/'SOURCE_AND_RUN_MANIFEST.pre_gpu.original.json')
 authority={'up_proj':{},'down_proj':{}}
 with (REPO/'docs/vm_tlb/review_packs/C16_LOWBIT_SPLITK_NATIVE_AB_109_V1/INPUT_AND_WEIGHT_BINDINGS.tsv').open(newline='') as f:
  for row in csv.DictReader(f,delimiter='\t'):
   if row['operator'] in authority and (row['tensor'] in ('qweight','qzeros','scales') or row['tensor']=='input_M256'):
    authority[row['operator']]['input' if row['tensor']=='input_M256' else row['tensor']]=row['sha256']
 manifest['weight_semantic_sha256']={role:{name:authority[role][name] for name in ('qweight','qzeros','scales')} for role in ('up_proj','down_proj')}
 for item in manifest['input_files']: item['semantic_tensor_sha256']=authority[item['operator']]['input']
 source_names=['splitk_memory_state_prepare.py','splitk_memory_state_runner.py','splitk_memory_state_validate_launch.py','splitk_memory_state_analyze.py','splitk_memory_state_reseal.py','run_splitk_memory_state_locked.sh']
 manifest['sources']=[]
 for name in source_names:
  path=REPO/'util/vm_tlb/c16'/name
  manifest['sources'].append({'path':str(path.relative_to(REPO)),'sha256':sha(path),'bytes':path.stat().st_size})
 manifest['status']='PREEXECUTION_SOURCE_AND_PARAMETERS_REFROZEN_AFTER_TRANSCRIPTION_FIX'
 manifest['refrozen_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 attempts.append({'attempt':attempt,'status':'FAIL_BEFORE_TIMING_OR_NCU','reason':'manual transcribed hash constant mismatch; replaced all input/weight/output hashes with direct immutable pack parsing','gpu_lock_release_confirmed':True,'archive_relative_path':str(archive.relative_to(ROOT/run_id))})
 manifest['engineering_preflight_attempts']=attempts
 atomic_json(raw/'SOURCE_AND_RUN_MANIFEST.pre_gpu.json',manifest)
 atomic_json(PACK/'SOURCE_AND_RUN_MANIFEST.json',manifest)
 print(json.dumps({'status':manifest['status'],'run_id':run_id,'archive':str(archive)}))

if __name__=='__main__': main()
