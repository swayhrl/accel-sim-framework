"""Read-only live frontend inventory and a new unarmed exact-generation plan.
No GDB, process control, authority/claim writes, or scientific launch.
"""
import pathlib,json,hashlib,importlib.util,os,argparse,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');D=F/'ops/revision19';read=lambda p:json.loads(P(p).read_bytes());sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
ap=argparse.ArgumentParser();ap.add_argument('--output',type=P,default=F/'control/R19_LIVE_RESOURCE_OVERRIDE_PLAN_CANDIDATE_V1.json');args=ap.parse_args();h=load('r19_runtime_plan_payload',D/'runtime_resource_override_v1.py');helper=load('r19_runtime_plan_code_identity',T/'tools/sweep_live_ram_override_v1.py');n=load('r19_runtime_plan_readonly_authority',T/'tools/sweep_native_cap1m.py');host=load('r19_runtime_plan_host4',T/'tools/sweep_host_execution_v4.py');old_affinity=os.sched_getaffinity(0)
try:host.install(n);v4=helper.code_identity(n.resources)
finally:os.sched_setaffinity(0,old_affinity)
reg,epoch=n.read_current_authority();q=reg['registered_future_requests'][h.ORIG];resource=load('r19_runtime_plan_resource',D/'resource_accounting_v1.py');_,ghost,_,_=resource.policy_and_ghosts(reg);targets={};closed=[];holes=[];unknown=[]
for c,row in q['consumed'].items():
 out=T/'DTC/run/results'/row['uuid'];ip=T/'control/qualification_ledger'/(c+'.INTENT.json');dp=ip.with_name(c+'.DONE.json')
 if'execution_receipt'in row:
  assert dp.exists()and read(dp)==read(out/'NATIVE_EXIT.json')==row['execution_receipt'];closed.append(c);continue
 if c in ghost and ghost[c]==row['uuid']:holes.append(c);continue
 try:
  p=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json');l=read(out/'NATIVE_LAUNCH.json');model=h.generation(p['pid']);launcher=h.generation(l['launcher_pid']);frontend=h.generation(launcher['parent_pid']);assert model['start_ticks']==p['start_ticks']and model['state']not in ['Z','X']and launcher['state']not in ['Z','X']and frontend['state']not in ['Z','X'];assert sha(ip)==row['intent_sha256']and read(ip)['uuid']==row['uuid'];cmd=(P('/proc')/str(frontend['pid'])/'cmdline').read_bytes().replace(b'\0',b' ').decode();assert 'python'in cmd and any(x in cmd for x in ['sweep_frontend','original_frontend_observer','frontend_v1.py','bin/native','bin/experiment'])
  ackpath=T/'control/live_ram_override'/(c+'.ACK.json');expected=v4;layer='HOST_V4'
  if ackpath.exists():
   ack=read(ackpath)
   if all(ack.get(k)==v for k,v in dict(uuid=row['uuid'],frontend_pid=frontend['pid'],frontend_start_ticks=frontend['start_ticks'],model_pid=p['pid'],model_start_ticks=p['start_ticks']).items()):expected=ack['after_resource_function'];layer='PRESERVED_R12_RAM_WRAPPER'
  if layer=='HOST_V4':assert read(ip).get('host_execution_binding',{}).get('profile')=='HOST_ACTUAL4G40_V4'
  targets[c]=dict(uuid=row['uuid'],frontend_pid=frontend['pid'],frontend_start_ticks=frontend['start_ticks'],model_pid=p['pid'],model_start_ticks=p['start_ticks'],launcher_pid=launcher['pid'],launcher_start_ticks=launcher['start_ticks'],output=str(out),intent_sha256=sha(ip),PID_receipt_sha256=sha(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json'),launch_receipt_sha256=sha(out/'NATIVE_LAUNCH.json'),expected_resource_function_code_identity=expected,resource_function_source_sha256=sha(expected['filename']),before_layer=layer,frontend_cmdline=cmd)
 except(FileNotFoundError,ProcessLookupError,KeyError,AssertionError)as e:unknown.append(dict(cohort=c,uuid=row['uuid'],error=repr(e)))
require_ok=not unknown;plan=dict(schema='R19_LIVE_RUNTIME_EXACT_GENERATION_RESOURCE_PLAN_V1',profile_id=h.PROFILE,phase='PREPARED_NOT_REGISTERED_NOT_APPLIED',patch_source_path=str(D/'runtime_resource_override_v1.py'),patch_source_sha256=sha(D/'runtime_resource_override_v1.py'),request=h.ORIG,unchanged_native_source_path=str(T/'tools/sweep_native_cap1m.py'),unchanged_native_source_sha256=sha(T/'tools/sweep_native_cap1m.py'),resource_module_path=str(D/'resource_accounting_v1.py'),resource_module_sha256=sha(D/'resource_accounting_v1.py'),policy_path=str(resource.POLICY),policy_sha256=sha(resource.POLICY),observed_original_consumed_prefix_count=len(q['consumed']),observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),targets=targets,real_closed_cohorts=closed,certified_receiptless_departed_cohorts=holes,unknown_blockers=unknown,ready_to_arm_after_source_publication=require_ok,required_transfer_API='runtime_resource_override_v1.require_all_live_original_runtime_corrections(registry)',activation_barrier='Actual ACK and fresh latest real RESOURCE sample for every still-live original generation, or actual DONE closure; exact3 certified receiptless generations remain unaccepted. No NEW4 registration before barrier.',scientific_process_attaches=0,signals=0,authority_or_control_mutations=0)
with args.output.open('x')as f:json.dump(plan,f,indent=2);f.write('\n')
print(json.dumps(dict(path=str(args.output),sha256=sha(args.output),prepared_targets=len(targets),layers={layer:sum(x['before_layer']==layer for x in targets.values())for layer in {x['before_layer']for x in targets.values()}},real_closed=len(closed),certified_holes=len(holes),unknown=unknown,armed=False)))
