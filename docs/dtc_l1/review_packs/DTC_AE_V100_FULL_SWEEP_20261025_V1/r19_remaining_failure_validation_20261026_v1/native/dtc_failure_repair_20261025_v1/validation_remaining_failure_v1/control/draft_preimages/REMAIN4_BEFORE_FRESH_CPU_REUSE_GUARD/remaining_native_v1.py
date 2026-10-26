"""New finite correctness-validation engine overlay; never rewrites original starts.

Reuses the pinned observed native launcher/BA/raw-capture loop in a private module
instance. ROOT, request, admission, exact spec, authority and host binding are new.
The independently qualified observer-exit overlay is mandatory before any launch.
"""
import pathlib,json,hashlib,importlib.util,os,copy,fcntl,datetime,subprocess
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1/validation_remaining_failure_v1');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2');REQ='DTC_AE_REMAINING_FAILURE_REPAIR_20261026_V1';ORIGINAL='DTC_AE_V100_FULL_SWEEP_20261025_V1';G=1024**3;M=1024**2
PRIOR_REPAIR='DTC_AE_FAILURE_REPAIR_VALIDATION_20261025_V1';R1=P('/root/data/dtc_failure_repair_20261025_v1/validation')
LAVA='DTC_AE_LAVAMEM_REPAIR_20261026_V2';R2=P('/root/data/dtc_failure_repair_20261025_v1/validation_lava_memory_v2')
PREVIOUS_LATE='DTC_AE_LATE_FAILURE_REPAIR_20261026_V1';R3=P('/root/data/dtc_failure_repair_20261025_v1/validation_late_failure_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def original_native():return load('repair_independent_original_native',T/'tools/sweep_native_cap1m.py')
def original_plan():return read(R/'control/REMAINING_SCOPE_CANDIDATE_V1.json')
def plan():return read(R/'control/EXECUTION_PLAN_V1.json')
def authority():return original_native().read_current_authority()
def registered():
 reg,epoch=authority();q=reg['registered_future_requests'][REQ];p=plan();scope=read(p['scope_path']);assert q['execution_plan_sha256']==sha(R/'control/EXECUTION_PLAN_V1.json') and q['spec_request_sha256']==sha(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json') and q['authorized_parent_request']==ORIGINAL and q['budget']==scope['finite_budget']==4 and p['scope_sha256']==sha(p['scope_path']) and p['build_profile_sha256']==sha(R/'control/REMAINING_BUILD_PROFILE_V1.json')
 for item in p['source_pins']:assert sha(item['path'])==item['sha256'],('repair source changed',item['path'])
 assert q['engine_sha256']==sha(__file__) and q['correctness_validation_only'] and q['model_automatic_retries']==0
 return reg,epoch,q,p
def spec_for(cell):
 reg,epoch,q,p=registered();path=R/'control/specs'/(cell+'.json');s=read(path);assert q['admitted_specs'][cell]==sha(path) and s['cohort']==cell and s['request']==REQ and s['project']=='DTC';resource=p['per_cohort_memory'][cell];assert s['limits']['max_process_tree_rss_bytes']==resource['max_process_tree_rss_bytes'] and s['estimated_peak_model_RAM_bytes']==resource['estimated_peak_model_RAM_bytes'] and 4*G<=resource['estimated_peak_model_RAM_bytes']<=resource['max_process_tree_rss_bytes']
 assert cell.startswith('E2-AEREPAIR-REMAIN4-') and s['cell'] in ['CM','CH','DM','DH'] and s['program'] in ['histo','lavamd','stencil']
 if s.get('validation_kind')=='COMPONENT_SENTINEL_NOT_FORMAL':assert s['correctness_validation_only'] and s['source_kind'] and s.get('prior_original_point') is None
 else:assert s['prior_original_point']['cohort'] not in q['consumed']
 claim=read(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'].get(cell)
 if claim is not None:
  assert claim['host_cpu'] in p['allowed_model_CPUs'];s=copy.deepcopy(s);s['host_cpu']=claim['host_cpu']
 return s
def output_cap(spec):
 upper=spec['limits']['max_result_directory_bytes'];root={ORIGINAL:T,PRIOR_REPAIR:R1,LAVA:R2,PREVIOUS_LATE:R3,REQ:R}[spec['request']];path=root/'control'/('OPERATIONAL_OUTPUT_CAP_'+spec['cohort']+'.json')
 if not path.exists():return upper
 cap=read(path);value=cap['effective_result_cap_bytes'];assert cap['cohort']==spec['cohort'] and type(value) is int and 0<value<=upper
 if root in [R,R1,R2,R3]:assert sha(path)==spec['operational_output_cap_sha256'] and cap['frozen_upper_result_cap_bytes']==upper and cap['evidence_audit_sha256']==sha(cap['evidence_audit_path'])
 return value
def check_input(spec):
 path=P(spec.get('input_binding_path',str(T/'control/input_bindings'/(spec['input_digest']+'.json'))));assert sha(path)==spec['input_binding_sha256'];binding=read(path);domain=binding['qualification'];assert domain['status']=='BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS' and not domain['issues'];entry=P(domain['trace_entry']);assert sha(entry)==binding['asset']['commandlist_sha256'];fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(entry)],text=True))['filesystems'][0]
 synthetic=spec.get('validation_kind')=='COMPONENT_SENTINEL_NOT_FORMAL' and 'SYNTHETIC' in spec.get('source_kind','')
 assert (fs['fstype']=='fuse.sshfs' and fs['source']=='admin-wcx@10.208.130.164:/home/shared') or (synthetic and fs['fstype']=='ext4' and entry.stat().st_dev==R.stat().st_dev)
 for row in domain['rows']:
  member=P(row['path']);st=member.stat();assert [st.st_size,st.st_mtime_ns]==row['full_SHA_current_size_mtime']
  if synthetic:assert sha(member)==row['sha256'],'new engineering synthetic body bytes changed'
  else:
   with member.open('rb') as stream:assert stream.read(1)
 return {'status':'EXACT_REPAIR_OR_ENGINEERING_INPUT_BINDING_PASS','input_digest':spec['input_digest'],'input_binding_path':str(path),'input_binding_sha256':sha(path),'source_kind':spec.get('source_kind','ORIGINAL_CAPTURED_FULL_INPUT_REPAIR'),'synthetic_component_never_formal':synthetic,'kernels':len(domain['rows']),'native_numerical_values':'UNPROVEN'}
