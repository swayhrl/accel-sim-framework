"""Focused dynamic-leaf integration inside real E aging and real FrameGuard."""
import sys
sys.dont_write_bytecode=True
import pathlib,json,os,types,threading,importlib.util,copy
P=pathlib.Path;D=P(__file__).parent;G=1024**3;checks=[]
def guard(event,args):
 if event in ['subprocess.Popen','os.exec','os.system','os.kill','os.killpg']:raise RuntimeError('NO_REAL_MODELS_OR_SIGNALS')
 if event=='open':
  p,mode,flags=args
  if (isinstance(mode,str)and any(c in mode for c in 'wax+'))or flags&(os.O_WRONLY|os.O_RDWR):
   if isinstance(p,(str,bytes)):assert P(os.fsdecode(p)).resolve().is_relative_to(D.resolve())
sys.addaudithook(guard)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def ck(name,value):assert value,name;checks.append(name)
F=load('broad_owner_prefix_builder',D/'cpu_prefix_fixture.py');plan=F.read(F.A/'coordinator/BROAD_SHARED_CPU_SCOPE_CANDIDATE_V1/SCOPE_CANDIDATE.json')
target=next(x['cohort']for x in plan['rows']if x['program']=='lavamd'and x['cell']=='CH'and x['profile']=='P0');f=F.build_fixture(cohort=target,kind='PRIMARY');F.put(f.root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={}))
for row in plan['rows']:
 c=row['cohort']
 if c!=f.c:
  spec=F.read(F.R/'control/specs'/(c+'.json'));forecast=F.load('owner_original_forecast_'+c,F.R/'tools/l2_resources.py').forecast(spec,F.read(F.R/'control/HISTORICAL_RSS.json'),F.read(F.R/'control/RESOURCE_POLICY.json'));spec['estimated_peak_model_RAM_bytes']=max(spec['estimated_peak_model_RAM_bytes'],forecast['predicted_peak_RAM_bytes']);F.put(f.root/'control/specs'/(c+'.json'),spec);F.put(f.root/'control'/(c+'_SPEC.json'),spec);f.q['admitted_specs'][c]=F.sha(f.root/'control/specs'/(c+'.json'))
