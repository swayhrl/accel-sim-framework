"""Independent per-profile E qualification; reuse applicable finite native evidence."""
from pathlib import Path
import sys,json,time,copy,subprocess
P=Path(__file__).resolve().parent;ROOT=P.parents[3];PACKS=P.parent
sys.path.insert(0,str(ROOT/'util/ep_l2/mechanism_e'))
import coordinator as c,runner
from headroom_config import options
legacy=runner.legacy
A=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-a-core-v1')
AP=A/'docs/ep_l2/review_packs/MS20261020_A2_FORMAL_WAD_PRODUCER_RELEASE_r1'
AV=A/'docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/a/full_system_v2'
BASE=PACKS/'MS20261020_E2_MAIN61_TERMINAL_COMPAT_r1'
CONV=PACKS/'MS20261020_E2_MAIN61_CONV_QUALIFICATION_r1'
PROFILES={'W_ONLY':(1,0,0,0),'F_MINUS_V':(1,0,1,1),'F_MINUS_R':(1,1,0,0),'S_COPY_FREE':(0,0,0,0),'WV_M':(1,1,0,1),'WV_T':(1,1,1,0)}
ALIASES={'WV_M':'WV_M_ONLY','WV_T':'WV_T_ONLY'}
def read(p):return json.loads(Path(p).read_text())
def ref(p):return dict(path=str(Path(p).resolve()),sha256=c.digest(p))
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def main():
 coord=c.Coordinator();s=coord.snapshot();assert s['controller']['state']=='STOPPED' and s['actual_starts']==20
 source=s['final_source_identity'];a=read(AP/'RELEASE.json');manifest=read(AP/'SUPPORTED_PROFILES.json');assert a['source_identity']==manifest['source_identity']==source
 assert c.digest(AP/'SUPPORTED_PROFILES.json')==a['supported_profiles_manifest']['sha256']
 for f in ['SUPPORTED_PROFILES.json','RELEASE.json']:
  assert subprocess.check_output(['git','-C',str(A),'show','73d1951bdc88df8562da7614c0ad0275fd6b1230:'+str((AP/f).relative_to(A))])==(AP/f).read_bytes()
 assert c.digest(a['binary_path'])==source['binary_sha256'] and c.digest(a['production_archive']['path'])==a['production_archive']['sha256']
 core=Path(a['production_source_path']);aggregate=read(AV/'COMMON_NATIVE64_AND_REQUIRED_R14_FINAL_AGGREGATE_r1.json')
 unchanged={}
 for rel in ['src/gpgpu-sim/ep-l2-ft-cache.inc','src/gpgpu-sim/ep-l2-ro-transactions.h','src/gpgpu-sim/ep-l2-tvd-directory.h','src/gpgpu-sim/l2cache.cc']:
  old=git(core,'rev-parse',aggregate['runtime_producer_core']+':'+rel);new=git(core,'rev-parse',source['core_source_commit']+':'+rel);assert old==new,rel
  unchanged[rel]=dict(prior_producer=aggregate['runtime_producer_core'],old_blob=old,current_blob=new)
 qbase=read(BASE/'convolutionSeparable_QUALIFICATION.json');assert qbase['source_identity']==source
 cases={}
 for g in qbase['gates'].values():
  assert c.digest(g['evidence_path'])==g['evidence_sha256'];record=read(g['evidence_path'])
  for group in ['retained_unchanged_native_assertions','current_affected_native']:
   for e in record.get(group,[]):cases[e['case']]=e
 for e in aggregate['tests']:
  if e['case'] in ['S_COPY_FREE_local','S_COPY_FREE_ROP7','ro_native_dram_warm_R_without_V']:
   assert e['expectation_verified'] and e['actual_exit']==0 and c.digest(e['receipt'])==e['receipt_SHA256']
   assert c.digest(e['raw_log'])==e['raw_SHA256'];assert e['required_terminal'] in Path(e['raw_log']).read_text(errors='replace')
   cases[e['case']]=e
 needed={'W_ONLY':['U_observer0','new_legacy_credit_rollback','new_A1_UID_Bank_mode2'],
 'F_MINUS_V':['ro_native_dram_warm_R_without_V','new_T1M1','new_legacy_credit_rollback'],
 'F_MINUS_R':['WV_observer','full_victim_cycle','new_dirty_WAD128_drain','new_TVD_credit_rollback'],
 'S_COPY_FREE':['S_COPY_FREE_local','S_COPY_FREE_ROP7','new_A1_UID_Bank_mode1'],
 'WV_T':['combined_factor_tag_T1_M0','combined_factor_line_T1_M0','new_T1M0','new_combined_shared_pool'],
 'WV_M':['combined_factor_tag_T0_M1','combined_factor_line_T0_M1','new_T0M1','new_combined_shared_pool']}
 reasons={'W_ONLY':'Separate removal of copy/static partition from V/RO under exact finite unified backing.',
 'F_MINUS_V':'RO kept ON and complete certificate; V lookup/retention disabled. Compare exact accepted F without changing R.',
 'F_MINUS_R':'V kept ON with T/M both OFF. Supplies WV corner and separates RO query/bypass from retention.',
 'S_COPY_FREE':'Only COPY_READ/COPY_WRITE physical services exempt; finite1168,16staticWB,ROP and all noncopy physical services retained. Diagnostic, never hardware P1 throughput.',
 'WV_M':'M-only on fixed WV background; with F and F_MINUS_R distinguishes M from T and query cost.',
 'WV_T':'T-only on fixed WV background; completes2x2 T/M corners, retaining possible zero-detach negative evidence.'}
 rows=[];matrix=s['full_system_matrix']['matrix'];entries={}
 for profile,switch in PROFILES.items():
  alias=ALIASES.get(profile,profile);assert tuple(manifest['source_supported'][alias]['research_switches'][k] for k in ['W','V','T','M'])==switch
  cell=next(e for e in matrix['conditions'] if e['condition_id']=='V2_convolutionSeparable_'+profile)
  assert tuple(cell[k] for k in ['W','V','T','M'])==switch
  wp=P/profile;wp.mkdir(exist_ok=True);files=list((AV/'PREPARED_APPLICATION_CONFIGS_r1').glob('*_convolutionSeparable_'+alias+'.config'));assert len(files)==1
  cfg=wp/'profile.config';cfg.write_text(files[0].read_text().replace('# DRAFT ONLY: not native-qualified and not application launch authority.','# E exact-profile binding; dispatch only after its independent qualification and original live gates.'))
  template=read(CONV/('convolutionSeparable_'+('F' if switch[0] else 'S')+'_SPEC.json'))
  sem=copy.deepcopy(qbase['supported_profiles']['F' if switch[0] else 'S']);sem['research_switches']=dict(zip(['W','V','T','M'],switch))
  feature=sem['feature_vector'];feature.update(unified_wb=bool(switch[0]),tvd=bool(switch[1]),ro_tag_detach=bool(switch[2]),ro_line_mshr_bypass=bool(switch[3]))
  sem['ideal_vector']['copy_free']=profile=='S_COPY_FREE';sem['labels'].update(diagnostic=profile=='S_COPY_FREE',subset=profile,oracle=bool(switch[2] or switch[3]),readonly_scope='TRACE_MODEL_CLOSED_WORLD' if switch[2] or switch[3] else 'OFF',victim_scope='CLEAN_DIRTY_PENDING_INFLIGHT' if switch[1] else 'OFF')
  template['configs'][-1]['path']=str(cfg);sem['effective_options']=options([x['path'] for x in template['configs']])
  previous=qbase['supported_profiles']['F' if switch[0] else 'S']['effective_options'];diff={k:[previous.get(k),v] for k,v in sem['effective_options'].items() if previous.get(k)!=v}
  assert set(diff)<=set(sem['comparison_variable_options']),diff
  effective=sem['effective_options'];assert int(effective['-gpgpu_ep_l2_ft_mode'])==(2 if switch[0] else 1)
  for key,value in {'-gpgpu_ep_l2_tvd_clean':switch[1],'-gpgpu_ep_l2_tvd_dirty':switch[1],'-gpgpu_ep_l2_ro_tag_detach':switch[2],'-gpgpu_ep_l2_ro_line_mshr_bypass':switch[3],'-gpgpu_ep_l2_diag_copy_free':int(profile=='S_COPY_FREE')}.items():assert int(effective[key])==value
  selected=[]
  for name in needed[profile]:
   e=cases[name];exitcode=e.get('actual_exit',e.get('exit_code'));assert exitcode==0
   path=e['raw_log'];sha=e.get('raw_log_sha256',e.get('raw_SHA256'));assert sha and c.digest(path)==sha
   if e.get('terminal_checks'):assert all(e['terminal_checks'].values())
   selected.append(e)
  review=dict(schema='E2_EXACT_CONTROL_PROFILE_INDEPENDENT_QUALIFICATION_V1',gate='profile_specific_mode_and_diagnostic_semantics',status='PASS',production_driven=True,reviewed_by='E2',at_unix=time.time(),profile=profile,source_identity=source,producer_supported_profile=ref(AP/'SUPPORTED_PROFILES.json'),source_supported_is_not_E_qualification=True,condition_id=cell['condition_id'],research_switches=sem['research_switches'],ideal_vector=sem['ideal_vector'],labels=sem['labels'],effective_options=effective,config=ref(cfg),nonresearch_changes=[],changed_research_options=diff,scientific_question=reasons[profile],retained_independent_profile_cases=selected,unchanged_production_blobs=unchanged,current_delta_review=ref(CONV/'DELTA_APPLICABILITY_REVIEW.json'),applicability='Distinct exact mode/diagnostic review. Unchanged FT/payload/RO/TVD headers retain original finite assertions. Core27 RO origin repair has fresh E detailed T/M modes; d010 only reorders own-pending WAD guard, exercised by retained E17 native retry/rollback/bank cases. No S/F application result is used as control-specific native correctness evidence.',new_native_invocations=0,new_builds=0,extra_joint_B_C_scenario_qualified=False,numeric_SASS_output_validated=False)
  rp=wp/'PROFILE_QUALIFICATION_REVIEW.json';c.write_json(rp,review)
  q=copy.deepcopy(qbase);q.update(schema='E2_ONE_EXACT_CONV_CONTROL_QUALIFICATION_V1',qualified_unix=time.time(),supported_profiles={profile:sem},scope_note=profile+' only: '+reasons[profile]+' Independently reviewed retained mode-specific production evidence plus current WAD delta; original18 shared obligations retained. Fixed complete Conv input and main61 only. No extra failed joint fixture promotion or numeric SASS output claim.',profile_qualification_review=ref(rp))
  q['affected_additional_gates']=list(q['affected_additional_gates'])+['profile_specific_mode_and_diagnostic_semantics'];q['gates']['profile_specific_mode_and_diagnostic_semantics']=dict(status='PASS',production_driven=True,evidence_path=str(rp),evidence_sha256=c.digest(rp))
  qp=wp/'QUALIFICATION.json';c.write_json(qp,q);qid=coord.register_qualification(qp)
  spec=template;spec.update(profile=profile,profile_semantics=sem,labels=sem['labels'],qualification_id=qid,parser=q['terminal_parser'],condition_id=cell['condition_id'],budget_bucket=c.policy_v2.GROUP_BUCKET[cell['group']],preparation_status='INDEPENDENT_EXACT_PROFILE_READY_NO_AUTOMATIC_REPLAY')
  spec['identity'].update(feature_vector=feature,ideal_vector=sem['ideal_vector'])
  configs=legacy.asset_manifest(spec['configs'],ordered=True);assets=legacy.asset_manifest(spec['auxiliary_assets']);spec['identity']['runtime_config_sha256']=legacy.content_hash(dict(ordered_configs=configs,auxiliary_assets=assets,environment=spec['environment']))
  changes=sem['comparison_variable_options'];spec['comparison_invariants_sha256']=legacy.content_hash(dict(source=source,trace=spec['identity']['trace_content_sha256'],epoch=spec['identity']['epoch_range'],termination=spec['identity']['termination_contract'],environment=spec['environment'],auxiliary_assets=assets,nonresearch_options={k:v for k,v in effective.items() if k not in changes},comparison_variable_options=sorted(changes)))
  sp=wp/'SPEC.json';c.write_json(sp,spec);audit=runner.inspect(spec,coord);assert not any(e['run_key']==audit['run_key'] for e in s['attempts']);atomic=legacy.validate_atomic_input_scope(spec,spec['input_scope_admission'],audit['traces']);c.write_json(wp/'PREFLIGHT.json',dict(audit,complete_atomic_scope=atomic))
  queue=dict(campaign_id=c.CAMPAIGN,authority_commit=c.AUTHORITY,prepared_by='E',input_and_profile_freeze_unix=time.time(),specs=[ref(sp)],pairs=[]);queuepath=wp/'QUEUE.json';c.write_json(queuepath,queue)
  row=dict(profile=profile,condition_id=cell['condition_id'],budget_bucket=spec['budget_bucket'],qualification=ref(qp),qualification_id=qid,review=ref(rp),spec=ref(sp),queue=ref(queuepath),estimated_wall_seconds=[3300,5100],timeout_seconds=spec['timeout_seconds'],estimated_result_bytes=[100000000,130000000],maximum_result_bytes=spec['maximum_result_bytes'],expected_full_instructions=audit['expected_full_instructions'],question=reasons[profile]);rows.append(row);print('INDEPENDENTLY_QUALIFIED',profile,qid,flush=True)
 baseline=dict(at_unix=time.time(),actual_starts=20,T0=s['t0_unix'],output_usage=c.output_usage(),source_identity=source,full_system_matrix=s['full_system_matrix'],controller=s['controller'],resources=c.local_resources(),accepted_pairs=s['accepted_pairs'])
 c.write_json(P/'BASELINE.json',baseline);plan=dict(schema='E2_ORIGINAL_CONV_CONTROL_ADMISSION_PLAN_V1',at_unix=time.time(),source_identity=source,profiles=rows,priority_order=list(PROFILES),original_matrix_unchanged=True,no_FWT_Vector_Btree_retry=True,planned_actual_starts=6,expected_after_starts=26,remaining_after_starts=14,source_supported_profiles=ref(AP/'SUPPORTED_PROFILES.json'),A_HEAD='73d1951bdc88df8562da7614c0ad0275fd6b1230',D_HEAD='0eb15c6458cf84403ce2eddfa1a25f4864c52787',max_simulators=2,original_start_deadline=c.START_DEADLINE,original_intake_deadline=c.INTAKE_DEADLINE,worst_result_addition_bytes=sum(r['maximum_result_bytes'] for r in rows),worst_new_result_bytes=baseline['output_usage']['new_bytes']+sum(r['maximum_result_bytes'] for r in rows),worst_total_result_bytes=baseline['output_usage']['total_bytes']+sum(r['maximum_result_bytes'] for r in rows))
 assert plan['worst_new_result_bytes']<=6*c.GIB and plan['worst_total_result_bytes']<=20*c.GIB
 c.write_json(P/'ADMISSION_PLAN.json',plan)
 print('ALL_SIX_PROFILE_QUALIFICATIONS_COMPLETE_NO_FULL_APP_STARTED',flush=True)
if __name__=='__main__':main()
