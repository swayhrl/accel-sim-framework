#!/usr/bin/env python3
"""Private CPU only. No science registration, native invocation, Git, or real controls."""
import sys,os,json,hashlib,subprocess,tempfile,copy,importlib.util,time,tarfile,io,ast
from pathlib import Path as P
D=P(__file__).parent;sys.path.insert(0,str(D));import finite_main_authorized18 as E
A=D.parent;manifest=A/'control/EXACT_EXECUTION_MANIFEST.json';results=[]
def ck(name,ok=True,detail=None):
 assert ok,name
 results.append(dict(name=name,status='PASS',detail=detail))
def rejected(name,fn):
 try:fn()
 except Exception as e:ck(name,True,type(e).__name__+':'+str(e)[-240:]);return
 raise AssertionError('not rejected '+name)
def module(root,name):
 for key in list(sys.modules):
  q=getattr(sys.modules[key],'__file__',None)
  if q and ('qualified_runtime' in q or key.startswith('ep_perf_') or key=='mode_contract'):sys.modules.pop(key,None)
 sys.path.insert(0,str(root));return __import__(name)
def work(root,fn):
 s=importlib.util.spec_from_file_location('privatework',fn);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 return m
obj=E.Executor(manifest);ck('real18_manifest_passive_prepare',len(obj.points)==18)
ck('actual_FWT256_plus_highclock128_not_duplicate384',max(s['limits']['result_bytes']for c,s in obj.specs.items()if c in E.SYSTEM)==256*E.M and max(s['limits']['result_bytes']for c,s in obj.specs.items()if c in E.HIGH)==128*E.M)
from types import SimpleNamespace
ns=SimpleNamespace(f_bavail=300*E.M,f_frsize=1,f_flag=0);mount=dict(source='admin-wcx@10.208.130.164:/home/shared',fstype='fuse.sshfs');fwtspec=next(s for c,s in obj.specs.items()if c in E.SYSTEM and '_FWT_'in c)
ck('fresh_NAS_actual_FWT256_plus_metadata_pass',E.nas_capacity_gate(fwtspec,mount,ns)['archive_increment_plus_metadata_bytes']==258*E.M)
rejected('fresh_NAS_full_rejected_before_consume',lambda:E.nas_capacity_gate(fwtspec,mount,SimpleNamespace(f_bavail=257*E.M,f_frsize=1,f_flag=0)))
rejected('fresh_NAS_wrong_source_rejected',lambda:E.nas_capacity_gate(fwtspec,dict(source='TEST_ONLY_WRONG',fstype='fuse.sshfs'),ns))
rejected('fresh_NAS_readonly_rejected',lambda:E.nas_capacity_gate(fwtspec,mount,SimpleNamespace(f_bavail=300*E.M,f_frsize=1,f_flag=1)))
B=P(tempfile.mkdtemp(prefix='CPU_ONLY_',dir=D));E.put(B/'TEST_ONLY.json',dict(no_science_start=True,authority_writes=False,all_acceptances_synthetic=True))
original_admission=E.ADMISSION;original_ownership=E.OWNERSHIP;E.ADMISSION=B/'ADMISSION.lock';E.OWNERSHIP=B/'OWNER.lock'
# Preserve every formal spec byte, relocate only test refs/roots.
obj.C=B/'central';obj.C.mkdir();obj.m=copy.deepcopy(obj.m);obj.m['control_root']=str(obj.C);obj.m['accept_serial_lock']=str(obj.C/'ACCEPT_SERIAL.lock')
for g in E.REQUESTS:obj.m['groups'][g]['data_root']=str(B/g)
for p in obj.points:
 original=P(p['spec_ref']['path']);dest=B/p['group']/'cases'/p['cohort']/'control/FROZEN_SPEC.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(original.read_bytes());p['spec_ref']=E.ref(dest)
