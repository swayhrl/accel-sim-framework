"""New explicitly named memory/padding/IO replay AND original performance strict.
No old B5 PASS is invented. Historical unbound generations use their old chain.
"""
import pathlib,json,hashlib,importlib.util
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');SOURCE_R=R
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def rawsha(b):return hashlib.sha256(b).hexdigest()
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def terminal(c,base_proof):
 assert base_proof['performance_accepted']is True,'Original full physics/performance strict mandatory';ip=R/'control/qualification_ledger'/(c+'.INTENT.json');intent=read(ip)
 if'additional_cpu_spare_memory_admission_binding'not in intent:return base_proof
 assert 'additional_future_memory_admission_binding'not in intent,'New CPU generation cannot also claim old memory binding'
 out=P(intent['output']);dbp=R/'control/dispatch_bindings'/(c+'.json');db=read(dbp);canonicalp=R/'control/specs'/(c+'.json');canonical=read(canonicalp)
 assert db['cohort']==c and db['canonical_spec_sha256']==sha(canonicalp)
 docs=[intent,read(out/'NATIVE_LAUNCH.json'),read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')];b=intent['additional_cpu_spare_memory_admission_binding'];assert all(x['additional_cpu_spare_memory_admission_binding']==b for x in docs);snapshot_path=out/'CPU_SPARE_MEMORY_ADMISSION_SNAPSHOT.json';assert sha(snapshot_path)==b['snapshot_sha256'];snap=read(snapshot_path);cfg=snap['config'];assert sha(__file__)==cfg['extra_strict_sha256'];lib=load('memory_strict_qualified_library',cfg['library_path']);assert lib.sha(lib.__file__)==cfg['library_sha256'];assert b['schema']==snap['schema']==lib.ID and b['request']==cfg['request']==lib.REQ and lib.objsha(cfg)==b['config_sha256'];assert b['padding_optin']is False and snap['padding_optin']is False;assert 'additional_padding_admission_binding'not in intent;assert lib.objsha(dict(canonical,host_cpu=db['host_cpu']))==db['resolved_spec_sha256'];assert all(x['dispatch_binding_sha256']==sha(dbp)for x in docs);assert docs[2]['host_cpu_affinity_actual']==[db['host_cpu']]==[b['selected_cpu']];assert snap['invocation']['selected_cpu']==b['selected_cpu'];assert 'additional_future_memory_admission_binding'not in docs[1]and 'additional_future_memory_admission_binding'not in docs[2];qualified={r:cfg[r+'_sha256']for r in lib.ROLES};assert b['qualified_sources']==qualified
 assert rawsha(snap['canary_qualification_utf8'].encode())==cfg['canary_qualification_sha256']
 canary=json.loads(snap['canary_qualification_utf8'])
 assert canary['status']=='PASS_CPU_SPARE_CANARY_NATURAL_STRICT_ARCHIVE_NATIVE_RESTORE'
 assert canary['production_release_eligible']is True and canary['original_performance_accepted']is True
 assert canary['cohort']in cfg['previous_cpu_v1_config']['cpu_exception_scope']['allowed_cohorts']
 assert b['old_V2_PRESSURE_PASS_claimed']is False
 assert snap['full_forecast_preflights']==[p['native_full_forecast']for p in snap['fresh_preflights']]
 for p in snap['fresh_preflights']:
  raw=p['base_resource_snapshot'];rows=[r for r in raw['own_ram_forecasts']if r['cohort']==c]
  assert len(rows)==1 and rows[0]['kind']=='CLAIM_OR_CANDIDATE'and rows[0]['RSS_bytes']==0
  assert rows[0]['additional_reserved_bytes']==canonical['estimated_peak_model_RAM_bytes']
  f=p['native_full_forecast'];assert f['canonical_estimated_peak_model_RAM_bytes']==canonical['estimated_peak_model_RAM_bytes']
  assert f['forecast_source_sha256']==cfg['expected_pins'][str(SOURCE_R/'tools/l2_resources.py')]
  assert f['forecast']['workload']==canonical['workload']and f['forecast']['predicted_peak_RAM_bytes']<=canonical['estimated_peak_model_RAM_bytes']
 if b['mode']=='CPU_SPARE_PER_COHORT':assert b['final_cpu_evidence_sha256']==lib.objsha(snap['fresh_preflights'][-1]['cpu_evidence'])
 else:assert b['final_cpu_evidence_sha256']is None and all('cpu_evidence'not in p for p in snap['fresh_preflights'])
 for role in lib.ROLES:assert snap['source_snapshots'][role]['sha256']==qualified[role]==rawsha(snap['source_snapshots'][role]['utf8'].encode('utf-8'))
 assert rawsha(snap['QA_utf8'].encode())==cfg['QA_sha256']==b['QA_sha256']and rawsha(snap['readback_utf8'].encode())==cfg['readback_sha256']==b['readback_sha256'];qa=json.loads(snap['QA_utf8']);back=json.loads(snap['readback_utf8']);assert qa['status']=='PASS'and qa['native_prefix_qualified']and qa['joint_strict_qualified']and back['verified'];assert qa['qualified_sources']==back['qualified_sources']==qualified and qa['expected_pins']==back['expected_pins']==cfg['expected_pins'];assert snap['record']['status']=='ACTIVE'and all(snap['record'][k]==v for k,v in lib.record(cfg).items());assert rawsha(snap['io_active_utf8'].encode())==cfg['io_active_sha256'];assert snap['fresh_preflights'];memory_results=[lib.verify_memory_proof(p,require_native=True)for p in snap['fresh_preflights']];assert all(p['base_resource_snapshot']['source_module_sha256']==cfg['expected_pins'][str(SOURCE_R/'tools/l2_resources.py')]and p['base_resource_snapshot']['policy_sha256']==cfg['expected_pins'][str(SOURCE_R/'control/RESOURCE_POLICY.json')]for p in snap['fresh_preflights']);assert snap['invocation']['cohort']==c==b['cohort'];assert b['mode']==snap['mode']in ('CPU_SPARE_PER_COHORT','MEMORY_ONLY_OLD_CPU_RULES');assert all(p['mode']==b['mode'] and p['context']['cohort']==c and p['context']['selected_cpu']==b['selected_cpu']for p in snap['fresh_preflights']);assert 'additional_shared_json_io_binding'in intent,'IO evidence mandatory';iocfg=json.loads(snap['io_active_utf8']);proof=dict(base_proof)
 if snap['padding_optin']:
  assert 'additional_padding_admission_binding'in intent;joint=load('memory_joint_padding_replay',cfg['joint_padding_path']);assert sha(joint.__file__)==cfg['joint_padding_sha256'];joint.R=R;joint._MEMORY_VERIFY=lib.verify_memory_proof;pcfg=read(out/'PADDING_ACTIVATION_CONFIG.json');assert pcfg['extra_strict_sha256']==cfg['expected_pins'][str(SOURCE_R/'control/operational_amendments/padding_only_v1/padding_extra_strict.py')];pad=joint.terminal(c,pcfg,proof,snap['fresh_preflights'],pcfg['extra_strict_sha256']);assert pad['status']=='PASS_PADDING_MEMORY_AND_ORIGINAL_PERFORMANCE';proof['additional_future_memory_padding_strict']=pad;io=load('memory_joint_IO_replay',cfg['joint_io_path']);assert sha(io.__file__)==cfg['joint_io_sha256'];io.R=R;proof=io.terminal(c,proof);io_key='additional_future_memory_io_strict'
 else:
  assert 'additional_padding_admission_binding'not in intent;io=load('memory_original_IO_replay',iocfg['extra_strict_path']);assert sha(io.__file__)==iocfg['extra_strict_sha256'];io.R=R;proof=io.terminal(c,proof);io_key='additional_shared_json_io_strict'
 result=dict(status='PASS_CPU_SPARE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE',old_CPU_full_gate_PASS_claimed=False,original_performance_strict_required=True,padding_optin=snap['padding_optin'],old_B5_strict_PASS_claimed=False,new_memory_source_sha256=cfg['library_sha256'],extra_strict_source_sha256=sha(__file__),snapshot_sha256=sha(snapshot_path),memory_preflights=memory_results,IO_sidecar_sha256=proof[io_key]['sidecar_sha256'],qualified_sources=qualified,policy_fraction=.95,host_and_cgroup_floor_bytes=10*1024**3);side=out/'CPU_SPARE_MEMORY_EXTRA_STRICT.json';data=lib.js(result)
 if side.exists():assert side.read_bytes()==data
 else:lib.atomic(side,result)
 return dict(proof,additional_cpu_spare_memory_admission_strict=dict(result,sidecar_path=str(side),sidecar_sha256=rawsha(data)))
