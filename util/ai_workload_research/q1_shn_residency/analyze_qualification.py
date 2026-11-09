"""Independent paired comparison of recorded real C_D qualification steps."""
import json
import math
import sys
from pathlib import Path

W=Path('/home/huangrulin/workspace/worktrees/accel-sim-aiarch-q1-shn-gpu-residency-109-v1')
OUT=W/'docs/ai_workload_research/runs/AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1'
base=OUT/'.private/JOBS'
state=sys.argv[1] if len(sys.argv)>1 else 'C_D'
assert state in ('C_D','C_FINAL')
if state=='C_D':
    off=base/'CD_NUMERIC_OFF_15140_15144';on=base/'CD_NUMERIC_ON_15140_15144';steps=range(15140,15144)
else:
    off=base/'CFINAL_NUMERIC_OFF_15301_15305';on=base/'CFINAL_NUMERIC_ON_15301_15305';steps=range(15301,15305)
assert json.loads((off/'RESULT.json').read_text())['status']=='COMPLETE'
assert json.loads((on/'RESULT.json').read_text())['status']=='COMPLETE'
checks=[]
for step in steps:
    a=json.loads((off/f'NUMERIC_STEP_{step}.json').read_text())
    b=json.loads((on/f'NUMERIC_STEP_{step}.json').read_text())
    metadata=['step','sample_IDs','counter','optimizer_step','camera_ids','U_count','U_first',
              'current_visible_count','next_visible_count','next_visible_first']
    for key in metadata:
        if a[key]!=b[key]:
            checks.append({'step':step,'field':key,'status':'SEMANTIC_MISMATCH','off':a[key], 'on':b[key]})
    for field in ['parameter','gradient','moment1','moment2','next_consumed_first']:
        x=a[field];y=b[field]
        assert len(x)==len(y) and all(len(p)==len(q) for p,q in zip(x,y))
        vals=[(u,v) for p,q in zip(x,y) for u,v in zip(p,q)]
        max_ref=max((abs(u) for u,v in vals),default=0.0)
        diffs=[abs(u-v) for u,v in vals]
        max_abs=max(diffs,default=0.0)
        rms=math.sqrt(sum(z*z for z in diffs)/len(diffs)) if diffs else 0.0
        threshold=2e-6+2e-4*max_ref
        checks.append({'step':step,'field':field,'status':'PASS' if max_abs<=threshold else 'NUMERIC_FAIL',
                       'elements':len(vals),'max_abs':max_abs,'rms_abs':rms,'reference_max_abs':max_ref,
                       'frozen_threshold':threshold})
status='PASS_SAMPLED_SHORT_WINDOW' if all(x['status']=='PASS' for x in checks) else 'STOP_NUMERIC_OR_SEMANTIC'
receipt_path=OUT/'.private/RESOURCE_RECEIPT_WINDOW1.json' if state=='C_D' and (OUT/'.private/RESOURCE_RECEIPT_WINDOW1.json').exists() else OUT/'RESOURCE_RECEIPT.json'
receipt=json.loads(receipt_path.read_text())
result={'status':status,'source_state':state,'steps':[steps.start,steps.stop],
        'qualification_scope':'512 deterministic shN rows plus first128 next-camera rows per step; not full-state equivalence',
        'checks':checks,'resource':{k:receipt.get(k) for k in ['status','lock_attempt_count','lock_acquired','lock_released','reservation_created','reservation_cleanup','own_GPU_contexts_cleared','GPU_lock_held_seconds','peak_own_NVML_bytes','peak_sampled_RSS_bytes','peak_charged_bytes']}}
(OUT/('NUMERIC_AND_FRONTIER_AUDIT_'+state+'.json')).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':status,'failed':[{'step':x['step'],'field':x['field'],'status':x['status'],'max_abs':x.get('max_abs'),'threshold':x.get('frozen_threshold')} for x in checks if x['status']!='PASS'],
                  'peak_own_NVML_GiB':round(receipt['peak_own_NVML_bytes']/1024**3,3),'lock_released':receipt['lock_released']}))