def assert_parent_lease():
 old=original_native();lease=old.assert_batch_lease();reg,epoch,q,p=registered();source=P(p['parent_controller_path']);assert sha(source)==p['parent_controller_sha256']==lease['controller_sha256'] and q['orchestrator_sha256']==lease['controller_sha256'] and reg['registered_future_requests'][ORIGINAL]['orchestrator_sha256']==lease['controller_sha256'];assert {REQ,PRIOR_REPAIR,LAVA,PREVIOUS_LATE}<=set(lease.get('additional_requests',[])),'sole original lease must explicitly retain old repair and authorize new request';return lease
def update_authority(mutator):
 lock=(N/'control/science_authority/REGISTRY_UPDATE.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX)
 rp=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';ep=N/'control/CURRENT_SCIENCE_EPOCH.json';reg=read(rp);epoch=read(ep);assert sha(rp)==epoch['native_registry_sha256'];peers={k:copy.deepcopy(v) for k,v in reg['registered_future_requests'].items() if k!=REQ};old_history=copy.deepcopy((reg['old_source_history'],reg['qualification_history']));prior={'registry':sha(rp),'epoch':sha(ep)};history=N/'control/science_authority/request_history';history.mkdir(exist_ok=True)
 for path in [rp,ep]:
  backup=history/(path.stem+'.'+sha(path)+'.json')
  if not backup.exists():backup.write_bytes(path.read_bytes())
 mutator(reg);assert all(reg['registered_future_requests'][k]==v for k,v in peers.items()) and old_history==(reg['old_source_history'],reg['qualification_history']),'repair engine must not change any original/peer request or old history'
 reg['new_scientific_budget_remaining']=sum(v.get('remaining',max(0,v.get('budget',0)-(v.get('consumed',0) if isinstance(v.get('consumed',0),int) else len(v.get('consumed',{}))))) for v in reg['registered_future_requests'].values());temp=rp.with_name('.REPAIR_REGISTRY.writing')
 with temp.open('w') as stream:json.dump(reg,stream,sort_keys=True,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
 temp.replace(rp);epoch['native_registry_sha256']=sha(rp);epoch['new_budget_remaining']=reg['new_scientific_budget_remaining'];epoch['request_revision']={'request_id':REQ,'operation':'FAILURE_REPAIR_CORRECTNESS_VALIDATION_EXACT_UPDATE','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prior_registry_sha256':prior['registry'],'prior_current_epoch_sha256':prior['epoch']};temp=ep.with_name('.REPAIR_EPOCH.writing')
 with temp.open('w') as stream:json.dump(epoch,stream,sort_keys=True,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
 temp.replace(ep)
 for folder in [rp.parent,ep.parent]:fd=os.open(folder,os.O_RDONLY);os.fsync(fd);os.close(fd)
def _rss(row,root):
 path=root/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
 if not path.exists():return 0
 bound=read(path);proc=P('/proc')/str(bound['pid'])
 try:
  st=(proc/'stat').read_text().rsplit(')',1)[1].split()
  if int(st[19])!=bound['start_ticks'] or st[0] in ['Z','X']:return 0
  return int(next(x.split()[1] for x in (proc/'status').read_text().splitlines() if x.startswith('VmRSS:')))*1024
 except (FileNotFoundError,ProcessLookupError,StopIteration):return 0
def _point_spec(cell,root):return read(root/'control'/((cell+'_SPEC.json') if root==T else ('specs/'+cell+'.json')))
def _known_writes(q,root):
 total=G;entries=[]
 for cell,row in q.get('consumed',{}).items():
  if (root/'control'/(cell+'_ARCHIVE_RECEIPT.json')).exists():continue
  out=root/'DTC/run/results'/row['uuid'];size=sum(x.stat().st_size for x in out.rglob('*') if x.is_file()) if out.exists() else 0;done=row.get('execution_receipt');spec=_point_spec(cell,root);cap=output_cap(spec) if root in [R,R1,R2,R3] else spec['limits']['max_result_directory_bytes'];reserved=size+16*M if done else max(0,2*cap-size);total+=reserved;entries.append({'cohort':cell,'remaining_write_and_restore_bytes':reserved,'closed':bool(done)})
 claims=read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
 for cell,claim in claims.items():
  if cell in q.get('consumed',{}):continue
  spec=_point_spec(cell,root);expected=output_cap(spec) if root in [R,R1,R2,R3] else spec['limits']['max_result_directory_bytes'];assert claim['result_cap_bytes']==expected,'serialized claim cap must equal exact effective output cap';reserved=2*expected;total+=reserved;entries.append({'cohort':cell,'claimed_before_INTENT_write_and_restore_bytes':reserved})
 return total,entries
def resources(s,fresh_source=False):
 p=plan();overlay=p['resource_accounting_overlay'];assert sha(overlay['path'])==overlay['sha256'],'R19 shared resource accounting changed'
 shared=load('remaining_exact_five_scope_resource_accounting',P(overlay['path']))
 return shared.resources(s,fresh_source)
def prepare(cell):
 reg,epoch,q,p=registered();assert epoch['epoch']==2 and epoch['state']=='NATIVE_SCIENCE_ACTIVE' and epoch['holder']==os.uname().nodename and q['state'] in ['ARMED','RUNNING'] and q['remaining']>0 and cell not in q['consumed'];assert_parent_lease();s=spec_for(cell);native=original_native();native.identity();assert R.stat().st_dev==T.stat().st_dev
 assert not (R/'control/qualification_ledger'/(cell+'.INTENT.json')).exists();assert set(q['consumed'])=={x.name.removesuffix('.INTENT.json') for x in (R/'control/qualification_ledger').glob('E2-AEREPAIR-*.INTENT.json')}
 claims=read(R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];assert cell in claims and s['host_cpu']==claims[cell]['host_cpu'] and claims[cell]['result_cap_bytes']==output_cap(s);other_CPUs=[v['host_cpu'] for root in [T,R1,R2,R3] for v in read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'].values()]+[v['host_cpu'] for key,v in claims.items() if key!=cell];assert s['host_cpu'] not in other_CPUs,'repair CPU must not collide with any original or other repair reservation'
 for item in s['runtime_files']:assert P(item['actual_realpath']).is_file() and sha(item['actual_realpath'])==item['sha256']
 assert sha(s['native_simulator_argv'][0])==s['binary_sha256']
 for kind in ['core','framework']:
  repo=P(s['source_worktrees'][kind]);assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==s[kind+'_commit'] and not subprocess.check_output(['git','-C',str(repo),'status','--porcelain'],text=True).strip()
 assert str((R/'DTC/env/lib/libcudart.so').resolve())==p['core_library_path'] and sha(p['core_library_path'])==p['core_library_sha256'];asset=check_input(s);sample=resources(s,True);assert sample['physical_RAM_pass'] and sample['physical_disk_pass'],'RESOURCE_HOLD_NO_START'
 return {'status':'REPAIR_EXACT_FINITE_PREPARE_PASS_NO_START','cohort':cell,'request':REQ,'selected_host_cpu':s['host_cpu'],'identity':native.identity(),'resources':sample,'asset':asset,'operational_resource_profile':{'name':'FAILURE_REPAIR_CORE_FW_OBSERVER_V1','engine_overlay_sha256':sha(__file__),'reused_native_loop_sha256':sha(T/'tools/sweep_native_cap1m.py'),'execution_plan_sha256':sha(R/'control/EXECUTION_PLAN_V1.json'),'correctness_validation_only':True},'scientific_starts':0}
def engine():
 reg,epoch,q,p=registered();n=original_native();n.ROOT=R;n.REQUEST=REQ;n.COHORTS={c:'DTC' for c in q['admitted_specs']};n.spec_for=spec_for;n.prepare=prepare;n.resources=resources;n.output_cap=output_cap;n.assert_batch_lease=assert_parent_lease;n.update_authority=update_authority;n.check_input=check_input
 original_child=n.child_info
 def child_info(pid):
  result=original_child(pid);result['host_cpu_affinity_actual']=sorted(os.sched_getaffinity(pid));return result
 n.child_info=child_info;old_exclusive=n.exclusive
 def exclusive(path,obj):
  path=P(path)
  if path.name.endswith('.INTENT.json') or path.name in ['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:
   obj=dict(obj,repair_execution_overlay={'request':REQ,'engine_sha256':sha(__file__),'execution_plan_sha256':sha(R/'control/EXECUTION_PLAN_V1.json'),'reused_native_loop_sha256':sha(T/'tools/sweep_native_cap1m.py'),'observer_overlay_sha256':p['observer_overlay']['sha256'],'correctness_validation_only':True})
  if path.name.endswith('.INTENT.json'):
   old_requests=original_native().read_current_authority()[0]['registered_future_requests'];assert obj['uuid'] not in {v['uuid'] for key in [ORIGINAL,PRIOR_REPAIR,LAVA,PREVIOUS_LATE] for v in old_requests.get(key,{'consumed':{}})['consumed'].values()},'new capacity validation UUID must never reuse either older scope identity'
  if path.name=='NATIVE_LAUNCH.json':
   uid=obj['scientific_qualification_uuid'];matches=[cell for cell,row in registered()[2]['consumed'].items() if row['uuid']==uid];assert len(matches)==1;cell=matches[0];snapshots={'REPAIR_FROZEN_SPEC.json':R/'control/specs'/(cell+'.json'),'REPAIR_INTENT_SNAPSHOT.json':R/'control/qualification_ledger'/(cell+'.INTENT.json'),'REPAIR_EXECUTION_PLAN.json':R/'control/EXECUTION_PLAN_V1.json','REPAIR_APPROVAL_REQUEST.json':R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json','REPAIR_BUILD_PROFILE.json':R/'control/REMAINING_BUILD_PROFILE_V1.json','REPAIR_OPERATIONAL_OUTPUT_CAP.json':R/'control'/('OPERATIONAL_OUTPUT_CAP_'+cell+'.json')}
   for name,source in snapshots.items():
    with (path.parent/name).open('xb') as stream:stream.write(source.read_bytes());stream.flush();os.fsync(stream.fileno())
  return old_exclusive(path,obj)
 n.exclusive=exclusive;overlay=p['observer_overlay'];assert sha(overlay['path'])==overlay['sha256'];loaded=load('repair_qualified_observer_exit_overlay',P(overlay['path']));n=loaded.install(n);return n
def run_native(cell):return engine().finish_cell(cell)
