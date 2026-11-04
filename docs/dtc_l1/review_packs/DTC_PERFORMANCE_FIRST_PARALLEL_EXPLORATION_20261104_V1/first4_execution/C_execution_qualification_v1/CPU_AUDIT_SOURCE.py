import sys,pathlib,json,hashlib,types,copy,ast,os,subprocess,datetime,fcntl,shlex,gzip,zlib
sys.dont_write_bytecode=True
P=pathlib.Path;R=P('/root/data/dtc_perf_first_parallel_exploration_20261104_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1');O=A/'C_first4_execution_qualification_v1';O.mkdir(exist_ok=True);F=O/'private_fixtures';F.mkdir(exist_ok=True)
REQ='DTC_PERF_FIRST_PHYS768_FIRST4_20261104_V1';N=P('/root/data/ep_l2_dtc_l1_native_v2');checks=[]
def rd(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(n,v):(O/n).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def check(n,v):assert v,n;checks.append(dict(name=n,PASS=True))
def reject(n,fn):
 try:fn()
 except (AssertionError,KeyError,ValueError,TypeError,FileNotFoundError):check(n,True);return
 raise AssertionError('DID_NOT_REJECT '+n)
def load(n,p):
 m=types.ModuleType(n);m.__file__=str(p);exec(compile(P(p).read_bytes(),str(p),'exec'),m.__dict__);return m
plan=rd(R/'control/EXECUTION_PLAN.json');candidate=rd(R/'control/REGISTRY_REQUEST_CANDIDATE.json');matrix=rd(R/'control/MATRIX.json');psha=sha(R/'control/EXECUTION_PLAN.json');csha=sha(R/'control/REGISTRY_REQUEST_CANDIDATE.json')
check('final_direction_released_plan',psha=='f656a7a122ec270df1174ed12d6c669c85a329c0d1bd7fb2ebfe308c9d4220d4');check('final_candidate',csha=='3e513d48000bae1aa3a3561c0bcd8e79cf6efa0f1e4854e332de1b8fb4c54738');check('55_distinct_source_pins',len(plan['source_pins'])==len({x['path']for x in plan['source_pins']})==55)
for x in plan['source_pins']:check('pin:'+x['path'],sha(x['path'])==x['sha256'])
for p in (R/'tools').glob('*.py'):compile(p.read_bytes(),str(p),'exec');check('compile:'+p.name,True)
check('exact_fixed4_programs',{x['program']for x in matrix['points']}=={'2DCONV','GEMM','MVT','BICG'} and len(matrix['points'])==4);check('budget4_one_use_only',candidate['budget']==candidate['remaining']==4 and not candidate['consumed']and candidate['model_automatic_retries']==0 and candidate['all_other_candidate_grants']==0 and candidate['execution_plan_sha256']==psha)
with(N/'control/science_authority/REGISTRY_UPDATE.lock').open('rb')as h:
 fcntl.flock(h,fcntl.LOCK_SH);reg=rd(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json');ep=rd(N/'control/CURRENT_SCIENCE_EPOCH.json');check('epoch_registry_atomic_pair',sha(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')==ep['native_registry_sha256'])
