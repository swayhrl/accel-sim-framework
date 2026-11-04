from pathlib import Path
import types,json,hashlib,ast,copy,sys,datetime
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_execution_20261105_v1/agents/A_owner_resource_v1');sys.dont_write_bytecode=True
records=[]
def ck(name,okay):assert okay,name;records.append(dict(check=name,pass_=True))
def raises(name,fn):
 try:fn()
 except(AssertionError,KeyError,OSError,ValueError):ck(name,True);return
 raise AssertionError('expected conservative reject '+name)
def load(name):
 p=O/(name+'.py');m=types.ModuleType(name+'_cpu_private');m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
r=load('perf16_resources');a=load('perf16_parent_addon');ops=load('perf16_ops');G=r.G;M=r.M
ck('three modules compile/import without applying dispatcher or registration',all(hasattr(m,'R')for m in [r,a,ops]))
ck('fixed16 identical across resource parent ops',len(set(r.EXPECTED16_COHORTS))==16 and r.EXPECTED16_COHORTS==a.EXPECTED16_COHORTS==ops.EXPECTED16_COHORTS)
pol=r.policy(r.read(O/'RESOURCE_POLICY.template.json'));proof=r.verify_direction_release(pol);ck('actual Root release fixedSHA/exact16/sourcepins',proof['exact_candidate_count']==16)
for label,mut in [('wrongpath',lambda x:x['direction_release'].update(path='/nonexistent')),('wrongsha',lambda x:x['direction_release'].update(sha256='0'*64))]:
 v=copy.deepcopy(pol);mut(v);ck('direction '+label+' holds new admission',r.direction_release_gate(v)['pass']is False)
# Pure request projection does not invoke the real authority/owner.
prior={'old':dict(request='old',budget=28,remaining=0,admitted_specs={'x':'oldsha'},consumed={'x':dict(uuid='old-live',execution_receipt=None)},state='RUNNING')};reg=dict(registered_future_requests=copy.deepcopy(prior));candidate=dict(request=r.REQ,budget=16,remaining=16,admitted_specs={c:'s'+str(i)for i,c in enumerate(r.EXPECTED16_COHORTS)},consumed={})
a.register_exact_request(reg,candidate,proof);ck('newrequest only old28 runningUUID/budget untouched',reg['registered_future_requests']['old']==prior['old']and reg['registered_future_requests'][r.REQ]['runtime_release_evidence']==proof)
raises('duplicate request cannot register/retry',lambda:a.register_exact_request(reg,candidate,proof))
for label,mut in [('budget17',lambda v:v.update(budget=17)),('missingcohort',lambda v:v['admitted_specs'].pop(next(iter(v['admitted_specs'])))),('foreigncohort',lambda v:v['admitted_specs'].update(foreign='f'))]:
 v=copy.deepcopy(candidate);mut(v);raises(label,lambda:a.register_exact_request(dict(registered_future_requests=copy.deepcopy(prior)),v,proof))
