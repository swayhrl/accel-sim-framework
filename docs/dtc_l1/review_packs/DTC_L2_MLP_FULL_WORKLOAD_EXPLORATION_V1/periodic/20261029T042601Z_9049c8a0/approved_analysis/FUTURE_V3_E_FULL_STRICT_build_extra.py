"""Build new candidate from immutable V2 preimage; never edit the preimage."""
from pathlib import Path
O=Path(__file__).parent
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
old=A/'agents/E/strace_bpf_strict_consumer_v2/bpf_extra_strict.py'
s=old.read_text()
def replace(a,b):
 global s
 assert s.count(a)==1,(a[:90],s.count(a))
 s=s.replace(a,b)
s=s.replace("ID='DTC_STRACE_FUTURE_ENTRY_V2'","ID='DTC_STRACE_FUTURE_ENTRY_V3'")
s=s.replace("MAIN_EXCLUSION_SHA=", "FROZEN_POLICY_SHA='389be2e9dc01e071bc4c3edae10f8fa67ba1555c357840225b4a9687b8622b91'\nMAIN_EXCLUSION_SHA=",1)
start=s.index('def normalize_contract(');end=s.index('def proc(',start)
s=s[:start]+'''def normalize_contract(cfg,root,source_sha256=None,qualification_only=False):
 require(cfg['schema']==cfg['overlay_id']==ID,'V3 configuration required')
 require(cfg['root']==str(root),'Wrong root')
 return dict(root=str(root),qualification_only=qualification_only,cfg=copy.deepcopy(cfg),
  primary_statistics_excluded=False,validated_union_authorized=False)
def verify_science_rule(spec,rule,contract):
 require(spec['host_cpu']is None,'Canonical CPU must remain unbound')
 require(rule['route']=='V3_FUTURE_BPF_CANDIDATE','Engineering4 or nonselected must retain old route')
 require(rule['reference_cycles_equality_required']is False,'PRIMARY/IR cannot compare cross-profile cycles')
 require(science_sha(spec)==rule['science_projection_sha256'],'Scientific projection changed')
''' +s[end:]
replace("expected_pins=cfg['expected_pins'],QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],modes=cfg['modes'],future_primary_policy=cfg['future_primary_policy'])", "expected_pins=cfg['expected_pins'],QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],future_primary_policy=cfg['future_primary_policy'],future_ir_policy=cfg['future_ir_policy'],policy_source_sha256=cfg['policy_source_sha256'],canary4_prerequisite_sha256=cfg['canary4_prerequisite_sha256'])")
replace("root=P(root);rule=contract['cohorts'][c];ip=root/'control/qualification_ledger'/(c+'.INTENT.json');intent=read(ip);out=P(intent['output'])", "root=P(root);ip=root/'control/qualification_ledger'/(c+'.INTENT.json');intent=read(ip);out=P(intent['output'])")
replace(" require(contract['formal_exclusion_contract_sha256']==MAIN_EXCLUSION_SHA and sha(root/'control/SCOPE.json')==contract['original_primary_SCOPE_sha256'],'Frozen primary scope/contract drift')\n require(sha(MAIN_EXCLUSION_PATH)==MAIN_EXCLUSION_SHA and read(MAIN_EXCLUSION_PATH)['scope_cohorts']==contract['cohorts'],'Main scope rules changed')\n", "")
replace("cfg['status']=='ACTIVE_FUTURE_ONLY'", "cfg['status']=='ACTIVE_FUTURE_SCOPED'")
replace(" require(cfg['future_primary_policy']=='NONE','Broad primary rollout is not qualified by this engineer consumer')", " require(cfg['future_primary_policy']=='MATRIX_REGISTERED_UNSPENT_BPF_REQUIRED'and cfg['future_ir_policy']=='EXACT_REGISTERED_IR11_BPF_REQUIRED','Unqualified future policy')\n verify_release_prerequisite(cfg,authority)")
replace(" require(cfg['modes'].get(c)==snap['mode']==binding['mode']==rule['mode'],'Mode contract drift')", " require(snap['mode']==binding['mode']=='BPF_REQUIRED','PRIMARY/IR require proven BPF; no fallback mode')")
replace(" verify_science_rule(spec,rule,contract)\n for name in ['SCOPE.json','MATRIX_CURRENT.json']:\n  require(not any(p['cohort']==c for p in read(root/'control'/name)['points']),'Canary leaked into primary '+name)", " producer=load_pinned(cfg['source_paths']['producer'],cfg['qualified_sources']['producer'],'v3_strict_producer')\n rule,metadata=producer.classify_scope(cfg,c,authority,spec=spec,stage='TERMINAL',historical_context=snap)\n require(rule==snap['scope_policy'],'Historical scope policy changed')\n verify_science_rule(spec,rule,contract)\n require(utfsha(snap['policy_source_utf8'])==cfg['policy_source_sha256']==sha(cfg['policy_source_path']),'Frozen policy source snapshot')\n require(utfsha(snap['canary4_prerequisite_utf8'])==cfg['canary4_prerequisite_sha256']==sha(cfg['canary4_prerequisite_path']),'Real canary gate snapshot')\n require(utfsha(snap['ir_plan_utf8'])==cfg['ir_plan_sha256']==sha(cfg['ir_plan_path']),'Frozen IR plan snapshot')\n trace=snap['trace_contract'];reference=json.loads(snap['trace_reference_spec_utf8'])\n require(trace['source_science_sha256']==science_sha(reference),'Trace reference scientific projection')\n require(trace['input_digest']==spec['input_digest']==reference['input_digest']and trace['input_binding_sha256']==spec['input_binding_sha256']==reference['input_binding_sha256'],'Trace reference identity')\n require(trace['expected']==spec['expected']==reference['expected'],'Complete frozen trace counts changed')\n for key in ['source_cohort','source_science_sha256','input_digest','input_binding_sha256','expected']:\n  require(trace[key]==metadata['trace_contract'][key],'Current frozen trace reference changed '+key)\n require(reference['cohort']==trace['source_cohort'],'Wrong trace reference cohort')")
replace("return dict(intent=intent,out=out,docs=docs,binding=binding,snapshot=snap,verdict=verdict,scientific_identity=si)", "return dict(intent=intent,out=out,docs=docs,binding=binding,snapshot=snap,verdict=verdict,scientific_identity=si,scope_policy=rule,spec=spec)")
replace(" require(utfsha(snap['policy_source_utf8'])==cfg['policy_source_sha256']==sha(cfg['policy_source_path']),'Frozen policy source snapshot')", " require(utfsha(snap['policy_source_utf8'])==cfg['policy_source_sha256']==sha(cfg['policy_source_path'])==FROZEN_POLICY_SHA,'Frozen policy source snapshot')")
anchor=" require(reference['cohort']==trace['source_cohort'],'Wrong trace reference cohort')"
replace(anchor,anchor+"\n route=producer.read_route_claim(cfg,c,spec);rp=producer.route_claim_path(cfg,c)\n require(sha(rp)==snap['route_claim_sha256']==binding['route_claim_sha256']==utfsha(snap['route_claim_utf8']),'Persistent V3 route claim binding')\n require(json.loads(snap['route_claim_utf8'])==route and route['scientific_role']==rule['scientific_role']and route['primary_statistics_excluded']==rule['primary_statistics_excluded'],'Route claim role/science mismatch')\n memory=json.loads(snap['memory_configuration_utf8']);captured_memory=read(out/'CPU_SPARE_MEMORY_ADMISSION_SNAPSHOT.json')['config']\n require(c in memory['allowed_cohorts']and set(memory['allowed_cohorts'])<=set(captured_memory['allowed_cohorts']),'Official memory scope capture mismatch')\n require({k:v for k,v in memory.items()if k!='allowed_cohorts'}=={k:v for k,v in captured_memory.items()if k!='allowed_cohorts'},'Memory generation changed outside official allow append')\n if rule['scientific_role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL':\n  plan=json.loads(snap['ir_plan_utf8']);rows=[r for r in plan['rows']if r['new_cohort']==c];require(len(rows)==1,'IR one-to-one plan identity')\n  row=rows[0];require(sha(row['draft_spec']['path'])==row['draft_spec']['sha256'],'Frozen IR draft spec changed')\n  draft=read(row['draft_spec']['path']);require(spec['incident_recovery_trial_lineage']==draft['incident_recovery_trial_lineage'],'Full IR negative/source lineage changed')\n  old=root/'analysis'/(row['original_cohort']+'.RESULT.json');require(sha(old)==row['original_negative_RESULT_sha256'],'Original negative changed')\n  negative=read(old);require(negative.get('cycles')is None and negative.get('proof',{}).get('performance_accepted')is not True,'Original negative cannot become accepted')\n  require(authority['consumed'][row['original_cohort']]['uuid']==row['original_uuid'],'Original failed UUID changed')\n  require(sha(root/'control/qualification_ledger'/(row['original_cohort']+'.DONE.json'))==row['original_DONE_sha256'],'Original failure DONE changed')")
start=s.index(" rule=contract['cohorts'][c];reference_path=")
end=s.index(' side=out/SIDE;',start)
s=s[:start]+''' rule=v['scope_policy'];spec=v['spec']
 require(base_proof['cell']==spec['cell']and base_proof['profile']==spec['profile'],'Actual design/profile')
 require(base_proof['effective_options']==spec['expected_options']==rule['expected_options']and len(base_proof['effective_options'])==270,'Actual all270 options changed')
 for actual,frozen in [('CTA','CTA'),('instructions','instructions'),('kernel_count','kernels')]:
  require(base_proof[actual]==spec['expected'][frozen]==rule['expected'][frozen],'Complete frozen ROI count '+actual)
 require(type(base_proof['cycles'])is int and base_proof['cycles']>0,'Positive actual cycles required')
 if rule['scientific_role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL':
  require(v['intent']['uuid']!=spec['incident_recovery_trial_lineage']['original_uuid'],'Original failed UUID reused')
 result=dict(schema=ID,status='PASS_STRACE_V3_AND_ORIGINAL_CPU2_IO',cohort=c,uuid=v['intent']['uuid'],mode=v['binding']['mode'],
  snapshot_sha256=sha(out/SNAP),activation_sha256=sha(out/ACT),fork_plan_sha256=sha(out/FORK),extra_strict_source_sha256=sha(__file__),
  scientific_identity=v['scientific_identity'],activation=v['verdict'],original_strict_required=True,CPU2_strict_required=True,IO_strict_required=True,
  scientific_role=rule['scientific_role'],science_projection_sha256=rule['science_projection_sha256'],
  primary_statistics_excluded=rule['primary_statistics_excluded'],validated_union_authorized=False,
  cross_profile_or_failed_cycles_equality_required=False,actual_cycles=base_proof['cycles'])
''' +s[end:]
(O/'bpf_extra_strict.py').write_text(s+'\n'+(O/'gate_functions.py').read_text())
