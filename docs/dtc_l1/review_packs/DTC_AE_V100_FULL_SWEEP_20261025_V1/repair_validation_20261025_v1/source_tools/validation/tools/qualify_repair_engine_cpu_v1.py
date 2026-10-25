"""CPU-only new-engine/source/authority/resource fixtures; no simulator entry."""
import pathlib,json,hashlib,importlib.util,copy,tempfile,types,ast,gzip,datetime
P=pathlib.Path;R=P('/root/data/dtc_failure_repair_20261025_v1/validation');T=P('/root/data/dtc_main_v100_sweep_20261025_v1');F=R.parent;G=1024**3;checks=[]
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
sources=[R/'tools'/name for name in ['repair_native_v1.py','repair_strict_v1.py','repair_outbox_v1.py','repair_frontend_v1.py','repair_ops_v1.py','repair_prepare_specs_v1.py','repair_prepare_scope_v2.py']]
for p in sources:ast.parse(p.read_text())
checks.append('all_new_overlay_sources_parse_without_executing_simulators')
engine=load('CPU_only_repair_engine_overlay',R/'tools/repair_native_v1.py');scope=read(R/'control/REPAIR_SCOPE_CANDIDATE_V2.json');assert len(scope['points'])==scope['finite_budget']==23 and len({p['cohort'] for p in scope['points']})==23 and sum(p['validation_kind']=='COMPONENT_SENTINEL_NOT_FORMAL' for p in scope['points'])==10 and len(read(R/'control/REPAIR_SCOPE_CANDIDATE_V1.json')['points'])==13;checks.append('13_original_failures_and_engineering_issues_plus10_nonformal_sentinels_are_distinct_new_cohorts')
observer=F/'ops/observer_exit_race_v1.py';profile={'observer_overlay':{'path':str(observer),'sha256':sha(observer)}};fakeq={'admitted_specs':{p['cohort']:'fixture' for p in scope['points']}};old_registered=engine.registered;engine.registered=lambda:({}, {},fakeq,profile);native=engine.engine();assert native.ROOT==R and native.REQUEST==engine.REQ and native.resources is engine.resources and native.spec_for is engine.spec_for and native.update_authority is engine.update_authority and native.assert_batch_lease is engine.assert_parent_lease and native.__file__==str(T/'tools/sweep_native_cap1m.py') and native.run_native.__globals__ is native.__dict__ and native.finish_cell.__globals__ is native.__dict__;assert native.exclusive.__code__.co_filename==str(observer) and native._OBSERVER_PROC_RACE_BINDING['adapter_sha256']==sha(observer);engine.registered=old_registered;checks.append('actual_observer_install_preserves_new_ROOT_request_resource_authority_lease_and_nested_metadata_bindings')
# Read actual system counters but inject isolated in-memory request accounting.
old_authority=engine.authority;old_read=engine.read;empty={'consumed':{},'reserved_write_bytes':35*G};repair_empty={'consumed':{},'reserved_write_bytes':int(8.125*G)};fake_reg={'registered_future_requests':{engine.ORIGINAL:empty,engine.REQ:repair_empty}}
engine.authority=lambda:(copy.deepcopy(fake_reg),{});engine.read=lambda path:{'claims':{}} if P(path) in [T/'control/POOL_DISPATCH_RESERVATIONS.json',R/'control/POOL_DISPATCH_RESERVATIONS.json'] else old_read(path)
sample=engine.resources({'cohort':'CPU_ONLY_METADATA','request':engine.REQ},False);assert sample['required_free_bytes']==7*G and sample['known_remaining_writes_by_request'][engine.ORIGINAL]==G and sample['known_remaining_writes_by_request'][engine.REQ]==G;checks.append('shared_actual_write_budget_uses_two_known1GiB_metadata_envelopes_not_original35GiB_or_repair8_125GiB_ceilings')
candidate={'cohort':'E2-AEREPAIR-CPU_FIXTURE-NO_START','request':engine.REQ,'limits':{'max_result_directory_bytes':256*1024**2,'max_process_tree_rss_bytes':16*G}};fresh=engine.resources(candidate,True);assert fresh['required_free_bytes']==7*G+512*1024**2 and fresh['reserved_additional_live_and_candidate_RAM_bytes']==4*G and fresh['RAM_reservation_entries'][-1]['hard_cap_bytes']==16*G;checks.append('candidate_reserves_double_effective_output_cap_and4GiB_initial_RAM_without_lowering16GiB_hard_cap')
engine.authority=old_authority;engine.read=old_read
# Real update_authority implementation, isolated filesystem, never native registry.
real_N=engine.N
with tempfile.TemporaryDirectory(prefix='CPU_ONLY_REPAIR_AUTHORITY_',dir=R/'analysis') as folder:
 sandbox=P(folder);assert sandbox.resolve().is_relative_to((R/'analysis').resolve());engine.N=sandbox;(sandbox/'control/science_authority').mkdir(parents=True);registry={'registered_future_requests':{engine.ORIGINAL:{'budget':7,'remaining':7,'consumed':{}},engine.REQ:{'budget':23,'remaining':23,'consumed':{}}},'old_source_history':['immutable'],'qualification_history':['immutable'],'new_scientific_budget_remaining':30};rp=sandbox/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';ep=sandbox/'control/CURRENT_SCIENCE_EPOCH.json';rp.write_text(json.dumps(registry));ep.write_text(json.dumps({'native_registry_sha256':sha(rp)}));engine.update_authority(lambda reg:reg['registered_future_requests'][engine.REQ].update(remaining=22));after=read(rp);assert after['registered_future_requests'][engine.ORIGINAL]==registry['registered_future_requests'][engine.ORIGINAL] and after['new_scientific_budget_remaining']==29 and read(ep)['request_revision']['request_id']==engine.REQ and read(ep)['native_registry_sha256']==sha(rp);checks.append('actual_authority_writer_updates_only_new_request_and_keeps_original_peer_history_and_hash_epoch_join')
 before=sha(rp)
 try:engine.update_authority(lambda reg:reg['registered_future_requests'][engine.ORIGINAL].update(remaining=0))
 except AssertionError:pass
 else:raise AssertionError('Cross-request mutation was accepted')
 assert sha(rp)==before;checks.append('actual_authority_writer_rejects_original_request_mutation_before_commit')
