#!/usr/bin/env python3
"""CPU only; never invoke live native, modify live holds, stop or launch."""
import sys,copy,tempfile,types,os,json,time
from pathlib import Path as P
D=P(__file__).parent;sys.path.insert(0,str(D));import finite_main_concurrency10 as C
E=C.E;B=P(tempfile.mkdtemp(prefix='CPU_ONLY_',dir=D));checks=[]
def ck(name,ok=True):assert ok,name;checks.append(dict(name=name,status='PASS'))
def reject(name,fn):
 try:fn()
 except Exception:ck(name);return
 raise AssertionError('not rejected '+name)
ck('cap10_global9_accept10th',C.concurrency_capacity(9,0,10));ck('cap10_global10_reject11th',not C.concurrency_capacity(10,0,10));ck('cap10_local10_reject11th',not C.concurrency_capacity(9,10,10));reject('dynamic11_forbidden',lambda:C.concurrency_capacity(0,0,11))
previous=E.read(C.V/'activation_20261104_v1/recovery_20261104_v1/control/EXACT_EXECUTION_MANIFEST.json');o=C.Executor10.__new__(C.Executor10);o.m=copy.deepcopy(previous);o.C=B/'control';o.C.mkdir();o.points=o.m['points'];o.bypoint={p['cohort']:p for p in o.points};o.specs={p['cohort']:E.exact(p['spec_ref'])for p in o.points};o.manifest_path=B/'manifest.json';E.put(o.manifest_path,o.m);o.states={};o.running={};o.pending_accept=[];o.started=time.monotonic();o.lastresource={};o.session='CPU_ONLY';o.failures={};o.fatal=[];o.phase_cache={}
ck('default_cap10_no_mutation',o.effective_cap()==10);policy=dict(approved_by='EP-MAIN',manifest_ref=E.ref(o.manifest_path),max_concurrent_models=6);E.put(o.C/'MAIN_MODEL_CONCURRENCY_POLICY.json',policy);ck('Main_can_lower_cap_to6',o.effective_cap()==6);policy['max_concurrent_models']=11;E.put(o.C/'MAIN_MODEL_CONCURRENCY_POLICY.json',policy);reject('Main_policy_cannot_exceed_user10',o.effective_cap);(o.C/'MAIN_MODEL_CONCURRENCY_POLICY.json').unlink()
# Actual start method, private claim/native leaves, global nine FOREIGN EP models.
reg=dict(registered_future_requests={'EP_CPU_FOREIGN':dict(consumed={str(i):dict(state='RUNNING')for i in range(9)})});rr={};o.rows=lambda:(reg,rr);o.technical_holds=lambda:set();claims=[];native=[];o.claim=lambda p,cpu:claims.append(p['cohort']);o.group_call=lambda *a,**k:types.SimpleNamespace(returncode=0,stdout='',stderr='');o.release_unconsumed_claim=lambda p:None
class FakeProcess:
 pid=os.getpid()
def fake_native(op,c,**kw):native.append(c);reg['registered_future_requests']['EP_CPU_FOREIGN']['consumed']['NEW']=dict(state='RUNNING');return FakeProcess()
o.native=fake_native;oldadmission=C.ADMISSION;oldnas=C.nas_capacity_gate;C.ADMISSION=B/'admission.lock';C.nas_capacity_gate=lambda s:dict(status='CPU_ONLY_NAS_PASS')
try:
 p=o.points[0];ck('actual_start9_foreign_allows10th',o.start(p));ck('actual_start10_foreign_rejects11th',not o.start(o.points[1]));ck('reject11th_before_claim_or_fork',len(claims)==1 and len(native)==1)
