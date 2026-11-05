"""CPU_SHARED_TIMESLICE proof AND original physics/IO; no CPU2 PASS claimed."""
import pathlib,json,hashlib,importlib.util,os,uuid
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');SOURCE_R=R
ID='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1'
FIELD='additional_cpu_shared_timeslice_binding'
KEY='additional_cpu_shared_timeslice_strict'
SNAP='CPU_SHARED_TIMESLICE_SNAPSHOT.json'
STATUS='PASS_CPU_SHARED_DYNAMIC_IO_AND_ORIGINAL_PERFORMANCE'
DESIGN_SHA='a8c7446a0edaeb166402400f6a8efbf558e54aac690d26dccfda5bbc63a3edc9'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def rawsha(b):return hashlib.sha256(b).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def atomic(path,data):
 path=P(path);temporary=path.with_name('.'+path.name+'.'+uuid.uuid4().hex)
 try:
  with temporary.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
  try:os.link(temporary,path)
  except FileExistsError:assert path.read_bytes()==data
  fd=os.open(path.parent,os.O_RDONLY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if temporary.exists():temporary.unlink()
def terminal(c,base_proof,root=None,authority=None,readonly=False):
 root=P(root or R)
 assert base_proof.get('performance_accepted')is True and type(base_proof.get('cycles'))is int and base_proof['cycles']>0,'Original full physics strict mandatory'
 assert 'additional_cpu_spare_memory_admission_strict'not in base_proof,'Shared CPU cannot claim old CPU2 strict PASS'
 ip=root/'control/qualification_ledger'/(c+'.INTENT.json');intent=read(ip);out=P(intent['output'])
 assert FIELD in intent,'Selected shared generation missing binding'
 forbidden=['additional_cpu_spare_memory_admission_binding','additional_future_memory_admission_binding','additional_padding_admission_binding']
 docs=[intent,read(out/'NATIVE_LAUNCH.json'),read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')]
 assert all(not any(k in doc for k in forbidden)for doc in docs),'Ambiguous or falsely claimed old memory generation'
 b=intent[FIELD];assert all(doc[FIELD]==b for doc in docs),'Three shared bindings differ'
 snapshot_path=out/SNAP;assert sha(snapshot_path)==b['snapshot_sha256'];snap=read(snapshot_path);cfg=snap['config']
 assert snap['schema']==b['schema']==ID and b['request']==cfg['request']and b['cohort']==c
 assert b['mode']==snap['mode']=='CPU_SHARED_DYNAMIC_PER_COHORT'and cfg['max_shared_running']is None,'Explicit dynamic shared reservation generation'
 assert b['padding_optin']is False and snap['padding_optin']is False and b['CPU2_spare_PASS_claimed']is False and snap['CPU2_spare_PASS_claimed']is False,'Shared NOFLAG and honest CPU generation'
 assert cfg['source_paths']['extra_strict']==str(P(__file__).resolve())and cfg['qualified_sources']['extra_strict']==sha(__file__),'Shared extra source mismatch'
 lib=load('exact_shared_resource_library',cfg['source_paths']['library']);assert sha(lib.__file__)==cfg['qualified_sources']['library']and lib.ID==ID
 assert lib.objsha(cfg)==b['config_sha256']
 assert rawsha(snap['design_contract_utf8'].encode())==DESIGN_SHA,'Shared Main contract snapshot'
 design=json.loads(snap['design_contract_utf8']);assert design['resource_id']==ID and design['schema']=='CPU_SHARED_DYNAMIC_RESOURCE_CONTRACT_V1'
 assert cfg['qualification_stage']=='AFTER_REAL_ENGINEERING4_GATE'and cfg['max_shared_running']is None,'Broad dynamic scope only'
 first=snap['fresh_preflights'][0]
 fields=['broad_approval_utf8','broad_gate_utf8','broad_source_artifacts_utf8','scope_contract_utf8']
 for field in fields:assert snap[field]==first[field],'Resource top/proof broad prerequisite mismatch'
 certificate=lib.validate_broad_approval(cfg,authority,first['broad_approval_utf8'],first['broad_gate_utf8'],first['broad_source_artifacts_utf8'],first['scope_contract_utf8'])
 assert c in cfg['allowed_cohorts']
 for p in snap['fresh_preflights']:
  for field in fields:assert p[field]==first[field],'Broad prerequisite witnesses differ'
 canonical_path=root/'control/specs'/(c+'.json');alias=root/'control'/(c+'_SPEC.json');canonical=read(canonical_path)
 assert canonical['host_cpu']is None and sha(canonical_path)==sha(alias),'Canonical identity/alias drift'
 assert rawsha(snap['canonical_spec_utf8'].encode())==snap['canonical_spec_sha256']==sha(canonical_path)and json.loads(snap['canonical_spec_utf8'])==canonical,'Captured canonical source'
 dbp=root/'control/dispatch_bindings'/(c+'.json');db=read(dbp)
 assert db['cohort']==c and db['canonical_spec_sha256']==sha(canonical_path)
 assert rawsha(snap['dispatch_binding_utf8'].encode())==snap['dispatch_binding_sha256']==sha(dbp)and json.loads(snap['dispatch_binding_utf8'])==db,'Captured dispatch source'
 assert lib.objsha(dict(canonical,host_cpu=db['host_cpu']))==db['resolved_spec_sha256']
 assert all(doc['dispatch_binding_sha256']==sha(dbp)for doc in docs),'Three dispatch joins'
 assert docs[2]['host_cpu_affinity_actual']==[db['host_cpu']]==[b['selected_cpu']]
 assert snap['invocation']['selected_cpu']==b['selected_cpu']and snap['invocation']['cohort']==c
 if authority is not None:
  assert authority['admitted_specs'][c]==sha(canonical_path)and authority['consumed'][c]['uuid']==intent['uuid']and authority['consumed'][c]['intent_sha256']==sha(ip)
 for k in ['cohort','uuid','input_digest','core_commit','framework_commit','binary_sha256']:
  expected=c if k=='cohort'else intent['uuid']if k=='uuid'else canonical[k]
  assert base_proof[k]==expected,'Physics/shared identity '+k
 assert len(canonical['expected_options'])==270 and base_proof['effective_options']==canonical['expected_options']
 for actual,frozen in [('CTA','CTA'),('instructions','instructions'),('kernel_count','kernels')]:assert base_proof[actual]==canonical['expected'][frozen]
 qualified=cfg['qualified_sources'];assert set(qualified)==set(lib.ROLES)and b['qualified_sources']==qualified
 for role in lib.ROLES:
  source=snap['source_snapshots'][role];assert source['path']==cfg['source_paths'][role]and source['sha256']==qualified[role]==rawsha(source['utf8'].encode())and sha(source['path'])==qualified[role]
 assert rawsha(snap['QA_utf8'].encode())==cfg['QA_sha256']==b['QA_sha256']
 assert rawsha(snap['readback_utf8'].encode())==cfg['readback_sha256']==b['readback_sha256']
 qa=json.loads(snap['QA_utf8']);back=json.loads(snap['readback_utf8'])
 assert qa['status']=='PASS'and all(qa[k]is True for k in ['cpu_shared_resource_qualified','native_binding_qualified','dynamic_concurrency_qualified'])and back['verified']
 assert qa['qualified_sources']==back['qualified_sources']==qualified and qa['expected_pins']==back['expected_pins']==cfg['expected_pins']
 assert snap['overlay_record']['status']=='ACTIVE'and all(snap['overlay_record'][k]==v for k,v in lib.record(cfg).items())
 assert snap['full_forecast_preflights']==[p['native_full_forecast']for p in snap['fresh_preflights']]and snap['fresh_preflights']
 proofs=[]
 for p in snap['fresh_preflights']:
  assert p['config']==cfg and p['schema']==ID and p['mode']==b['mode'],'Preflight resource generation/config mismatch'
  assert p['canonical_spec_sha256']==snap['canonical_spec_sha256']and p['canonical_spec_utf8']==snap['canonical_spec_utf8'],'Preflight canonical source mismatch'
  raw=p['base_resource_snapshot'];rows=[v for v in raw['own_ram_forecasts']if v['cohort']==c]
  assert len(rows)==1 and rows[0]['kind']=='CLAIM_OR_CANDIDATE'and rows[0]['RSS_bytes']==0
  assert rows[0]['additional_reserved_bytes']==canonical['estimated_peak_model_RAM_bytes'],'Candidate cost may not be discounted'
  f=p['native_full_forecast'];assert f['canonical_estimated_peak_model_RAM_bytes']==canonical['estimated_peak_model_RAM_bytes']
  assert f['forecast_source_sha256']==cfg['expected_pins'][str(SOURCE_R/'tools/l2_resources.py')]
  assert f['forecast']['workload']==canonical['workload']and f['forecast']['predicted_peak_RAM_bytes']<=canonical['estimated_peak_model_RAM_bytes']
  assert p['context']['cohort']==c and p['context']['selected_cpu']==b['selected_cpu']
  proofs.append(lib.verify_proof(p,require_native=True))
 last=snap['fresh_preflights'][-1]
 assert b['final_cpu_evidence_sha256']==lib.objsha(last['cpu_evidence'])
 assert b['final_slot_evidence_sha256']==lib.objsha(last['slot_evidence'])
 assert 'additional_shared_json_io_binding'in intent and rawsha(snap['io_active_utf8'].encode())==cfg['io_active_sha256']
 iocfg=json.loads(snap['io_active_utf8']);io=load('shared_CPU_original_IO_strict',iocfg['extra_strict_path']);assert sha(io.__file__)==iocfg['extra_strict_sha256'];io.R=root
 if readonly:
  # The original IO helper can only validate its already committed sidecar.
  proofkey='additional_shared_json_io_strict'
  existing=out/'SHARED_JSON_IO_EXTRA_STRICT.json';assert existing.exists(),'Readonly IO evidence absent'
 proof=io.terminal(c,base_proof)
 result=dict(status=STATUS,schema=ID,cohort=c,uuid=intent['uuid'],original_performance_strict_required=True,original_IO_strict_required=True,
  shared_CPU_is_not_idle_spare_CPU=True,old_CPU2_PASS_claimed=False,old_CPU_full_gate_PASS_claimed=False,
  extra_strict_source_sha256=sha(__file__),library_source_sha256=cfg['qualified_sources']['library'],snapshot_sha256=sha(snapshot_path),
  qualified_sources=qualified,shared_preflights=proofs,IO_sidecar_sha256=proof['additional_shared_json_io_strict']['sidecar_sha256'])
 side=out/'CPU_SHARED_TIMESLICE_EXTRA_STRICT.json';data=lib.js(result)
 if readonly:assert side.exists()and side.read_bytes()==data,'Readonly shared proof missing/changed'
 elif side.exists():assert side.read_bytes()==data,'Immutable shared proof conflict'
 else:atomic(side,data)
 return dict(proof,**{KEY:dict(result,sidecar_path=str(side),sidecar_sha256=rawsha(data))})