check('new_REQ_absent_and_epoch2',REQ not in reg['registered_future_requests']and ep['epoch']==2)
oldident={k:dict(budget=v.get('budget'),remaining=v.get('remaining'),consumed=v.get('consumed'))for k,v in reg['registered_future_requests'].items()};put('OLD_IDENTITIES_PRE_REGISTRATION.json',oldident)
old48=reg['registered_future_requests']['DTC_STAGE_IIA_REMAINING48_CH_MATCH_20261104_V1'];check('old48_all48_consumed_rem0',old48['budget']==len(old48['consumed'])==48 and old48['remaining']==0)
owner=P('/proc/1498278');stat=owner.joinpath('stat').read_text().rsplit(')',1)[1].split();check('same_owner_generation',int(stat[19])==977758783 and stat[0]not in['Z','X']);check('owner_disables_pyc',b'\x00-B\x00'in(owner/'cmdline').read_bytes());check('owner_main_mask32_63',os.sched_getaffinity(1498278)==set(range(32,64)))
for fd,target in [(3,'/root/data/dtc_main_v100_sweep_20261025_v1/control/FINITE_CONTROLLER.lock'),(4,str(N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock'))]:check('owner_exact_retained_fd'+str(fd),os.readlink(owner/'fd'/str(fd))==target and 'FLOCK'in(owner/'fdinfo'/str(fd)).read_text())
lease=rd('/root/data/dtc_main_v100_sweep_20261025_v1/control/BATCH_LEASE.json');check('lease_fresh_scope_not_yet_attached',lease['pid']==1498278 and lease['start_ticks']==977758783 and REQ not in lease['additional_requests'])
e=load('C_isolated_perf4_native',R/'tools/perf4_native.py');original_authority=e.authority;e.authority=lambda:(dict(reg,registered_future_requests=dict(reg['registered_future_requests'],**{REQ:copy.deepcopy(candidate)})),copy.deepcopy(ep))
check('inmemory_exact4_registered',set(e.registered()[2]['admitted_specs'])=={p['cohort']for p in matrix['points']})
base=e.base();base.ROOT=R;specs=[];build=rd(R/'control/BUILD_PROFILE.json');body=[]
for row in matrix['points']:
 c=row['cohort'];s=e.canonical(c);specs.append(s);check('specSHA:'+c,sha(row['canonical_spec_path'])==candidate['admitted_specs'][c]==row['canonical_spec_sha256']);check('exact_scientific_scope:'+c,s['cell']=='DH'and s['downstream_profile']=='P0'and s['profile']==s['structure_variant']=='PHYS768_TAG64x8'and s['host_cpu']is None)
 check('expected_geometry:'+c,s['expected']==row['expected']);check('270_options:'+c,len(s['expected_options'])==270);check('only_physical_target:'+c,s['expected_options']['-gpgpu_dtc_l1_physical_lines']==['768']and s['expected_options']['-gpgpu_dtc_l1_logical_sets']==['64']and s['expected_options']['-gpgpu_dtc_l1_logical_ways']==['8']);check('clock850_hash1_p0:'+c,s['expected_options']['-gpgpu_clock_domains']==['1410.0:1410.0:1410.0:850.0']and s['expected_options']['-gpgpu_frfcfs_dram_sched_queue_size']==['64']and s['expected_options']['-gpgpu_dtc_l1_tag_hash_bankrow']==['1'])
 b=rd(s['input_binding_path']);check('bindingROI:'+c,sha(s['input_binding_path'])==s['input_binding_sha256']and b['input_digest']==s['input_digest']and b['qualification']['expected_instructions']==s['expected']['instructions']and b['qualification']['expected_CTA']==s['expected']['CTA']);body.append(base.check_input(s));check('real_currentstat_true164_input:'+c,body[-1]['status']=='CURRENT_FULL_BODY_SHA_BOUND_GENUINE164_INPUT')
 for x in s['configs']:check('config:'+c+':'+P(x['path']).name,sha(x['path'])==x['sha256'])
 for x in s['runtime_files']:check('runtime:'+c+':'+x['target'],sha(x['actual_realpath'])==x['sha256']and (R/x['target']).resolve()==P(x['actual_realpath']).resolve())
 check('resource_caps:'+c,s['estimated_peak_model_RAM_bytes']<=s['limits']['max_process_tree_rss_bytes']<=s['limits']['max_process_tree_vms_bytes']and s['limits']['max_result_directory_bytes']==64*1024**2)
reject('unknown_old_cohort_rejected',lambda:e.canonical('E2-DTC2A48-wrong-CH-F128-V1'));reject('Tag_HOLD_cohort_rejected',lambda:e.canonical('E2-DTCPF4-'+specs[0]['input_digest'][:16]+'-DH-TAG64x16-V1'))
for label,key,val in [('badbudget','budget',5),('badremaining','remaining',3),('retry','model_automatic_retries',1),('badplan','execution_plan_sha256','0'*64)]:
 bad=copy.deepcopy(candidate);bad[key]=val;e.authority=lambda b=bad:(dict(reg,registered_future_requests={REQ:b}),ep);reject('registered_rejects_'+label,e.registered)
e.authority=original_authority
for k in ['core','framework']:
 repo=build['source_worktrees'][k];check('fixed_git_'+k,subprocess.check_output(['git','-C',repo,'rev-parse','HEAD'],text=True).strip()==build[k+'_commit']);check('clean_git_'+k,not subprocess.check_output(['git','-C',repo,'status','--porcelain'],text=True).strip())
# Independent parse actual quoted multi-line configs, same canonical tokenization as full option contract.
def parse(paths):
 out={}
 for path in paths:
  toks=[word for token in shlex.split(P(path).read_text(),comments=True)for word in token.split()];key=None
  for t in toks:
   if t.startswith('-')and len(t)>1 and t[1].isalpha():key=t;out[key]=[]
   else:assert key is not None;out[key].append(t)
 return out
for s in specs:
 actual=parse([x['path']for x in s['configs']]);actual['-trace']=[s['native_simulator_argv'][2]];check('actual_all270_options:'+s['program'],all(s['expected_options'].get(k)==v for k,v in actual.items()))
oldopt=parse(sorted(P('/root/data/dtc_l2_mlp_exploration_20261027_v1/DTC/env/DH_P0').glob('config-*.config')));newopt=parse([x['path']for x in specs[0]['configs']]);check('only_model_delta_physical640_to768',{k:(oldopt.get(k),newopt.get(k))for k in set(oldopt)|set(newopt)if oldopt.get(k)!=newopt.get(k)}=={'-gpgpu_dtc_l1_physical_lines':(['640'],['768'])})
# Real header parser adaptation only, no trace/raw/model execution.
cap=load('C_capacity_private',R/'tools/perf4_capacity_strict.py');legacy,bind=cap.load_for(specs[0]);check('capacity49152_only_terminal_gauge',bind['capacity_bound']==768*64 and bind['replacement_count']==1 and bind['all_other_parser_source_bytes_unchanged']and bind['peak_occupancy_not_proven']);source=cap.LEGACY_PATH.read_text();check('legacy9039_original_unchanged',sha(cap.LEGACY_PATH)==cap.LEGACY_SHA256)
for key,val in [('-gpgpu_dtc_l1_physical_lines',['640']),('-gpgpu_n_clusters',['63'])]:
 bad=copy.deepcopy(specs[0]);bad['expected_options'][key]=val;reject('capacity_reject_'+key,lambda b=bad:cap.load_for(b))
strict=(R/'tools/perf4_strict.py').read_text();check('strict_original270_population_preserved','old.population(raw,s,domain,legacy)'in strict and 'capacity_adapter.load_for(s)'in strict);check('strict_natural_identity_sourcekeep_restore','d==row[\'execution_receipt\']==read(out/\'NATIVE_EXIT.json\')'in strict and "last['end']=='NATURAL'"in strict and 'SOURCE_KEEP=True'in strict)
# Inert owner adapter pure route and fail-fast tests. No apply path can pass owner check in this process.
addon=load('C_addon_private',R/'tools/perf4_parent_addon.py');ops=load('C_ops_private',R/'tools/perf4_ops.py');before=(N/'bin/native').read_bytes();block=(R/'control/NATIVE_ROUTE_BLOCK.sh').read_bytes();after=addon.exact_native_route(before,block);check('route_preserves_all_old_bytes',after.replace(block,b'',1)==before)
for n,b,bl in [('duplicate',after,block),('wrongheader',b'#!invalid',block),('wrongscope',before,b'E2-DTC2A48'),('empty',before,b'')]:reject('route_rejects_'+n,lambda b=b,bl=bl:addon.exact_native_route(b,bl))
for s in specs:check('exact_route_for_'+s['program'],s['cohort'].encode()in block)
check('exact_route_no_Tag_or28',b'TAG64x16'not in block and b'DTCPF28'not in block);reject('apply_wrong_OS_owner_before_sideeffects',lambda:addon.apply(str(R)));reject('scheduler_wrong_OS_owner_before_sideeffects',ops.run_scheduler)
so=(R/'tools/perf4_ops.py').read_text();sa=(R/'tools/perf4_parent_addon.py').read_text();check('protected_mask_guard_before_affinity',so.index('PROTECTED_GES_MAIN_CPU_OVERLAP')<so.index('os.sched_setaffinity'));check('serialized_preclaim_before_binding_claim',so.index('fresh=res.resources(spec,True)')<so.index('if db.exists():')<so.index('claims[c]=dict('));check('spent_UUID_not_model_requeued',"if c not in q['consumed']and c not in claims"in so and 'Only same-UUID evidence work can be reconsumed'in so);check('exact4_owner_no_extension','budget=4'in so and "candidate['budget']==candidate['remaining']==4"in sa and 'other28_granted=False'in so);check('original_FD_handles_retained',"{h.fileno()for h in handles}=={3,4}"in sa and "handles=target.__globals__['_KEEPERS']"in sa)
mask=set(plan['new_dispatcher_cpu_allowance']);check('planned_mask_protects_old_Main_and_GES',mask and not mask&({2,258}|set(range(32,64))|set(range(288,320))))
# Real fresh host/peer sampling, isolated in-memory hypothetical request injection only; no registry or claims written.
res=load('C_resources_private',R/'tools/perf4_resources.py');policy=rd(R/'control/RESOURCE_POLICY.json');sample=res.sample_system();peer=res._peer();real_authority=peer.authority;peer.authority=lambda:(dict(reg,registered_future_requests=dict(reg['registered_future_requests'],**{REQ:copy.deepcopy(candidate)})),copy.deepcopy(ep));resources=[]
for s in specs:
 v=res.resources(s,True);resources.append(dict(program=s['program'],resources=v));check('fresh_resource_candidate_'+s['program'],v['physical_RAM_pass']and v['physical_disk_pass']and v['admission_disk_pass'])
peer.authority=real_authority
check('fresh_old_completion_release_matched',not res.old_completion_gate(sample,policy)['pause_new']);p=copy.deepcopy(policy);p['old_final_review_release']=None;check('old_terminal_without_direction_pauses',res.old_completion_gate(sample,p)['pause_new']);p=copy.deepcopy(policy);p['old_final_review_release']['old_terminal_manifest_sha256']='0'*64;check('stale_release_rejected',res.old_completion_gate(sample,p)['pause_new']);check('unknown_old_status_pauses',res.old_completion_gate({},policy)['pause_new'])
reject('missing_RAM_forecast_rejected',lambda:res.forecast(dict(limits={'max_process_tree_rss_bytes':2**40})))
# RAM pressure must not turn runtime-safe archive into false RAM; disk has its own independent admission gate.
G=1024**3;b=dict(required_free_bytes=5*G,peer_reservations=[],reserved_additional_live_and_candidate_RAM_bytes=0,per_scope_write_ceiling_pass={},known_remaining_writes_by_request={});own=dict(projected_write_bytes=64*1024**2,additional_RAM_bytes=G,projection_within_registered_ceiling=True,actual_unarchived_output_bytes=0,ram=[],writes=[]);s=copy.deepcopy(sample);s.update(native_free_bytes=20*G,archive_free_bytes=100*G,free_inodes=1000000,true164_mount_verified=True,host_MemAvailable_bytes=G,cgroup_effective_headroom_bytes=G);rt=res._evaluate(specs[0],False,s,None,b,{},own,candidate,policy);fr=res._evaluate(specs[0],True,s,None,b,{},own,candidate,policy);check('pressure_holds_new_keeps_runtime_archive_safe',not fr['physical_RAM_pass']and rt['physical_RAM_pass']and rt['physical_disk_pass']and rt['admission_disk_pass']);s['native_free_bytes']=4*G;v=res._evaluate(specs[0],False,s,None,b,{},own,candidate,policy);check('actual_below_native_floor_unsafe',not v['physical_disk_pass']);s['native_free_bytes']=20*G;s['true164_mount_verified']=False;v=res._evaluate(specs[0],False,s,None,b,{},own,candidate,policy);check('wrong_archive_mount_holds_archive',not v['admission_disk_pass'])
# Current frozen direction-review identity and scope are source-pinned, not implicit all28 grants.
rel=policy['old_final_review_release'];check('direction_review_bytes_bound',sha(rel['direction_review_path'])==rel['direction_review_sha256']=='e67392dd1f64f9eafdb8beb4f4444628db580c60fa6724edf91545356a033e36');check('first4_only_not_28_grant',candidate['all_other_candidate_grants']==0 and not policy['other28_scientific_release'])
check('no_new_registration_after_CPU',REQ not in rd(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']);check('no_first4_INTENT_models',not list((R/'control/qualification_ledger').glob('*.INTENT.json')))
put('CPU_CHECKS.json',dict(status='PASS',count=len(checks),checks=checks));put('REAL_INPUT_AND_CAPACITY_CHECKS.json',dict(real_inputs=body,capacity_binding=bind));put('FRESH_HYPOTHETICAL_CANDIDATE_RESOURCES.json',dict(status='PASS',explicitly_unregistered_inmemory_candidate_only=True,real_host_peer_stat_sampling=True,rows=resources));put('SOURCE_PINS.json',plan['source_pins']);put('QUALIFICATION_SCOPE.json',dict(real_registry_writes=0,model_entrypoints_called=[],model_starts=0,owner_callbacks=0,signals=0,affinity_changes=0,private_process_only_module_substitutions=True,real_prepare_not_called=True,no_existing_package_changes=True,old_final_review_release_bound=True))
report=dict(schema='C_PERFFIRST_FIRST4_FINAL_CPU_QUALIFICATION_V1',status='PASS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),execution_plan_sha256=psha,registry_candidate_sha256=csha,request=REQ,budget=4,count=len(checks),CPU_only_not_model_acceptance=True,no_prepare_or_run_native_called=True,sole_existing_owner_pid=1498278,sole_existing_owner_start_ticks=977758783,other28_granted=False,Tag16_safety_HOLD=True,remaining28_conditional_authority='119217415136f6bae824ed25ecb5d0776fcd67eeff9dcae7fde6b5a0ce73f894',actual_route_runtime_and_lifecycle_still_required=True,old48_unchanged=True,Root_only_registration_and_callback=True,evidence={n:dict(path=str(O/n),sha256=sha(O/n))for n in ['CPU_CHECKS.json','REAL_INPUT_AND_CAPACITY_CHECKS.json','FRESH_HYPOTHETICAL_CANDIDATE_RESOURCES.json','SOURCE_PINS.json','QUALIFICATION_SCOPE.json','OLD_IDENTITIES_PRE_REGISTRATION.json']})
put('FINAL_CPU_QUALIFICATION.json',report);print(json.dumps(dict(status='PASS',count=len(checks),path=str(O/'FINAL_CPU_QUALIFICATION.json'),sha256=sha(O/'FINAL_CPU_QUALIFICATION.json'))))

