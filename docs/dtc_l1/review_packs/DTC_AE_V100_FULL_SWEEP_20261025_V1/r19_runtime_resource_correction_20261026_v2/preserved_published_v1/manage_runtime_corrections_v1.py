"""Published, finite operational delivery of R19 corrections to frontends only.
Default action prepare writes an unarmed plan. No process signal or science start.
Root must separately stop the R18 metadata parent; scientific models stay live.
"""
import pathlib,json,hashlib,importlib.util,os,sys,argparse,subprocess,time,datetime,copy
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');D=F/'ops/revision19';ORIG='DTC_AE_V100_FULL_SWEEP_20261025_V1';PARENT_SHA='b7c302aff28712729efc4c06d5744e8cd184c115a069b2536c52b2cba45e6b31';PLAN=F/'control/R19_LIVE_RESOURCE_OVERRIDE_PLAN_V1.json'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def need(v,why):
 if not v:raise RuntimeError(why)
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def write(p,obj):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x')as f:json.dump(obj,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def deps():
 return [P(__file__).resolve(),D/'resource_accounting_v1.py',D/'runtime_resource_override_v1.py',D/'prepare_r19_live_runtime_plan_v1.py',D/'qualify_r19_resource_accounting_cpu_v1.py',D/'RESOURCE_ACCOUNTING_CPU_QUALIFICATION_V1.json',D/'qualify_r19_runtime_gate_cpu_v1.py',D/'RUNTIME_PRECONDITION_CPU_QUALIFICATION_V1.json',D/'qualify_r19_runtime_pending_call_cpu_v1.py',D/'RUNTIME_PENDING_CALL_CPU_QUALIFICATION_V1.json',D/'qualify_r19_runtime_management_cpu_v1.py',D/'RUNTIME_MANAGEMENT_CPU_QUALIFICATION_V1.json',F/'control/R19_RESOURCE_ACCOUNTING_POLICY_V1.json',F/'control/R19_CLOSED_SCOPE_CERTIFICATE_V1.json',F/'ops/revision17/THREE_DEPARTED_ORIGINAL_RAM_CERTIFICATE_V1.json',F/'ops/revision17/admission_resource_adapter_v1.py',T/'tools/sweep_native_cap1m.py',T/'tools/sweep_live_ram_override_v1.py',F/'ops/revision18/sweep_controller.py']
def publication(path):
 p=read(path);need(p.get('verified')is True and isinstance(p.get('commit'),str)and len(p['commit'])==40,'publication not fully verified');need(p.get('helper_sha256')==sha(__file__),'helper publication mismatch');pins={x['path']:x['sha256']for x in p['source_pins']};need(len(pins)==len(p['source_pins']),'duplicate publication source pins')
 for f in deps():need(pins.get(str(f))==sha(f),'unpublished or drifted source: '+str(f))
 for f in [D/'RESOURCE_ACCOUNTING_CPU_QUALIFICATION_V1.json',D/'RUNTIME_PRECONDITION_CPU_QUALIFICATION_V1.json',D/'RUNTIME_PENDING_CALL_CPU_QUALIFICATION_V1.json',D/'RUNTIME_MANAGEMENT_CPU_QUALIFICATION_V1.json']:
  q=read(f);need(q['status']=='PASS','CPU qualification missing PASS')
  if 'payload_sha256'in q:need(q['payload_sha256']==sha(D/'runtime_resource_override_v1.py'),'CPU payload pin stale')
  if 'resource_module_sha256'in q:need(q['resource_module_sha256']==sha(D/'resource_accounting_v1.py'),'CPU resource pin stale')
  if 'helper_sha256'in q:need(q['helper_sha256']==sha(__file__),'management CPU source stale')
  if 'source_path'in q:need(q['source_sha256']==sha(q['source_path']),'CPU qualified source stale')
  if 'policy_sha256'in q:need(q['policy_sha256']==sha(F/'control/R19_RESOURCE_ACCOUNTING_POLICY_V1.json'),'CPU policy pin stale')
  driver={'RESOURCE_ACCOUNTING_CPU_QUALIFICATION_V1.json':'qualify_r19_resource_accounting_cpu_v1.py','RUNTIME_PRECONDITION_CPU_QUALIFICATION_V1.json':'qualify_r19_runtime_gate_cpu_v1.py','RUNTIME_PENDING_CALL_CPU_QUALIFICATION_V1.json':'qualify_r19_runtime_pending_call_cpu_v1.py','RUNTIME_MANAGEMENT_CPU_QUALIFICATION_V1.json':'qualify_r19_runtime_management_cpu_v1.py'}[f.name];need(q['driver_sha256']==sha(D/driver),'CPU driver source stale')
 return p
