"""Finite4 metadata completion using the frozen original finish_evidence API.

Never calls run_cell, experiment, prepare, run_native, or an authority writer.
Original V2 consumer keeps running; its per-point lock serializes completion.
"""
import pathlib,json,hashlib,importlib.util,fcntl,os,time,argparse,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');R=F/'validation';O=F/'ops'
REQ='DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1';BINDING=O/'REPAIR_COMPLETION_ADOPTER_BINDING_V1.json';PUB=O/'REPAIR_COMPLETION_ADOPTER_PUBLICATION_READBACK_V1.json';QUAL=O/'REPAIR_COMPLETION_ADOPTER_CPU_QUALIFICATION_V1.json'
CELLS=['E2-AEREPAIR-977e34578994c3d2-CH-V1','E2-AEREPAIR-977e34578994c3d2-DM-V1','E2-AEREPAIR-09f94fcc7494a03b-DM-V1','E2-AEREPAIR-09f94fcc7494a03b-DH-V1']
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,value):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def forbidden(*a,**k):raise RuntimeError('scientific execution forbidden in metadata adopter')
def bound(execute=False):
 b=read(BINDING);assert b['schema']=='FINITE4_FROZEN_FINISH_EVIDENCE_METADATA_ADOPTION_BINDING_V1' and set(b['points'])==set(CELLS) and b['request']==REQ and b['wrapper_sha256']==sha(__file__)
 for pin in b['source_pins']:assert sha(pin['path'])==pin['sha256'],('source changed',pin['path'])
 engine=load('adopter_readonly_engine',R/'tools/repair_native_v1.py');outbox=load('adopter_pinned_outbox',R/'tools/repair_outbox_v1.py');strict=load('adopter_pinned_strict',R/'tools/repair_strict_v1.py');ops=load('adopter_pinned_finish',R/'tools/repair_ops_v1.py')
 assert sha(R/'tools/repair_ops_v1.py')=='6493e48b9083e09e58dbd02b6ae8ee10113b089d66199ee1cf6670daafe5251b'
 assert sha(R/'tools/repair_strict_v1.py')=='f9fb0385e69e2265c933c9d827ce0c4da1c0a5de67eb506613d74f8182f6831e'
 ops.run_cell=forbidden
 q=engine.registered()[2];assert q['budget']==23 and q['remaining']==0 and len(q['consumed'])==23
 if execute:
  p=read(PUB);qualification=read(QUAL);assert p['verified'] and p['commit'] and p['tool_sha256']==sha(__file__) and p['qualification_sha256']==sha(QUAL) and p['binding_sha256']==sha(BINDING)
  assert qualification['status']=='PASS' and qualification['wrapper_sha256']==sha(__file__) and qualification['binding_sha256']==sha(BINDING)
 return b,engine,outbox,strict,ops
