"""Offline projection of frozen E accepted declarations; never a qualifier/acceptor.
Uses existing D pointer, mechanism, cache and snapshot readers. No registry access.
"""
import csv, datetime, hashlib, json, math, subprocess, sys
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_study_lane_d'))
import sync_intake as intake
import full_v2_analysis as full
import control_incremental as incremental
import paper_four_pair_details as detail
OUT=Path(__file__).resolve().parent
E='ca2dbc456b061885b1c5e7503de91fc38a8e90c8'
EP='docs/ep_l2/review_packs/MS20261021_E2_PRIMARY_FOUR_EXECUTION_r1/'
D='docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/'
CACHES=[ROOT/'docs/ep_l2/review_packs/MS20261021_D_DWT_FOUR_KERNEL_r1',ROOT/(D+'controls_20261021_r4/accepted_snapshot_04'),ROOT/(D+'controls_20261020_r3/accepted_event_1792510573934001466')]
def save(name,v): (OUT/name).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def csvout(name,rows):
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with (OUT/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=keys,lineterminator="\n");w.writeheader();w.writerows(rows)
def frozen(name):
 data=subprocess.check_output(['git','show',E+':'+EP+name],cwd=ROOT)
 (OUT/('E_'+name.replace('/','__'))).write_bytes(data)
 return json.loads(data) if name.endswith('.json') else data.decode()