before=b'#!/bin/sh\nset -eu\n# existing R28 bytes and route\nE2-DTCPF28-keep\n';block=b'# E2-DTCPFV2- exact own route\n'
after=a.exact_native_route(before,block);ck('new block removes to byte-identical prior native route',after.replace(block,b'',1)==before)
raises('duplicate native route block rejected',lambda:a.exact_native_route(after,block));raises('unrelated route prefix rejected',lambda:a.exact_native_route(before,b'wrong'))
# Actual production evaluation function, synthetic bounded inputs.
s=dict(utc='CPU_FIXTURE',host_MemAvailable_bytes=128*G,cgroup_memory_max=str(256*G),cgroup_memory_current=128*G,cgroup_effective_headroom_bytes=128*G,native_free_bytes=20*G,free_inodes=200000,archive_free_bytes=100*G,true164_mount_verified=True,monotonic=100,host_pswpout_pages=0,host_oom_kill_count=0,cgroup_swap_current_bytes=0,cgroup_memory_events={},direction_release={'pass':True},memory_pressure={},cpu_pressure={},io_pressure={},host_memory_pressure={},host_cpu_pressure={},host_io_pressure={})
b=dict(required_free_bytes=5*G+int(2.5*G)+4*G+G,peer_reservations=[dict(request=r.REQ,reserved_write_bytes=int(2.5*G)),dict(request=r.V1_REMAINING28_REQ,reserved_write_bytes=4*G),dict(request='UNKNOWN_FOREIGN',reserved_write_bytes=G)],reserved_additional_live_and_candidate_RAM_bytes=0,per_scope_write_ceiling_pass={'known':True},known_remaining_writes_by_request={},remaining48_closed_metadata_forward_projection={})
peers={r.V1_REMAINING28_REQ:dict(projected_write_bytes=256*M,additional_RAM_bytes=2*G,projection_within_registered_ceiling=True)};own=dict(projected_write_bytes=512*M,actual_unarchived_output_bytes=64*M,additional_RAM_bytes=G,projection_within_registered_ceiling=True,ram=[],writes=[]);q=dict(reserved_write_bytes=int(2.5*G))
def ev(ss=None,fresh=True,oo=None,bb=None):return r._evaluate({},fresh,ss or s,None,bb or b,peers,oo or own,q,pol)
v=ev();ck('dynamic V1 static ceiling replaced once unknown peer retained',v['required_free_bytes']==5*G+G+512*M+256*M and v['admission_disk_pass']and v['physical_RAM_pass'])
v=copy.deepcopy(s);v['host_memory_pressure']={'full':{'avg10':1.}};ck('host PSI pauses prepare',not ev(v)['physical_RAM_pass']);ck('host PSI does not kill runtime or hold restore disk',ev(v,False)['physical_RAM_pass']and ev(v,False)['physical_disk_pass']and ev(v,False)['admission_disk_pass'])
v=copy.deepcopy(s);v['direction_release']={'pass':False};ck('release HOLD only prepare',not ev(v)['physical_RAM_pass']and ev(v,False)['physical_RAM_pass']and ev(v,False)['admission_disk_pass'])
v=copy.deepcopy(s);v['cgroup_effective_headroom_bytes']=4*G;ck('cgroup floor pauses prepare runtime healthy',not ev(v)['physical_RAM_pass']and ev(v,False)['physical_RAM_pass'])
v=copy.deepcopy(s);v['native_free_bytes']=6*G;ck('future restore budget shortage pauses prepare/archive not healthy runtime',not ev(v)['admission_disk_pass']and ev(v,False)['physical_disk_pass']and not ev(v,False)['archive_disk_pass'])
v=copy.deepcopy(s);v['native_free_bytes']=5*G;ck('actual native floor unsafe runtime',not ev(v,False)['physical_disk_pass'])
v=copy.deepcopy(s);v['true164_mount_verified']=False;ck('unverified true164 holds new/archive',not ev(v)['admission_disk_pass']and ev(v,False)['actual_native_runtime_safe'])
v=copy.deepcopy(s);v['free_inodes']=99999;ck('actual inode floor unsafe',not ev(v,False)['physical_disk_pass'])
o=copy.deepcopy(own);o['actual_unarchived_output_bytes']=3*G;ck('actual own ceiling overrun unsafe',not ev(fresh=False,oo=o)['physical_disk_pass'])
o=copy.deepcopy(own);o['additional_RAM_bytes']=120*G;ck('88percent RAM forecast prevents overadmission',not ev(oo=o)['physical_RAM_pass'])
o=copy.deepcopy(own);o['projection_within_registered_ceiling']=False;ck('future own write ceiling holds new/archive',not ev(oo=o)['admission_disk_pass']and ev(fresh=False,oo=o)['physical_disk_pass'])
bb=copy.deepcopy(b);bb['per_scope_write_ceiling_pass']={'known':False};ck('unknown peer/knownscope ceiling never silently ignored',not ev(bb=bb)['admission_disk_pass'])
previous=copy.deepcopy(s);previous['monotonic']=99
for label,key,value in [('hostoom','host_oom_kill_count',1),('cgoom','cgroup_memory_events',{'oom_kill':1}),('swapout','host_pswpout_pages',100000),('cgswap','cgroup_swap_current_bytes',128*M)]:
 v=copy.deepcopy(s);v[key]=value;ck('fresh '+label+' increase pauses',bool(r.pressure_reasons(v,previous,pol)))