finally:C.ADMISSION=oldadmission;C.nas_capacity_gate=oldnas
for r in o.running.values():r['log'].close()
o.running={};o.native=C.Executor10.native.__get__(o,C.Executor10);o.m['preserved_consumed_spec_refs']={o.points[0]['cohort']:o.points[0]['spec_ref']};reject('preserved_consumed_no_run_or_reaccept',lambda:o.native('run-native',o.points[0]['cohort']))
# Actual immutable-stage migration uses the REAL qualified production gate read-only.
# Only a private copy's controller_manifest_ref differs; original review kept byte-identical.
hroot=P(previous['groups']['highclock']['data_root']);actual=hroot/'control/NEW_SOURCE_850_PAIR_MAIN_REVIEW.json';oldhash=E.sha(actual);review=E.read(actual);private_h=B/'highclock';dest=private_h/'control/NEW_SOURCE_850_PAIR_MAIN_REVIEW.json';E.put(dest,review);o.m['groups']['highclock']['data_root']=str(private_h);o.group_call=C.Executor10.group_call.__get__(o,C.Executor10)
new=copy.deepcopy(review);new['controller_manifest_ref']=E.ref(o.manifest_path);oldprivate=E.sha(dest);r=o.immutable(dest,new);ck('inherited_B850_controller_change_verified_actual_engine_no_rewrite',r['sha256']==oldprivate and E.sha(dest)==oldprivate and E.sha(actual)==oldhash)
bad=copy.deepcopy(new);bad['source_identity']=dict(bad['source_identity'],binary_sha256='0'*64);reject('inherited_stage_wrong_Source_rejected',lambda:o.immutable(dest,bad));bad=copy.deepcopy(new);bad['accepted_point_refs']['S']=bad['accepted_point_refs']['F'];reject('inherited_stage_wrong_point_population_rejected',lambda:o.immutable(dest,bad))
oldcall=o.group_call;o.group_call=lambda *a,**k:types.SimpleNamespace(returncode=2,stderr='CPU_ONLY_ACTUAL_GATE_REJECT',stdout='');reject('inherited_actual_gate_reject_failclosed',lambda:o.immutable(dest,new));o.group_call=oldcall
ck('existing_review_original_provenance_and_SHA_preserved',E.read(dest)['controller_manifest_ref']==review['controller_manifest_ref']and E.sha(actual)==oldhash)
# Stage math retained; cap is not extra science authorization.
ck('B1700_still_exact1p03',not E.high1700_gate(102999,100000,100000,100000)and E.high1700_gate(103000,100000,100000,100000));ck('combo_absolute_EP_not_Sratio',not E.system_combo_gate(100000,100001,100000));ck('source_scope18_stillfixed',C.BUDGETS==dict(system=12,highclock=6)and len(C.SYSTEM|C.HIGH)==18)
ck('explicit_amendment_checked_manifest_and_activation',P(C.__file__).read_text().count("concurrency_amendment_authorization_ref")>=5)
# Pure FWT predecessor gate still requires archived terminal quartet; failure does
# not count as accepted for combos but can complete the input before GEMM.
rows={};views={};specs=o.specs;refs={w:dict(cycles=100000)for w in ['FWT','GEMM']}
for c in C.SYSTEM:
 if C.system_meta(c)[0]=='FWT'and C.system_meta(c)[1]!='G64W16_FRFCFS256':rows[c]=dict(state='CLOSED_UNACCEPTED');views[c]=dict(archived=True,accepted=False)
pol=E.evaluate_policy(o.points,rows,views,specs,refs);ck('FWT_earlier_archived_negative_allows_GEMM',all(pol[c]['status']=='RELEASE'for c in C.SYSTEM if C.system_meta(c)[0]=='GEMM'and C.system_meta(c)[1]!='G64W16_FRFCFS256'));ck('failed_FWT_never_releases_combo',all(pol[c]['status']=='HOLD'for c in C.SYSTEM if C.system_meta(c)==('FWT','G64W16_FRFCFS256')))
# Static actual loop/start call sites ensure cap is read under same admission,
# with original locks/publisher/1800sec and no hidden fixed2 launch loop.
code=P(C.__file__).read_text();ck('actual_loop_uses_effective_cap',"while len(self.running)<self.effective_cap()"in code and'if not concurrency_capacity(count,len(self.running),cap)'in code);ck('global_locks_and_one_publisher_preserved',C.OWNERSHIP==E.OWNERSHIP and C.GITLOCK==E.GITLOCK and'>=1800'in code)

