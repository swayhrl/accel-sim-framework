import pathlib,json,hashlib,importlib.util,tempfile,copy,types,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');R=F/'validation_lava_memory_v2';C=R/'control'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_text())
def dump(p,d):P(p).parent.mkdir(parents=True,exist_ok=True);P(p).write_text(json.dumps(d,sort_keys=True,indent=2)+'\n')
path=R/'tools/lavamem_native_v2.py';sp=importlib.util.spec_from_file_location('lm2small',path);n=importlib.util.module_from_spec(sp);sp.loader.exec_module(n)
checks=[]
def ok(name,condition):assert condition,name;checks.append(name)
plan=read(C/'EXECUTION_PLAN_V2.json');profile=read(C/'LAVAMEM_BUILD_PROFILE_V2.json');q=read(C/'REGISTRY_REQUEST_CANDIDATE_V2.json')
for item in plan['source_pins']:assert sha(item['path'])==item['sha256'],item['path']
ok('all_frozen_plan_source_pins_match',True)
ok('R15_V1_candidate_compat_alias_exactbytes',(C/'REGISTRY_REQUEST_CANDIDATE_V1.json').read_bytes()==(C/'REGISTRY_REQUEST_CANDIDATE_V2.json').read_bytes())
unique={}
for cell,digest in q['admitted_specs'].items():
 s=read(C/'specs'/(cell+'.json'));prior=read(s['prior_original_point']['prior_frozen_spec_path']);canonical=C/'specs'/(cell+'.json')
 ok(cell+'_spec_and_alias_exact',sha(canonical)==digest==sha(C/(cell+'_SPEC.json')))
 for key in ['native_simulator_argv','expected_options','input_binding_path','input_binding_sha256','input_digest','binary_sha256','runtime_files','core_commit','framework_commit']:
  if key=='input_binding_path':ok(cell+'_same_original_input_binding_path',s.get(key,'/root/data/dtc_main_v100_sweep_20261025_v1/control/input_bindings/'+s['input_digest']+'.json')==prior.get(key,'/root/data/dtc_main_v100_sweep_20261025_v1/control/input_bindings/'+prior['input_digest']+'.json'))
  elif key in prior:ok(cell+'_unchanged_'+key,s[key]==prior[key])
  else:raise AssertionError((cell,key,'missing prior field'))
 ok(cell+'_hard128G',s['limits']['max_process_tree_rss_bytes']==128*n.G)
 ok(cell+'_complete_input_expected',s['expected']==prior['expected']) if 'expected' in s else None
 for item in s['runtime_files']:unique[item['actual_realpath']]=item['sha256']
 for k in ['prior_INTENT_path','prior_DONE_path','prior_archive_receipt_path']:
  p=s['prior_original_point'].get(k)
  if p:ok(cell+'_'+k,sha(p)==s['prior_original_point'][k.replace('_path','_sha256')])
