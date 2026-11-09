"""Create private new-Goal binding from verified frozen Q1 gate identity."""
import json
import subprocess
import shutil
import time
import urllib.request
from pathlib import Path

W=Path('/home/huangrulin/workspace/worktrees/accel-sim-aiarch-q1-shn-gpu-residency-109-v1')
Q=Path('/home/huangrulin/workspace/worktrees/accel-sim-aiarch-q1-completion-109/docs/ai_workload_research/runs/AI_ARCH_Q1_COMPLETION_109_V1')
OUT=W/'docs/ai_workload_research/runs/AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1'
SOURCE=Q/'windows/W2/EXECUTION_BINDING.json'
cfg=json.loads(SOURCE.read_text())
cfg['contract_commit']=subprocess.check_output(['git','-C',str(W),'rev-parse','HEAD'],text=True).strip()
cfg['contract_tree']=subprocess.check_output(['git','-C',str(W),'rev-parse','HEAD^{tree}'],text=True).strip()
url=cfg['shared_resident']['status_url']+'?challenge=aiarch_q1_shn_preflight'
with urllib.request.urlopen(urllib.request.Request(url,headers={'Cache-Control':'no-cache'}),timeout=4) as r:
    current=json.load(r)
assert current['challenge']=='aiarch_q1_shn_preflight'
assert time.time()-current['updated_unix']<5
s=cfg['shared_resident']
for actual,expect in [('run_nonce','run_nonce'),('build_commit','source_commit'),('loaded_function_hashes','loaded_function_hashes'),('loaded_modules','loaded_module_hashes'),('owner','owner')]:
    a=current[actual]
    if actual=='owner':a={k:a[k] for k in s['owner']}
    assert a==s[expect], actual
assert current['state']=='IMAGE_LAB_IDLE' and not current.get('reservation') and not current.get('kernel_holders')
assert current['live_ready'] and current['profile_monitor_alive'] and current['in_flight_scopes']==0
now=int(time.time())
cfg.update(goal_start_epoch=now,root=str(W),out=str(OUT),tool=str(W/'util/ai_workload_research/q1_shn_residency'),
           branch='hrl/aiarch-q1-shn-gpu-residency-109-v1',
           GPU_seconds_max=5400,held_seconds_max=5400,goal_seconds_max=43200,
           own_vram_bytes_max=14*1024**3,RSS_bytes_max=40*1024**3,rss_bytes_max=40*1024**3,
           charged_bytes_max=48*1024**3,disk_bytes_max=16*1024**3,
           free_bytes_min=32*1024**3,mem_available_bytes_min=10*1024**3,
           window_id='W1',terminal_handoff=True,
           current_goal='AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1',
           authorization='User-pasted new complete Goal, 2026-11-09; bounded 109 RTX4080 and gate protocol')
cfg.pop('external_readonly_state_root',None)
cfg.pop('user_new_authorization',None)
cfg['external_readonly_state_roots']={'C_D':str(Q/'.private/STATES'),
                                     'C_FINAL':str(Q/'windows/W2/.private/STATES')}
for name,root in cfg['external_readonly_state_roots'].items():
    assert (Path(root)/name/'MANIFEST.json').is_file()
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'.gitignore').write_text('.private/\nEXECUTION_BINDING.json\nraw/\n')
(OUT/'raw').mkdir(exist_ok=True)
for name,source in [('C_D',Q/'raw/STATE_C_D_MANIFEST.json'),
                    ('C_FINAL',Q/'windows/W2/raw/STATE_C_FINAL_MANIFEST.json')]:
    shutil.copyfile(source,OUT/'raw'/('STATE_'+name+'_MANIFEST.json'))
for p in ['.private/tmp','.private/cache','.private/JOBS']:(OUT/p).mkdir(parents=True,exist_ok=True)
(OUT/'EXECUTION_BINDING.json').write_text(json.dumps(cfg,indent=2)+'\n')
print(json.dumps({'status':'CPU_PREFLIGHT_READY','out':str(OUT),'goal_start_epoch':now,
                  'gate_state':current['state'],'source_states':['C_D','C_FINAL'],
                  'private_binding':True,'GPU_initialized':False}))