# Actual idle-handoff activation: private snapshots retain two REAL accepted
# points, but no real registry or process state is modified.
regreal=E.authority();fake=dict(registered_future_requests={});initial=set(C.R.INITIAL)
for g,qid in C.REQUESTS.items():
 q=copy.deepcopy(regreal['registered_future_requests'][qid]);q['consumed']={c:r for c,r in q['consumed'].items()if c in initial};q['remaining']=C.BUDGETS[g]-len(q['consumed']);fake['registered_future_requests'][qid]=q
z=C.Executor10.__new__(C.Executor10);z.__dict__=copy.deepcopy({k:v for k,v in o.__dict__.items()if k not in ['native','rows','group_call','claim','release_unconsumed_claim']});z.C=B/'idle';z.C.mkdir();z.m=copy.deepcopy(previous);z.m['predecessor_manifest_ref']=E.ref(C.V/'activation_20261104_v1/recovery_20261104_v1/control/EXACT_EXECUTION_MANIFEST.json');z.m['preserved_consumed_spec_refs']={c:z.bypoint[c]['spec_ref']for c in initial};z.m['concurrency_amendment_authorization_ref']=E.ref(C.CONTROL/'USER_CONCURRENCY10_AUTHORIZATION.json');z.manifest_path=B/'idle-manifest.json';E.put(z.manifest_path,z.m);z.rows=lambda:(fake,{c:r for q in fake['registered_future_requests'].values()for c,r in q['consumed'].items()});z.initial_consumed=sorted(initial);z.running={};z.states={};z.pending_accept=[]
clrefs={}
for g in C.REQUESTS:
 z.m['groups'][g]['data_root']=str(B/'idle'/g);clrefs[g]=E.put(B/'idle'/g/'control/DISPATCH_CLAIMS.json',dict(claims={}))
