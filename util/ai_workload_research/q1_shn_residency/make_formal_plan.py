"""Freeze both 50-camera windows and paired block order before formal results."""
import json
import random
from pathlib import Path

HERE=Path(__file__).resolve().parent
seed=20261109
rng=random.Random(seed)
rows=[]
for phase,state,start,stop in [('DISCOVERY','C_D',15150,15201),('VALIDATION','C_FINAL',15311,15362)]:
    # Each block restarts from the same immutable canonical state.
    for index,policy in enumerate(['OFF','ON','ON','OFF'],1):
        rows.append(dict(id=f'{phase}_WARM_{index}_{policy}',mode='WARMUP',phase=phase,
                         restore=state,stop_next=stop,window_start=start,window_end=stop-1,
                         closure_extra_steps=1,shn_resident=policy=='ON',OMP_cap=14))
    for pair in range(1,6):
        order=['OFF','ON'];rng.shuffle(order)
        for ordinal,policy in enumerate(order,1):
            rows.append(dict(id=f'{phase}_FORMAL_PAIR{pair}_{ordinal}_{policy}',mode='FORMAL',phase=phase,
                             pair=pair,restore=state,stop_next=stop,window_start=start,window_end=stop-1,
                             closure_extra_steps=1,shn_resident=policy=='ON',OMP_cap=14,
                             diagnostic=False,numeric_audit=False))
    for policy in ['OFF','ON']:
        rows.append(dict(id=f'{phase}_DIAG_{policy}',mode='DIAGNOSTIC',phase=phase,
                         restore=state,stop_next=stop,window_start=start,window_end=stop-1,
                         closure_extra_steps=1,shn_resident=policy=='ON',OMP_cap=14,
                         diagnostic=True,numeric_audit=False))
plan={'goal':'AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1','seed':seed,
      'frozen_before_formal_results':True,
      'discovery_target_cameras':[15150,15200], 'discovery_closure_step':15200,
      'validation_target_cameras':[15311,15361], 'validation_closure_step':15361,
      'semantics':'Half-open target ranges; the closure is included in measured Host window and closes target credit.',
      'rows':rows}
(HERE/'FORMAL_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
(HERE/'FORMAL_DISPATCH.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in rows))
print({'seed':seed,'jobs':len(rows),'formal_pairs_per_phase':5,
       'pair_orders':{phase:[[r['id'] for r in rows if r.get('mode')=='FORMAL' and r.get('phase')==phase and r.get('pair')==p] for p in range(1,6)] for phase in ['DISCOVERY','VALIDATION']}})