def model_state(pid,start):
 try:
  fields=(P('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()
  return 'RECORDED_GENERATION_ALIVE_OR_ZOMBIE' if int(fields[19])==start else 'RECORDED_GENERATION_GONE_PID_REUSED'
 except (FileNotFoundError,ProcessLookupError):return 'RECORDED_GENERATION_GONE'
def launcher_absent(pid):return not (P('/proc')/str(pid)).exists()
def context(cell,b,engine):
 assert cell in CELLS and cell in b['points'];point=b['points'][cell];q=engine.registered()[2];row=q['consumed'][cell]
 sp=R/'control/specs'/(cell+'.json');ip=R/'control/qualification_ledger'/(cell+'.INTENT.json');dp=ip.with_name(cell+'.DONE.json');s=read(sp);i=read(ip);out=P(i['output']);launch=read(out/'NATIVE_LAUNCH.json');pid=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')
 assert s.get('validation_kind')!='COMPONENT_SENTINEL_NOT_FORMAL' and s['request']==REQ and s['cohort']==cell
 assert sha(sp)==q['admitted_specs'][cell]==point['spec_sha256'] and sha(ip)==row['intent_sha256']==point['intent_sha256']
 assert i['uuid']==row['uuid']==point['uuid'] and out==R/'DTC/run/results'/row['uuid'] and i['cohort']==cell
 assert sha(out/'NATIVE_LAUNCH.json')==point['launch_sha256'] and sha(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')==point['pid_receipt_sha256']
 assert (pid['pid'],pid['start_ticks'],launch['launcher_pid'])==(point['model_pid'],point['model_start_ticks'],point['launcher_pid'])
 if not dp.exists() or 'execution_receipt' not in row:return {'state':'WAIT_REAL_DONE_AND_EXECUTION_RECEIPT','cohort':cell}
 done=read(dp);assert done==row['execution_receipt']==read(out/'NATIVE_EXIT.json') and done['cohort']==cell and done['uuid']==row['uuid'] and done['output']==str(out)
 assert done['actual_simulator_wait_and_file_evidence'] and done['launcher_is_strace_parent_of_native_simulator'] is True
 assert done['stop_reason'] is None and done['launcher_wait_returncode']==0 and done['native_simulator_observed'] is True,'non-natural completion requires independent negative review; never promote'
 if model_state(pid['pid'],pid['start_ticks'])=='RECORDED_GENERATION_ALIVE_OR_ZOMBIE' or not launcher_absent(launch['launcher_pid']):return {'state':'WAIT_MODEL_AND_STRACE_LAUNCHER_EXIT','cohort':cell}
 return {'state':'CLOSED_NATIVE_EVIDENCE_READY','cohort':cell,'uuid':row['uuid'],'out':str(out),'DONE_path':str(dp),'DONE_sha256':sha(dp),'model_pid':pid['pid'],'model_start_ticks':pid['start_ticks'],'launcher_pid':launch['launcher_pid'],'launcher_start_ticks':'NOT_CAPTURED; require PID entirely absent, never synthesize a generation','spec_sha256':sha(sp),'intent_sha256':sha(ip)}
def completed(cell,ctx,outbox):
 rp=R/'analysis'/(cell+'.RESULT.json');ap=R/'control'/(cell+'_ARCHIVE_RECEIPT.json');out=P(ctx['out']);sp=out/'REPAIR_STRICT.json';qp=R/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json')
 if not rp.exists():return None
 result=read(rp);assert result['cohort']==cell and result['uuid']==ctx['uuid'] and result['state']=='PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE' and result['accepted_cycles'] is None and result['correctness_validation_only'] is True
 assert ap.exists() and sp.exists() and qp.exists(),'existing RESULT incomplete/conflicting; require review'
 proof=read(sp);qualification=read(qp);assert result['proof']==proof and proof['cohort']==cell and proof['uuid']==ctx['uuid'] and proof['accepted_cycles'] is None and proof['correctness_validation_passed'] and proof['status']=='REPAIR_CORRECTNESS_VALIDATED_NOT_ORIGINAL_PERFORMANCE' and proof['strict_overlay_sha256']==sha(R/'tools/repair_strict_v1.py')
 assert qualification=={'status':'REPAIR_CORRECTNESS_VALIDATED_NOT_ORIGINAL_PERFORMANCE','cohort':cell,'uuid':ctx['uuid'],'strict_sha256':sha(sp),'accepted_cycles':None,'correctness_validation_only':True,'SOURCE_KEEP':True}
 verified=outbox.verify(cell);assert result['archive']==verified and verified['receipt']['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'
 return {'state':'EXISTING_FROZEN_FINISH_RESULT_AND_ARCHIVE_VERIFIED','cohort':cell,'uuid':ctx['uuid'],'RESULT_path':str(rp),'RESULT_sha256':sha(rp),'archive':verified,'model_starts':0}
def inspect(cell,b,engine,outbox,strict,full=False):
 ctx=context(cell,b,engine)
 if ctx['state']!='CLOSED_NATIVE_EVIDENCE_READY':return ctx
 existing=completed(cell,ctx,outbox)
 if existing:return existing
 ap=R/'control'/(cell+'_ARCHIVE_RECEIPT.json');out=P(ctx['out']);sp=out/'REPAIR_STRICT.json';qp=R/'DTC/control'/('SCIENCE_QUALIFICATION_'+cell+'.json');archive=None
 if ap.exists():
  assert sp.exists() and qp.exists(),'archive exists without exact original proof/qualification; cannot append archived out'
  archive=outbox.verify(cell);oldproof=read(sp);qualification=read(qp);assert oldproof['cohort']==cell and oldproof['uuid']==ctx['uuid'] and oldproof['accepted_cycles'] is None and oldproof['correctness_validation_passed'] and oldproof['status']=='REPAIR_CORRECTNESS_VALIDATED_NOT_ORIGINAL_PERFORMANCE' and oldproof['strict_overlay_sha256']==sha(R/'tools/repair_strict_v1.py')
  assert qualification=={'status':'REPAIR_CORRECTNESS_VALIDATED_NOT_ORIGINAL_PERFORMANCE','cohort':cell,'uuid':ctx['uuid'],'strict_sha256':sha(sp),'accepted_cycles':None,'correctness_validation_only':True,'SOURCE_KEEP':True}
 if full:
  proof=strict.terminal(cell);assert proof['uuid']==ctx['uuid'] and proof['accepted_cycles'] is None and proof['correctness_validation_passed'] and proof['strict_overlay_sha256']==sha(R/'tools/repair_strict_v1.py')
  if archive is not None:assert proof==oldproof
  ctx['readonly_full_frozen_strict_proof']=proof
 return dict(ctx,state='READY_FROZEN_METADATA_FINISH_ONLY',archive_already_exists=archive is not None)
def adoption_path(cell):return R/'analysis/completion_adoption_v1'/(cell+'.ADOPTION_RECEIPT.json')
def execute_point(cell,b,engine,outbox,strict,ops):
 lockpath=R/'analysis/postprocess_v2'/(cell+'.METADATA_CONSUMER.lock');lockpath.parent.mkdir(parents=True,exist_ok=True)
 with lockpath.open('a+b') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:return {'state':'WAIT_SHARED_V2_POINT_LOCK','cohort':cell}
  item=inspect(cell,b,engine,outbox,strict,False)
  if item['state']!='READY_FROZEN_METADATA_FINISH_ONLY':return item
  # Source mutation (if any) is done only by the actual frozen finish function.
  # Do not hold CLOSED_COPY.lock: pinned archive takes that different lock itself.
  result=ops.finish_evidence(cell)
  checked=completed(cell,context(cell,b,engine),outbox);assert checked and checked['uuid']==item['uuid'] and result['archive']==checked['archive']
  receipt={'schema':'FINITE4_METADATA_COMPLETION_ADOPTION_RECEIPT_V1','cohort':cell,'uuid':item['uuid'],'wrapper_sha256':sha(__file__),'binding_sha256':sha(BINDING),'frozen_finish_source_sha256':sha(R/'tools/repair_ops_v1.py'),'strict_source_sha256':sha(R/'tools/repair_strict_v1.py'),'actual_executor':'CURRENT_METADATA_ONLY_ADOPTER_CALLING_ORIGINAL_FROZEN_FINISH_EVIDENCE; not retired R14 controller','prior_canonical_RESULT_absent':True,'native_evidence':item,'result':checked,'model_starts':0,'new_INTENT_or_DONE_or_wait_status_created':False,'old_spent_or_authority_mutations':0,'accepted_cycles':None,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  put(adoption_path(cell),receipt);return checked
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true');ap.add_argument('--full-review',action='store_true');args=ap.parse_args();b,engine,outbox,strict,ops=bound(args.execute)
 if not args.execute:print(json.dumps([inspect(c,b,engine,outbox,strict,args.full_review) for c in CELLS],indent=2));return
 assert not args.full_review
 with (O/'REPAIR_COMPLETION_ADOPTER_SINGLETON.lock').open('a+b') as singleton:
  fcntl.flock(singleton,fcntl.LOCK_EX|fcntl.LOCK_NB);start=time.monotonic()
  while True:
   bound(True);finished=[]
   for cell in CELLS:
    # Unexpected error is fatal, with no loop retry or model restart. Existing
    # published evidence can only be reverified on a separately reviewed resume.
    result=execute_point(cell,b,engine,outbox,strict,ops)
    if result['state']=='EXISTING_FROZEN_FINISH_RESULT_AND_ARCHIVE_VERIFIED':finished.append(cell)
   if len(finished)==4:print(json.dumps({'state':'FINITE4_METADATA_FINISH_ARCHIVE_RESTORE_VERIFIED','cohorts':finished,'V2_consumer_continues_independent_closure':True,'model_starts':0}),flush=True);return
   assert time.monotonic()-start<7*86400,'finite metadata wait expired';time.sleep(10)
if __name__=='__main__':main()
