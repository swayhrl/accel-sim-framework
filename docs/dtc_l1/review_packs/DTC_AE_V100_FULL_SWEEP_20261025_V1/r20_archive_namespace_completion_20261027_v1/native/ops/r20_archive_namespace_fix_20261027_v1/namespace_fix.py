"""R20 metadata-only COPY namespace reconciliation. Frozen sources stay pinned."""
import pathlib,json,hashlib,importlib.util,copy,sys,os,time,threading,datetime,fcntl
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');R=F/'validation_storage_recovery12_v1';D=F/'ops/r20_archive_namespace_fix_20261027_v1';REQ='DTC_AE_STORAGE_RECOVERY12_20261026_V1';PARENT=F/'ops/revision20/sweep_controller.py';PARENT_SHA='de715b527c6194a65b30d0b921c34a26bc8af4433eddd78c957d98c123723c81'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def need(v,msg):
 if not v:raise RuntimeError(msg)
def load(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def identity(f):return dict(filename=f.__code__.co_filename,name=f.__code__.co_name)
def write(p,x):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x')as f:json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def plan():
 p=read(D/'PLAN.json');need(p['source_sha256']==sha(__file__),'source drift');need(sha(p['policy_path'])==p['policy_sha256'],'policy drift');return p
def corrected_outbox(module,p):
 need(str(P(module.__file__))==p['outbox_path']and sha(module.__file__)==p['outbox_sha256'],'unexpected outbox source');need(str(module.NAS)in[p['frozen_outbox_NAS'],p['pinned_policy_NAS']],'unknown archive namespace drift');module.NAS=P(p['pinned_policy_NAS']);return module
def make_loader(original,p):
 def loader(name,file):
  module=original(name,file)
  return corrected_outbox(module,p)if file=='recovery12_outbox_v1.py'else module
 return loader
def verify_one(cell,p,do_copy=False):
 item=p['points'][cell];engine=load('namespace_fix_engine',R/'tools/recovery12_native_v1.py');reg,epoch,q,execution=engine.registered();row=q['consumed'][cell];ip=R/'control/qualification_ledger'/(cell+'.INTENT.json');dp=ip.with_name(cell+'.DONE.json');intent=read(ip);done=read(dp);out=P(intent['output']);need(row['uuid']==item['uuid']==intent['uuid']==done['uuid']and row['intent_sha256']==sha(ip),'UUID/INTENT mismatch');need(done==row['execution_receipt']==read(out/'NATIVE_EXIT.json')and done['stop_reason']is None and done['launcher_wait_returncode']==0,'no actual clean native completion');need(sha(R/'analysis'/(cell+'.RESULT.json'))==item['old_RESULT_sha256'],'old engineering preimage drift')
 strict=load('namespace_fix_independent_strict',R/'tools/recovery12_strict_v1.py').terminal(cell);need(read(out/'REPAIR_STRICT.json')==strict and strict['correctness_validation_passed']and strict['accepted_cycles']is None,'actual full strict replay differs');ob=corrected_outbox(load('namespace_fix_private_outbox',P(p['outbox_path'])),p);ap=R/'control'/(cell+'_ARCHIVE_RECEIPT.json')
 if do_copy and not ap.exists():ob.archive(cell)
 archive=ob.verify(cell)if ap.exists()else None
 return dict(cohort=cell,uuid=row['uuid'],strict=strict,strict_sha256=sha(out/'REPAIR_STRICT.json'),archive=archive,old_RESULT_sha256=item['old_RESULT_sha256'],old_RESULT_preserved=True,accepted_cycles=None,never_merge_into_original288=True)
def apply_archives():
 p=plan();qual=read(D/'CPU_QUALIFICATION.json');need(qual['status']=='PASS'and qual['source_sha256']==sha(__file__)and qual['plan_sha256']==sha(D/'PLAN.json'),'qualification mismatch');lock=(D/'APPLY.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);results=[]
 # Replay every target before the first COPY, keeping true strict failures separate.
 for c in p['points']:verify_one(c,p,False)
 for c,item in p['points'].items():
  proof=verify_one(c,p,True);need(proof['archive']is not None,'archive not verified');closed=dict(proof,state='PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE',schema='R20_CORRECTED_NAMESPACE_INDEPENDENT_POSTPROCESS_V1',source_sha256=sha(__file__),plan_sha256=sha(D/'PLAN.json'),policy_sha256=p['policy_sha256'],actual_copy_namespace=p['pinned_policy_NAS'],old_error='COPY namespace not the pinned namespace',model_starts=0,model_retries=0,scientific_source_or_ledger_mutations=0,utc=datetime.datetime.now(datetime.timezone.utc).isoformat());dest=D/'points'/item['uuid'];backup=dest/'OLD_ENGINEERING_RESULT.PREIMAGE.json'
  if backup.exists():need(sha(backup)==item['old_RESULT_sha256'],'stored preimage changed')
  else:backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes((R/'analysis'/(c+'.RESULT.json')).read_bytes())
  target=dest/'POSTPROCESS.RESULT.json'
  if target.exists():stored=read(target);need(all(stored[k]==closed[k]for k in closed if k!='utc'),'postprocess conflict');closed=stored
  else:write(target,closed)
  results.append(dict(cohort=c,uuid=item['uuid'],postprocess_path=str(target),postprocess_sha256=sha(target),verified_entries=proof['archive']['independently_verified_restored_entries']));print(json.dumps(results[-1]),flush=True)
 summary=dict(status='ALL_TARGET_REAL_STRICT_ARCHIVE_NATIVE_RESTORE_PASS',results=results,source_sha256=sha(__file__),plan_sha256=sha(D/'PLAN.json'),models_started=0,old_RESULTs_preserved=True)
 if not(D/'ACTUAL_ARCHIVE_RESULTS.json').exists():write(D/'ACTUAL_ARCHIVE_RESULTS.json',summary)
 return summary
def install_parent():
 need(threading.current_thread()is threading.main_thread(),'main thread only');p=plan();qual=read(D/'CPU_QUALIFICATION.json');need(qual['status']=='PASS'and qual['source_sha256']==sha(__file__)and qual['plan_sha256']==sha(D/'PLAN.json'),'qualification mismatch');lease=read(T/'control/BATCH_LEASE.json');st=P('/proc/self/stat').read_text().rsplit(')',1)[1].split();need((os.getpid(),int(st[19]),lease['pid'],lease['start_ticks'])==(p['parent_pid'],p['parent_start_ticks'],p['parent_pid'],p['parent_start_ticks'])and sha(PARENT)==PARENT_SHA,'wrong metadata parent generation');frame=sys._getframe()
 while frame and not(frame.f_code.co_name=='main'and frame.f_globals.get('__file__')==str(PARENT)):frame=frame.f_back
 need(frame is not None,'exact parent frame absent');g=frame.f_globals;l=frame.f_locals;ops=l['ops'];need(sha(ops.__file__)==p['ops_sha256'],'worker source drift');ackpath=D/'ACTUAL_PARENT_ACK.json'
 if g.get('_R20_ARCHIVE_NAMESPACE_FIX_STATE'):
  saved=g['_R20_ARCHIVE_NAMESPACE_FIX_STATE'];need(saved==read(ackpath)and saved['plan_sha256']==sha(D/'PLAN.json'),'incompatible installed correction');return saved
 need(identity(ops.load)==p['expected_ops_loader'],'unexpected prior worker loader');oldloader=ops.load;oldresults=copy.deepcopy(l['results'][REQ]);oldblocked=set(l['blocked'][REQ]);newresults={}
 for c,item in p['points'].items():
  need(c in oldresults and oldresults[c]['state']=='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS'and c in oldblocked,'not exact blocked completed point');need(not any(x['cell']==c for x in l['running'].values()),'target still active');closed=read(D/'points'/item['uuid']/'POSTPROCESS.RESULT.json');need(closed['source_sha256']==sha(__file__)and closed['old_RESULT_sha256']==item['old_RESULT_sha256']and closed['state']=='PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE'and closed['accepted_cycles']is None,'missing independently verified closure');newresults[c]=closed
 replacement=make_loader(oldloader,p);ack=dict(status='ACTUAL_R20_PARENT_NAMESPACE_AND_FINITE_RESULT_JOIN_INSTALLED',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_pid=os.getpid(),parent_start_ticks=p['parent_start_ticks'],source_sha256=sha(__file__),plan_sha256=sha(D/'PLAN.json'),old_loader=identity(oldloader),new_loader=identity(replacement),corrected_namespace=p['pinned_policy_NAS'],completed_points=sorted(newresults),old_canonical_RESULTs_preserved=True,scientific_source_or_ledger_mutations=0,model_starts=0,model_signals=0);created=False
 try:
  ops.load=replacement;l['results'][REQ].update(newresults);l['blocked'][REQ].difference_update(newresults)
  with ackpath.open('x')as f:created=True;json.dump(ack,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 except BaseException:
  ops.load=oldloader;l['results'][REQ].clear();l['results'][REQ].update(oldresults);l['blocked'][REQ].clear();l['blocked'][REQ].update(oldblocked)
  if created:ackpath.unlink()
  raise
 g['_R20_ARCHIVE_NAMESPACE_FIX_STATE']=ack;return ack
if __name__=='__main__':print(json.dumps(apply_archives(),indent=2))
