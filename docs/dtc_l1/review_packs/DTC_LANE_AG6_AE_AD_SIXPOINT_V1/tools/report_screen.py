"""Read-only six-point result extraction; no dispatch and no historical imports."""
from common import *
from fractions import Fraction
from run_screen import ORDER

def main():
 manifest=PACK/'EXECUTABLE_PREREGISTRATION.json'
 specs=[json.loads((PACK/n).read_text()) for n in json.loads(manifest.read_text())['ordered_specs']] if manifest.exists() else [dict(order=i,point=point,arm=point.split('_')[0],workload=point.split('_')[1],attempt_uuid='UNASSIGNED') for i,point in enumerate(ORDER)]
 results={};rows=[];metrics=[]
 for spec in specs:
  run=RAW/'attempts'/(spec['point']+'_'+spec['attempt_uuid']);path=run/'STRICT.json'
  if path.exists():results[spec['point']]=json.loads(path.read_text())
 for spec in specs:
  point=spec['point'];r=results.get(point,{});workload=spec['workload'];base=results.get('BASE_'+workload,{})
  accepted=r.get('performance_accepted') is True
  ratio='UNAVAILABLE';cycle_ratio='UNAVAILABLE'
  if accepted and base.get('performance_accepted') is True:
   require_cycles=lambda v:isinstance(v,int) and not isinstance(v,bool) and v>0
   assert require_cycles(base['cycles']) and require_cycles(r['cycles'])
   ratio=str(Fraction(base['cycles'],r['cycles']));cycle_ratio=str(Fraction(r['cycles'],base['cycles']))
  run=RAW/'attempts'/(point+'_'+spec['attempt_uuid'])
  rows.append(dict(order=spec['order'],point=point,workload=workload,arm=spec['arm'],attempt_uuid=spec['attempt_uuid'],reserved_start=int((run/'RUN_START.json').exists()),actual_child=int((run/'ENGINE/FORK_CHILD.json').exists()),status=r.get('status','NOT_STARTED_PRELAUNCH_HOLD'),cycles=r.get('cycles','UNAVAILABLE') if accepted else 'UNAVAILABLE',speedup_BASE_over_ON=ratio,cycle_ratio_ON_over_BASE=cycle_ratio,source='AG6_NEW_SAME_COHORT_ONLY'))
  for k,v in r.get('final_metrics',{}).items():metrics.append(dict(point=point,field=k,value=v,scope='ACTUALLY_PRINTED_LAST_CUMULATIVE_SNAPSHOT'))
 table(PACK/'FULL_MATRIX.tsv',rows)
 if metrics:table(PACK/'PER_ARM_METRICS.tsv',metrics)
 else:table(PACK/'PER_ARM_METRICS.tsv',[dict(point=p,field='ALL_METRICS',value='UNAVAILABLE_NOT_STARTED',scope='NO_PERFORMANCE_OBSERVATIONS') for p in ORDER])
 write(PACK/'RESULT_SUMMARY.json',dict(status='PRELAUNCH_HOLD' if not results else ('COMPLETE_SIX_POINT_DISCOVERY' if len(results)==6 and all(r.get('performance_accepted') is True for r in results.values()) else 'INCOMPLETE_NO_IMPUTATION'),authorized_actual_starts=6,reserved_starts=sum(r['reserved_start'] for r in rows),actual_starts=sum(r['actual_child'] for r in rows),strict_PASS=sum(r.get('performance_accepted') is True for r in results.values()),BASE_imported=False,attempts_remaining_unconsumed=6-sum(r['actual_child'] for r in rows),retry_or_replacement=False,host_wall_GPU_inference=False,GM12=False,independent_validation=False,discovery_inputs=2))
 print('REPORTED',len(rows),'points; actual starts',sum(r['actual_child'] for r in rows))
if __name__=='__main__':main()
