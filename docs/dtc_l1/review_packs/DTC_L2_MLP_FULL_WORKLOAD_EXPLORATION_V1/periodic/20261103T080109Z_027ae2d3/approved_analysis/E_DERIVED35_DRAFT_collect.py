"""Readonly frozen350/source-role gaps and proposed reference mapping. No GM/union."""
import pathlib,json,hashlib,importlib.util,datetime,collections,sys
sys.dont_write_bytecode=True
P=pathlib.Path;D=P(__file__).parent;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def objsha(v):return hashlib.sha256((json.dumps(v,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,v):
 with p.open('x')as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def audit(event,args):
 if event=='subprocess.Popen'or event.startswith('os.exec')or event in('os.system','os.kill','os.killpg'):raise AssertionError('Readonly analysis, no process/model/signal')
sys.addaudithook(audit)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');out=D/stamp;out.mkdir()
engine=load('derive_reference_native_ro',R/'tools/l2_native.py');q=engine.registered()[2]
consumer=load('derive_original_consumer_ro',R/'tools/l2_results.py');assert sha(consumer.__file__)=='6cc6cc30a71740df951327414d094953effb73a406e7036358ad0b702ebb0403'
gen=load('derive_qualified_config_generator',R/'tools/l2_config_generator.py');assert sha(gen.__file__)=='9c22cbdebce13c729768ac7dd1162d16aefbba5fb24dc0f018051b4588bfa281'
scopepath=R/'control/SCOPE.json';matrixpath=R/'control/MATRIX_CURRENT.json';scope=read(scopepath);matrix=read(matrixpath);assert len(scope['points'])==350 and len(matrix['points'])==350
assert {p['cohort']:p for p in scope['points']}=={p['cohort']:p for p in matrix['points']}
irpath=A/'agents/B/incident11_recovery_trials_plan_v1/DRAFT_PLAN.json';assert sha(irpath)=='72ce5472b5d3fc76d4f8d27c3aa3f4f7ad3d224a5ada3eaba88b3f1a2e6feff5';ir=read(irpath);irmap={r['original_cohort']:r['new_cohort']for r in ir['rows']};assert len(irmap)==11
r2planpath=A/'agents/E/supplemental_scan_m16_v2/CANDIDATE_PLAN.json';r2plan=read(r2planpath)
oldscan='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1';newscan='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V2';mapping={**{c:dict(role='INCIDENT_RECOVERY_PERFORMANCE_TRIAL',cohort=n)for c,n in irmap.items()},oldscan:dict(role='SUPPLEMENTAL_NEW_PERFORMANCE_TRIAL',cohort=newscan)}
certpath=A/'engineering_negative_evidence_v1'/oldscan/'1e968456ccefd837eacee605d7ffacc712860114e8a7fea17b4633b25cecbf5f/ENGINEERING_TERMINAL_NEGATIVE.json';assert sha(certpath)=='37842f4191c6a0f293a01d22834c28794c3e23a477b1d657976d01bdb055c9e7'
specs={};evidence={}
def measure(c):
 if c in evidence:return evidence[c]
 path=R/'control/specs'/(c+'.json');s=read(path);specs[c]=s;rp=R/'analysis'/(c+'.RESULT.json');result=None;read_error=None
 if rp.exists():
  try:result=read(rp)
  except(ValueError,OSError)as error:read_error=repr(error)
 accepted=bool(result and consumer.accepted(result));proof=(result or{}).get('proof',{});record=q.get('consumed',{}).get(c,{});dp=R/'control/qualification_ledger'/(c+'.DONE.json');natural=None;join=None
 if dp.exists():
  done=read(dp);native=R/'DTC/run/results'/done['uuid']/'NATIVE_EXIT.json';natural=done.get('stop_reason')is None and done.get('launcher_wait_returncode')==0;join=record.get('execution_receipt')==done and native.exists()and read(native)==done
 reuse=(result or{}).get('state')==consumer.REUSE
 if reuse:natural=(result or{}).get('reuse_verification',{}).get('natural_done_verified')
 build={k:(proof.get(k)==s[k]if k in proof else None)for k in ['core_commit','framework_commit','binary_sha256','input_digest']}
 options_equal=proof.get('effective_options')==s['expected_options']if 'effective_options'in proof else None
 counts={k:proof.get(k)==s['expected'][v]if k in proof else None for k,v in [('CTA','CTA'),('instructions','instructions'),('kernel_count','kernels')]}
 if reuse:
  verified=(result or{}).get('reuse_verification',{});options_equal=verified.get('complete_effective_options_equal');build['matched_reference_verification']=verified.get('core_framework_binary_equal');counts['matched_reference_input_scope']=verified.get('input_scope_equal')
 e=dict(cohort=c,scientific_role=s.get('scientific_role')or'ORIGINAL_PRIMARY_SLOT',spec_path=str(path),spec_sha256=sha(path),input_digest=s['input_digest'],input_binding_sha256=s['input_binding_sha256'],core_commit=s['core_commit'],framework_commit=s['framework_commit'],binary_sha256=s['binary_sha256'],expected_options_sha256=objsha(s['expected_options']),expected_option_count=len(s['expected_options']),expected_ROI=s['expected'],correctness_validation_only=s.get('correctness_validation_only'),performance_scope=s.get('performance_scope'),RESULT_path=str(rp)if rp.exists()else None,RESULT_sha256=sha(rp)if rp.exists()else None,raw_result_state=(result or{}).get('state','RESULT_UNREADABLE'if read_error else'NO_RESULT'),read_error=read_error,accepted_existing_receipt=accepted,actual_cycles=(result or{}).get('cycles')if accepted else None,uuid=(result or{}).get('uuid')or record.get('uuid'),consumed=c in q.get('consumed',{}),natural_done=natural,natural_DONE_EXIT_authority_join=join,DONE_path=str(dp)if dp.exists()else None,DONE_sha256=sha(dp)if dp.exists()else None,declared_source_role_primary_excluded=s.get('incident_recovery_trial_lineage',s.get('supplemental_trial_lineage',{})).get('primary_statistics_excluded'),validated_union_authorized=s.get('incident_recovery_trial_lineage',s.get('supplemental_trial_lineage',{})).get('validated_union_authorized'),proof_build_input_matches=build,proof_effective_options_equal=options_equal,proof_complete_ROI_matches=counts,archive_receipt_present=bool((result or{}).get('archive')),matched_P0_reference=reuse,evidence_level='EXISTING_STRICT_DONE_ARCHIVE_RECEIPTS_REUSED_NO_NEW_RAW_OR_ARCHIVE_REPLAY')
 if accepted:
  e['proof_status']=proof.get('status');e['archive_status']=(result or{}).get('archive',{}).get('receipt',{}).get('status')
 if c==oldscan:e.update(typed_engineering_negative_state=read(certpath)['state'],typed_certificate_path=str(certpath),typed_certificate_sha256=sha(certpath),original_accepted=False)
 evidence[c]=e;return e
rows=[];programs={}
for p in scope['points']:
 c=p['cohort'];base=measure(c);s=specs[c];digest=p['input_digest'];programs.setdefault(digest,dict(program=p['program'],suite=p['suite'],input_digest=digest,cells=[]))['cells'].append(c)
 ref=mapping.get(c);candidate=None
 if ref:
  cand=measure(ref['cohort']);ns=specs[ref['cohort']];keys=ir['science_projection_keys'];equal={k:s[k]==ns[k]for k in keys};assert all(equal.values()),(c,[k for k,v in equal.items()if not v]);assert base['accepted_existing_receipt']is False
  candidate=dict(**ref,measurement=cand,declared_frozen_science_all_keys_equal=True,declared_science_keys=keys,old_actual_complete_physics_not_claimed=True,measurement_identity_ready=True,strict_natural_archive_ready=bool(cand['accepted_existing_receipt']and cand['natural_done']and cand['natural_DONE_EXIT_authority_join']and cand['proof_effective_options_equal']and cand['archive_receipt_present']),statistical_use_currently_authorized_by_legacy_guard=False)
 row=dict(key=dict(input_digest=digest,program=p['program'],suite=p['suite'],cell=p['cell'],profile=p['profile']),original_cohort=c,original_measurement=base,predeclared_alternate=candidate,proposed_reference_rule='ORIGINAL_ACCEPTED_FIRST_ELSE_EXACT_PREDECLARED_IR1_OR_R2_IF_STRICT_COMPLETE_ELSE_MISSING',derived_reference_not_applied=True)
 rows.append(row)
# Qualified generator checks same-design P0→profile effective vectors without changing files.
bykey={(r['key']['input_digest'],r['key']['cell'],r['key']['profile']):r for r in rows};generator_checks=[]
for r in rows:
 k=r['key'];baseline=specs[bykey[(k['input_digest'],k['cell'],'P0')]['original_cohort']]['expected_options'];flat=lambda opts:{key:' '.join(value)if isinstance(value,list)else value for key,value in opts.items()};text=''.join(key+' '+value+'\n'for key,value in sorted(flat(baseline).items()));_,manifest=gen.generate([text],k['profile']);ok=manifest['effective_options']==flat(specs[r['original_cohort']]['expected_options']);assert ok,r['original_cohort'];generator_checks.append(dict(cohort=r['original_cohort'],same_design_baseline='P0',profile=k['profile'],all_non_target_and_fixed_geometry_clock_preserved=True))
gaps=[r for r in rows if not r['original_measurement']['accepted_existing_receipt']];alternate=[r for r in rows if r['predeclared_alternate']]
coverage=[]
for digest,pg in sorted(programs.items(),key=lambda x:x[1]['program'].lower()):
 pr=[r for r in rows if r['key']['input_digest']==digest];bp=[r['key']['cell']for r in pr if r['key']['profile']=='P0'and not r['original_measurement']['accepted_existing_receipt']]
 coverage.append(dict(program=pg['program'],suite=pg['suite'],input_digest=digest,original_accepted=sum(r['original_measurement']['accepted_existing_receipt']for r in pr),original_cells=len(pr),original_missing_cells=[dict(cell=r['key']['cell'],profile=r['key']['profile'],cohort=r['original_cohort'],state=r['original_measurement']['raw_result_state'],typed_negative=r['original_measurement'].get('typed_engineering_negative_state'),consumed=r['original_measurement']['consumed'],predeclared_alternate=r['predeclared_alternate']['cohort']if r['predeclared_alternate']else None)for r in pr if not r['original_measurement']['accepted_existing_receipt']],P0_missing_cells=bp,predeclared_reference_gap_count=sum(bool(r['predeclared_alternate'])for r in pr)))
summary=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),input_count=len(programs),original_scope_cells=len(rows),original_accepted=sum(r['original_measurement']['accepted_existing_receipt']for r in rows),original_missing=len(gaps),predeclared_alternate_gaps=len(alternate),IR1_gaps=sum(r['predeclared_alternate']['role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL'for r in alternate),R2_gaps=sum(r['predeclared_alternate']['role']=='SUPPLEMENTAL_NEW_PERFORMANCE_TRIAL'for r in alternate),alternate_existing_accepted=sum(r['predeclared_alternate']['measurement']['accepted_existing_receipt']for r in alternate),alternate_strict_natural_archive_ready=sum(r['predeclared_alternate']['strict_natural_archive_ready']for r in alternate),original_fully_covered_programs=sum(x['original_accepted']==10 for x in coverage),original_full35_GM_generated=False,derived_GM_generated=False,source_roles_unchanged=True,new_models_started=0,new_grants=0,production_changes=0)
sources=[scopepath,matrixpath,irpath,r2planpath,certpath,R/'tools/l2_results.py',R/'tools/l2_config_generator.py',R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',R/'control/SCIENCE_AUTHORIZATION.json',A/'coordinator/BROAD_SHARED_CPU_PREREQUISITE_APPROVAL_V1/APPROVAL.json',A/'agents/E/strace_bpf_future_policy_v3/future_policy.py',A/'agents/E/interaction_policy_v3/interaction_policy.py',A/'agents/E/supplemental_scan_m16_v2/supplemental_trial.py']
put(out/'SOURCE_MANIFEST.json',dict(schema='DERIVED35_READONLY_INPUT_SOURCE_MANIFEST_V1',sources=[dict(path=str(p),sha256=sha(p))for p in sources],consumer_sha256=sha(consumer.__file__),qualified_generator_sha256=sha(gen.__file__)))
put(out/'REFERENCE_MAP_350_DRAFT.json',dict(schema='DTC_L2_MLP_DERIVED35_REFERENCE_MAP_DRAFT_V1',status='NOT_APPROVED_NOT_APPLIED',summary=summary,rows=rows))
put(out/'CANDIDATE_REFERENCE_GAPS_12.json',dict(summary=summary,rows=alternate))
put(out/'ORIGINAL_MISSING_CELLS.json',dict(summary=summary,rows=gaps))
put(out/'PROGRAM_COVERAGE_35.json',dict(summary=summary,programs=coverage))
put(out/'GENERATOR_IDENTITY_CHECKS.json',dict(source_sha256=sha(gen.__file__),count=len(generator_checks),checks=generator_checks))
put(out/'SUMMARY.json',summary)
print(json.dumps(dict(directory=str(out),summary=summary,incomplete_programs=[x for x in coverage if x['original_accepted']<10])))
