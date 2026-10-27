"""Independent chooser consistency/window amendment. Import has no action.
No frozen file, registry, model cap or scientific peak prediction is changed.
Only the existing owner may install the wrapper in its existing resource module.
"""
import sys,threading,pathlib,os,json,hashlib
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');MARKER='DTC_L2_MLP_CONSISTENT_ADMISSION_V1'

def choose_consistent(original,res,pending,sample,claims,history,previous,policy,dispatch_index,baseline,max_inflight=4):
 assert type(max_inflight)is int and max_inflight>0
 observed={c for row in sample.get('observed_models',[])for c in row['cpus']};inflight=sum(v['host_cpu']not in observed for v in claims.values())
 if inflight>=max_inflight:return None
 exact=baseline();pool=list(pending)
 if not exact['physical_RAM_pass']or not exact['physical_disk_pass']or exact['admission_decision']['pressure_reasons']:return None
 while pool:
  decision=original(pool,sample,claims,history,previous,policy,dispatch_index)
  if decision is None:return None
  c=decision['cohort'];spec=next(x for x in pool if x['cohort']==c);new_estimate=max(decision['forecast']['predicted_peak_RAM_bytes'],spec.get('estimated_peak_model_RAM_bytes',0));total=exact['total_projected_additional_RAM_bytes']+new_estimate;gate=res.memory_admission(exact,total,previous,policy);extra_write=2*spec['limits']['max_result_directory_bytes'];write_ok=exact['native_free_bytes']>exact['required_free_bytes']+extra_write and exact['own_remaining_write_and_restore_bytes']+extra_write<=exact['own_reserved_write_ceiling_bytes']
  if gate['pass_admission']and write_ok:
   return dict(decision,consistent_admission=dict(additional_reserved_RAM_bytes=total,admission_RAM_budget_bytes=gate['admission_RAM_budget_bytes'],baseline_includes_all_peer_growth_and_live_10pct=True,inflight_preexec=inflight,max_inflight_preexec=max_inflight,global_model_capacity_unchanged=True))
  pool=[s for s in pool if s['cohort']!=c]
 return None

def apply_in_owner(max_inflight=4):
 assert threading.current_thread()is threading.main_thread()
 plan=json.loads((R/'control/EXECUTION_PLAN.json').read_bytes());assert os.getpid()==plan['parent_pid']==1498278;assert int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks']
 pin=next(x['sha256']for x in plan['source_pins']if P(x['path'])==R/'tools/l2_resources.py')
 return install_on_existing_thread(sys.modules['__main__'].DTC_L2_MLP_ADDON_THREAD,max_inflight,pin)

def install_on_existing_thread(thread,max_inflight=4,expected_resource_sha256=None):
 assert threading.current_thread()is threading.main_thread()
 main=sys.modules['__main__'];frame=sys._current_frames()[thread.ident]
 while frame is not None:
  if frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==R/'tools/l2_ops.py':break
  frame=frame.f_back
 assert frame is not None;assert type(max_inflight)is int and max_inflight>0
 res=frame.f_locals['res']
 if expected_resource_sha256 is not None:
  assert P(res.__file__)==R/'tools/l2_resources.py'and hashlib.sha256(P(res.__file__).read_bytes()).hexdigest()==expected_resource_sha256
 engine=frame.f_locals['engine'];original=res.choose_dispatch;assert not hasattr(main,MARKER)
 # Use a consumed reference identity, so resources(...,fresh_source=True)
 # accounts all current claims/growth but does not add any new candidate.
 q=engine.registered()[2];reference=next(iter(q['consumed']));reference_spec=engine.canonical(reference)
 def wrapper(pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
  def baseline():
   v=res.resources(reference_spec,True);v['own_reserved_write_ceiling_bytes']=engine.registered()[2]['reserved_write_bytes'];return v
  return choose_consistent(original,res,pending,sample,claims,history,previous,policy or {},dispatch_index,baseline,max_inflight)
 res.choose_dispatch=wrapper
 proof=dict(status='REGISTERED_EXISTING_OWNER_CONSISTENT_CHOOSER',owner_pid=os.getpid(),max_inflight_preexec=max_inflight,global_model_capacity=frame.f_locals['max_workers'],executor_id=id(frame.f_locals['pool']),reference_consumed_cohort=reference,resource_module_source_sha256=hashlib.sha256(P(res.__file__).read_bytes()).hexdigest(),no_peak_prediction_or_memory_safety_relaxation=True,no_registry_or_source_or_running_model_mutation=True)
 setattr(main,MARKER,dict(original=original,wrapper=wrapper,proof=proof));return proof

def restore_in_owner():
 assert threading.current_thread()is threading.main_thread()
 main=sys.modules['__main__'];saved=getattr(main,MARKER);thread=main.DTC_L2_MLP_ADDON_THREAD;frame=sys._current_frames()[thread.ident]
 while frame is not None:
  if frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==R/'tools/l2_ops.py':break
  frame=frame.f_back
 assert frame is not None and frame.f_locals['res'].choose_dispatch is saved['wrapper']
 frame.f_locals['res'].choose_dispatch=saved['original'];return dict(status='RESTORED_ORIGINAL_CHOOSER_ONLY',owner_pid=os.getpid(),claims_running_and_models_untouched=True)