for p,d in unique.items():assert sha(p)==d,p
ok('all_unique_runtime_SHA_current',True)
ok('new_pool224_255_disjoint_old_pools',set(plan['allowed_model_CPUs'])==set(range(224,256)) and set(plan['allowed_model_CPUs']).isdisjoint(range(64,144)) and set(plan['allowed_model_CPUs']).isdisjoint(range(160,224)))
proof=read(C/'REAL_NATIVE_PRE_POPEN_CPU_QUALIFICATION_V2.json');ok('deep_native_two_positive_one_missingalias_negative',proof['status']=='PASS' and proof['positive_count']==2 and proof['real_model_or_component_processes_forked']==0)
with tempfile.TemporaryDirectory(prefix='RESOURCE_CPU_',dir=R/'analysis') as td:
 d=P(td);n.T=d/'orig';n.R1=d/'oldrepair';n.R=d/'new';roots=[n.T,n.R1,n.R];ids=[n.ORIGINAL,n.PRIOR_REPAIR,n.REQ]
 for root in roots:dump(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
 specs={}
 for root,rid,cell,cap,hard in [(n.T,n.ORIGINAL,'o',256*n.M,16*n.G),(n.R1,n.PRIOR_REPAIR,'p',32*n.M,16*n.G),(n.R,n.REQ,'a',256*n.M,128*n.G),(n.R,n.REQ,'b',256*n.M,128*n.G)]:
  s={'request':rid,'cohort':cell,'limits':{'max_result_directory_bytes':cap,'max_process_tree_rss_bytes':hard}};specs[cell]=s;dump(root/'control'/((cell+'_SPEC.json') if root==n.T else ('specs/'+cell+'.json')),s)
 qs={rid:{'consumed':{},'reserved_write_bytes':100*n.G} for rid in ids};qs['peer']={'state':'ARMED','reserved_write_bytes':7*n.G};qs[n.ORIGINAL]['consumed']['o']={'uuid':'uo'};qs[n.PRIOR_REPAIR]['consumed']['p']={'uuid':'up'}
 n.authority=lambda:({'registered_future_requests':qs},{})
 n.plan=lambda:{'estimated_peak_model_RAM_bytes':96*n.G,'max_process_tree_rss_bytes':128*n.G}
 rss={'uo':2*n.G,'up':6*n.G};n._rss=lambda row,root:rss.get(row['uuid'],0)
 fake=d/'system';(fake/'cg').mkdir(parents=True);mem=fake/'meminfo';(fake/'cg/memory.max').write_text(str(1024*n.G));(fake/'cg/memory.current').write_text('0');(fake/'cg/memory.stat').write_text('file 0\ninactive_file 0\n')
 def memory(host=1024,cg=1024):mem.write_text('MemAvailable: '+str(host*n.G//1024)+' kB\n');(fake/'cg/memory.max').write_text(str(cg*n.G))
 memory();n.P=lambda p:P(mem if str(p)=='/proc/meminfo' else fake/'cg' if str(p)=='/sys/fs/cgroup' else p)
 n.os=types.SimpleNamespace(statvfs=lambda p:types.SimpleNamespace(f_bavail=1024*n.G,f_frsize=1,f_favail=1000000))
 a=n.resources(specs['a'],True);by={x['cohort']:x for x in a['RAM_reservation_entries']}
 ok('new_candidate96G_not4G_envelope',by['a']['envelope_bytes']==96*n.G)
 ok('original4G_floor_actual2G_additional2G',by['o']['envelope_bytes']==4*n.G and by['o']['additional_reserved_bytes']==2*n.G)
 ok('oldrepair_actual6G_doesnot_add96G',by['p']['envelope_bytes']==6*n.G and by['p']['additional_reserved_bytes']==0)
 ok('exact_all_three_scope_projected98G',a['reserved_additional_live_and_candidate_RAM_bytes']==98*n.G)
 ok('oldrepair_not_doublecounted_foreign_ceiling',a['other_outstanding_write_reservations_bytes']==7*n.G and len(a['peer_reservations'])==1)
 expected=5*n.G+3*n.G+512*n.M+64*n.M+512*n.M+7*n.G
 ok('knownwrites_exact_three_owned_metadata_and_live_candidate_caps',a['required_free_bytes']==expected)
 qs[n.REQ]['consumed']['a']={'uuid':'ua'};rss['ua']=110*n.G
 b=n.resources(specs['b'],True);by={x['cohort']:x for x in b['RAM_reservation_entries']}
 ok('live_new110G_uses_actual_above96G_no_extra',by['a']['envelope_bytes']==110*n.G and by['a']['additional_reserved_bytes']==0)
 ok('second_new_still_reserves96G',by['b']['additional_reserved_bytes']==96*n.G)
 memory(1024,100);ok('second_new_refused_when_cgroup100G_with48Gfloor',not n.resources(specs['b'],True)['physical_RAM_pass'])
 ok('runtime_uses_actual_headroom_not_future96G',n.resources(specs['a'],False)['physical_RAM_pass'])
 memory(63,1024);ok('runtime_host63G_rejected',not n.resources(specs['a'],False)['physical_RAM_pass'])
 memory(1024,47);ok('runtime_cgroup47G_rejected',not n.resources(specs['a'],False)['physical_RAM_pass'])
 memory();qs[n.REQ]['reserved_write_bytes']=n.G;ok('new_own_write_ceiling_insufficient_rejected',not n.resources(specs['b'],True)['physical_disk_pass'])
 dump(n.R1/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{'x':{'result_cap_bytes':1}}});specs['x']=dict(specs['p'],cohort='x');dump(n.R1/'control/specs/x.json',specs['x'])
 try:n.resources(specs['b'],True)
 except AssertionError:ok('serialized_claim_cap_mismatch_rejected',True)
 else:raise AssertionError('claim mismatch accepted')
out=C/'LAVAMEM_ENGINE_AND_FROZEN_METADATA_CPU_QUALIFICATION_V2.json'
pins={str(p):sha(p) for p in sorted((R/'tools').glob('*.py'))};pins.update({str(C/name):sha(C/name) for name in ['LAVAMEM_BUILD_PROFILE_V2.json','EXECUTION_PLAN_V2.json','SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json','REGISTRY_REQUEST_CANDIDATE_V2.json','REGISTRY_REQUEST_CANDIDATE_V1.json','SCIENCE_AUTHORIZATION.json','LAVAMEM_SCOPE_CANDIDATE_V2.json','REAL_NATIVE_PRE_POPEN_CPU_QUALIFICATION_V2.json']})
dump(out,{'schema':'LAVAMEM_FINAL_SOURCE_METADATA_AND_ACTUAL_RESOURCE_FUNCTION_CPU_QUALIFICATION_V2','status':'PASS','checks':checks,'check_count':len(checks),'unique_runtime_SHA_count':len(unique),'source_pins':[{'path':p,'sha256':h} for p,h in sorted(pins.items())],'resource_fixture':'Actual frozen resources/_known_writes/_point_spec/output_cap functions with private temp scopes, fake system memory, RSS and authority. No real authority/entry/model action.','input_body_not_rescanned':'Fresh full20.8GB FW header+SHA evidence pinned in profile; immutable input binding and original270options retained.','actual_model_starts':0,'actual_registration_or_entry_changes':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
print(json.dumps({'status':'PASS','check_count':len(checks),'proof':str(out),'sha256':sha(out)},indent=2))