ir=next(x['cohort']for x in plan['rows']if x['role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL');ir_spec=f.native.canonical(ir)
for ref in F.read(F.R/'control/SCOPE.json')['points']:
 if ref['profile']=='P0'and ref['input_digest']==ir_spec['input_digest']:
  path=f.root/'control/specs'/(ref['cohort']+'.json')
  if not path.exists():path.write_bytes((F.R/'control/specs'/(ref['cohort']+'.json')).read_bytes())
consumer=load('broad_owner_pristine_consumer',F.R/'tools/l2_results.py')
def fixture_loader(*a):raise AssertionError('No physics terminal call in owner qualification')
consumer.load=fixture_loader
oldcalls=[]
def oldworker(c):oldcalls.append(c);return dict(state='EXACT_OLD',cohort=c)
def oldleaf(pending,*a):oldcalls.append(tuple(s['cohort']for s in pending));return None
oldres=load('broad_owner_original_allocator',F.R/'tools/l2_resources.py')
def resources(spec,fresh_source=False):
 value=f.native.resources(spec,fresh_source);claims=F.read(f.root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];ids=set(claims)|{spec['cohort']};rows=[dict(cohort=c,kind='CLAIM_OR_CANDIDATE',RSS_bytes=0,additional_reserved_bytes=f.native.canonical(c)['estimated_peak_model_RAM_bytes'])for c in ids]
 value.update(own_ram_forecasts=rows,total_projected_additional_RAM_bytes=sum(x['additional_reserved_bytes']for x in rows));return value
config=dict(C=0,R=0,provider_calls=0,fail_second=False)
def frames(pending,sample,claims,history,previous,policy,index):
 config['provider_calls']+=1
 if config['fail_second']and config['provider_calls']>=2:raise json.JSONDecodeError('controlled fresh failure','',0)
 costs=[dict(cohort=s['cohort'],input_digest=s['input_digest'],program=s['program'],cell=s['cell'],profile=s['profile'],cost_bytes=s['estimated_peak_model_RAM_bytes'],first_eligible_monotonic=0)for s in pending]
 return dict(now=10000,budget_bytes=100*G+config['C'],effective_total_growth_bytes=100*G,memory_utilization_fraction=.95,own_live=[dict(cohort='CPU_PRIVATE_LIVE',uuid='CPU_ONLY',pid=123,start_ticks=4,RSS_bytes=100*G,anon_PSS_bytes=100*G,effective_future_bytes=0,PSS_sample_monotonic=10000)],consumed={},claim_cohorts=list(claims),closures=[],pending=costs,active_input_digests=[],started_programs=['lavamd'],pressure_reasons=[],accounted_growth_by_cohort={},total_padding_discount_bytes=0,padding_discount_by_cohort={})
agingmod=load('real_old_E_aging',F.R/'control/operational_amendments/large_job_aging_v1/large_job_aging.py');aging=agingmod.AgingChooser(oldleaf,frames)
fgmod=load('real_E_FrameGuard',F.R/'control/operational_amendments/frame_read_guard_v1/frame_read_guard.py');fg=fgmod.FrameReadGuard(aging,sleeper=lambda _:None)
res=types.SimpleNamespace(choose_dispatch=fg.wrapper,resources=resources,forecast=oldres.forecast,cpu_candidates=oldres.cpu_candidates,DTC_LARGE_JOB_AGING_INSTALLED=aging)
frame=types.SimpleNamespace(f_locals=dict(engine=f.native,res=res,consumer=consumer,claims={}),f_globals={'worker':oldworker});main=sys.modules['__main__'];E=load('real_broad_E_consumer',f.cfg['source_paths']['consumer']);E.install_on_frame(frame,f.root/'CONFIG.json',f.native.assert_parent_lease,qualification_loader_sha256=F.sha(__file__))
ops=load('broad_old_raw_worker',F.R/'tools/l2_ops.py');main.DTC_L2_MLP_PADDING_ONLY_OWNER_V1={'worker':ops.worker};original_advance=aging.state.advance
f.producer.install_owner_dispatch(frame,f.root/'CONFIG.json',E.consumer_check,armed=False,hooks={'memory_lib':f.hooks['memory_lib']});marker=getattr(main,f.producer.OWNER_MARKER)
ck('closed worker defers before routeclaim or fork',frame.f_globals['worker'](f.c)['state']=='ZERO_START_DEFERRED'and not f.calls and not(f.root/'control/broad_shared_cpu_route_claims'/f.c).exists())
f.producer.arm_owner_dispatch()
history=F.read(F.R/'control/HISTORICAL_RSS.json');policy=F.read(F.R/'control/RESOURCE_POLICY.json')
def reset(C,R,fail=False):
 config.update(C=C,R=R,provider_calls=0,fail_second=fail);aging.state.target=dict(cohort=target,input_digest=f.spec['input_digest'],program='lavamd',cell='CH',profile='P0',cost_bytes=f.spec['estimated_peak_model_RAM_bytes'],first_eligible_monotonic=0);aging.state.protected=R;aging.state.previous_C=C;aging.state.pending_releases={};aging.state.last_live={};aging.state.seen_completions=set()
reset(ir_spec['estimated_peak_model_RAM_bytes']+10*G-1,10*G);calls=aging.calls;value=res.choose_dispatch([f.spec,ir_spec],{}, {},history,None,policy,0)
ck('E protected75 fence blocks backfill without emptying full pending or second advance',value is None and aging.calls==calls+1 and aging.state.target['cohort']==target and aging.state.protected==10*G)
reset(ir_spec['estimated_peak_model_RAM_bytes']+10*G,10*G);calls=aging.calls;value=res.choose_dispatch([f.spec,ir_spec],{}, {},history,None,policy,0)
ck('IR11 outside old43 is eligible inside E allowed25 pool with one advance',value is not None and value['cohort']==ir and aging.calls==calls+1 and aging.state.protected==10*G and value['large_job_aging']['protected_bytes']==10*G)
reset(f.spec['estimated_peak_model_RAM_bytes'],10*G);calls=aging.calls;value=res.choose_dispatch([ir_spec,f.spec],{}, {},history,None,policy,0)
ck('lavamd CH P0 target goes first full cost through unchanged E fresh gate',value is not None and value['cohort']==target and aging.calls==calls+1 and value['large_job_aging']['offer_target_first']==target)
reset(ir_spec['estimated_peak_model_RAM_bytes']+10*G,10*G,True);before=copy.deepcopy(aging.state.__dict__);calls=aging.calls;value=res.choose_dispatch([f.spec,ir_spec],{}, {},history,None,policy,0)
ck('real FrameGuard second fresh failure rolls back same state all bookkeeping',value is None and aging.state.__dict__==before and aging.calls==calls and fg.last_issue['state_restored']is True)
reset(ir_spec['estimated_peak_model_RAM_bytes']+10*G,10*G);other=next(x['cohort']for x in plan['rows']if x['role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL'and x['cohort']!=ir);claims={other:dict(host_cpu=1,workload=f.native.canonical(other)['workload'],cpu_shared_timeslice_overlay_id='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1')};F.put(f.root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims=claims));value=res.choose_dispatch([f.spec,ir_spec],{},claims,history,None,policy,0)
ck('two shared reservations allowed by quota and full RAM with no fixed one-job cap',value is not None and marker['last_proof']['slot_evidence']['prospective_cpu_threads']==2 and marker['last_proof']['cpu_evidence']['reserved_prospective_cpu_threads']==2 and marker['last_proof']['config']['max_shared_running']is None)
ck('original advance callback identity and global resource provider retained',aging.state.advance.__func__ is original_advance.__func__ and res.resources is resources and marker['previous_choose']is fg.wrapper)
F.put(f.root/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={}));f.producer.restore_owner_dispatch();ck('no birth reverse restores exact prior worker chooser and aging leaf',frame.f_globals['worker']is oldworker and res.choose_dispatch is fg.wrapper and aging.original is oldleaf)
report=dict(status='PASS_DYNAMIC_AGING_LEAF_REAL_E_FRAMEGUARD_CPU_ONLY',count=len(checks),checks=checks,source_observation=f.cfg['qualified_sources'],source_resource=f.memcfg['qualified_sources'],unchanged_aging_source_sha256=F.sha(agingmod.__file__),unchanged_FrameGuard_source_sha256=F.sha(fgmod.__file__),actual_models_started=0,new_grants=0,production_changes=0,production_release_eligible=False,standins=['private frame/lease/authority/consumer physics leaf','controlled frame budgets/PSS/closure-free aging conditions','CPU/memory/proc counters via explicit private fixture','real original AgingChooser/FrameReadGuard and new resource/native/strict source paths'])
p=D/'CPU_DYNAMIC_AGING_LEAF_QUALIFICATION.json'
if p.exists():
 old=D/('DEVELOPMENT_PREIMAGE_'+F.sha(p)+'.json')
 if not old.exists():old.write_bytes(p.read_bytes())
F.put(p,report);print(json.dumps(dict(path=str(p),sha256=F.sha(p),count=len(checks))))
