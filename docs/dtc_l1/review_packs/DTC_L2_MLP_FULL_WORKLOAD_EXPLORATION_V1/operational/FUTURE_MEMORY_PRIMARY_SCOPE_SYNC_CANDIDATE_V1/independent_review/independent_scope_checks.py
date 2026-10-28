from pathlib import Path as P
import json,hashlib,importlib.util,types,tempfile,copy,threading,time
B=P(__file__).parent;sp=importlib.util.spec_from_file_location('B_scope_sync_limited',B/'scope_sync.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);read=lambda p:json.loads(P(p).read_bytes());sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest();checks=[]
def put(p,v):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(m.raw(v))
def ck(n,v):assert v,n;checks.append(n)
def make_case():
 root=P(tempfile.mkdtemp(prefix='B_CPU_SCOPE_',dir=B));mp=root/'ACTIVE_MEMORY.json';old=dict(request=m.REQ,overlay_id='MEM',scope_mode='ALL_UNSPENT_FUTURE',allowed_cohorts=['OLD'],source='same');new=dict(old,allowed_cohorts=['OLD','PRIMARY']);put(mp,old);record=lambda c:dict(request=c['request'],overlay_id=c['overlay_id'],scope_mode=c['scope_mode'],allowed_cohorts=c['allowed_cohorts']);oldrec=dict(record(old),status='ACTIVE',publication={'commit':'preserve-exact','unknown_nested':[1,{'x':2}]},other_extra='KEEP');newrec=copy.deepcopy(oldrec);newrec.update(record(new));q=dict(admitted_specs={'OLD':'S','PRIMARY':'S'},additional_operational_overlays={'MEM':oldrec},reserved_model_starts=999,consumed={'LIVE':{'uuid':'unchanged'}});reg=dict(registered_future_requests={m.REQ:q});memory={'lib':types.SimpleNamespace(ID='MEM',record=record),'context':{'cfg':old}};calls=[]
 def auth(fn):calls.append('AUTHORITY');fn(reg)
 def update(cfg,ownerassert):ownerassert();memory['context']['cfg']=cfg
 s=m.ScopeSync.__new__(m.ScopeSync);s.cfg=dict(source_sha256=sha(B/'scope_sync.py'),memory_active_path=str(mp),preserved_nonprimary_cohorts=['R2']);s.memory=memory;s.engine=types.SimpleNamespace(update_authority=auth);s.owner_module=types.SimpleNamespace(update_scope_in_owner=update);s.check=lambda:(q,{});evidence={'PRIMARY':{'cohort':'PRIMARY','complete':'CPU_MOCK'}};s.committed=lambda:(q,evidence);s.stable_memory=lambda:(q,memory['context']['cfg']);s.checkpoint=lambda phase:None
 tx=dict(schema=m.ID,source_sha256=s.cfg['source_sha256'],old_config=old,new_config=new,old_config_utf8=mp.read_bytes().decode('utf-8'),old_config_sha256=sha(mp),new_config_sha256=hashlib.sha256(m.raw(new)).hexdigest(),old_record=oldrec,new_record=newrec,added_cohorts=['PRIMARY'],committed_evidence=[evidence['PRIMARY']],request_paths=[]);return root,s,tx,q,calls,mp
root,s,tx,q,calls,mp=make_case();p=root/'transactions'/m.digest(tx)/'PREPARED.json';put(p,tx);before={k:copy.deepcopy(v)for k,v in q.items()if k!='additional_operational_overlays'};ack=s.apply_transaction(p,lambda:None);ck('actual_apply_transaction_preserves_full_MEM_unknown_provenance_and_budget',q['additional_operational_overlays']['MEM']==tx['new_record']and {k:v for k,v in q.items()if k!='additional_operational_overlays'}==before and ack['grants_added']==0)
root,s,tx,q,calls,mp=make_case();tx['new_record'].pop('publication');p=root/'transactions'/m.digest(tx)/'PREPARED.json';put(p,tx)
try:s.apply_transaction(p,lambda:None);rejected=False
except AssertionError as e:rejected='MEMORY_PROVENANCE_CHANGED'in str(e)
ck('rehashed_transaction_dropping_full_unknown_MEM_provenance_rejected_before_authority',rejected and not calls)
root,s,tx,q,calls,mp=make_case();p=root/'transactions'/m.digest(tx)/'PREPARED.json';put(p,tx)
def fault(phase):
 if phase=='AFTER_AUTHORITY':raise OSError('CPU_INTERRUPTED_AFTER_AUTHORITY')
s.checkpoint=fault
try:s.apply_transaction(p,lambda:None)
except OSError:pass
s.checkpoint=lambda p:None;ack=s.apply_transaction(p,lambda:None);ck('metadata_forward_recovery_after_authority_no_repeated_authority_or_grant',calls==['AUTHORITY']and read(mp)==tx['new_config']and ack['grants_added']==0 and p.with_name('ACK.json').exists())
root,s,tx,q,calls,mp=make_case();tx['old_config_utf8']='{}';p=root/'transactions'/m.digest(tx)/'PREPARED.json';put(p,tx)
try:s.apply_transaction(p,lambda:None);rejected=False
except AssertionError:rejected=True
ck('rehashed_transaction_with_false_exact_ACTIVE_preimage_rejected',rejected and not calls)
# Real selection filter only: no old chooser dispatches and no model is created.
root,s,tx,q,calls,mp=make_case();s.enabled=True;s.root=root;s.directory=root;s.recovery_tick=lambda:None;s.stable_memory=lambda:(q,dict(tx['new_config']));put(root/'control/SCOPE.json',dict(points=[{'cohort':'OLD'}]));pendingtx=root/'transactions/CPU_UNACKED/PREPARED.json';put(pendingtx,{'added_cohorts':['PRIMARY']});s.prior_choose=lambda pending,*a:[x['cohort']for x in pending];pending=[dict(cohort=x)for x in ['OLD','PRIMARY','R2','UNREGISTERED']];v=s.choose(pending,{}, {},[]);ck('before_ACK_newprimary_blocked_R2_and_initial_preserved',v==['OLD','R2']);put(pendingtx.with_name('ACK.json'),{});v=s.choose(pending,{}, {},[]);ck('after_ACK_only_explicit_primary_scope_can_pass_old_gates',v==['OLD','PRIMARY','R2'])
# Actual CPython pending-call API, no owner/controller attachment.
seen=[];queue=m.RetainedMainQueue(lambda:seen.append(threading.get_ident())or{'status':'CPU_MAIN_DRAIN_ONLY'});worker=threading.Thread(target=lambda:queue('/CPU/REQUEST'));worker.start();worker.join();deadline=time.monotonic()+2
while queue.pending and time.monotonic()<deadline:time.sleep(.01)
ck('retained_real_PyAddPendingCall_runs_only_Main_without_model',seen==[threading.main_thread().ident]and queue.last_error is None and queue.last_result=={'status':'CPU_MAIN_DRAIN_ONLY'})
report=dict(schema='B_SCOPE_SYNC_LIMITED_INDEPENDENT_CPU_CHECKS_V1',status='PASS_FINAL_SOURCE_LIMITED_CPU_CHECKS',source_sha256=sha(B/'scope_sync.py'),checks=checks,passed=len(checks),authority_memory_and_oldchooser_are_explicit_private_CPU_mocks=True,real_PyAddPendingCall_exercised_in_isolated_B_process=True,production_mutations=0,owner_attaches=0,model_starts=0,signals=0);put(B/'INDEPENDENT_CPU_CHECKS.json',report);print(json.dumps(report))