# Dynamic future write accounting with a new private filesystem fixture only.
F=O/'cpu_fixture';F.mkdir(exist_ok=True);(F/'control/specs').mkdir(parents=True,exist_ok=True);origR=r.R;r.R=F
spec=dict(cohort='candidate',estimated_peak_model_RAM_bytes=512*M,input_digest='fixture',limits=dict(max_result_directory_bytes=64*M,max_process_tree_rss_bytes=4*G));sp=F/'control/specs/candidate.json';sp.write_text(json.dumps(spec));qq=dict(request=r.REQ,budget=16,remaining=16,consumed={},admitted_specs={'candidate':r.sha(sp)},reserved_write_bytes=int(2.5*G))
class Peer:
 def rss(self,root,row):return(row.get('rss',0),row.get('live',False))
 def size(self,root):return 32*M
 def archived(self,root,c,row):return row.get('archived',False)
peer=Peer();d=r._dynamic(peer,F,qq,{},256*M,spec,True);ck('only selected candidate is reserved not all16 unused',d['projected_write_bytes']==256*M+128*M and len(d['writes'])==1 and d['additional_RAM_bytes']==512*M)
qq['consumed']={'candidate':dict(uuid='u',rss=128*M,live=True)};qq['remaining']=15;d=r._dynamic(peer,F,qq,{},256*M);ck('active source bytes already in df are not reserved twice',d['projected_write_bytes']==256*M+128*M-32*M)
qq['consumed']['candidate'].update(live=False,execution_receipt={'natural':True});d=r._dynamic(peer,F,qq,{},256*M);ck('done unrestored exact source plus margin held',d['projected_write_bytes']==256*M+32*M+16*M and d['additional_RAM_bytes']==0)
# Unique cohort avoids reuse of intentionally mocked archive cache.
r._JOIN.clear();qq['consumed']['candidate']['archived']=True;d=r._dynamic(peer,F,qq,{},256*M);ck('closed archived nonlive point no future source growth',d['projected_write_bytes']==256*M and d['exact_archived_nonlive_count']==1 and d['writes']==[])
r.R=origR
# Static interface restrictions supplement pure function fixtures; no dispatcher run.
ops_src=(O/'perf16_ops.py').read_text();parent_src=(O/'perf16_parent_addon.py').read_text()
ck('ops no old family seed or first4 gate',all(x not in ops_src for x in ['family_seeds','seed_runtime_witness','first4_completion_gate']))
ck('ops exact16 with no extra actual canary',"len(cohorts)==len(set(cohorts))==16"in ops_src and 'range(max_workers-len(running))'in ops_src)
ck('parent actual apply guarded same owner/start/mainthread/existing locks',all(x in parent_src for x in ['os.getpid()==1498278','==977758783','threading.main_thread()','{3,4}','OBSERVE_EXISTING_ADDON_NO_BLIND_REAPPLY']))
ck('no simulator or registration called by this QA',True)

# Actual new typed-HOLD helpers with private evidence, not production control files.
profile=next(iter(r.VARIANT_TOKENS));co=r.EXPECTED16_COHORTS[0];evp=F/'TYPED_SAFETY_FIXTURE.json';evp.write_text('{"CPU_fixture_only":true}')
hold=dict(profile=profile,request=r.REQ,classification='CONFIGURATION_OR_LIFECYCLE_SAFETY_HOLD',reason='CPU_SYNTHETIC_INTERFACE',evidence_path=str(evp),evidence_sha256=r.sha(evp),decided_by='DTC_MAIN',created_utc='CPU_FIXTURE')
hq=dict(request=r.REQ,consumed={},admission_holds={});hs=dict(cohort=co,profile=profile,structure_variant=profile)
ck('empty holds are not a typed safety hold',r.admission_hold(hq,hs)is None)
hq['admission_holds']={profile:hold};ck('profile-key typed Root HOLD recognized',r.admission_hold(hq,hs)['profile']==profile)
hq['admission_holds']={co:dict(hold,cohort=co)};ck('matching exact cohort-key typed HOLD recognized',r.admission_hold(hq,hs)['profile']==profile)
for label,mut in [('wrongclassification',lambda x:x.update(classification='PERFORMANCE_NEGATIVE')),('wrongdecider',lambda x:x.update(decided_by='AUTO_SPEEDUP')),('staleevidence',lambda x:x.update(evidence_sha256='0'*64)),('wrongprofile',lambda x:x.update(profile='FOREIGN'))]:
 bad=copy.deepcopy(hold);mut(bad);hq['admission_holds']={profile:bad};raises('typed HOLD '+label+' fails closed',lambda:r.admission_hold(hq,hs))