def stopped_parent(h):
 lease=read(T/'control/BATCH_LEASE.json');need(lease['controller_sha256']==PARENT_SHA and lease['request']==ORIG,'not the qualified R18 lease');state=h.generation(lease['pid']);need(state['start_ticks']==lease['start_ticks']and state['state']in ['T','t'],'R18 metadata parent must already be STOPPED by root');cmd=(P('/proc')/str(lease['pid'])/'cmdline').read_bytes();need(str(F/'ops/revision18/sweep_controller.py').encode()in cmd,'stopped PID is not exact metadata controller');return lease
def profile(plan,plan_path,pub):
 return dict(profile_id=plan['profile_id'],plan_sha256=sha(plan_path),patch_source_sha256=plan['patch_source_sha256'],policy_sha256=plan['policy_sha256'],targets=copy.deepcopy(plan['targets']),publication_commit=pub['commit'],helper_sha256=sha(__file__))
def validate_plan(plan,path,h):
 need(P(path).resolve()==PLAN,'only canonical actual runtime plan accepted');need(plan['ready_to_arm_after_source_publication']is True and not plan['unknown_blockers'],'plan has unknown generations');need(plan['profile_id']==h.PROFILE and plan['request']==ORIG,'plan request/profile mismatch')
 for a,b in [('patch_source_path','patch_source_sha256'),('resource_module_path','resource_module_sha256'),('policy_path','policy_sha256'),('unchanged_native_source_path','unchanged_native_source_sha256')]:need(sha(plan[a])==plan[b],'plan source drift '+a)
 need(plan['patch_source_path']==str(D/'runtime_resource_override_v1.py')and plan['resource_module_path']==str(D/'resource_accounting_v1.py')and plan['unchanged_native_source_path']==str(T/'tools/sweep_native_cap1m.py'),'plan source path mismatch');need(len({x['frontend_pid']for x in plan['targets'].values()})==len(plan['targets']),'nonunique frontends')
def exact_target(c,b,reg,h):
 q=reg['registered_future_requests'][ORIG];r=q['consumed'][c];need(r['uuid']==b['uuid'],'consumed UUID changed');ip=T/'control/qualification_ledger'/(c+'.INTENT.json');out=T/'DTC/run/results'/r['uuid'];need(str(out)==b['output']and sha(ip)==r['intent_sha256']==b['intent_sha256'],'INTENT changed');need(read(ip)['uuid']==r['uuid'],'INTENT UUID changed');pp=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json';lp=out/'NATIVE_LAUNCH.json';need(sha(pp)==b['PID_receipt_sha256']and sha(lp)==b['launch_receipt_sha256'],'PID or launch receipt drift');pr=read(pp);lr=read(lp);need((pr['pid'],pr['start_ticks'],lr['launcher_pid'])==(b['model_pid'],b['model_start_ticks'],b['launcher_pid']),'model/launcher receipt identity changed')
 if 'execution_receipt'in r:
  dp=ip.with_name(c+'.DONE.json');need(read(dp)==read(out/'NATIVE_EXIT.json')==r['execution_receipt'],'closed receipt not genuinely joined');need(h._gone(b['model_pid'],b['model_start_ticks']),'closed model generation still live');return 'REAL_DONE_SKIP'
 states={k:h.generation(b[k+'_pid'])for k in ['frontend','model','launcher']}
 for k,s in states.items():need(s['start_ticks']==b[k+'_start_ticks']and s['state']not in ['Z','X','T','t'],'target generation not actively runnable: '+k)
 need(states['launcher']['parent_pid']==b['frontend_pid'],'launcher parent no longer frontend');need(b['frontend_pid']not in [b['model_pid'],b['launcher_pid']],'frontend equals model or launcher');cmd=(P('/proc')/str(b['frontend_pid'])/'cmdline').read_bytes().replace(b'\0',b' ');need(b'python'in cmd and any(x in cmd for x in [b'frontend_v1.py',b'sweep_frontend',b'original_frontend_observer',b'bin/native',b'bin/experiment']),'frontend command not allowlisted')
 # Cross-check all original consumed receipts, not merely this target.
 for other in q['consumed'].values():
  root=T/'DTC/run/results'/other['uuid']
  for name,key in [('NATIVE_SIMULATOR_PID_AND_MAPS.json','pid'),('NATIVE_LAUNCH.json','launcher_pid')]:
   file=root/name
   if file.exists():need(read(file)[key]!=b['frontend_pid'],'attach PID collides with scientific model/launcher')
 return 'EXACT_LIVE_FRONTEND'