def main():
 final=frozen('FINAL_RECEIPT.json'); frozen('FINAL_STATUS.md'); deliveries=frozen('D_DELIVERY_INDEX.json'); plan=frozen('PLAN.json')
 frozen('V2_convolutionSeparable_F_L2_DATA_FREE/FINITE_RESIDUAL_SERVICE_GATE.json')
 decls={**final['accepted_main_pairs'],**final['accepted_controls']};refs={}
 for p in decls.values():
  assert p['status']=='CURRENT_ACCEPTED' and p['accepted_by']=='E'
  for ref in p['endpoints'].values():
   aid=ref['attempt_id']
   if aid in refs: assert refs[aid]==ref
   refs[aid]=ref
 # Verify delivery links to exactly the frozen four declarations; preserve E decision.
 checks=[]
 for item in deliveries['deliveries']:
  pid=item['receipt']['accepted_pair_id']
  accepted=frozen(pid+'_CURRENT_ACCEPTED.json')
  frozen(pid+'_D_DELIVERY_RECEIPT.json')
  frozen(pid+'_ACCEPTED_PAIR.json')
  checks.append(dict(pair_id=pid,acceptance='CURRENT_ACCEPTED',endpoints=decls[pid]['endpoints'],remote_publication=item['receipt']['remote_publication'],frozen_current_accepted_sha256=intake.digest(OUT/('E_'+pid+'_CURRENT_ACCEPTED.json'))))
 assert len(checks)==4
 save('FOUR_DELIVERY_IDENTITIES.json',checks)
 parsed={pid:intake.analyze_pair(pid,p,refs) for pid,p in decls.items()}
 assert all(r['status']=='E_ACCEPTED_D_ANALYZED' for r in parsed.values())
 records={aid:intake.pointer(ref) for aid,ref in refs.items()}
 identities=[];obs={};provenance=[];points={};mech=[]
 for aid,r in records.items():
  i=r['identity'];w=i['workload'];profile=r['profile'];key=(w,profile)
  assert key not in points
  assert i['binary_sha256']==final['source_identity']['binary_sha256']
  points[key]=aid
  identities.append(dict(workload=w,profile=profile,attempt_id=aid,cycles=r['summary']['cycles'],instructions=r['summary']['instructions'],receipt_path=refs[aid]['path'],receipt_sha256=refs[aid]['sha256'],raw_sha256=r['raw_log_sha256'],run_key=r['run_key'],qualification_id=r['qualification_id'],trace_sha256=i['trace_content_sha256'],config_sha256=i['runtime_config_sha256'],core=i['core_source_commit'],framework=i['framework_source_commit'],binary=i['binary_sha256'],vendor=r['source_identity']['vendor_pybind11_commit'],selection_id=r['selection_id'],invariants_sha256=r['comparison_invariants_sha256'],epoch_scope=i['epoch_range'],labels=r['labels'],feature_vector=i['feature_vector'],ideal_vector=i['ideal_vector']))
  o,prov=incremental.cached_observation(dict(workload=w,profile=profile,attempt_id=aid),r,CACHES,OUT)
  assert o['frames'][-1]['gpu_tot_sim_cycle']==r['summary']['cycles']
  obs[key]=o;provenance.append(prov);save('OBSERVATIONS_'+aid+'.json',o)
 csvout('ACCEPTED_ENDPOINT_IDENTITIES.csv',identities);save('ACCEPTED_ENDPOINT_IDENTITIES.json',identities)
 mainrows=[]
 for pid,p in final['accepted_main_pairs'].items():
  r=parsed[pid];s,f=r['baseline_cycles'],r['variant_cycles']
  assert p['cycles_left']==s and p['cycles_right']==f
  mainrows.append(dict(workload=r['workload'],pair_id=pid,S_attempt=r['baseline_attempt_id'],F_attempt=r['variant_attempt_id'],S_cycles=s,F_cycles=f,F_minus_S_cycles=f-s,speedup_S_over_F=s/f,speedup_percent=100*(s/f-1),F_cycle_change_percent=100*(f/s-1),instructions_each=r['baseline_instructions'],S_receipt_sha256=r['baseline_receipt_sha256'],F_receipt_sha256=r['variant_receipt_sha256'],S_config_sha256=r['baseline_config'],F_config_sha256=r['variant_config'],trace_sha256=r['trace'],binary=r['binary']))
 csvout('MAIN_FIVE_PERFORMANCE.csv',mainrows)
 gm=math.exp(sum(math.log(r['speedup_S_over_F']) for r in mainrows)/len(mainrows))
 summary=dict(E_authority=E,D_base='2789e3034493bb57a66948c77a67fdcb26bf6ef0',observed_BJT=datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),main_count=len(mainrows),main_members=[r['workload'] for r in mainrows],GM_S_over_F=gm,GM_speedup_percent=100*(gm-1),original_seven_GM='UNKNOWN',missing_original_seven=['FWT_7_21','btree'],original_seven_denominator=7,main_subset_denominator=5,actual_starts_as_published_by_E=final['actual_starts'],maximum=final['maximum'],remaining=final['remaining'],source_identity=final['source_identity'],new_applications=0,new_native=0,new_builds=0,registry_reads=0,registry_writes=0,trace_reads=0,EN_v22_modified=False,acceptance_owner='E',E_gates_reexecuted=False,snapshot_provenance=provenance)
 save('SUMMARY.json',summary)
 for pid,r in parsed.items():
  for m in full.mechanism_table(r):
   m.update(left_profile=r['baseline_profile'],right_profile=r['variant_profile']);m['left']=m.pop('S');m['right']=m.pop('F');m['right_minus_left']=m.pop('F_minus_S');mech.append(m)
 csvout('ACCEPTED_PAIR_TERMINAL_MECHANISMS.csv',mech)
 timing=[]
 contrasts=[(r['workload'],'S','F') for r in mainrows]+[('dwt2d','S','W_ONLY'),('dwt2d','W_ONLY','F_MINUS_R'),('dwt2d','F_MINUS_R','F'),('convolutionSeparable','S','S_L2_DATA_FREE'),('convolutionSeparable','F','F_L2_DATA_FREE')]
 for w,left,right in contrasts:
  lo,ro=obs[w,left],obs[w,right]
  assert [f.get('kernel_launch_uid') for f in lo['frames'] if f.get('kernel_name')]==[f.get('kernel_launch_uid') for f in ro['frames'] if f.get('kernel_name')]
  rr=detail.paired_timing(w,{'S':lo,'F':ro})
  for x in rr:
   x.update(left_profile=left,right_profile=right,left_attempt=points[w,left],right_attempt=points[w,right])
   x['right_minus_left_cycles']=x.pop('F_minus_S_cycles')
   for k in list(x):
    if k.startswith('S_'):x['left_'+k[2:]]=x.pop(k)
    elif k.startswith('F_'):x['right_'+k[2:]]=x.pop(k)
  assert sum(x['right_minus_left_cycles'] for x in rr)==records[points[w,right]]['summary']['cycles']-records[points[w,left]]['summary']['cycles']
  timing.extend(rr)
 csvout('KERNEL_TIMING_AND_MECHANISM_DELTAS.csv',timing)
 stages=[]
 for w,profiles in [('dwt2d',['S','W_ONLY','F_MINUS_R','F']),('convolutionSeparable',['S','S_L2_DATA_FREE','F','F_L2_DATA_FREE']),('vectorAdd_4M',['S','F'])]:
  fs={p:[f for f in obs[w,p]['frames'] if f.get('kernel_name')] for p in profiles}
  assert all([f['kernel_name'] for f in v]==[f['kernel_name'] for f in fs[profiles[0]]] for v in fs.values())
  for n in range(len(fs[profiles[0]])):
   x=dict(workload=w,kernel_ordinal=n+1,kernel_name=fs[profiles[0]][n]['kernel_name'])
   for p in profiles:x[p]=fs[p][n]['gpu_sim_cycle']
   stages.append(x)
 csvout('FOCUSED_STAGE_CYCLES.csv',stages)
 # All explicit scalar snapshot increments, with OFF/missing UNKNOWN preserved.
 stagecounts=[]
 for (w,p),o in obs.items():
  for n,f in enumerate(o['frames']):
   for k,v in f['counter_snapshot_delta'].items():stagecounts.append(dict(workload=w,profile=p,attempt=points[w,p],snapshot_ordinal=n+1,kernel_name=f.get('kernel_name','FINAL_TERMINAL'),metric=k,value=v,scope='adjacent cumulative snapshot increments; waits nonexclusive'))
 csvout('ACCEPTED_STAGE_MECHANISMS.csv',stagecounts)
 save('DATA_VALIDATION.json',dict(all_E_declarations_projected=len(parsed),unique_accepted_endpoints=len(records),four_new_deliveries=4,main_pairs=5,all_same_main61=True,all_exact_endpoint_hashes=True,all_named_kernel_sequences_and_UIDs_equal=True,all_ten_contrast_elapsed_closures=True,raw_observed_new=sum(p['mode']=='NEW_ACCEPTED_RAW_OBSERVED_ONCE' for p in provenance),old_snapshots_reused=sum(p['mode']=='HASH_BOUND_SNAPSHOT_REUSED' for p in provenance),trace_reads=0,active_raw_reads=0,qualification_reexecution=False,old_E014_E027_E028_failures_not_used=True,negative_Vector_retained=True,original_seven_GM='UNKNOWN'))
 print(json.dumps(dict(main=mainrows,GM=gm,new_raw=[p['attempt_id'] for p in provenance if p['mode']=='NEW_ACCEPTED_RAW_OBSERVED_ONCE'],stages=stages),indent=2))
if __name__=='__main__':main()
