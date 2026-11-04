from pathlib import Path
import json,hashlib,datetime,subprocess,os,sys
sys.dont_write_bytecode=True
A1=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1');O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_remaining48_execution_20261104_v1/agents/A_resource_config_v1');P=A1/'root_remaining48_proposal_v1/PROPOSED_MATRIX.json';H=lambda b:hashlib.sha256(b).hexdigest();sha=lambda p:H(Path(p).read_bytes());j=json.loads(P.read_bytes());assert sha(P)=='d474de469f9b13d48687a8aa5ebfbc6ca3127fc8cd5ae1d7f4cfe2c099d4e8e2';prev=A1/'agents/A_remaining48_readonly_qualification_v1';assert sha(prev/'MANIFEST.json')=='7e569888e5d91c067e2d9ce29a4f1cc05c75ddf1d03a752d9b857961ecc634e6';old=json.loads((prev/'QUALIFICATION_EVIDENCE.json').read_text());assert not old['qualification_gaps'];checks=[];pins={};inputs=[];cfg=[]
for pin in json.loads((prev/'MANIFEST.json').read_text())['files']:assert sha(prev/pin['path'])==pin['sha256']
for kind in ['original_results96','old_specs72']:
 for x in old[kind]:
  assert sha(x['path'])==x['sha256'];pins[x['path']]=dict(path=x['path'],sha256=x['sha256'],kind=kind)
  z=json.loads(Path(x['path']).read_text())
  if kind=='original_results96':assert z['proof']['performance_accepted']is True and z['proof']['binary_sha256']=='02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d'
 checks.append(kind+'_fresh_all_SHA_and_accepted_where_applicable')
for x in old['inputs24']:
 assert sha(x['input_binding']['path'])==x['input_binding']['sha256'];bd=json.loads(Path(x['input_binding']['path']).read_text());q=bd['qualification'];assert q['status']=='BODY_COMPLETE_SHA_AND_BASIC_FORMAT_PASS'and not q['issues'];assert bd['input_digest']==x['input_digest'];assert sha(x['trace_entry'])==bd['asset']['commandlist_sha256']
 for row in q['rows']:
  st=Path(row['path']).stat();assert [st.st_size,st.st_mtime_ns]==row['full_SHA_current_size_mtime']
 inputs.append(dict(input_digest=x['input_digest'],program=x['program'],suite=x['suite'],input_binding=x['input_binding'],trace_entry=x['trace_entry'],commandlist_sha256=bd['asset']['commandlist_sha256'],expected=x['expected'],member_count=len(q['rows']),body_SHA_reused_with_current_size_mtime=True))
checks.append('24bindings_traceentry_SHA_and_all_member_size_mtime')
for profile,v in old['config_profiles'].items():
 for x in v['configs']:
  fp=prev/x['readonly_plan_copy'];assert sha(fp)==x['sha256'];cfg.append(dict(profile=profile,git_path=x['git_path'],commit=x['fixed_commit'],sha256=x['sha256'],readonly_bytes_path=str(fp)))
checks.append('8_fixed5001_config_bytecopies_SHA')
oldids=json.loads((prev/'REMAINING48_PLAN_IDENTITIES.json').read_text())['candidates48'];assert {x['plan_candidate_id']for x in oldids}=={x['candidate_id']for x in j['candidates']};assert len(j['candidates'])==48;assert len({x['input_digest']for x in j['candidates']})==24
checks.append('exact_authorized_proposal_set48_no_membership_change')
measured=json.loads((O/'INITIAL_REAL_RESOURCE_OBSERVATION.json').read_text());legal=list(range(512));ownerMain=list(range(32,64));newmask=[i for i in legal if i not in ownerMain];assert len(newmask)==480
cpu=dict(schema='REMAINING48_NEW_ADDON_THREAD_CPU_PLANNING_V1',observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cgroup_cpuset='0-511',cgroup_CPU_quota_equivalents=384,host_visible_CPU_count=512,new_addon_allowed_cpu_mask='0-31,64-511',new_addon_allowed_CPUs=newmask,owner_main_mask_preserved='32-63',only_new_addon_thread_may_set_its_own_affinity=True,main_or_old_thread_affinity_changes_authorized=False,new_cpu_claims_must_recheck_observed_models_and_affinity=True,observation_not_CPU_grant=True)
(O/'NEW_ADDON_CPU_MASK.json').write_text(json.dumps(cpu,indent=2)+'\n')
report=dict(schema='REMAINING48_CONFIG_INPUT_REQUALIFICATION_V1',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PASS_READONLY_SCIENTIFIC_IDENTITY_AND_CONFIGURATION',authorized_proposal_commit='5f67b4d6b94568a9f1acc80c3e56736bd81e4753',authorized_proposal_sha256=sha(P),fixed_contract_commit='5001c3f35052f7f91f1ad41eeff83f2947a0878d',source_prior_qualification_manifest_sha256=sha(prev/'MANIFEST.json'),checks=checks,candidates48=[dict(candidate_id=x['candidate_id'],program=x['program'],suite=x['suite'],input_digest=x['input_digest'],profile=x['profile'],expected=x['expected'],input_binding=x['input_binding'],source_reference_paths={k:x[k]['result_evidence']['path']for k in ['parent_CH_P0','matched_DH_P0','matched_DH_variant']})for x in j['candidates']],inputs24=inputs,original_source_pins=list(pins.values()),fixed_config8=cfg,qualification_gaps=[],new_scientific_registrations_by_agent=0,new_model_starts_by_agent=0,large_trace_bodies_not_reread=True,old_files_not_changed=True,resource_forecast_and_cap_contract='RESOURCE_SPEC_FIELDS.json; does not alter science inputs/options')
(O/'CONFIG_INPUT_QUALIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],inputs=len(inputs),refs=len(pins),configs=len(cfg),CPUmask=cpu['new_addon_allowed_cpu_mask'])))
