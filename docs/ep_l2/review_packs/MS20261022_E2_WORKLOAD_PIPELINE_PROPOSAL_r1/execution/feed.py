"""Finite approved workload feeder of the ORIGINAL E controller.

Run a sealed FWT-only queue immediately, or one sealed four-condition queue when
SGEMM own qualification is published. Never edit a running queue. A later phase
uses the same original controller API/lock after natural STOPPED; no app restart.
"""
from pathlib import Path
import argparse,importlib.util,json,subprocess,sys,threading,time
E=Path(__file__).resolve().parent;P=E.parent;ROOT=P.parents[3]
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,controller,runner,workload_policy as policy,capacity_policy,concurrency_policy
sp=importlib.util.spec_from_file_location('e2_workload_report',E/'report.py');report=importlib.util.module_from_spec(sp);sp.loader.exec_module(report)
def read(p):return json.loads(Path(p).read_text())
def checked(a):
 path=Path(a['path']);c.require(c.digest(path)==a['sha256'],'sealed artifact changed: '+str(path));return path

def published(commit,path):
 path=Path(path).resolve();relative=path.relative_to(ROOT).as_posix()
 c.require(subprocess.check_output(['git','-C',str(ROOT),'show',commit+':'+relative])==path.read_bytes(),'unpublished phase asset: '+relative)

def verify_plan(plan,coord):
 s=coord.snapshot();c.require(policy.active(s),'exact workload amendment not adopted')
 c.require(s['t0_unix']==plan['T0']==1792414193,'T0 changed')
 c.require(plan['source_identity']==policy.SOURCE and plan['maximum_new_actual_starts']==4,'wrong approved producer or batch')
 c.require(set(plan['authorized_exact_condition_ids'])==set(policy.CONDITIONS),'wrong four approved condition IDs')
 conditions=plan['conditions'];c.require(1<=len(conditions)<=4 and len({r['condition_id'] for r in conditions})==len(conditions),'phase condition count/duplicate')
 c.require(s['controller']['state']=='STOPPED' and s['uncertain_start_intents']==0,'controller active or unresolved start intent')
 data=read(c.SHARED/'RUN_REGISTRY.json')
 c.require(not any(r['status'] in c.ACTIVE and r.get('experiment_id')==c.CAMPAIGN for r in data['runs'].values()),'existing E native owns original work')
 queue=read(checked(plan['queue']));c.require(queue['specs']==[r['spec'] for r in conditions] and queue['pairs']==plan['pairs'],'queue/plan mismatch')
 for row in conditions:
  spec=read(checked(row['spec']));policy.basic_spec(spec)
  c.require(row['condition_id']==spec['condition_id'] and row['run_key']==c.run_key(spec['identity']),'wrong planned spec identity')
  c.require(policy.scope_allowed(s,spec),'exact condition not bound by original central authority')
  qpath=checked(row['qualification']);c.require(row['qualification_id']==c.digest(qpath)==spec['qualification_id'],'qualification binding changed')
  q=s['qualifications'].get(spec['qualification_id']);c.require(q and q['sha256']==c.digest(qpath) and q['qualification']['source_identity']==policy.SOURCE,'unregistered/wrong producer qualification')
  coord.require_no_hold(s,spec['qualification_id'])
  c.require(spec['profile_semantics']==q['qualification']['supported_profiles'][spec['profile']],'own profile qualification absent')
  existing=[a for a in s['attempts'][46:] if a.get('condition_id')==row['condition_id']]
  c.require(len(existing)<=1,'duplicate approved condition')
  if existing:c.require(existing[0]['state'] in ('COMPLETE_VALID','FAILED','INCOMPLETE','TIMEOUT','RESOURCE_LIMIT','CANCELLED_BEFORE_START'),'active condition cannot resume')
 c.require(concurrency_policy.resource_only(s,'simulation'),'original resource-only admission required')
 return queue

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--publication-commit',required=True)
 ap.add_argument('--execute-approved-workload-phase',action='store_true',required=True);args=ap.parse_args()
 coord=c.Coordinator();plan=read(args.plan);queue=verify_plan(plan,coord)
 subprocess.check_call(['git','-C',str(ROOT),'merge-base','--is-ancestor',args.publication_commit,'HEAD'])
 for path in [Path(__file__),E/'report.py',args.plan,checked(plan['queue']),P/'USER_APPROVAL.json']:
  published(args.publication_commit,path)
 for row in plan['conditions']:
  published(args.publication_commit,checked(row['spec']));published(args.publication_commit,checked(row['qualification']))
 original_roll=controller.roll_pairs
 def incremental(coord,requests):
  accepted=original_roll(coord,requests)
  for pair in accepted:report.checkpoint(pair['pair_id']+'_CURRENT_ACCEPTED',plan,pair)
  return accepted
 controller.roll_pairs=incremental
 original_execute=controller.execute;lock=threading.Lock()
 def guarded_execute(spec,coord):
  with lock:
   s=coord.snapshot();c.require(policy.active(s),'workload authority invalid');policy.batch_guard(s,spec)
   limits=capacity_policy.effective_limits(s);data=read(c.SHARED/'RUN_REGISTRY.json');resources=c.local_resources();usage=c.output_usage()
   pending=sum(max(0,r.get('disk_growth_bytes',c.FULL_GROWTH)-c.retained_tree_bytes(Path(r['result_directory']))) for r in data['runs'].values() if r['status'] in c.ACTIVE and r.get('experiment_id')==c.CAMPAIGN)
   pending+=sum(r.get('result_growth_bytes',0) for r in data['resource_leases'].values() if r['status'] in c.ACTIVE and r.get('experiment_id')==c.CAMPAIGN)
   margin=plan['collector_and_qualification_reserve_bytes']
   c.require(usage['new_bytes']+pending+spec['maximum_result_bytes']+margin<=limits['additional_results_max_bytes'] and usage['total_bytes']+pending+spec['maximum_result_bytes']+margin<=limits['old_plus_new_results_max_bytes'],'collector/qualification and endpoint cumulative growth reserve unavailable')
   c.resource_gate(data,'simulation',1,spec['memory_bytes'],spec['maximum_result_bytes'],resources,usage)
   c.write_json(E/(spec['condition_id']+'_ACTUAL_PRESTART_REVIEW.json'),dict(status='PASS_BEFORE_ORIGINAL_CONTENT_INSPECT_RESERVE_POPEN',at_unix=time.time(),
    actual_starts=s['actual_starts'],source_identity=policy.SOURCE,identity=spec['identity'],qualification_id=spec['qualification_id'],
    resources=resources,output_usage=usage,pending_result_reservations_bytes=pending,collector_and_qualification_reserve_bytes=margin,controller=s['controller']))
  return original_execute(spec,coord)
 controller.execute=guarded_execute
 result=controller.step(coord,checked(plan['queue']))
 dst=E/(args.plan.stem+'_CONTROLLER_RESULT.json');c.write_json(dst,result)
 report.checkpoint(args.plan.stem+'_CONTROLLER_TERMINAL',plan,extra=[dst,*E.glob('*_ACTUAL_PRESTART_REVIEW.json'),*E.glob('*_D_DELIVERY_RECEIPT.json')])
 print(json.dumps(dict(status='AUTHORIZED_PHASE_DRAINED_OR_PRECISE_LEGAL_STOP',controller=coord.snapshot()['controller'],result=result)),flush=True)
if __name__=='__main__':main()
