"""CPU-only exact-stage artifact builder. Never registers/consumes/launches.

No actual invocation is made in this preparation. Incomplete freeze input fails
before creating output files. No UUID is generated: the native one-use consume
owns UUID assignment. CLI is provided for Main after independent freeze only.
"""
from pathlib import Path
import argparse,copy,hashlib,json,re,os

AUTHORITY='18b1ee9d339902e555fc2e04ef51c84f77dfe1b1'
CORE_BASE='9eedb3131937748f0492fa83aad37d3691118d70'
FW='02775fd795cde5aae1480d81cee6eb481d0a08f4'
MATRIX_SHA='11d5bfc7642a6262fde719119603c940ca64eb98de69d2554124f24b2302a3ee'
BASE=Path('/root/data/dtc_controlled_oracle_20261106_v1')
ARCHIVE=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1')
ENUM={'OFF_MATCHED':0,'M_DATAREAD':1,'L2_DATAREAD':2,'L1_DATAREADY':3}
QUAL={'OFF_MATCHED':'vectorAdd','M_DATAREAD':'vectorAdd','L2_DATAREAD':'ATAX','L1_DATAREADY':'MVT'}
OWNER_PID=1498278;OWNER_START=977758783
def rd(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bs(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def jsonsha(v):return hashlib.sha256(bs(v)).hexdigest()
def validsha(v,n=64):return isinstance(v,str) and len(v)==n and all(c in '0123456789abcdef' for c in v)
def pinned(pin):
 assert set(pin)>={'path','sha256'} and validsha(pin['sha256'])
 assert sha(pin['path'])==pin['sha256'],'PIN_DRIFT '+pin['path'];return Path(pin['path'])
def exact_rows(matrix,stage,q):
 assert stage in ('initial8','remaining24') and q and len(set(q))==len(q) and set(q)<=set(ENUM)-{'OFF_MATCHED'}
 rows=[r for r in matrix['rows'] if r['initial_fixed8']==(stage=='initial8') and r['mode'] in ['OFF_MATCHED']+q]
 assert len(rows)==(8 if stage=='initial8' else 24)*(1+len(q))
 assert len({r['plan_id'] for r in rows})==len(rows)
 assert all(r['design']=='DH' for r in rows)
 return rows
def layout_pin(release,stage):return release['launcher_layouts'][stage]
def cohort_for(row,stage):
 # New namespace; the static plan ID is retained separately and not an actual
 # UUID. Stage names cannot select input scope outside the frozen matrix.
 return 'E2-DTCORACLE-'+('I8' if stage=='initial8' else 'R24')+'-'+row['input_digest'][:16]+'-DH-'+row['mode']+'-V1'
def route_block(points,root,stage):
 assert all(re.fullmatch(r'[A-Za-z0-9_-]+',p['cohort']) for p in points)
 assert re.fullmatch(r'/[A-Za-z0-9_./-]+',str(root))
 cases='|'.join(t+':'+p['cohort'] for p in points for t in ('experiment','result'))
 return ('# DTC_ORACLE_'+stage.upper()+'_V1_ROUTE; exact conditional authorized rows only.\n'
  'if [ "$#" -ge 3 ]; then\n case "$1:$3" in\n  '+cases+')\n'
  '   export DTC_CONTROLLED_ORACLE_NATIVE_ENTRY=1\n'
  '   exec /usr/bin/python3 -B '+str(root/'tools/oracle_frontend.py')+' "$@"\n   ;;\n esac\nfi\n').encode()
def execution_identity(spec):
 keys=('plan_id','input_digest','expected_options','core_commit','framework_commit','binary_sha256','runtime_files','configs','native_simulator_argv','original_environment','limits','expected','source_worktrees','host_cpu')
 return {key:spec[key] for key in keys}
def validate_input(release,matrix_path,stage,phase='final'):
 assert phase in ('cpu-draft','final')
 assert release['schema']=='DTC_ORACLE_REGISTRATION_BUILD_INPUT_V1'
 assert release['authority_commit']==AUTHORITY and release['core_base']==CORE_BASE and release['framework_commit']==FW
 assert validsha(release['core_commit'],40) and release['core_commit']!=CORE_BASE
 assert release['immutable_binary'] is True and release['CH_budget']==0
 assert release.get('archive_workers',1)==1,'SINGLE_SHARED_RESTORE_ARCHIVE_WORKER_REQUIRED'
 assert sha(matrix_path)==MATRIX_SHA and release['frozen_matrix_sha256']==MATRIX_SHA
 if phase=='final':assert release['Gate0_CPU_source_strict_independent_review']=='PASS'
 else:
  assert release['Gate0_CPU_source_strict_independent_review'] in ('PASS','PENDING_FINAL_NATIVE_CPU_LAYOUT')
  assert release['source_lifecycle_independent_review']=='PASS' and release['CPU_lifecycle_qualification']=='PASS'
 assert release['new_option']=='-gpgpu_dtc_oracle_mode'
 assert release['expected_options_count']==271
 if stage=='remaining24' and phase=='final':
  gates=release['Gate2_mode_releases'];assert set(gates)==set(release['qualified_modes'])
  assert any(v['status']=='PASS' for v in gates.values()),'ANY_REAL_MODE_GATE2_PASS_REQUIRED'
  assert all(v['status'] in ('PASS','WAIT','HOLD') for v in gates.values())
 q=release['qualified_modes'];rows=exact_rows(rd(matrix_path),stage,q)
 assert release['owner_pid']==OWNER_PID and release['owner_start_ticks']==OWNER_START
 for name in ('source_freeze','independent_CPU_review_manifest','launcher_native_cwd_qualification','result_engine_pin','resource_policy','build_profile','runtime_guard','runtime_guard_policy','observer_overlay','peer_disk_adapter','actual_qualification_reviewer','Gate0_release','project_authority'):
  pinned(release[name])
 if phase=='final':
  layout=rd(pinned(layout_pin(release,stage)))
  assert layout['status']=='PASS' and layout['request']==release['request_ids'][stage],'STAGE_SPECIFIC_LAYOUT_REQUEST_REQUIRED'
  assert layout['scientific_models_started']==0 and layout['final_binary_layout_qualified'] is True,'NEW_BINARY_CPU_LAYOUT_REQUIRED'
  assert layout['files']
  for pin in layout['files']:pinned(pin)
 assert re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',release['actual_qualification_reviewer']['function'])
 if stage=='remaining24' and phase=='final':pinned(release['Gate2_release'])
 for name in ('oracle_native.py','oracle_ops.py','oracle_resources.py','oracle_frontend.py','oracle_strict.py','oracle_parent_addon.py','oracle_outbox.py','oracle_pendingcall.py','oracle_plan_builder.py'):
  pinned(release['runtime_tools'][name])
 for name,pin in release['runtime_tools'].items():
  assert re.fullmatch(r'oracle_[A-Za-z0-9_]+\.py',name);pinned(pin)
 binary=pinned(release['binary']);pinned(release['libcudart'])
 assert release['binary_sha256']==release['binary']['sha256'] and release['libcudart_sha256']==release['libcudart']['sha256']
 if release.get('mock') is not True:
  for pin in (release['binary'],release['libcudart']):
   actual=Path(pin['path']).resolve();assert BASE/'shared' in actual.parents,'NEW_RUNTIME_BINARY_AND_CUDART_MUST_BE_NATIVE_SHARED'
   assert os.stat(actual).st_dev==2128,'NEW_RUNTIME_MUST_BE_NATIVE_DEVICE2128'
 build_profile=rd(release['build_profile']['path'])
 assert build_profile['core_commit']==release['core_commit'] and build_profile['framework_commit']==FW
 assert build_profile['libcudart_sha256']==release['libcudart_sha256']
 assert build_profile['source_worktrees']==release['source_worktrees']
 assert release['source_worktrees']=={'core':str(ARCHIVE/'source/integration-core'),'framework':str(ARCHIVE/'source/framework-build')},'NEW_SOURCE_WORKTREES_REQUIRED'
 project=rd(release['project_authority']['path'])
 assert project['authority']==AUTHORITY and project['core_base']==CORE_BASE and project['framework']==FW
 assert isinstance(release['protected_cpu_ids'],list) and len(set(release['protected_cpu_ids']))==len(release['protected_cpu_ids'])
 assert not(set(release['new_dispatcher_cpu_allowance'])&set(release['protected_cpu_ids'])),'PROTECTED_CPU_OVERLAP'
 for r in rows:
  base=rd(pinned(release['base_specs'][r['input_digest']]))
  assert base['input_digest']==r['input_digest'] and base['cell']=='DH' and base['downstream_profile']=='P0'
  assert base['core_commit']==CORE_BASE and base['framework_commit']==FW
  assert base['expected']==r['capture_identity']['expected']
  assert len(base['expected_options'])==270 and '-gpgpu_dtc_oracle_mode' not in base['expected_options']
  assert base['expected_options']['-gpgpu_perfect_mem']==['0'] and base['expected_options']['-l2_ideal']==['0']
  assert base['expected_options']['-gpgpu_dtc_l1_physical_lines']==['640'] and base['expected_options']['-gpgpu_dtc_l1_oo_pib_entries']==['128']
  assert base['expected_options']['-gpgpu_dtc_l1_logical_sets']==['64'] and base['expected_options']['-gpgpu_dtc_l1_logical_ways']==['8']
  assert len(base['configs'])==4
  configs=release['configs_by_mode'][r['mode']]
  assert len(configs)==5,'FOUR_ORIGINAL_PLUS_ONE_ORACLE_CONFIG_REQUIRED'
  assert [c['sha256'] for c in configs[:4]]==[c['sha256'] for c in base['configs']]
  for cfg in configs:pinned(cfg)
  assert pinned(configs[4]).read_text().strip()=='-gpgpu_dtc_oracle_mode '+str(ENUM[r['mode']])
  assert r['input_digest'] in release['resource_fields_by_input']
  pinned({'path':base['input_binding_path'],'sha256':base['input_binding_sha256']})
 assert release['request_ids']['initial8']!=release['request_ids']['remaining24']
 for req in release['request_ids'].values():assert re.fullmatch(r'DTC_ORACLE_[A-Z0-9_]+',req)
 return rows
def build(release,matrix_path,stage,target_root=None,phase='final',finalize_draft=False):
 rows=validate_input(release,matrix_path,stage,phase)
 R=Path(target_root) if target_root is not None else BASE/stage
 assert release.get('mock') is True or R.resolve()==(BASE/stage).resolve(),'EXACT_NATIVE_ROOT_REQUIRED'
 if finalize_draft:
  assert phase=='final' and R.exists(),'FINALIZE_ONLY_EXISTING_CPU_DRAFT'
  assert not (R/'control/PARENT_ADDON_ACK.json').exists() and not (R/'control/REGISTRY_REQUEST_CANDIDATE.json').exists(),'NO_SCIENTIFIC_FROZEN_STAGE_OVERWRITE'
  draft=rd(R/'control/CPU_DRAFT_BUILD.json')
  assert draft['schema']=='DTC_ORACLE_CPU_DRAFT_BUILD_V1' and draft['stage']==stage
  assert rd(R/'control/EXECUTION_PLAN.json')['preparation_phase']=='CPU_DRAFT_NO_REGISTRATION'
  for item in draft['files']:assert sha(R/item['path'])==item['sha256'],'CPU_DRAFT_BYTES_DRIFT '+item['path']
 else:assert not R.exists(),'NEW_EMPTY_STAGE_ROOT_REQUIRED_NO_OVERWRITE'
 req=release['request_ids'][stage];n=len(rows);q=release['qualified_modes']
 files={};points=[];specpins={};inputs={};sourcepins=[]
 def add(rel,v):
  b=v if isinstance(v,bytes) else bs(v);files[rel]=b;return {'path':str(R/rel),'sha256':hashlib.sha256(b).hexdigest()}
 # Copy immutable reviewed source bytes into the new request-local tools tree;
 # importing a source module is never part of this builder.
 for name,pin in release['runtime_tools'].items():sourcepins.append(add('tools/'+name,pinned(pin).read_bytes()))
 # Small immutable gate/identity records read by lock-held checks reside on
 # native storage. Their exact source bytes/SHA remain unchanged by copying.
 localrefs={}
 for name in ('source_freeze','independent_CPU_review_manifest','launcher_native_cwd_qualification','result_engine_pin','resource_policy','Gate0_release'):
  localrefs[name]=add('control/'+name.upper()+'.fixed.json',pinned(release[name]).read_bytes());sourcepins.append(localrefs[name])
 # Qualified native/outbox/layout consumers use these exact standard names.
 # Keep fixed-source copies above and add byte-identical aliases explicitly in
 # the draft manifest so no pre-layout manual file repair is required.
 for name,alias in (('result_engine_pin','RESULT_ENGINE_PIN.json'),('resource_policy','RESOURCE_POLICY.json')):
  localrefs[name]=add('control/'+alias,pinned(release[name]).read_bytes());sourcepins.append(localrefs[name])
 if phase=='final':
  localrefs['launcher_layout']=add('control/LAUNCHER_LAYOUT.fixed.json',pinned(layout_pin(release,stage)).read_bytes());sourcepins.append(localrefs['launcher_layout'])
 else:localrefs['launcher_layout']={'path':str(R/'control/LAUNCHER_LAYOUT.fixed.json'),'sha256':None,'status':'PENDING_FINAL_NATIVE_CPU_LAYOUT'}
 authoritypin=add('control/PROJECT_AUTHORITY.fixed.json',pinned(release['project_authority']).read_bytes());sourcepins.append(authoritypin)
 if stage=='remaining24' and phase=='final':
  localrefs['Gate2_release']=add('control/GATE2_RELEASE.fixed.json',pinned(release['Gate2_release']).read_bytes());sourcepins.append(localrefs['Gate2_release'])
 reviewer=add('tools/oracle_actual_qualification_reviewer.py',pinned(release['actual_qualification_reviewer']).read_bytes())
 sourcepins.append(reviewer);reviewer['function']=release['actual_qualification_reviewer']['function']
 for r in rows:
  source=release['base_specs'][r['input_digest']];base=rd(pinned(source));s=copy.deepcopy(base);cohort=cohort_for(r,stage)
  # Remove old repair/recovery identity decorations. Preserve their historical
  # source bytes outside the new scientific identity via original_spec_source.
  for key in list(s):
   if 'recovery' in key or key in ('uuid','scientific_qualification_uuid','original_plan_id','new_base_reuse','correctness_validation_only'):s.pop(key)
  configs=copy.deepcopy(release['configs_by_mode'][r['mode']]);options=copy.deepcopy(base['expected_options']);options[release['new_option']]=[str(ENUM[r['mode']])]
  resource=release['resource_fields_by_input'][r['input_digest']]
  s.update({'request':req,'cohort':cohort,'profile':r['mode'],'oracle_mode':r['mode'],'oracle_mode_enum':ENUM[r['mode']],'oracle_static_plan_id':r['plan_id'],'plan_id':r['plan_id'],
   'original_spec_source':source,'core_base':CORE_BASE,'core_commit':release['core_commit'],'framework_commit':FW,'binary_sha256':release['binary_sha256'],'source_worktrees':copy.deepcopy(release['source_worktrees']),
   'historical_DH_P0_spec_path':source['path'],'historical_DH_P0_spec_sha256':source['sha256'],
   'configs':configs,'historical_options270_sha256':jsonsha(base['expected_options']),'expected_options':options,'expected_options_count':271,
   'runtime_files':copy.deepcopy(release['runtime_files']),'execution_mnt_namespace':release['execution_mnt_namespace'],'host_cpu':None,
   'host_launcher_layout':localrefs['launcher_layout'],'initial_actual_qualification':r['initial_fixed8'] and r['program']==QUAL[r['mode']],
   'input_digest':r['input_digest'],'frozen_candidate_matrix_sha256':MATRIX_SHA,'downstream_profile':'P0','performance_scope':'CONTROLLED_DH_ORACLE_COUNTERFACTUAL_NOT_MATHEMATICAL_BOUND',
   'estimated_peak_model_RAM_bytes':resource['estimated_peak_model_RAM_bytes'],'limits':resource['limits'],'source_freeze':localrefs['source_freeze'],'result_engine_pin':localrefs['result_engine_pin']})
  if release.get('mock') is True:s['mock_not_scientific']=True
  s['native_simulator_argv']=[release['binary']['path'],'-trace',r['capture_identity']['trace_entry']]+[arg for c in configs for arg in ('-config',c['path'])]
  assert len(s['expected_options'])==271 and s['original_environment']==base['original_environment']
  assert all(s['expected_options'][k]==v for k,v in base['expected_options'].items())
  pin=add('control/specs/'+cohort+'.json',s);sourcepins.append(pin);specpins[cohort]=pin['sha256'];add('control/'+cohort+'_SPEC.json',s)
  point={k:r[k] for k in ('plan_id','program','suite','input_digest','mode','initial_fixed8')};point.update({'cohort':cohort,'profile':r['mode'],'oracle_mode_enum':ENUM[r['mode']],'request':req,'stage':stage,'actual_qualification_row':s['initial_actual_qualification']});points.append(point)
  item=inputs.setdefault(r['input_digest'],{'program':r['program'],'suite':r['suite'],'specs':[]});item['specs'].append(cohort)
 points.sort(key=lambda p:(not p['actual_qualification_row'],p['oracle_mode_enum']!=0,p['oracle_mode_enum'],p['program']))
 matrixpin=add('control/MATRIX.fixed.json',{'schema':'DTC_ORACLE_STAGE_MATRIX_V1','authority_commit':AUTHORITY,'stage':stage,'qualified_modes':q,'points':points});sourcepins.append(matrixpin)
 approval={'schema':'DTC_ORACLE_ONE_USE_EXACT_STAGE_APPROVAL_V1','authority_commit':AUTHORITY,'stage':stage,'request':req,'input_digests':sorted(inputs),'qualified_modes':q,'exact_budget':n,'cohorts':list(specpins),'CH_budget':0,'new_UUIDs_only_at_native_one_use_consume':True,'no_hidden_canary':True}
 approvalpin=add('control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',approval);sourcepins.append(approvalpin)
 add('control/SCIENCE_AUTHORIZATION'+('.DRAFT' if phase=='cpu-draft' else '')+'.json',{'schema':'DTC_ORACLE_SCIENCE_AUTHORIZATION_V1','explicit_user_approval':True,'ready_for_registration':phase=='final','owner_bindings_ratified':phase=='final','target_resource_policy_ratified':phase=='final','authority_commit':AUTHORITY,'stage':stage,'approval_request_sha256':approvalpin['sha256'],'budgets':dict.fromkeys(specpins,1)})
 routepin=add('control/NATIVE_ROUTE_BLOCK.sh',route_block(points,R,stage));sourcepins.append(routepin)
 buildprofilepin=add('control/BUILD_PROFILE.json',pinned(release['build_profile']).read_bytes());sourcepins.append(buildprofilepin)
 for name in ('source_freeze','independent_CPU_review_manifest','launcher_native_cwd_qualification','result_engine_pin','resource_policy','runtime_guard','runtime_guard_policy','observer_overlay','peer_disk_adapter','project_authority'):
  sourcepins.append(release[name])
 sourcepins+=list(release['base_specs'][key] for key in sorted(inputs))
 sourcepins+=[release['binary'],release['libcudart']]
 for mode in ['OFF_MATCHED']+q:sourcepins+=release['configs_by_mode'][mode]
 parent=release['parent_controller'];pinned(parent)
 plan={'schema':'DTC_CONTROLLED_ORACLE_EXECUTION_PLAN_V1','authority_commit':AUTHORITY,'approved_contract_commit':AUTHORITY,'execution_root':str(R),'stage':stage,'request':req,'qualified_modes':q,'expected_new_starts':n,
  'initial_finite_budget':n,'authorized_cohorts':list(specpins),'exact_input_count':len(inputs),'parent_pid':OWNER_PID,'parent_start_ticks':OWNER_START,
  'parent_controller_path':parent['path'],'parent_controller_sha256':parent['sha256'],'source_pins':sourcepins,'independent_CPU_review_manifest':localrefs['independent_CPU_review_manifest'],
  'source_freeze':localrefs['source_freeze'],'launcher_layout':localrefs['launcher_layout'],'launcher_native_cwd_qualification':localrefs['launcher_native_cwd_qualification'],
  'result_engine_pin':localrefs['result_engine_pin'],'resource_policy':localrefs['resource_policy'],'new_dispatcher_cpu_allowance':release['new_dispatcher_cpu_allowance'],
  'protected_cpu_ids':release['protected_cpu_ids'],'project_authority':authoritypin,
  'archive_workers':1,'dynamic_native_reservation_policy':'PER_STAGE_ACTUAL_CLAIMS_SINGLE_RESTORE_PLUS_256M_METADATA_V1',
  'shared_pool_roots':release.get('shared_pool_roots',[str(BASE/'initial8'),str(BASE/'remaining24')]),'shared_pool_dispatch_reservations_path':release.get('shared_pool_dispatch_reservations_path',str(BASE/'control/SHARED_POOL_DISPATCH_RESERVATIONS.json')),
  'mode_gate2_reviews':release.get('mode_gate2_reviews',{mode:str(BASE/'control/GATE2_MODE_REVIEWS'/(mode+'.json')) for mode in q}),'extension_automation':release.get('extension_automation'),
  'build_profile_sha256':buildprofilepin['sha256'],'runtime_guard':release['runtime_guard'],'runtime_guard_policy':release['runtime_guard_policy'],'observer_overlay':release['observer_overlay'],'peer_disk_adapter':release['peer_disk_adapter'],
  'source_candidate_matrix_sha256':MATRIX_SHA,'source_build_release':release['source_build_release'],'archive_target_root':release['archive_target_root']+'/'+stage,
  'archive_tier':'GENUINE164_SOURCE_KEEP_FULL_NATIVE_RESTORE','source_tier':'NATIVE_BOUNDED_STREAMING_GZIP_SOURCE_KEEP','no_extra_canary_or_baseline_reruns':True,
  'old_request_or_UUID_reuse':False,'model_automatic_retries':0,'CH_budget':0,'paper':'ENGLISH_LATEX_v0.23_FROZEN',
  'preparation_phase':'CPU_DRAFT_NO_REGISTRATION' if phase=='cpu-draft' else 'SCIENCE_FINAL_FROZEN','gate0_release':localrefs['Gate0_release'],'gate2_release':localrefs.get('Gate2_release'),'actual_qualification_reviewer':reviewer,'initial_qualifiers':{m:next((p['cohort'] for p in points if p['mode']==m and p['actual_qualification_row']),None) for m in ['OFF_MATCHED']+q}}
 if release.get('mock') is True:plan['mock']=True
 planpin=add('control/EXECUTION_PLAN.json',plan)
 candidate={'schema':'DTC_CONTROLLED_ORACLE_REGISTERED_REQUEST_V1','request':req,'authority_commit':AUTHORITY,'approved_contract_commit':AUTHORITY,'stage':stage,'qualified_modes':q,'budget':n,'remaining':n,'consumed':{},'sealed':{},'admission_holds':{},'admitted_specs':specpins,'admitted_inputs':inputs,'state':'ARMED','model_automatic_retries':0,'new_registration_only':True,'old_request_budget_reused':False,
  'owner_pid':OWNER_PID,'owner_start_ticks':OWNER_START,'controller_path':str(R/'tools/oracle_ops.py'),'controller_sha256':sha(release['runtime_tools']['oracle_ops.py']['path']),
  'engine_sha256':sha(release['runtime_tools']['oracle_native.py']['path']),'strict_sha256':sha(release['runtime_tools']['oracle_strict.py']['path']),'execution_plan_sha256':planpin['sha256'],'spec_request_sha256':approvalpin['sha256'],
  'outbox_sha256':sha(release['runtime_tools']['oracle_outbox.py']['path']),
  'archive_target_root':plan['archive_target_root'],'reserved_write_bytes':release.get('initial_reserved_write_bytes_by_stage',{}).get(stage,release['reserved_write_bytes']),'maximum_source_plus_restore_lifetime_bytes':release['maximum_source_plus_restore_lifetime_bytes'],'performance_scope':plan['paper']+';CONTROLLED_ORACLE_COUNTERFACTUAL','all_other_candidate_grants':0}
 if release.get('mock') is True:candidate['mock']=True
 candidate['ready_for_registration']=phase=='final'
 add('control/REGISTRY_REQUEST_CANDIDATE'+('.DRAFT' if phase=='cpu-draft' else '')+'.json',candidate)
 if phase=='cpu-draft':
  add('control/CPU_DRAFT_BUILD.json',{'schema':'DTC_ORACLE_CPU_DRAFT_BUILD_V1','stage':stage,'request':req,'qualified_modes':q,'models_started':0,'registered':False,'files':[{'path':name,'sha256':hashlib.sha256(data).hexdigest()} for name,data in sorted(files.items())]})
 if finalize_draft:
  oldspecs={p.stem:rd(p) for p in (R/'control/specs').glob('*.json')}
  assert set(oldspecs)==set(specpins),'CPU_DRAFT_POPULATION_OR_Q_CHANGED'
  for cohort,old in oldspecs.items():
   new=json.loads(files['control/specs/'+cohort+'.json'])
   assert execution_identity(old)==execution_identity(new),'CPU_DRAFT_EXECUTION_IDENTITY_CHANGED '+cohort
  archive=Path(release['cpu_draft_archive_root'])/stage/sha(R/'control/CPU_DRAFT_BUILD.json')
  assert release.get('mock') is True or ARCHIVE in archive.parents,'CPU_DRAFT_ARCHIVE_MUST_STAY_IN_THIS_GOAL'
  archive.mkdir(parents=True,exist_ok=False)
  for item in draft['files']+[{'path':'control/CPU_DRAFT_BUILD.json'}]:
   dst=archive/item['path'];dst.parent.mkdir(parents=True,exist_ok=True)
   with dst.open('xb') as h:h.write((R/item['path']).read_bytes())
  add('control/CPU_DRAFT_FINALIZATION.json',{'schema':'DTC_ORACLE_CPU_DRAFT_FINALIZATION_V1','draft_archive_root':str(archive),'draft_manifest_sha256':sha(R/'control/CPU_DRAFT_BUILD.json'),'execution_identity_preserved':True,'model_starts':0,'registrations':0,'source_binary_input_population_unchanged':True})
 # Only now create outputs, after complete in-memory validation. No authority
 # reader/writer, shell/model command, UUID generator, lease or route mutation.
 if not finalize_draft:R.mkdir(parents=True,exist_ok=False)
 for rel,b in files.items():
  p=R/rel;p.parent.mkdir(parents=True,exist_ok=True)
  if finalize_draft:
   tmp=p.with_name('.'+p.name+'.CPU_DRAFT_FINALIZING')
   with tmp.open('xb') as h:h.write(b)
   os.replace(tmp,p)
  else:
   with p.open('xb') as h:h.write(b)
 return {'root':str(R),'stage':stage,'phase':phase,'finalized_cpu_draft':finalize_draft,'exact_budget':n,'rows':len(points),'registered':False,'models_started':0,'UUIDs_generated':0,'files':len(files)}
def qualify_final_stage_artifacts(stage_root):
 """CPU-only exact generated-artifact qualification for unattended attachment.

 Source/lifecycle/independent review remains the frozen external Gate0. This
 function actually checks final bytes and gates and writes its own truthful
 CPU result; it never invents a model result or a scientific qualification.
 """
 R=Path(stage_root).resolve();assert R in (BASE/'initial8',BASE/'remaining24')
 plan=rd(R/'control/EXECUTION_PLAN.json');candidate=rd(R/'control/REGISTRY_REQUEST_CANDIDATE.json')
 assert plan['preparation_phase']=='SCIENCE_FINAL_FROZEN' and not plan.get('mock',False)
 assert candidate['ready_for_registration'] is True and not candidate.get('mock',False)
 q=plan['qualified_modes'];n=(8 if plan['stage']=='initial8' else 24)*(1+len(q))
 assert candidate['budget']==candidate['remaining']==plan['expected_new_starts']==n and candidate['consumed']=={}
 for pin in plan['source_pins']:pinned(pin)
 for cohort,h in candidate['admitted_specs'].items():
  p=R/'control/specs'/(cohort+'.json');assert sha(p)==h==sha(R/'control'/(cohort+'_SPEC.json'))
  s=rd(p);assert s['request']==plan['request'] and s['plan_id']==s['oracle_static_plan_id']
  old=rd(pinned({'path':s['historical_DH_P0_spec_path'],'sha256':s['historical_DH_P0_spec_sha256']}))
  expected=dict(old['expected_options']);expected['-gpgpu_dtc_oracle_mode']=[str(s['oracle_mode_enum'])]
  assert len(expected)==271 and expected==s['expected_options']
  assert s['source_worktrees']==rd(R/'control/BUILD_PROFILE.json')['source_worktrees']
 layout=rd(pinned(plan['launcher_layout']));assert layout['request']==plan['request'] and layout['status']=='PASS'
 assert layout['scientific_models_started']==0 and layout['final_binary_layout_qualified'] is True
 for pin in layout['files']:pinned(pin)
 # Import request-local resources only to check the reviewed frozen release;
 # verify_frozen_release does no science registration or model execution.
 import types
 res=types.ModuleType('oracle_final_stage_CPU_resources');res.__file__=str(R/'tools/oracle_resources.py')
 exec(compile(Path(res.__file__).read_bytes(),res.__file__,'exec'),res.__dict__)
 evidence=res.verify_frozen_release(plan,candidate)
 result={'schema':'DTC_ORACLE_FINAL_GENERATED_ARTIFACT_CPU_QUALIFICATION_V1','status':'PASS','execution_plan_sha256':sha(R/'control/EXECUTION_PLAN.json'),'registry_candidate_sha256':sha(R/'control/REGISTRY_REQUEST_CANDIDATE.json'),'exact_specs':n,'model_starts':0,'science_registrations':0,'runtime_release_evidence':evidence,'qualifier_source_sha256':sha(__file__)}
 p=R/'control/CPU_QUALIFICATION.json';assert not p.exists(),'CPU_QUALIFICATION_ALREADY_EXISTS_NO_OVERWRITE'
 with p.open('xb') as h:h.write(bs(result));h.flush();os.fsync(h.fileno())
 return result
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--release',required=True);ap.add_argument('--matrix',required=True);ap.add_argument('--stage',choices=['initial8','remaining24'],required=True);ap.add_argument('--phase',choices=['cpu-draft','final'],default='final');ap.add_argument('--finalize-draft',action='store_true')
 a=ap.parse_args();r=rd(a.release);assert r.get('mock') is not True,'CLI_REFUSES_MOCK_RELEASE';print(json.dumps(build(r,a.matrix,a.stage,phase=a.phase,finalize_draft=a.finalize_draft)))
if __name__=='__main__':main()
