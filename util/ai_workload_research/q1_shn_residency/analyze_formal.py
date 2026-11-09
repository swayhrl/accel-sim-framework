"""Recompute paired complete Host windows from every actual Q1 shN job result."""
import csv
import json
import math
import statistics as st
from pathlib import Path

W=Path('/home/huangrulin/workspace/worktrees/accel-sim-aiarch-q1-shn-gpu-residency-109-v1')
OUT=W/'docs/ai_workload_research/runs/AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1'
plan=json.loads((OUT/'FORMAL_PLAN.json').read_text())
jobs=OUT/'.private/JOBS'
actual=[];issues=[]
for p in plan['rows']:
    result_path=jobs/p['id']/'RESULT.json'
    error_path=jobs/p['id']/'ERROR.json'
    if not result_path.exists():
        issues.append({'job':p['id'],'reason':'MISSING_RESULT','error':json.loads(error_path.read_text()) if error_path.exists() else None})
        continue
    result=json.loads(result_path.read_text())
    frontier=result.get('frontier',{})
    required={'processed_GPU_step':p['stop_next']-1,
              'CPU_applied_through_step':p['stop_next']-2,
              'pending_CPU_gradient_step':p['stop_next']-1,
              'prepared_camera_step':p['stop_next']}
    complete=(result.get('status')=='COMPLETE' and result.get('reached_next_step')==p['stop_next']
              and result.get('closed_window_wall_seconds') is not None
              and all(frontier.get(k)==v for k,v in required.items()))
    if not complete:issues.append({'job':p['id'],'reason':'INCOMPLETE_OR_FRONTIER','status':result.get('status'),'frontier':frontier})
    if not result.get('finite_state_checks') or not all(result['finite_state_checks'].values()):
        issues.append({'job':p['id'],'reason':'NONFINITE_OR_MISSING_STATE_CHECK'})
    rows=result.get('rows',[])
    target=list(range(p['window_start'],p['stop_next']))
    if [r['step'] for r in rows]!=target:issues.append({'job':p['id'],'reason':'WINDOW_STEPS_OR_CREDIT_MISMATCH','actual_steps':[r['step'] for r in rows]})
    actual.append({'plan':p,'result':result,'complete':complete and [r['step'] for r in rows]==target})

camera_by_phase={}
work_by_phase={}
work_variation=[]
for item in actual:
    p=item['plan'];r=item['result'];phase=p['phase']
    cameras=[tuple(row['camera_ids']) for row in r.get('rows',[])]
    work=[(row['N_total'],row['N_visible'],row['N_updated']) for row in r.get('rows',[])]
    if phase not in camera_by_phase:camera_by_phase[phase]=cameras;work_by_phase[phase]=work
    if cameras!=camera_by_phase[phase]:issues.append({'job':p['id'],'reason':'CAMERA_IDENTITY_MISMATCH'})
    if work!=work_by_phase[phase]:
        reference=work_by_phase[phase]
        variation={'job':p['id'],'phase':phase,
            'visible_sum_delta':sum(x[1] for x in work)-sum(x[1] for x in reference),
            'update_sum_delta':sum(x[2] for x in work)-sum(x[2] for x in reference),
            'visible_step_difference_count':sum(a[1]!=b[1] for a,b in zip(work,reference)),
            'update_step_difference_count':sum(a[2]!=b[2] for a,b in zip(work,reference)),
            'N_identical':all(a[0]==b[0] for a,b in zip(work,reference))}
        work_variation.append(variation)
        if not variation['N_identical']:issues.append({'job':p['id'],'reason':'N_MISMATCH'})

sample_rows=[];stats={}
for phase in ('DISCOVERY','VALIDATION'):
    phase_formal=[x for x in actual if x['plan']['phase']==phase and x['plan']['mode']=='FORMAL' and x['complete']]
    pools={'OFF':[],'ON':[]};pairs={}
    for x in phase_formal:
        p=x['plan'];r=x['result'];policy='ON' if p['shn_resident'] else 'OFF'
        seconds=float(r['closed_window_wall_seconds'])
        row={'phase':phase,'pair':p['pair'],'job':p['id'],'policy':policy,'seconds':seconds,
             'N_min':min(t['N_total'] for t in r['rows']),'N_max':max(t['N_total'] for t in r['rows']),
             'visible_sum':sum(t['N_visible'] for t in r['rows']),
             'update_sum':sum(t['N_updated'] for t in r['rows']),
             'torch_allocated_peak_bytes':r.get('torch_allocated_peak'),
             'torch_reserved_peak_bytes':r.get('torch_reserved_peak')}
        sample_rows.append(row);pools[policy].append(seconds);pairs.setdefault(p['pair'],{})[policy]=row
    pair_rows=[{'pair':i,'off_s':v['OFF']['seconds'],'on_s':v['ON']['seconds'],
                'on_minus_off_s':v['ON']['seconds']-v['OFF']['seconds'],
                'speedup_pct':100*(v['OFF']['seconds']/v['ON']['seconds']-1),
                'visible_sum_delta_on_minus_off':v['ON']['visible_sum']-v['OFF']['visible_sum'],
                'update_sum_delta_on_minus_off':v['ON']['update_sum']-v['OFF']['update_sum']}
                for i,v in sorted(pairs.items()) if 'ON' in v and 'OFF' in v]
    def medmad(a):
        if not a:return {'median':None,'MAD':None,'n':0}
        med=st.median(a);return {'median':med,'MAD':st.median(abs(v-med) for v in a),'n':len(a)}
    stats[phase]={'OFF':medmad(pools['OFF']),'ON':medmad(pools['ON']),
                  'paired':pair_rows,'median_on_minus_off_s':st.median([p['on_minus_off_s'] for p in pair_rows]) if pair_rows else None,
                  'median_speedup_pct':st.median([p['speedup_pct'] for p in pair_rows]) if pair_rows else None,
                  'camera_count':len(camera_by_phase.get(phase,[])),
                  'camera_IDs':camera_by_phase.get(phase,[])}
    if len(pools['OFF'])!=5 or len(pools['ON'])!=5 or len(pair_rows)!=5:
        issues.append({'phase':phase,'reason':'FIVE_PAIRED_FORMAL_BLOCKS_NOT_COMPLETE'})

with (OUT/'FORMAL_SAMPLES.tsv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(sample_rows[0]) if sample_rows else ['phase','pair','job','policy','seconds'],delimiter='\t',lineterminator='\n')
    writer.writeheader();writer.writerows(sample_rows)
summary={'status':('PARTIAL_OR_NONCOMPARABLE' if issues else
                   'COMPLETE_DESCRIPTIVE_WORK_VARIATION' if work_variation else 'COMPLETE_IDENTICAL_RECORDED_WORK'),
         'measurement':'Host monotonic closed 50 target cameras plus one closure; OFF formal has no per-operation observer',
         'frozen_seed':plan['seed'],'stats':stats,'issues':issues,
         'work_variation':work_variation,
         'formal_sample_count':len(sample_rows),'warmup_count':sum(x['plan']['mode']=='WARMUP' and x['complete'] for x in actual),
         'diagnostic_count':sum(x['plan']['mode']=='DIAGNOSTIC' and x['complete'] for x in actual)}
(OUT/'FORMAL_ANALYSIS.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'status':summary['status'],'formal_sample_count':len(sample_rows),'issues':issues,
                  'phase_summary':{k:{'OFF':v['OFF'],'ON':v['ON'],'median_speedup_pct':v['median_speedup_pct']} for k,v in stats.items()}},indent=2))