obj.bypoint={p['cohort']:p for p in obj.points};obj.specs={p['cohort']:E.exact(p['spec_ref'])for p in obj.points};obj.manifest_path=B/'TEST_MANIFEST.json';E.put(obj.manifest_path,obj.m)
reg=dict(registered_future_requests={gqid:dict(budget=E.BUDGETS[g],remaining=E.BUDGETS[g],admitted_specs={p['cohort']:p['spec_ref']['sha256']for p in obj.points if p['group']==g},consumed={})for g,gqid in E.REQUESTS.items()})
rows={};views={};refs=obj.system_refs()
def accepted(c,cycles):
 p=obj.bypoint[c];s=obj.specs[c];g=p['group'];uid='CPU_ONLY_'+c;out=B/g/'synthetic'/c;out.mkdir(parents=True,exist_ok=True)
 ar=dict(status='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS',cohort=c,uuid=uid,source_keep=True,archive_ref=dict(path='/root/share/mnt164/TEST_ONLY_NEVER_CREATED/'+c,sha256='a'*64),native_restores=[dict(status='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS',target='/TEST_ONLY/'+c+'/'+lab,restore_label=lab,archive_sha256='a'*64)for lab in ['FIRST','INDEPENDENT']])
 pt=dict(status='EP_FULL_PERF_APPLICATION_ACCEPTED',cohort=c,mode=s['mode'],source_identity=s['source_identity'],input_identity_sha256=s['input_identity_sha256'],uuid=uid,spec_ref=p['spec_ref'],cycles=cycles,hardware_drained=True,instructions=s['expected_instructions'],CTA=s['expected_CTA'],kernel_count=1)
 row=dict(state='CLOSED_ACCEPTED',uuid=uid,accepted_point_ref=E.put(out/'point.json',pt),archive_receipt_ref=E.put(out/'archive.json',ar));rows[c]=row;reg['registered_future_requests'][E.REQUESTS[g]]['consumed'][c]=row;views[c]=obj.closed_view(c,row)