engine.N=real_N
strict=load('CPU_only_repair_strict',R/'tools/repair_strict_v1.py');old=load('CPU_only_reused_population',T/'tools/sweep_strict_cap1m.py');cell='E2-AEV100-e7bb67e63e3c3847-CM';intent=read(T/'control/qualification_ledger'/(cell+'.INTENT.json'));s=read(T/'control/effective_specs'/(cell+'.json'));domain=read(T/'control/input_bindings'/(s['input_digest']+'.json'))['qualification'];s=copy.deepcopy(s);s['component_mode']='BASE';s['terminal_contract']={'mode_label':'PAPER_BASE','zero_counters':['DTC_L1_pib_occupancy','DTC_L1_lower_outstanding'],'equal_counter_pairs':[['DTC_L1_pib_admits','DTC_L1_pib_retires'],['DTC_L1_lower_requests_acquired','DTC_L1_lower_requests_released']],'constant_counters':{}}
with gzip.open(P(intent['output'])/'raw.log.gz','rt') as stream:raw=stream.read()
proof=strict.sentinel_population(raw,s,domain,old.legacy());assert proof['instructions']==84000768 and proof['CTA']==23438;checks.append('generic_component_population_and_source_backed_contract_replay_real_existing_complete_BASE_stdout')
bad=copy.deepcopy(s);bad['terminal_contract']['mode_label']='PAPER_OO'
try:strict.sentinel_population(raw,bad,domain,old.legacy())
except AssertionError:pass
else:raise AssertionError('Wrong mode accepted')
checks.append('generic_component_strict_rejects_wrong_mode')
for point in scope['points']:
 if point['validation_kind']!='COMPONENT_SENTINEL_NOT_FORMAL':continue
 template=read(point['spec_template_path']);template.update(validation_kind=point['validation_kind'],source_kind=point['source_kind'],input_binding_path=point['input_binding_path'],input_binding_sha256=point['input_binding_sha256']);engine.check_input(template)
checks.append('all10_real_full_or_explicit_synthetic_sentinel_bindings_and_current_SHA_identity_pass_without_simulation')
result={'status':'PASS','check_count':len(checks),'checks':checks,'source_pins':[{'path':str(p),'sha256':sha(p)} for p in sources],'observer_overlay_sha256':sha(observer),'scope23_sha256':sha(R/'control/REPAIR_SCOPE_CANDIDATE_V2.json'),'actual_native_registry_or_entry_mutations':0,'scientific_or_component_simulations_started':0,'run_native_calls':0,'CPU_fixture_only_no_new_scientific_acceptance':True,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};path=R/'control/ENGINE_OVERLAY_CPU_QUALIFICATION_V1.json';assert not path.exists();path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
