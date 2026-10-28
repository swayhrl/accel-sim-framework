from pathlib import Path as P
import sys,importlib.util,json,copy,types,tempfile,time,hashlib
sys.dont_write_bytecode=True
B=P(__file__).parent;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest();read=lambda p:json.loads(P(p).read_bytes());checks=[]
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('B_tiny_facade_readonly_review',B/'facade_memory.py');rt=load('B_real_RuntimeFrames_tiny_review',R/'control/operational_amendments/large_job_aging_v1/aging_runtime_frames.py');fg=load('B_real_FrameGuard_tiny_review',R/'control/operational_amendments/frame_read_guard_v1/frame_read_guard.py');ag=load('B_real_aging_tiny_review',R/'control/operational_amendments/large_job_aging_v1/large_job_aging.py');lib=load('B_real_mem_math_tiny_review',R/'control/operational_amendments/future_memory_admission_v1/future_memory.py');root=P(tempfile.mkdtemp(prefix='B_CPU_TINY_FACADE_',dir=B));(root/'control').mkdir();(root/'control/MATRIX_CURRENT.json').write_text(json.dumps({'points':[]}));base=read(B.parent/'memory_headroom_review_current_v1/SNAPSHOT.json')['padding_resource_snapshot'];runtime=object();mode={'value':'BASE','calls':0};active={'scope_mode':'ALL_UNSPENT_FUTURE'}
def original(s,f=False):
 if not f:return runtime
 mode['calls']+=1
 if mode['value']=='RUNTIME_ERROR':raise RuntimeError('CPU original-provider failure')
 if mode['value']=='JSON':raise json.JSONDecodeError('CPU transient','',0)
 if mode['value']=='TAMPERED95':return dict(lib.project(base),UNAPPROVED_MEMORY_CREDIT=1)
 return base
obj=m.FacadeMemory.__new__(m.FacadeMemory);obj.original=original;obj.lib=lib;obj.FrameUnavailable=fg.FrameUnavailable;obj.guard=lambda:active
frames=rt.RuntimeFrames.__new__(rt.RuntimeFrames);frames.root=root;frames.engine=types.SimpleNamespace(registered=lambda:(None,None,dict(consumed={'REFERENCE':{'uuid':'CPU_NOT_REAL'}},request=lib.REQ),None));frames.res=types.SimpleNamespace(resources=obj.resources,forecast=lambda *a:dict(predicted_peak_RAM_bytes=1));frames.consumer=types.SimpleNamespace(accepted=lambda x:False);frames.effective_rows=lambda x:copy.deepcopy(x['own_ram_forecasts']);frames.refresh=30;frames.last_pss_refresh=time.monotonic();frames.pss={};frames.completion_cache={};frames.first_eligible=time.monotonic();frames.first_eligible_source={'CPU_FIXTURE':True};frames.generation=lambda *a:None
aging=ag.AgingChooser(lambda *a:None,frames);gate=fg.FrameReadGuard(aging,sleeper=lambda x:None);args=([],{}, {},{},None,{},0)
def ck(n,v):assert v,n;checks.append(n)
frame=frames(*args);ck('real_RuntimeFrames_uses_qualified95_projection_without_growth_change',frame['memory_utilization_fraction']==.95 and frame['budget_bytes']==lib.budget(base)and frame['effective_total_growth_bytes']==base['total_projected_additional_RAM_bytes']);active['scope_mode']='FINITE_CANARY';ck('FINITE_and_freshFalse_return_exact_original_objects',obj.resources({},True)is base and obj.resources({},False)is runtime);active['scope_mode']='ALL_UNSPENT_FUTURE'
def rollback_case(name,prepare,status):
 before=copy.deepcopy(aging.state.__dict__);calls=aging.calls;prepare();value=gate.wrapper(*args);ck(name,value is None and gate.last_issue['status']==status and aging.state.__dict__==before and aging.calls==calls)
def guard_error():raise AssertionError('CPU source/config drift')
oldguard=obj.guard;rollback_case('source_guard_error_is_real_sentinel_and_original_Guard_rollback',lambda:setattr(obj,'guard',guard_error),'AGING_FACADE_SOURCE_OR_MEMORY_CONFIG_INVALID');obj.guard=oldguard
rollback_case('upstream_runtime_error_is_real_sentinel_and_Guard_rollback',lambda:mode.update(value='RUNTIME_ERROR'),'AGING_FACADE_UPSTREAM_ENGINEERING_EXCEPTION')
mode['calls']=0;rollback_case('transient_JSON_exact_three_retries_and_Guard_rollback',lambda:mode.update(value='JSON'),'FRAME_READ_UNAVAILABLE');ck('three_provider_attempts_preserved',mode['calls']==3)
rollback_case('already95_tampered_extra_credit_refused_without_double_projection',lambda:mode.update(value='TAMPERED95'),'AGING_FACADE_PROJECTION_INVALID')
report=dict(schema='B_TINY_FACADE_INDEPENDENT_CPU_REVIEW_V1',status='PASS',source_sha256=sha(B/'facade_memory.py'),checks=checks,passed=len(checks),negative_cases=4,real_frozen_RuntimeFrames_FrameGuard_AgingChooser_and_MEM_project=True,provider_authority_resources_and_modes_explicit_private_CPU_fixtures=True,production_mutations=0,owner_attaches=0,model_starts=0,signals=0);(B/'INDEPENDENT_CPU_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
