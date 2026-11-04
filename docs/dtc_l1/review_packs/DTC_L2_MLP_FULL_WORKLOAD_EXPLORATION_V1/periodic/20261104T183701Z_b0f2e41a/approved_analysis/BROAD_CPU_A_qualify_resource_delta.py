"""Dynamic-scope/resource delta only. Private authority; no models or production changes."""
import pathlib as P,json,hashlib,copy,importlib.util,types,os,ast,time,traceback
D=P.Path(__file__).parent;A=D.parents[2];R=P.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def read(p):return json.loads(P.Path(p).read_bytes())
def sha(p):return hashlib.sha256(P.Path(p).read_bytes()).hexdigest()
def put(p,v):p=P.Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
fx=load('broad_resource_private_fixture',D/'cpu_fixture.py');f=fx.fixture();lib=f.lib;checks=[]
def check(name,fn):
 try:result=fn();checks.append(dict(name=name,status='PASS',details=result))
 except BaseException as e:checks.append(dict(name=name,status='FAIL',error=repr(e),traceback=traceback.format_exc()))
def rejects(fn):
 try:fn()
 except Exception as e:return str(e)
 raise AssertionError('Expected rejection')
def actual_approval():
 cfg=copy.deepcopy(f.cfg);cfg.update(qualification_only=False,broad_approval_path=str(A/'coordinator/BROAD_SHARED_CPU_PREREQUISITE_APPROVAL_V1/APPROVAL.json'),broad_approval_sha256='5c5124f795bb46e0883d1aa8b2ab12144c162bb179fe9d453a18b7022062d682')
 q=read('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests'][lib.REQ]
 result=lib.validate_broad_approval(cfg,q);again=lib.validate_broad_approval(cfg,None,result['certificate_utf8'],result['gate_utf8'],result['source_artifacts_utf8'],result['scope_contract_utf8']);assert result==again
 assert len(cfg['allowed_cohorts'])==26 and len(json.loads(result['gate_utf8'])['rows'])==4
 bad=copy.deepcopy(result['source_artifacts_utf8']);key=next(iter(bad));bad[key]+=' '
 assert rejects(lambda:lib.validate_broad_approval(cfg,None,result['certificate_utf8'],result['gate_utf8'],bad,result['scope_contract_utf8']))
 return dict(real_actual_four_artifacts_readonly=True,actual_gate='2a5422d1097c2e6578ff3ba4b2769a64918378bd120c35a305c7ab90c8e990b9',scope26=True,artifact_tamper_rejected=True)
check('real_mixed4_approval_source_scope_online_offline',actual_approval)
def private_fixture_boundary():
 lib.validate(f.cfg,f.q);cfg=copy.deepcopy(f.cfg);cfg['qualification_only']=False
 assert rejects(lambda:lib.validate_broad_approval(cfg,None))
 unknown=copy.deepcopy(f.cfg);unknown['allowed_cohorts']+=['UNAPPROVED']
 assert rejects(lambda:lib._scope(unknown,f.q))
 q=copy.deepcopy(f.q);c=next(x['cohort']for x in q['authorized_incident_recovery_trials']);q['authorized_incident_recovery_trials'][0]['original_uuid']='FORGED'
 assert rejects(lambda:lib._scope(f.cfg,q))
 assert lib.eligible_cohort(f.cfg,f.q,f.c,'NATIVE')and not lib.eligible_cohort(f.cfg,f.q,f.c,'OWNER_CHOOSE',f.claims)
 q=copy.deepcopy(f.q);q['consumed'][f.c]={'uuid':'NO_RETRY'};assert not lib.eligible_cohort(f.cfg,q,f.c,'NATIVE')
 return dict(private_gate_cannot_release_production=True,unknown_scope_IRlineage_and_spent_rejected=True,Native_self_claim_allowed=True)