hq['admission_holds']={profile:{}};raises('malformed relevant empty entry fails closed',lambda:r.admission_hold(hq,hs))
hq['consumed']={co:{'uuid':'healthy'}};ck('profile HOLD never signals or blocks consumed healthy model',r.admission_hold(hq,hs)is None)
I=r.read(O.parent/'C_spec_strict_v1/INTERFACE.fixed.json');points=[dict(x,cohort=x['proposed_native_cohort'])for x in I['candidates']]
dec=dict(schema='DTC_PERFV2_CODESIGN16_PROFILE_HOLD_DECISION_V1',authority_commit=r.AUTHORITY_COMMIT,approval_scope=dict(request=r.REQ,profile=profile,candidate_cohorts=[x['cohort']for x in points if x['profile']==profile]),**hold)
hp=F/'control/PROFILE_HOLD_DECISIONS';hp.mkdir(parents=True,exist_ok=True);dp=hp/'ROOT_SYNTHETIC_DECISION.json';dp.write_text(json.dumps(dec))
v=ops.validate_profile_hold_decision(dp,points,r);ck('Root profile immutable decision scope exact8 validated',v['profile']==profile and v['decision_sha256']==r.sha(dp))
bad=copy.deepcopy(dec);bad['approval_scope']['candidate_cohorts'].pop();badp=F/'BAD_SCOPE.json';badp.write_text(json.dumps(bad));raises('wrong profile decision population rejected',lambda:ops.validate_profile_hold_decision(badp,points,r))
class Engine:
 REQ=r.REQ
 def __init__(self):self.reg={'registered_future_requests':{r.REQ:dict(request=r.REQ,budget=16,remaining=16,consumed={},admitted_specs={x['cohort']:'fixtureSHA'for x in points})}};self.updates=0
 def registered(self):return self.reg,{},self.reg['registered_future_requests'][r.REQ],{}
 def update_authority(self,fn):fn(self.reg);self.updates+=1
eng=Engine();origopsR=ops.R;ops.R=F
ops.consume_profile_hold_decisions(eng,points,r);ops.consume_profile_hold_decisions(eng,points,r);oq=eng.registered()[2]
ck('sameowner update projection appends HOLD once preserves16budget no UUID consumption',eng.updates==1 and oq['budget']==oq['remaining']==16 and not oq['consumed']and len(oq['admitted_specs'])==16)
uh=ops.unused_hold_status(oq,points,r);ck('profile HOLD covers only matching eight unconsumed identities',len(uh)==8 and all(x['profile']==profile for x in points if x['cohort']in uh))
cohorts=[x['cohort']for x in points];state={c:ops.TERMINAL[0]for c in cohorts};other=[c for c in cohorts if c not in uh];tq=copy.deepcopy(oq);tq['consumed']={c:{'uuid':'u'+str(i)}for i,c in enumerate(other)};tq['remaining']=8
ck('allconsumed closed and allunused typedHOLD can terminate with8credits',ops.terminal_unused_ready(tq,state,cohorts,uh,0,0))
for label,running,post in [('healthy_running',1,0),('archive_pending',0,1)]:ck(label+' prevents unused terminal',not ops.terminal_unused_ready(tq,state,cohorts,uh,running,post))
u=dict(uh);u.pop(next(iter(u)));ck('one missing typedHOLD prevents terminal',not ops.terminal_unused_ready(tq,state,cohorts,u,0,0))
ss=dict(state);ss[other[0]]='PENDING';ck('one nonterminal consumed identity prevents terminal',not ops.terminal_unused_ready(tq,ss,cohorts,uh,0,0))
ops.R=origopsR
ck('admission pressure boolean explicit to native',ev()['admission_pressure_pass']is True)

out=dict(schema='PERFV2_CODESIGN16_OWNER_RESOURCE_CPU_QUALIFICATION_V1',status='PASS',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),check_n=len(records),checks=records,source_sha256={n:r.sha(O/(n+'.py'))for n in ['perf16_resources','perf16_parent_addon','perf16_ops']},models_started=0,registry_writes=0,owner_callbacks=0,services_started=0,fixture_scope='pure in-memory registration projection, private bounded resource fixtures, exact byte-preserving route transformation; not actual owner/trace qualification')
(O/'CPU_QUALIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(status=out['status'],checks=len(records),source_sha256=out['source_sha256'])))