def mutate_profile(reg,expected,h):
 before=copy.deepcopy(reg);q=reg['registered_future_requests'][ORIG];need(h.FIELD not in q,'already armed; no repeat authority mutation');q[h.FIELD]=copy.deepcopy(expected);check=copy.deepcopy(reg);del check['registered_future_requests'][ORIG][h.FIELD];need(check==before,'non-profile authority mutation');return before
def ack_validate(ack,b,plan,path,h):
 need(ack['status']=='EXACT_RUNTIME_RESOURCE_LOOKUP_INSTALLED'and ack['plan_sha256']==sha(path)and ack['patch_source_sha256']==plan['patch_source_sha256']and ack['policy_sha256']==plan['policy_sha256']and ack['resource_module_sha256']==plan['resource_module_sha256'],'ACK source/plan mismatch')
 for k in ['uuid','frontend_pid','frontend_start_ticks','model_pid','model_start_ticks','launcher_pid','launcher_start_ticks']:need(ack[k]==b[k],'ACK generation mismatch '+k)
 need(ack['before_resource_function']==b['expected_resource_function_code_identity'],'ACK before function mismatch');module=load('r19_management_ack_resource',plan['resource_module_path']);after=h.identity(h.make_wrapper(lambda *a:{},lambda:({},{}),{},sha(path),sha(h.__file__),module,plan['policy_sha256']));need(ack['after_resource_function']==after,'ACK installed function mismatch')
def carrier(work,planpath):
 code=('import importlib.util,pathlib;_r19s=importlib.util.spec_from_file_location("r19_published_runtime_payload",'+repr(str(D/'runtime_resource_override_v1.py'))+');_r19m=importlib.util.module_from_spec(_r19s);_r19s.loader.exec_module(_r19m);_r19m.apply(pathlib.Path('+repr(str(planpath))+'))').encode()+b'\0';need(len(code)<4096,'pending carrier exceeds one page');blob=work/'pending.bin';blob.write_bytes(code);commands=work/'attach.gdb';commands.write_text('set pagination off\nset confirm off\nset auto-load python-scripts off\nset scheduler-locking off\nset $buf = (void *)mmap((void*)0,4096,3,34,-1,0)\nprintf "BUFFER=%p\\n",$buf\nrestore '+str(blob)+' binary $buf\nset $queued = (int)Py_AddPendingCall((int(*)(void*))PyRun_SimpleString,$buf)\nprintf "QUEUED=%d\\n",$queued\ndetach\nquit\n');return commands