E.put(z.manifest_path,z.m);snapref=E.put(B/'idle-snapshot.json',dict(requests=fake['registered_future_requests']));started=E.put(B/'old-start.json',dict(manifest_ref=z.m['predecessor_manifest_ref'],process=dict(pid=99999999,start_ticks=0,state='Z')))
a=dict(schema='EP_MAIN_V2_CAP10_IDLE_HANDOFF_ACTIVATION_V1',status='MAIN_REVIEWED_IDLE_OWNER_CAP10_HANDOFF_AUTHORIZED',approved_by='EP-MAIN',executor_ref=E.ref(C.__file__),manifest_ref=E.ref(z.manifest_path),no_retry=True,no_refund=True,concurrency_amendment_authorization_ref=z.m['concurrency_amendment_authorization_ref'],predecessor_started_ref=started,consumed_snapshot_ref=snapref,claims_snapshot_refs=clrefs);E.put(z.C/'MAIN_CAP10_IDLE_HANDOFF_AUTHORIZATION.json',a)
z.check_activation();ck('actual_idle_activation_two_archived_claims0_original_budget')
bad=copy.deepcopy(a);bad['concurrency_amendment_authorization_ref']=started;E.put(z.C/'MAIN_CAP10_IDLE_HANDOFF_AUTHORIZATION.json',bad);reject('activation_missing_cap10_amendment_rejected',z.check_activation);E.put(z.C/'MAIN_CAP10_IDLE_HANDOFF_AUTHORIZATION.json',a)
live=E.put(B/'live-start.json',dict(manifest_ref=z.m['predecessor_manifest_ref'],process=E.pid_identity(os.getpid())));bad=copy.deepcopy(a);bad['predecessor_started_ref']=live;E.put(z.C/'MAIN_CAP10_IDLE_HANDOFF_AUTHORIZATION.json',bad);reject('old_controller_still_live_rejects_cap10_handoff',z.check_activation);E.put(z.C/'MAIN_CAP10_IDLE_HANDOFF_AUTHORIZATION.json',a)
g='system';clpath=B/'idle'/g/'control/DISPATCH_CLAIMS.json';E.put(clpath,dict(claims={'CPU_ONLY_LIVE':dict()}));reject('nonempty_claims_rejects_idle_handoff',z.check_activation);E.put(clpath,dict(claims={}))
class Loop(C.Executor10):
 def __init__(self):
  self.__dict__=copy.deepcopy({k:v for k,v in z.__dict__.items()if k!='rows'});self.C=B/'loop';self.C.mkdir();self.running={};self.pending_accept=[];self.states={};self.m['accept_serial_lock']=str(self.C/'accept.lock');self.fake=copy.deepcopy(fake);self.calls=[];self.archived=set(initial);self.maximum=0;self.started=time.monotonic();self.lastpublish=time.monotonic();self.session='CPU_ONLY_LOOP'
 def rows(self):return self.fake,{c:r for q in self.fake['registered_future_requests'].values()for c,r in q['consumed'].items()}
 def check_activation(self):pass
 def start(self,p):
  c=p['cohort'];assert c not in self.rows()[1];g=p['group'];q=self.fake['registered_future_requests'][C.REQUESTS[g]];q['consumed'][c]=dict(state='RUNNING');q['remaining']-=1;self.running[c]=dict(cpu=self.available_cpu());self.maximum=max(self.maximum,len(self.running));self.calls.append(c);return True
 def poll(self):
  for c in list(self.running):self.running.pop(c);self.pending_accept.append(c);self.rows()[1][c]['state']='COMPLETED'
 def accept_one(self):
  if not self.pending_accept:return
  c=self.pending_accept.pop(0);assert c not in initial;self.rows()[1][c]['state']='CLOSED_UNACCEPTED';self.archived.add(c)
 def closed_view(self,c,row):
  if c in initial:return E.Executor.closed_view(self,c,row)
  return dict(archived=c in self.archived,accepted=False)
 def publish(self,final=False):self.lastpublish=time.monotonic();E.put(self.C/'REMOTE_PUBLICATION_RECEIPT.json',dict(final=final,HEAD='CPU_ONLY',remote_HEAD='CPU_ONLY'))
 def archive_summary(self):pass
loop=Loop();oldowner=C.OWNERSHIP;oldadmission=E.ADMISSION;sleep=C.time.sleep;C.OWNERSHIP=B/'owner.lock';E.ADMISSION=B/'emitadmission.lock';C.time.sleep=lambda _:None
try:loop.run()
finally:C.OWNERSHIP=oldowner;E.ADMISSION=oldadmission;C.time.sleep=sleep
ck('actual_cap10_loop_more_than2_when_ready_gates_allow',loop.maximum>2 and loop.maximum<=10);ck('actual_cap10_loop_never_reforks_previous_consumed',not(set(loop.calls)&initial));ck('actual_cap10_loop_finite_scope_failure_no_refund',len(loop.calls)==8 and all(loop.rows()[1][c]['state']=='CLOSED_ACCEPTED'for c in initial)and loop.fake['registered_future_requests'][C.REQUESTS['system']]['remaining']==4 and loop.fake['registered_future_requests'][C.REQUESTS['highclock']]['remaining']==4)
ck('actual_cap10_loop_source_and_stage_summary',E.read(loop.C/'RESULTS_CURRENT.json')['authorized_max_global_EP_models']==10 and (loop.C/'EXECUTOR_FINISHED.json').exists());reject('actual_duplicate_cap10_loop_rejected',loop.run)

E.put(D/'ACTUAL_CONCURRENCY10_CPU_CONTROLS.json',dict(status='PASS',count=len(checks),controls=checks,executor_ref=E.ref(C.__file__),private_fixture=str(B),original_inherited_review_ref=E.ref(actual),scientific_starts=0,native_invocations=0,live_hold_writes=0,registry_writes=0,Git_writes=0));print(json.dumps(dict(status='PASS',count=len(checks))))
