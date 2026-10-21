"""D-only projection of E-accepted capacity pairs. No new acceptor or execution."""
import argparse,datetime,hashlib,json,math,subprocess
from pathlib import Path
from zoneinfo import ZoneInfo
import sync_intake as intake
import full_v2_analysis as full
import control_incremental as inc
import paper_four_pair_details as detail
ROOT=Path(__file__).resolve().parents[3]
EP='docs/ep_l2/review_packs/MS20261021_E2_CAPACITY_DIAGNOSTIC_r1/'
def save(out,name,data):(out/name).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
def csvout(out,name,rows):
 import csv
 keys=list(dict.fromkeys(k for row in rows for k in row))
 with (out/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=keys,lineterminator='\n');w.writeheader();w.writerows(rows)
def aggregate(rows,key,operation):
 values=[r.get(key) for r in rows]
 if not values or not all(type(x) in (int,float) for x in values):return 'UNKNOWN'
 return {'min':min,'max':max,'sum':sum}[operation](values)
def git(commit,name):return subprocess.check_output(['git','show',commit+':'+EP+name],cwd=ROOT)
def analyze(commit,out,caches):
 if out.exists() and any(out.iterdir()):raise ValueError('Use a new revision; preserve old evidence')
 out.mkdir(parents=True,exist_ok=True)
 names=subprocess.check_output(['git','ls-tree','-r','--name-only',commit,EP],cwd=ROOT,text=True).splitlines()
 paths=[p for p in names if Path(p).name.startswith('CAPACITY_DIAGNOSTIC_') and p.endswith('_ACCEPTED_PAIR.json')]
 pairs={};frozen=[];refs={}
 for path in paths:
  name=Path(path).name;raw=git(commit,name);p=json.loads(raw)['accepted_pair']
  if p['status']!='CURRENT_ACCEPTED':continue
  assert p['pair_id']+'_ACCEPTED_PAIR.json'==name and p['accepted_by']=='E'
  (out/('E_'+name)).write_bytes(raw)
  frozen.append(dict(source_commit=commit,source_path=EP+name,local='E_'+name,sha256=hashlib.sha256(raw).hexdigest()))
  dn=p['pair_id']+'_D_DELIVERY_RECEIPT.json';dr=git(commit,dn);(out/('E_'+dn)).write_bytes(dr)
  frozen.append(dict(source_commit=commit,source_path=EP+dn,local='E_'+dn,sha256=hashlib.sha256(dr).hexdigest()))
  pairs[p['pair_id']]=p
  for x in p['endpoints'].values():
   if x['attempt_id'] in refs:assert refs[x['attempt_id']]==x
   refs[x['attempt_id']]=x
 perf=[];identities=[];timing=[];metrics=[];capacity=[];classes=[];supp=[];obs_prov=[];consumed=[]
 for pid,p in sorted(pairs.items()):
  row=intake.analyze_pair(pid,p,refs);assert row['status']=='E_ACCEPTED_D_ANALYZED'
  w=row['workload'];observations={};records={}
  for side,label in [('left','OFF'),('right','ON')]:
   ref=p['endpoints'][side];r=intake.pointer(ref);records[label]=r;i=r['identity']
   identities.append(dict(workload=w,condition=label,attempt_id=r['attempt_id'],accepted_receipt=ref,raw_sha256=r['raw_log_sha256'],run_key=r['run_key'],qualification_id=r['qualification_id'],identity=i,source_identity=r['source_identity'],labels=r['labels'],selection_id=r['selection_id'],comparison_invariants_sha256=r['comparison_invariants_sha256'],instructions=r['summary']['instructions'],wall_seconds=r['wall_seconds'],peak_process_tree_rss_bytes=r['peak_process_tree_rss_bytes']))
   o,prov=inc.cached_observation(dict(workload=w,profile=r['profile'],attempt_id=r['attempt_id']),r,caches,out)
   assert o['frames'][-1]['gpu_tot_sim_cycle']==r['summary']['cycles']
   observations[label]=o;obs_prov.append(prov);save(out,'OBSERVATIONS_'+r['attempt_id']+'.json',o)
   c=r['summary']['capacity_diagnostic'];cl=r['summary']['capacity_classification'];assert c['effective_master']==(label=='ON')
   classes.append(dict(workload=w,condition=label,attempt_id=r['attempt_id'],E_classification=cl['label'],E_classification_scope=cl.get('scope','OFF_NOT_APPLICABLE'),maximum_covered_bound_fraction=cl.get('maximum_measured_highwater_or_conservative_bound_fraction','UNKNOWN'),unknown_coverage=cl.get('unknown_coverage',[]),binding_resources=cl.get('binding_resources',[]),criterion=cl.get('criterion','OFF_NOT_APPLICABLE')))
   slices=c['slices'];assert len(slices)==64
   for key in sorted({k for s in slices.values() for k in s['resources']}):
    rr=[s['resources'][key] for s in slices.values() if key in s['resources']];covered=[x for x in rr if x.get('counter_covered')]
    capacity.append(dict(workload=w,condition=label,resource=key,slices=len(rr),covered_slices=len(covered),capacity_min=aggregate(rr,'capacity','min'),capacity_max=aggregate(rr,'capacity','max'),highwater_or_bound_min=aggregate(rr,'highwater','min'),highwater_or_bound_max=aggregate(rr,'highwater','max'),capacity_full_check_observations=aggregate(rr,'capacity_refusals','sum'),coverage_kinds=sorted({x['coverage_kind'] for x in rr}),scope='E decoded native counters; uncovered zero is not evidence of no refusals; per-slice peaks not simultaneous global peak'))
   ss=r['summary'];tags=ss['native_capacity_records'].get('tag_replacements',{})
   supp.append(dict(workload=w,condition=label,wb_created=ss['wb_created'],wb_lower_accepted=ss['wb_lower_accepted'],wb_completed=ss['wb_completed'],unique_requesters=ss['unique_requesters'],responses=ss['responses'],payload_free=ss['payload_free'],payload_roles=ss['payload_roles'],tag_replacement_records=tags,unchanged_local_service=r['mechanism_metrics'].get('unchanged_local_service',{})))
  a,b=row['baseline_cycles'],row['variant_cycles'];assert (a,b)==(p['cycles_left'],p['cycles_right'])
  perf.append(dict(workload=w,pair_id=pid,OFF_attempt=row['baseline_attempt_id'],ON_attempt=row['variant_attempt_id'],OFF_cycles=a,ON_cycles=b,ON_minus_OFF_cycles=b-a,ratio_OFF_over_ON=a/b,speedup_percent=100*(a/b-1),cycle_change_percent=100*(b/a-1),ON_classification=records['ON']['summary']['capacity_classification']['label'],binary=row['binary'],core=row['core'],framework=row['framework'],trace=row['trace'],OFF_config_sha256=row['baseline_config'],ON_config_sha256=row['variant_config'],OFF_receipt_sha256=row['baseline_receipt_sha256'],ON_receipt_sha256=row['variant_receipt_sha256'],instructions_each=row['baseline_instructions']))
  so,fo=observations['OFF'],observations['ON']
  assert [x.get('kernel_launch_uid') for x in so['frames'] if x.get('kernel_name')]==[x.get('kernel_launch_uid') for x in fo['frames'] if x.get('kernel_name')]
  rr=detail.paired_timing(w,{'S':so,'F':fo})
  for r in rr:
   r['ON_minus_OFF_cycles']=r.pop('F_minus_S_cycles');r['pair_id']=pid
   for k in list(r):
    if k.startswith('S_'):r['OFF_'+k[2:]]=r.pop(k)
    elif k.startswith('F_'):r['ON_'+k[2:]]=r.pop(k)
  assert sum(r['ON_minus_OFF_cycles'] for r in rr)==b-a;timing.extend(rr)
  for r in full.mechanism_table(row):
   r['OFF']=r.pop('S');r['ON']=r.pop('F');r['ON_minus_OFF']=r.pop('F_minus_S');metrics.append(r)
  consumed.append(dict(status='CONSUMED',pair_id=pid,E_commit=commit,endpoints=p['endpoints'],cycles_OFF_ON=[a,b],ON_classification_preserved=records['ON']['summary']['capacity_classification']['label'],kernel_elapsed_closure=True,acceptance_owner='E',D_native_qualification=False))
 csvout(out,'DIAGNOSTIC_PERFORMANCE.csv',perf);csvout(out,'DIAGNOSTIC_KERNEL_AND_MECHANISM_DELTAS.csv',timing);csvout(out,'DIAGNOSTIC_TERMINAL_MECHANISMS.csv',metrics);csvout(out,'RESOURCE_CAPACITY_EVIDENCE.csv',capacity)
 save(out,'EXACT_ACCEPTED_IDENTITIES.json',identities);save(out,'E_CAPACITY_CLASSIFICATIONS.json',classes);save(out,'SUPPLEMENTAL_FINAL_COUNTS.json',supp);save(out,'FROZEN_E_INDEX.json',frozen)
 gm=math.exp(sum(math.log(x['ratio_OFF_over_ON']) for x in perf)/len(perf)) if perf else 'UNKNOWN'
 summary=dict(observed_BJT=datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),E_commit=commit,consumed_pairs=len(perf),diagnostic_subset_members=[x['workload'] for x in perf],diagnostic_subset_GM=gm,complete_five_diagnostic_GM=gm if len(perf)==5 else 'UNKNOWN',main61_five_MAIN_GM_unchanged=0.9977331348587999,original_seven_MAIN_GM='UNKNOWN',classification_authority='E',snapshot_provenance=obs_prov,application_starts=0,native_runs=0,builds=0,trace_reads=0,active_raw_reads=0,registry_writes=0,controller_actions=0,background_poller=False,scope='Joint capacity/data-service diagnostic only; no hardware performance upper bound or additive stall attribution')
 save(out,'SUMMARY.json',summary);save(out,'CONSUMED.json',dict(status='CONSUMED',E_commit=commit,pairs=consumed,main61_unchanged=True,pending_missing_pairs=[w for w in ['convolutionSeparable','cfd_097k','dwt2d','sad','vectorAdd_4M'] if w not in summary['diagnostic_subset_members']],new_acceptor=False,read_only_E_evidence=True))
 save(out,'FILES_SHA256.json',{p.name:intake.digest(p) for p in out.iterdir() if p.is_file() and p.name!='FILES_SHA256.json'})
 print(json.dumps(dict(consumed=summary['consumed_pairs'],performance=perf,timing=[{k:r[k] for k in ['workload','kernel_ordinal','OFF_gpu_sim_cycle','ON_gpu_sim_cycle','ON_minus_OFF_cycles']} for r in timing]),indent=2))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--e-commit',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--cache',type=Path,action='append',default=[]);a=p.parse_args();analyze(a.e_commit,a.out,a.cache)
if __name__=='__main__':main()