def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','arm','deliver','verify'],nargs='?',default='prepare');ap.add_argument('--publication',type=P,required=True);ap.add_argument('--plan',type=P,default=PLAN);ap.add_argument('--cohort');ap.add_argument('--wait-seconds',type=int,default=40);args=ap.parse_args();pub=publication(args.publication);h=load('r19_management_payload',D/'runtime_resource_override_v1.py');n=load('r19_management_authority',T/'tools/sweep_native_cap1m.py');need(0<=args.wait_seconds<=45,'wait bound0..45s');stopped_parent(h)
 if args.action=='prepare':
  need(args.plan.resolve()==PLAN and not args.plan.exists(),'actual plan must be canonical and new');subprocess.run([sys.executable,'-B',str(D/'prepare_r19_live_runtime_plan_v1.py'),'--output',str(args.plan)],check=True);p=read(args.plan);validate_plan(p,args.plan,h);print(json.dumps(dict(status='PREPARED_NOT_ARMED',plan=str(args.plan),sha256=sha(args.plan),targets=len(p['targets']),publication_commit=pub['commit'])));return
 plan=read(args.plan);validate_plan(plan,args.plan,h);reg,epoch=n.read_current_authority();expected=profile(plan,args.plan,pub);work=F/'control/live_resource_accounting_R19_operations'/sha(args.plan);work.mkdir(parents=True,exist_ok=True)
 if args.action=='arm':
  existing=reg['registered_future_requests'][ORIG].get(h.FIELD)
  if existing is not None:need(existing==expected,'incompatible armed profile');print(json.dumps(dict(status='ALREADY_EXACTLY_ARMED_NO_WRITE')));return
  def mutation(r):
   stopped_parent(h);need(len(r['registered_future_requests'][ORIG]['consumed'])==plan['observed_original_consumed_prefix_count'],'new consumed after inventory');need(r['registered_future_requests'][ORIG]['budget']==356,'original budget changed')
   for c,b in plan['targets'].items():exact_target(c,b,r,h)
   write(work/'REGISTRY_PREIMAGE.json',read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'));(work/'REGISTRY_PREIMAGE.bytes').write_bytes((N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json').read_bytes());(work/'EPOCH_PREIMAGE.bytes').write_bytes((N/'control/CURRENT_SCIENCE_EPOCH.json').read_bytes());mutate_profile(r,expected,h)
  n.update_authority(mutation);after,e=n.read_current_authority();before=read(work/'REGISTRY_PREIMAGE.bytes');restored=copy.deepcopy(after);del restored['registered_future_requests'][ORIG][h.FIELD];need(restored==before,'arm changed nonoperational registry fields');receipt=dict(status='EXACT_PROFILE_ARMED',utc=utc(),plan_sha256=sha(args.plan),publication_commit=pub['commit'],helper_sha256=sha(__file__),registry_before_sha256=sha(work/'REGISTRY_PREIMAGE.bytes'),epoch_before_sha256=sha(work/'EPOCH_PREIMAGE.bytes'),registry_after_sha256=sha(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'),profile_field=h.FIELD,scientific_starts=0,signals=0,only_added_profile_field=True);write(work/'ARM_RECEIPT.json',receipt);print(json.dumps(receipt));return
 need(reg['registered_future_requests'][ORIG].get(h.FIELD)==expected,'exact published profile is not armed')
 if args.action=='deliver':
  cells=[args.cohort]if args.cohort else sorted(plan['targets']);need(set(cells)<=set(plan['targets']),'cohort not in finite plan');results=[]
  for c in cells:
   publication(args.publication);stopped_parent(h);reg,_=n.read_current_authority();b=plan['targets'][c];state=exact_target(c,b,reg,h)
   if state=='REAL_DONE_SKIP':results.append(dict(cohort=c,status=state));continue
   h.authorized(n.read_current_authority,dict(b,cohort=c),sha(args.plan),plan['patch_source_sha256'],plan['policy_sha256']);ackpath=h.ACKROOT/(c+'.'+b['uuid']+'.ACK.json')
   if ackpath.exists():ack_validate(read(ackpath),b,plan,args.plan,h);results.append(dict(cohort=c,status='EXISTING_EXACT_ACK_NO_REINSTALL',ACK_sha256=sha(ackpath)));continue
   target=work/(c+'.delivery');target.mkdir(exist_ok=False);commands=carrier(target,args.plan)
   # Last checks immediately before ptrace; PID is derived solely from bound frontend.
   stopped_parent(h);reg,_=n.read_current_authority();need(exact_target(c,b,reg,h)=='EXACT_LIVE_FRONTEND','generation closed during delivery prep');start=time.monotonic();r=subprocess.run(['/usr/bin/gdb','--nx','--quiet','--batch','-p',str(b['frontend_pid']),'-x',str(commands)],capture_output=True,text=True,timeout=8);(target/'GDB.stdout').write_text(r.stdout);(target/'GDB.stderr').write_text(r.stderr);need(r.returncode==0 and 'QUEUED=0'in r.stdout,'pending delivery not queued; inspect external GDB logs');deadline=time.monotonic()+10
   while not ackpath.exists()and time.monotonic()<deadline:time.sleep(.1)
   need(ackpath.exists(),'no actual ACK; do not retry installation');ack_validate(read(ackpath),b,plan,args.plan,h);receipt=dict(cohort=c,status='ACTUAL_FRONTEND_PENDING_CALL_ACK_VERIFIED',frontend_pid=b['frontend_pid'],frontend_start_ticks=b['frontend_start_ticks'],ACK_path=str(ackpath),ACK_sha256=sha(ackpath),elapsed_seconds=time.monotonic()-start,scientific_model_attaches=0,signals=0,scientific_starts=0);write(target/'DELIVERY_RECEIPT.json',receipt);results.append(receipt);print(json.dumps(receipt),flush=True)
  print(json.dumps(dict(status='DELIVERIES_COMPLETE_VERIFY_REAL_SAMPLES_NEXT',results=results)));return
 deadline=time.monotonic()+args.wait_seconds
 while True:
  try:
   publication(args.publication);stopped_parent(h);reg,epoch=n.read_current_authority();proof=h.require_all_live_original_runtime_corrections(reg,args.plan);break
  except(RuntimeError,FileNotFoundError,ProcessLookupError,ValueError,KeyError):
   if time.monotonic()>=deadline:raise
   time.sleep(1)
 proof.update(publication_commit=pub['commit'],publication_receipt_sha256=sha(args.publication),helper_sha256=sha(__file__),registry_sha256=sha(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'),epoch_sha256=sha(N/'control/CURRENT_SCIENCE_EPOCH.json'));dest=work/('ACTUAL_RUNTIME_VERIFIED_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json');write(dest,proof);print(json.dumps(dict(status=proof['status'],path=str(dest),sha256=sha(dest),live_count=proof['live_count'],real_closed_count=proof['real_closed_count'])))
if __name__=='__main__':main()