check('explicit_finite_scope_private_approval_no_retry_and_IRauthorization',private_fixture_boundary)
def dynamic():
 others=[c for c in f.cfg['allowed_cohorts']if c!=f.c][:2];claims=copy.deepcopy(f.claims)
 for i,c in enumerate(others,1):claims[c]={'host_cpu':i,'cpu_shared_timeslice_overlay_id':lib.ID}
 put(f.root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims});slot=lib.capture_slot_evidence(f.cfg,f.q,f.c,0,root=f.root);verdict=lib.verify_slot_evidence(slot,f.cfg,f.c,0)
 assert slot['max_shared_running']is None and slot['prospective_shared_count']==3 and slot['prospective_cpu_threads']==3
 cpu=f.cpu(0,3);assert lib.verify_cpu_evidence(cpu,0,3)['quota_checks'][0]['prospective_threads']==3
 assert rejects(lambda:lib.verify_cpu_evidence(f.cpu(0,11),0,11)) # fixture 16quota,2used: 13>12
 bad=copy.deepcopy(slot);bad['prospective_cpu_threads']=1;assert rejects(lambda:lib.verify_slot_evidence(bad,f.cfg,f.c,0))
 bad=copy.deepcopy(slot);bad['unspent_claim_canonical_costs'].pop(others[0]);assert rejects(lambda:lib.verify_slot_evidence(bad,f.cfg,f.c,0))
 i=f.inputs();i['base']['host_MemAvailable_bytes']=500*lib.G;i['base']['cgroup_effective_headroom_bytes']=600*lib.G
 for c in others:i['base']['own_ram_forecasts'].append(dict(cohort=c,kind='CLAIM_OR_CANDIDATE',RSS_bytes=0,additional_reserved_bytes=slot['unspent_claim_canonical_costs'][c]['estimated_peak_model_RAM_bytes']))
 i['base']['total_projected_additional_RAM_bytes']=sum(x['additional_reserved_bytes']for x in i['base']['RAM_reservation_entries']+i['base']['own_ram_forecasts'])
 p=lib.project_for_candidate(**i)[lib.PROOF];assert lib.verify_proof(p)['full_growth_bytes']==i['base']['total_projected_additional_RAM_bytes']
 bad=copy.deepcopy(p);bad['base_resource_snapshot']['own_ram_forecasts']=[x for x in bad['base_resource_snapshot']['own_ram_forecasts']if x['cohort']!=others[0]];raw=bad['base_resource_snapshot'];raw['total_projected_additional_RAM_bytes']=sum(x['additional_reserved_bytes']for x in raw['RAM_reservation_entries']+raw['own_ram_forecasts']);bad['old95_resource_snapshot']=lib._OLD.project(raw);bad['growth_unchanged_bytes']=raw['total_projected_additional_RAM_bytes']
 assert rejects(lambda:lib.verify_proof(bad))
 put(f.root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':f.claims})
 return dict(shared_three_pass_no_static_cap=True,all_otherclaims_reserved_CPU_and_RAM=True,quota_exceed_and_forged_reservation_omission_rejected=True)
check('dynamic_multijob_quota_allclaims_RAM_reservations_not_cap1',dynamic)
def busy_quota():
 e=f.cpu(0);v=lib.verify_cpu_evidence(e,0);assert v['host_mean_busy']>.85 and v['min_idle_core_rule_applied']is False
 for mutate in [lambda e:e['raw_cpu2_evidence']['second']['cgroups']['visible'][0]['stat'].update(nr_throttled=1),lambda e:e['raw_cpu2_evidence']['second']['cgroups']['visible'][0]['stat'].pop('usage_usec')]:
  bad=copy.deepcopy(e);mutate(bad);assert rejects(lambda:lib.verify_cpu_evidence(bad,0))
 actual=lib.sample_cpu_evidence(None,.5);verdict=lib.verify_cpu_evidence(actual);assert verdict['hidden_ancestor_limits_excluded']is False
 return dict(raw_busy_fixture=v['host_mean_busy'],actual_readonly_double_sample=verdict,old_CPU2_PASS_claimed=False)
check('busy_host_timesharing_real_sample_quota_throttle_missingfields',busy_quota)
def physical():
 lib.project_for_candidate(**f.inputs())
 for kind in ['RAM','disk','pressure','fullcandidate']:
  i=f.inputs()
  if kind=='RAM':i['base']['host_MemAvailable_bytes']=10*lib.G
  if kind=='disk':i['base']['physical_disk_pass']=False
  if kind=='pressure':i['base']['admission_decision']['pressure_reasons'].append('io_pressure_full')
  if kind=='fullcandidate':i['base']['own_ram_forecasts']=[];i['base']['total_projected_additional_RAM_bytes']=3*lib.G
  assert rejects(lambda:lib.project_for_candidate(**i)),kind
 return dict(RAM_disk_IO_fullcandidate_still_HOLD=True,budget_fraction=.95,floor_GiB=10)
check('original_fullRAM_disk_IOpressure_candidate_forecast_gates_preserved',physical)
def science():
 contract=read(f.cfg['scope_contract_path']);spec=copy.deepcopy(f.spec);spec['estimated_peak_model_RAM_bytes']+=123456;spec['limits']['max_process_tree_rss_bytes']+=123456;lib.verify_science_scope(spec,f.c,contract)
 spec['core_commit']='FORGED';assert rejects(lambda:lib.verify_science_scope(spec,f.c,contract))
 row=next(x for x in contract['rows']if x['role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL');c=row['cohort'];spec=read(f.root/'control/specs'/(c+'.json'));lib.verify_science_scope(spec,c,contract);spec['incident_recovery_trial_lineage']['original_uuid']='FORGED';assert rejects(lambda:lib.verify_science_scope(spec,c,contract))
 return dict(legal_RSS_limit_refresh_allowed=True,GPU_science_IR_oldnegative_lineage_drift_rejected=True)
check('operational_canonical_refresh_science_and_IR_role_separation',science)
def closed():
 q=copy.deepcopy(f.q);other=next(c for c in f.cfg['allowed_cohorts']if c!=f.c);uid='PRIVATE_DYNAMIC_CONSUMED';q['consumed'][other]={'uuid':uid};out=f.root/'CPU_ONLY_MISSING_PID';ip=f.root/'control/qualification_ledger'/(other+'.INTENT.json');dp=f.root/'control/qualification_ledger'/(other+'.DONE.json');put(ip,dict(cohort=other,uuid=uid,output=str(out),**{lib.FIELD:{'schema':lib.ID}}))
 slot=lib.capture_slot_evidence(f.cfg,q,f.c,0,root=f.root,proc_reader=lambda pid:{'pid':pid,'missing':True});lib.verify_slot_evidence(slot,f.cfg,f.c,0);assert slot['prospective_cpu_threads']==2
 done=dict(cohort=other,uuid=uid);q['consumed'][other]['execution_receipt']=done;put(dp,done);slot=lib.capture_slot_evidence(f.cfg,q,f.c,0,root=f.root);lib.verify_slot_evidence(slot,f.cfg,f.c,0);assert slot['prospective_cpu_threads']==1
 ip.unlink();dp.unlink();return dict(PIDgone_without_DONE_keeps_future_CPU_reservation=True,joined_DONE_releases_reservation_without_refund_or_retry=True)
check('unclosed_generation_reserved_closed_DONE_releases_only_reservation',closed)
def binder():
 native=types.SimpleNamespace(R=f.root,__file__=str(lib.R/'tools/l2_native.py'),registered=lambda:(None,None,f.q,None),assert_parent_lease=lambda:{'pid':os.getpid(),'fixture':True},spec_for=lambda c:dict(f.spec,host_cpu=0),resources=lambda spec,fresh_source=False:f.base())
 native.engine=lambda:types.SimpleNamespace(exclusive=lambda path,obj:put(path,obj))
 lib.sample_cpu_evidence=f.cpu;lib.capture_legal_cpu_evidence=f.legal;old=native.resources;lib.install_future_native(native,f.cfg,False,invocation_cohort=f.c)
 assert lib.PROOF not in native.resources(f.spec,False)
 out=f.root/'UNIT_NEW_NATIVE_BINDER';out.mkdir();ip=f.root/'control/qualification_ledger'/(f.c+'.INTENT.json');n=native.engine();n.exclusive(ip,dict(cohort=f.c,uuid='PRIVATE_UNIT_NOT_ACTUAL',output=str(out)))
 for name in ['NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json']:n.exclusive(out/name,dict(cohort=f.c))
 docs=[read(p)for p in [ip,out/'NATIVE_LAUNCH.json',out/'NATIVE_SIMULATOR_PID_AND_MAPS.json']];snap=read(out/lib.SNAP);assert all(x[lib.FIELD]==docs[0][lib.FIELD]for x in docs)
 assert snap['schema']==lib.ID and json.loads(snap['broad_approval_utf8'])['qualification_only']is True and json.loads(snap['broad_gate_utf8'])['qualification_only']is True
 for p in snap['fresh_preflights']:lib.verify_proof(p,True)
 assert rejects(lambda:lib.verify_proof(lib.project_for_candidate(**f.inputs(kind='OWNER_FRAME'))[lib.PROOF],True))
 return dict(actual_library_installer_and_exclusive_threebind=True,freshFalse_exact_base=True,actual_native_loop_or_Popen=False,owner_frame_cannot_native=True)
check('new_snapshot_3bindings_fullforecast_native_context_freshFalse',binder)
oldpath=A/'agents/A/cpu_shared_timeslice_stage2_v1/cpu_shared.py';oldtree=ast.parse(oldpath.read_text());newtree=ast.parse((D/'cpu_shared.py').read_text());of={n.name:ast.dump(n,include_attributes=False)for n in oldtree.body if isinstance(n,ast.FunctionDef)};nf={n.name:ast.dump(n,include_attributes=False)for n in newtree.body if isinstance(n,ast.FunctionDef)}
result=dict(schema='BROAD_SHARED_DYNAMIC_RESOURCE_DELTA_CPU_QUALIFICATION_V1',status='PASS'if all(x['status']=='PASS'for x in checks)else'FAIL',checks=checks,count=len(checks),source_path=str(D/'cpu_shared.py'),source_sha256=sha(D/'cpu_shared.py'),driver_path=__file__,driver_sha256=sha(__file__),fixture_sha256=sha(D/'cpu_fixture.py'),fixture_root=str(f.root),unchanged_functions=[k for k,v in of.items()if nf.get(k)==v],changed_functions=[k for k,v in of.items()if nf.get(k)!=v],new_functions=sorted(set(nf)-set(of)),actual_gate_readonly_checked=True,private_role_QA_readback_standins=True,actual_native_loop_or_Popen=False,old20_rerun=False,production_mutations=0,new_grants=0,models_started=0)
put(D/'CPU_RESOURCE_QUALIFICATION.json',result);print(json.dumps(dict(status=result['status'],source_sha256=result['source_sha256'],QA_sha256=sha(D/'CPU_RESOURCE_QUALIFICATION.json'),cases=[(x['name'],x['status'],x.get('error'))for x in checks]),indent=2))