for c in E.SYSTEM:
 w,f=E.system_meta(c)
 if f!='G64W16_FRFCFS256':accepted(c,max(1,refs[w]['cycles']*98//100))
for m in ['S','F']:
 accepted(f'EP_PERF_CC_CAM_VECTOR4M_{m}_850_V1',100000)
 accepted(f'EP_PERF_CC_CAM_VECTOR4M_{m}_1275_V1',97000 if m=='S'else 99500)
policy=E.evaluate_policy(obj.points,rows,views,obj.specs,refs)
ck('four_combo_and_two_1700_release',all(policy[c]['status']=='RELEASE'for c in E.SYSTEM if E.system_meta(c)[1]=='G64W16_FRFCFS256')and all(policy[f'EP_PERF_CC_CAM_VECTOR4M_{m}_1700_V1']['status']=='RELEASE'for m in ['S','F']))
obj.emit_stage_receipts(policy,views,refs,rows,only_group='system');obj.emit_stage_receipts(policy,views,refs,rows,only_group='highclock');ck('actual_only_group_emit_api')
Croot=P(obj.m['groups']['system']['runtime_root']);Broot=P(obj.m['groups']['highclock']['runtime_root']);C=module(Croot,'mode_contract')
for c in E.SYSTEM:
 if E.system_meta(c)[1]=='G64W16_FRFCFS256':
  q=C.validate_combo_release(obj.specs[c],reg,B/'system/control/conditional_release'/(c+'.json'),data_root=B/'system');ck('producer_to_actual_C_gate_'+c,q['status']=='ABSOLUTE_EP_COMBINATION_CRITERION_PASS')
c=next(c for c in E.SYSTEM if E.system_meta(c)==('FWT','G64W16_FRFCFS256'));qreg=copy.deepcopy(reg);failc=next(c for c in E.SYSTEM if E.system_meta(c)==('FWT','G64W16')and obj.specs[c]['mode']=='S');qreg['registered_future_requests'][E.REQUESTS['system']]['consumed'][failc]['state']='CLOSED_UNACCEPTED'
rejected('C_actual_gate_one_unaccepted_blocks_combo',lambda:C.validate_combo_release(obj.specs[c],qreg,B/'system/control/conditional_release'/(c+'.json'),data_root=B/'system'))
badspec=copy.deepcopy(obj.specs[c]);badspec['source_identity']['core_source_commit']='0'*40
rejected('C_actual_gate_wrong_Source',lambda:C.validate_combo_release(badspec,reg,B/'system/control/conditional_release'/(c+'.json'),data_root=B/'system'))
H=module(Broot,'ep_perf_native_wv_modes_draft');H.ROOT=B/'highclock';hq=reg['registered_future_requests'][E.REQUESTS['highclock']]
for f in [850,1275,1700]:
 for m in ['S','F']:
  c=f'EP_PERF_CC_CAM_VECTOR4M_{m}_{f}_V1';r=H.enforce_stage_gates(obj.specs[c],hq,reg);ck('producer_to_actual_B_gate_'+m+'_'+str(f),r['status']in ['FRESH_NEW_SOURCE_850_PAIR_NO_ACCEPTED_ANCHOR_REQUIRED','NEW_SOURCE_HIGH_CLOCK_PRECURSOR_GATE_PASS'])
c='EP_PERF_CC_CAM_VECTOR4M_F_1700_V1';badq=copy.deepcopy(hq);badq['consumed']['EP_PERF_CC_CAM_VECTOR4M_S_850_V1']['state']='CLOSED_UNACCEPTED'
rejected('B_actual_gate_one850_failure_holds_high',lambda:H.enforce_stage_gates(obj.specs[c],badq,reg))
badq=copy.deepcopy(hq);badq['consumed']['EP_PERF_CC_CAM_VECTOR4M_S_1275_V1']['accepted_point_ref']=badq['consumed']['EP_PERF_CC_CAM_VECTOR4M_S_850_V1']['accepted_point_ref']
rejected('B_actual_gate_1275_wrong_spec_population',lambda:H.enforce_stage_gates(obj.specs[c],badq,reg))
# Pure policies: local failure isolation, negative outcomes archived permit next input.
r0={};v0={};p0=E.evaluate_policy(obj.points,r0,v0,obj.specs,refs)
ck('initial850_and_FWT_only',sum(x['status']=='RELEASE'for x in p0.values())==6)
rr=copy.deepcopy(rows);vv=copy.deepcopy(views);rr[failc]['state']='CLOSED_UNACCEPTED';vv[failc]['accepted']=False
pp=E.evaluate_policy(obj.points,rr,vv,obj.specs,refs);ck('FWT_archived_unaccepted_does_not_block_GEMM_singles',all(pp[c]['status']=='RELEASE'for c in E.SYSTEM if E.system_meta(c)[0]=='GEMM'and E.system_meta(c)[1]!='G64W16_FRFCFS256'))
ck('FWT_failed_single_does_block_its_combo',all(pp[c]['status']=='HOLD'for c in E.SYSTEM if E.system_meta(c)==('FWT','G64W16_FRFCFS256')))
vv[failc]['archived']=False;pp=E.evaluate_policy(obj.points,rr,vv,obj.specs,refs);ck('FWT_unarchived_blocks_GEMM',all(pp[c]['status']=='WAIT'for c in E.SYSTEM if E.system_meta(c)[0]=='GEMM'and E.system_meta(c)[1]!='G64W16_FRFCFS256'))
rr=copy.deepcopy(rows);rr['EP_PERF_CC_CAM_VECTOR4M_S_850_V1']['state']='CLOSED_UNACCEPTED';pp=E.evaluate_policy(obj.points,rr,views,obj.specs,refs);ck('high_failure_does_not_globalblock_system',all(pp[c]['status']=='RELEASE'for c in E.SYSTEM if E.system_meta(c)[1]!='G64W16_FRFCFS256')and pp['EP_PERF_CC_CAM_VECTOR4M_S_1275_V1']['status']=='HOLD')
ck('combo_requires_absolute_EP_not_S_ratio',not E.system_combo_gate(100000,100001,100000))
ck('combo_exact_threshold',E.system_combo_gate(100000,99000,99000)and not E.system_combo_gate(100000,99001,99000))
ck('1700_exact_speedup_ratio_not_cyclepercent',E.high1700_gate(103000,100000,100000,100000)and not E.high1700_gate(102999,100000,100000,100000))
ck('S_only_1700_trigger_not_EP_success',E.high1700_gate(103000,100000,100000,100001))
# Check actual immutable common/archive locks from both runtimes in isolated processes.
worker=D/'lock_worker.py';worker.write_text(r"""import sys,json,time,os,hashlib,tarfile,io
from pathlib import Path as P
root,test,kind,label=sys.argv[1:];sys.path.insert(0,root);import ep_perf_common_v2 as c;import ep_perf_archive as a
b=P(test);assert str(c.GLOBAL_MAIN_ADMISSION_LOCK).endswith('execution_performance_first_20261103_v1/control/ADMISSION.lock');assert str(c.GLOBAL_MAIN_RESTORE_WINDOW_LOCK).endswith('execution_performance_first_20261103_v1/control/ARCHIVE_SHARED_WINDOW.lock')
log=b/(kind+'.jsonl')
def event(x):
 with log.open('a')as f:f.write(json.dumps(dict(event=x,label=label,time=time.monotonic_ns()))+'\n')
if kind=='admission':
 with c.locked(b/'global_admission.lock'):event('ENTER');time.sleep(.06);event('EXIT')
else:
 a.GLOBAL_MAIN_RESTORE_WINDOW_LOCK=b/'global_restore.lock'
 def body(case):
  event('ENTER');p=b/label;p.mkdir();data=('TEST_ONLY_'+label).encode();tar=p/'tiny.tar';h=hashlib.sha256(data).hexdigest()
  with tarfile.open(tar,'w')as t:
   ti=tarfile.TarInfo('payload.txt');ti.size=len(data);t.addfile(ti,io.BytesIO(data))
  mf=p/'manifest.json';mf.write_text(json.dumps(dict(archive_sha256=a.sha(tar),members=[dict(member='payload.txt',bytes=len(data),sha256=h,uid=os.getuid(),gid=os.getgid(),mode=0o600,atime_ns=1700000000000000000,mtime_ns=1700000000000000000)])))
  for i in range(2):
   r=a.restore(tar,mf,p/('native'+str(i)),1024);assert r['status']=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS';time.sleep(.03)
  with c.locked(b/'global_admission.lock'):pass
  event('EXIT');return dict(status='CPU_ONLY_TWO_REAL_RESTORES_PASS')
 a._archive_case=body
 assert a.archive_case('TEST_ONLY')['status']=='CPU_ONLY_TWO_REAL_RESTORES_PASS'
print('PASS')
""")
locks=B/'locks';locks.mkdir();runtimepins=[]
for root in [Croot,Broot]:
 for name in ['ep_perf_common_v2.py','ep_perf_archive.py','ep_perf_native_wv_modes_draft.py']:runtimepins.append(E.ref(root/name))
 for textname,phrase in [('ep_perf_native_wv_modes_draft.py','with locked(GLOBAL_MAIN_ADMISSION_LOCK)'),('ep_perf_archive.py','with locked(GLOBAL_MAIN_RESTORE_WINDOW_LOCK)')]:ck('actual_runtime_lock_site_'+root.parent.name+'_'+textname,phrase in (root/textname).read_text())
ck('actual_consume_and_claim_update_two_global_lock_sites',all((r/'ep_perf_native_wv_modes_draft.py').read_text().count('with locked(GLOBAL_MAIN_ADMISSION_LOCK)')>=2 for r in [Croot,Broot]))
for kind in ['admission','archive']:
 ps=[subprocess.Popen([sys.executable,'-B',str(worker),str(root),str(locks),kind,kind+str(i)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)for i,root in enumerate([Croot,Broot,Croot,Broot])]
 for p in ps:
  stdout,stderr=p.communicate(timeout=30);assert p.returncode==0,(stdout,stderr)
 ev=sorted([json.loads(x)for x in (locks/(kind+'.jsonl')).read_text().splitlines()],key=lambda x:x['time']);active=0;maximum=0
 for x in ev:active+=1 if x['event']=='ENTER'else-1;maximum=max(active,maximum);assert active in [0,1]
 ck('multiprocess_actual_crossfamily_'+kind+'_mutex',maximum==1 and active==0,dict(processes=4,maximum_critical=maximum,events=ev))
# Actual bounded native-accept control, with private fake leaf returning states.
ac=E.Executor.__new__(E.Executor);ac.__dict__=obj.__dict__.copy();ac.C=B/'accept-control';ac.C.mkdir();(ac.C/'native_logs').mkdir();ac.pending_accept=['EP_PERF_CC_CAM_VECTOR4M_S_850_V1'];ac.states={};ac.running={};ac.m=copy.deepcopy(obj.m);ac.m['accept_serial_lock']=str(ac.C/'distinct-accept-serial.lock');ac.arows={};ac.native_calls=[]
case=ac.pending_accept[0];done=E.put(B/'done.json',dict(TEST_ONLY=True));ac.arows[case]=dict(state='COMPLETED',done_ref=done);E.put(B/'highclock/control/DISPATCH_CLAIMS.json',dict(claims={}))
ac.rows=lambda:({},ac.arows)
class Leaf:
 def __init__(self,n):self.n=n
 def wait(self):
  ac.arows[case]['state']='PARSE_HOLD'if self.n==1 else'CLOSED_UNACCEPTED';return 2 if self.n==1 else 0
def fake_native(op,c,**kwargs):
 assert op=='accept'and c==case;ac.native_calls.append(op);return Leaf(len(ac.native_calls))
ac.native=fake_native;ac.accept_one()
ck('actual_accept_bounded_one_archive_only_native_closure',len(ac.native_calls)==2 and ac.arows[case]['state']=='CLOSED_UNACCEPTED'and (ac.C/'ARCHIVE_ONLY_CLOSURES'/(case+'.json')).exists())
ac.arows[case]['state']='PARSE_HOLD';E.put(B/'highclock/control/DISPATCH_CLAIMS.json',dict(claims={case:dict(model_pid=os.getpid(),model_start_ticks=E.pid_identity(os.getpid())['start_ticks'])}))
rejected('actual_archive_only_rejects_live_model_generation',lambda:ac.archive_only_safe(case,ac.arows[case]))
ck('archive_only_uses_distinct_parent_lock',ac.m['accept_serial_lock']!=str(E.RESTORE)and ac.m['accept_serial_lock']!=str(E.ADMISSION))
# Real run loop with private fake native leafs; no processes or authority mutations.
class Loop(E.Executor):
 def __init__(self):
  self.__dict__=copy.deepcopy({k:v for k,v in obj.__dict__.items()if k not in ['running']});self.running={};self.pending_accept=[];self.C=B/'loop';self.C.mkdir();self.m['accept_serial_lock']=str(self.C/'accept.lock');self.started=time.monotonic();self.lastpublish=time.monotonic();self.fake={};self.calls=[];self.fakebudget=dict(system=12,highclock=6);self.fakeconsume=dict(system=0,highclock=0);self.done={};self.session='TEST_ONLY_LOOP';self.manifest_path=B/'TEST_MANIFEST.json'
 def check_activation(self):self.calls.append('TEST_ONLY_ACTIVATION_NO_REGISTRATION')
 def rows(self):return dict(registered_future_requests={qid:dict(budget=E.BUDGETS[g],remaining=self.fakebudget[g],state='TEST_ONLY')for g,qid in E.REQUESTS.items()}),self.fake
 def start(self,p):
  c=p['cohort'];assert c not in self.fake;assert len(self.running)<2;assert self.available_cpu()is not None;g=p['group'];self.fakebudget[g]-=1;self.fakeconsume[g]+=1;self.fake[c]=dict(state='RUNNING');self.running[c]=dict(cpu=self.available_cpu());self.calls.append('fake-native-leaf:'+c);return True
 def poll(self):
  for c in list(self.running):
   self.running.pop(c);self.pending_accept.append(c);self.fake[c]['state']='COMPLETED'
 def accept_one(self):
  if not self.pending_accept:return
  c=self.pending_accept.pop(0);self.fake[c]=dict(state='CLOSED_UNACCEPTED');self.done[c]=True
 def closed_view(self,c,row):return dict(archived=c in self.done,accepted=False)
 def publish(self,final=False):self.calls.append('fake-publication-final'if final else'fake-publication');self.lastpublish=time.monotonic();E.put(self.C/'REMOTE_PUBLICATION_RECEIPT.json',dict(final=final,HEAD='TEST_ONLY',remote_HEAD='TEST_ONLY'))
 def archive_summary(self):self.calls.append('fake-summary-archive-no164write')
loop=Loop();sleep=E.time.sleep;E.time.sleep=lambda _:None
try:loop.run()
finally:E.time.sleep=sleep
ck('actual_runloop_only_group_and_inherited_event_cpu_summary_interfaces',bool((loop.C/'EXECUTOR_FINISHED.json').exists())and all('LOCAL_STAGE_RECEIPT_HOLD'not in str(x)for x in loop.states.values()))
ck('runloop_failed_consumed_not_refunded_or_retried',loop.fakeconsume==dict(system=8,highclock=2)and loop.fakebudget==dict(system=4,highclock=4)and len([x for x in loop.calls if x.startswith('fake-native-leaf')])==10)
ck('runloop_other_input_after_archived_negative',any('_GEMM_'in x for x in loop.calls))
ck('runloop_initial_final_sameowner_publication',loop.calls.count('fake-publication-final')==1 and loop.calls.count('fake-publication')>=1)
ck('half_hour_publication_interval_remains1800','>=1800'in P(E.__file__).read_text())
rejected('runloop_duplicate_start_receipt_failclosed',lambda:loop.run())
# Inherited archive interface is deliberately failclosed on a fake non164 mount;
# real restore path already executed above in private storage.
orig=E.base.subprocess.check_output;E.base.subprocess.check_output=lambda *a,**k:json.dumps(dict(filesystems=[dict(source='TEST_ONLY',fstype='tmpfs')]))
try:rejected('inherited_archive_summary_interface_genuine164_guard',lambda:E.base.Executor.archive_summary(loop))
finally:E.base.subprocess.check_output=orig
# Unconsumed/consumed guard is before claim or native leaf.
origrows=obj.rows;obj.rows=lambda:(reg,rows);obj.technical_holds=lambda:set();obj.lastresource={};obj.running={};origcpu=obj.available_cpu;obj.available_cpu=lambda:0
rejected('actual_start_rejects_consumed_before_any_native_fork',lambda:obj.start(next(p for p in obj.points if p['cohort']in rows)))
E.ADMISSION=original_admission;E.OWNERSHIP=original_ownership
out=dict(schema='EP_MAIN_EXACT18_PRIVATE_CPU_CONTROLS_V1',status='PASS',count=len(results),executor_ref=E.ref(E.__file__),manifest_ref=E.ref(manifest),runtime_pins=runtimepins,private_fixture=str(B),controls=results,no_actual_model_or_native_start=True,no_registry_or_budget_write=True,no_Git_write=True,synthetic_acceptance_not_science=True)
E.put(D/'ACTUAL_CPU_CONTROLS.json',out);print(json.dumps(dict(status='PASS',count=len(results),receipt=str(D/'ACTUAL_CPU_CONTROLS.json'))))
