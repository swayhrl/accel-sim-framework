import pathlib
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents');IO=A/'B/shared_json_outer_v1';D=A/'A/future_memory_admission_v1';s=(IO/'qualify_io_native_prefix.py').read_text();s=s.replace("IO=P(__file__).parent;B=IO.parent/'padding_only_overlay_v1'","IO=P("+repr(str(IO))+");D=P(__file__).parent;B=IO.parent/'padding_only_overlay_v1'").replace("dir=IO","dir=D");anchor="outer.R=fixture;pcfgpath=";injected="""
memory=load('new_future_memory_library',D/'future_memory.py');memory_roles=dict(library='future_memory.py',frontend='memory_frontend.py',owner='memory_owner.py',extra_strict='memory_extra_strict.py',joint_padding='joint_padding_strict.py',joint_io='joint_io_strict.py');memory_qualified={k:core.sha(D/n)for k,n in memory_roles.items()};ioactive=fixture/'IO_ACTIVE_FIXTURE.json';ioactive.write_bytes(core.canonical(iocfg));mpins={x['path']:x['sha256']for x in plan['source_pins']};mpins[str(REAL/'control/RESOURCE_POLICY.json')]=core.sha(REAL/'control/RESOURCE_POLICY.json');mpins[str(REAL/'control/operational_amendments/padding_only_v1/padding_extra_strict.py')]=core.sha(B/'padding_extra_strict.py');mpins.update(pins);memoryqa=fixture/'MEMORY_CPU_QA_SYNTHETIC.json';memoryback=fixture/'MEMORY_CPU_BACK_SYNTHETIC.json';memoryval=dict(qualified_sources=memory_qualified,expected_pins=mpins);memoryqa.write_bytes(core.canonical(dict(memoryval,status='PASS',native_prefix_qualified=True,joint_strict_qualified=True,CPU_fixture_only=True)));memoryback.write_bytes(core.canonical(dict(memoryval,verified=True,CPU_fixture_only=True)));mcfg=dict(status='ACTIVE_FUTURE_ONLY',request=memory.REQ,overlay_id=memory.ID,scope_mode='FINITE_CANARY',memory_utilization_fraction=.95,host_floor_bytes=10*core.G,cgroup_floor_bytes=10*core.G,expected_pins=mpins,io_active_path=str(ioactive),io_active_sha256=core.sha(ioactive),allowed_cohorts=[c],QA_path=str(memoryqa),QA_sha256=core.sha(memoryqa),readback_path=str(memoryback),readback_sha256=core.sha(memoryback))
for role,name in memory_roles.items():mcfg[role+'_path']=str(D/name);mcfg[role+'_sha256']=core.sha(D/name)
q['additional_operational_overlays'][memory.ID]=dict(memory.record(mcfg),status='ACTIVE')
outer.R=fixture;pcfgpath=""";s=s.replace(anchor,injected);s=s.replace("native,overlay=outer.private_engine(iocfg,padding_mode,native_module=engine)","native,overlay=outer.private_engine(iocfg,padding_mode,native_module=engine);native=memory.install_future_native(native,mcfg,padding_mode)");s=s.replace("v=overlay.resources(resolved,True)if overlay else base_resource(resolved,True)","v=native.resources(resolved,True)");start=s.index("oldproof=dict(performance_accepted=True,CPU_fixture_base_mock=True)");s=s[:start]+'''
oldproof=dict(performance_accepted=True,CPU_fixture_base_mock=True);extra=load('prefix_memory_extra',D/'memory_extra_strict.py');extra.R=fixture;proof=extra.terminal(c,oldproof);ck('newmemory_IO_originalperformance_closed',proof['additional_future_memory_admission_strict']['status']=='PASS_FUTURE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE');ck('memory_three_bindings_exact',all(x['additional_future_memory_admission_binding']==intent['additional_future_memory_admission_binding']for x in documents));ck('memory_snapshot_exactSHA',intent['additional_future_memory_admission_binding']['snapshot_sha256']==core.sha(out/'FUTURE_MEMORY_ADMISSION_SNAPSHOT.json'));ck('no_oldB5_PASS_claimed',proof['additional_future_memory_admission_strict']['old_B5_strict_PASS_claimed']is False)
try:extra.terminal(c,dict(performance_accepted=False))
except AssertionError:checks.append('false_original_performance_never_promoted')
else:raise AssertionError('false original strict accepted')
snapshot=core.read(out/'FUTURE_MEMORY_ADMISSION_SNAPSHOT.json');runtime_base=base_resource(resolved,False);runtime_wrapper=memory.wrap_resources(lambda *a:runtime_base);ck('freshFalse exactoldobject_return',runtime_wrapper(resolved,False)is runtime_base);mp=snapshot['fresh_preflights'][0]
for label,mutate in [('growth_reduction',lambda p:p.update(growth_unchanged_bytes=p['growth_unchanged_bytes']-1)),('cachecredit_fabrication',lambda p:p.update(no_new_clean_cache_credit=False)),('sample_host_mismatch',lambda p:p['sample'].update(host_MemAvailable_bytes=p['sample']['host_MemAvailable_bytes']+1)),('pressure_erasure',lambda p:p.update(pressure_reasons=['CPU_FIXTURE_PRESSURE'])),('own_bound_bypass',lambda p:p.update(disk_and_own_bound_pass=False)),('budget_increase',lambda p:p['effective_decision'].update(admission_RAM_budget_bytes=p['effective_decision']['admission_RAM_budget_bytes']+1)),('canonical_cost_reduction',lambda p:p.update(canonical_candidate_and_claim_costs_unchanged=False))]:
 bad=copy.deepcopy(mp);mutate(bad)
 try:memory.verify_memory_proof(bad)
 except(RuntimeError,AssertionError):checks.append('memoryreject_'+label)
 else:raise AssertionError(label+' accepted')
saved=copy.deepcopy(pid);badpid=copy.deepcopy(pid);badpid['additional_future_memory_admission_binding']['snapshot_sha256']='0'*64;(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json').write_bytes(core.canonical(badpid))
try:extra.terminal(c,oldproof)
except AssertionError:checks.append('mismatched_newmemory_PIDbinding_rejected')
else:raise AssertionError('mismatched newmemorybinding accepted')
(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json').write_bytes(core.canonical(saved))
if padding_mode:
 joint=load('cpu_joint_memory_padding',D/'joint_padding_strict.py');joint.R=fixture;joint._MEMORY_VERIFY=memory.verify_memory_proof;legacy=load('cpu_old_padding_strict',B/'padding_extra_strict.py');legacy.R=fixture;ev=core.read(out/'PADDING_ADMISSION_EVIDENCE.json');overlaymod=load('cpu_joint_overlay',out/'PADDING_OVERLAY_SOURCE.py');ob=overlaymod.PaddingOverlay(fixture,out/'PADDING_POLICY.json',out/'PADDING_CERTIFICATES.json',ev['binding']['policy_sha256'],ev['binding']['certificate_sha256'],lambda:{},lambda *_:None)
 for old in ev['fresh_preflights']:ck('oldproof_legacy_replay_equivalent',legacy.replay_proof(old,ob,c)==joint.replay_proof(old,ob,c))
 original=ev['fresh_preflights'][0];T=original['effective_total_additional_RAM_bytes'];H=int((T/.95+10*core.G+T/.88+8*core.G)/2);oldbudget=int((H-8*core.G)*.88);newbudget=int((H-10*core.G)*.95);ck('synthetic_newbudget_only_window_exists',oldbudget<T<=newbudget);changed=copy.deepcopy(original);changed['base_resource_sample'].update(host_MemAvailable_bytes=H,cgroup_effective_headroom_bytes=H);changed['base_decision']['admission_RAM_budget_bytes']=oldbudget;changed['effective_decision']['admission_RAM_budget_bytes']=oldbudget;changed['base_decision']['pass_admission']=changed['base_total_additional_RAM_bytes']<=oldbudget;changed['effective_decision']['pass_admission']=False;matching=next(x for x in snapshot['fresh_preflights']if x['legacy_padding_proof_sha256']==memory.objsha(original));base=copy.deepcopy(matching['base_resource_snapshot']);base.update(host_MemAvailable_bytes=H,cgroup_effective_headroom_bytes=H,additional_padding_admission_proof=changed,admission_decision=copy.deepcopy(changed['effective_decision']),total_projected_additional_RAM_bytes=T,physical_RAM_pass=False);newmp=memory.project(base)['additional_future_memory_admission_proof'];newmp['legacy_padding_proof_sha256']=memory.objsha(changed);joint.replay_proof(changed,ob,c,newmp);checks.append('newjoint_strict_accepts_explicit095only_window_preservingallcosts')
 try:legacy.replay_proof(changed,ob,c)
 except AssertionError:checks.append('oldstrict_correctly_HOLD_same095only_window_not_claimedPASS')
 else:raise AssertionError('old strict wrongly accepted newwindow')
 for key in ['candidate_full_original','all_foreign_and_claims_unchanged','no_physical_headroom_credit']:
  bad=copy.deepcopy(changed);bad[key]=False
  try:joint.replay_proof(bad,ob,c,newmp)
  except(RuntimeError,AssertionError):checks.append('jointreject_'+key)
  else:raise AssertionError(key+' bypassed')
 for key in ['total_discount_bytes','snapshot_total_discount_cap_bytes','total_topup_bytes','effective_total_additional_RAM_bytes']:
  bad=copy.deepcopy(changed);bad[key]+=1
  try:joint.replay_proof(bad,ob,c,newmp)
  except(RuntimeError,AssertionError):checks.append('jointreject_'+key)
  else:raise AssertionError(key+' bypassed')
 if changed['claim_candidate_topups']:
  bad=copy.deepcopy(changed);bad['claim_candidate_topups'][0]['canonical_prediction']+=1
  try:joint.replay_proof(bad,ob,c,newmp)
  except(RuntimeError,AssertionError):checks.append('jointreject_canonical_fullprediction')
  else:raise AssertionError('canonical cost bypassed')
 if changed['discount_rows']:
  bad=copy.deepcopy(changed);bad['discount_rows'][0]['uuid']='WRONG_GENERATION'
  try:joint.replay_proof(bad,ob,c,newmp)
  except(RuntimeError,AssertionError):checks.append('jointreject_discount_generation')
  else:raise AssertionError('discount generation bypassed')
report=dict(status='PASS',mode='padding'if padding_mode else'noflag',checks=checks,passed=len(checks),actual_model_starts=0,model_Popen_was_mock=True,fixture=str(fixture),synthetic_authority_lease_headroom_proc_and_baseproof_only_in_CPU_fixture=True,production_mutations=0,qualified_sources=memory_qualified,expected_pins=mpins,model_signal_calls=0,original_IO_and_optional_padding_math_checks_retained=True);(D/('NATIVE_PREFIX_'+report['mode'].upper()+'.json')).write_bytes(core.canonical(report));print(json.dumps(dict(status='PASS',mode=report['mode'],checks=len(checks),path=str(D/('NATIVE_PREFIX_'+report['mode'].upper()+'.json')))))
''';(D/'qualify_native_prefix.py').write_text(s);print(str(D/'qualify_native_prefix.py'))
