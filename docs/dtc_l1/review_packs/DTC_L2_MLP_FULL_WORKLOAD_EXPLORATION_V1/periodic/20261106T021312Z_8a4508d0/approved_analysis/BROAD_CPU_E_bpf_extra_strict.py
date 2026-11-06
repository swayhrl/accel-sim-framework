"""Observation-only strict AND the existing original/CPU2/IO proof. No install."""
import copy,hashlib,importlib.util,json,pathlib,re
P=pathlib.Path
ID='DTC_STRACE_BROAD_SHARED_CPU_V1'
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
FIELD='additional_strace_bpf_observation_binding'
KEY='additional_strace_bpf_observation_strict'
ROLES=('entry','frontend','producer','extra_strict','consumer')
SNAP='STRACE_BPF_OBSERVATION_SNAPSHOT.json';ACT='STRACE_BPF_ACTIVATION.json';FORK='STRACE_BPF_FORK_PLAN.json';SIDE='STRACE_BPF_EXTRA_STRICT.json'
PRODUCTION_ROOT=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
SCIENCE_KEYS=('binary_sha256','cell','configs','core_commit','correctness_validation_only','downstream_profile','execution_mnt_namespace','expected','expected_options','framework_commit','input_binding_path','input_binding_sha256','input_digest','native_simulator_argv','original_environment','performance_scope','profile','project','request','runtime_files','schema','source_kind','source_worktrees','suite','workload','program')
FROZEN_POLICY_SHA='389be2e9dc01e071bc4c3edae10f8fa67ba1555c357840225b4a9687b8622b91'
MAIN_EXCLUSION_SHA='4d7e1d1990771d8dc8bc1a9afe6ea85b9dae0f8752e951332742664a28dd0aa7'
MAIN_EXCLUSION_PATH=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/coordinator/bpf_canary_orchestration_v1/ENGINEERING_EXCLUSION_CONTRACT.json')
class ObservationHold(RuntimeError):pass
def require(v,m):
 if not v:raise ObservationHold(m)
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def objsha(v):return hashlib.sha256(js(v)).hexdigest()
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def utfsha(v):return hashlib.sha256(v.encode('utf-8')).hexdigest()
def science_sha(spec):return hashlib.sha256(json.dumps({k:spec[k]for k in SCIENCE_KEYS},sort_keys=True,separators=(',',':')).encode()).hexdigest()
def normalize_contract(cfg,root,source_sha256=None,qualification_only=False):
 require(cfg['schema']==cfg['overlay_id']==ID,'V3 configuration required')
 require(cfg['root']==str(root),'Wrong root')
 return dict(root=str(root),qualification_only=qualification_only,cfg=copy.deepcopy(cfg),
  primary_statistics_excluded=False,validated_union_authorized=False)
def verify_science_rule(spec,rule,contract):
 require(spec['host_cpu']is None,'Canonical CPU must remain unbound')
 require(rule['route']=='V3_FUTURE_BPF_CANDIDATE','Engineering4 or nonselected must retain old route')
 require(rule['reference_cycles_equality_required']is False,'PRIMARY/IR cannot compare cross-profile cycles')
 require(science_sha(spec)==rule['science_projection_sha256'],'Scientific projection changed')
def proc(value):
 def stat(text):
  head,tail=text.rsplit(')',1);f=tail.split();return dict(pid=int(head.split('(',1)[0]),start=int(f[19]),state=f[0],ppid=int(f[1]))
 before,after=stat(value['stat_before_utf8']),stat(value['stat_after_utf8'])
 require(before['pid']==after['pid']==value['pid']and before['start']==after['start']==value['start_ticks'],'PID generation drift')
 require(before['state']not in('Z','X','x')and after['state']not in('Z','X','x')and before['ppid']==after['ppid'],'Dead or unstable PID')
 fields={k.strip():v.strip()for line in value['status_utf8'].splitlines()if ':'in line for k,v in[line.split(':',1)]}
 for key in ['Pid','PPid','TracerPid','Seccomp','Seccomp_filters']:require(key in fields,'Missing proc '+key)
 status={k:int(fields[k])for k in ['Pid','PPid','TracerPid','Seccomp','Seccomp_filters']}
 require(status['Pid']==value['pid']and status['PPid']==after['ppid'],'stat/status identity mismatch')
 require(value['mnt_namespace']and value['observed_UTC'],'Missing process observation')
 return dict(status,pid=value['pid'],start_ticks=value['start_ticks'],mnt_namespace=value['mnt_namespace'])
def record(cfg):
 return dict(request=cfg['request'],overlay_id=cfg['overlay_id'],configuration_sha256=objsha(cfg),qualified_sources=cfg['qualified_sources'],
 expected_pins=cfg['expected_pins'],QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],future_primary_policy=cfg['future_primary_policy'],future_ir_policy=cfg['future_ir_policy'],policy_source_sha256=cfg['policy_source_sha256'],canary4_prerequisite_sha256=cfg['canary4_prerequisite_sha256'],resource_configuration_sha256=cfg['resource_configuration_sha256'])
def verify_activation(activation,snapshot,fork,launch,pid):
 mode=snapshot['mode'];baseline1=proc(snapshot['baseline_preINTENT']);baseline2=proc(fork['baseline_prePopen'])
 require(activation['baseline_preINTENT']==snapshot['baseline_preINTENT']and activation['baseline_prePopen']==fork['baseline_prePopen'],'Baseline binding drift')
 require((baseline1['pid'],baseline1['start_ticks'])==(baseline2['pid'],baseline2['start_ticks']),'Frontend generation changed')
 for baseline in [baseline1,baseline2]:require((baseline['TracerPid'],baseline['Seccomp'],baseline['Seccomp_filters'])==(0,0,0),'Unknown/inherited seccomp baseline')
 model,tracer=proc(activation['model']),proc(activation['tracer'])
 require(model['pid']==pid['pid']and model['start_ticks']==pid['start_ticks'],'Wrong model PID/start')
 require(tracer['pid']==launch['launcher_pid']and tracer['PPid']==baseline2['pid'],'Wrong tracer/parent')
 require(model['PPid']==tracer['pid']and model['TracerPid']==tracer['pid'],'Wrong actual tracer relationship')
 require(tracer['TracerPid']==0 and(tracer['Seccomp'],tracer['Seccomp_filters'])==(0,0),'Nested/inherited tracer unsupported')
 require(model['mnt_namespace']==tracer['mnt_namespace']==baseline1['mnt_namespace']==baseline2['mnt_namespace']==pid['mnt_namespace'],'Namespace mismatch')
 expected=(2,1)if mode=='BPF_REQUIRED'else(0,0)if mode=='DEFAULT_CONTROL'else None
 require(expected is not None and(model['Seccomp'],model['Seccomp_filters'])==expected,'Silent fallback or unknown activation')
 require(mode=='BPF_REQUIRED','Broad scope is BPF only')
 expected_status='PASS_BROAD_SHARED_BPF_REQUIRED_ACTIVE'
 require(activation['verdict']['status']==expected_status,'Producer did not prove requested mode')
 return dict(status=expected_status,model_pid=model['pid'],model_start_ticks=model['start_ticks'],tracer_pid=tracer['pid'],tracer_start_ticks=tracer['start_ticks'],
  baseline_Seccomp=0,baseline_filters=0,model_Seccomp=expected[0],model_filters=expected[1],fallback_accepted=False)
def verified_files(c,root,contract,authority):
 root=P(root);ip=root/'control/qualification_ledger'/(c+'.INTENT.json');intent=read(ip);out=P(intent['output'])
 require(out==root/'DTC/run/results'/intent['uuid'],'Wrong output namespace')
 require(root==PRODUCTION_ROOT or(contract.get('qualification_only')is True and authority.get('qualification_only')is True),'Nonproduction root without private qualification')
 docs=[intent,read(out/'NATIVE_LAUNCH.json'),read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')];binding=intent[FIELD]
 require(all(x[FIELD]==binding for x in docs),'Missing or unequal three observation bindings')
 require(binding['schema']==binding['overlay_id']==ID and binding['request']==REQ and binding['cohort']==c and binding['uuid']==intent['uuid'],'Observation identity')
 require(sha(out/SNAP)==binding['snapshot_sha256'],'Snapshot SHA mismatch');snap=read(out/SNAP);cfg=snap['config']
 require(snap['schema']==cfg['schema']==cfg['overlay_id']==ID and cfg['status']=='ACTIVE_FUTURE_SCOPED','Snapshot configuration schema/status')
 require(cfg['root']==str(root)and cfg['request']==REQ and objsha(cfg)==binding['config_sha256'],'Configuration identity')
 require(cfg['future_primary_policy']=='MATRIX_REGISTERED_UNSPENT_BPF_REQUIRED'and cfg['future_ir_policy']=='EXACT_REGISTERED_IR11_BPF_REQUIRED','Unqualified future policy')
 verify_release_prerequisite(cfg,authority,resource_configuration_utf8=snap['resource_configuration_utf8'],resource_snapshot=read(out/'CPU_SHARED_TIMESLICE_SNAPSHOT.json'))
 require(not cfg['qualification_only']or authority.get('qualification_only')is True,'CPU fixture cannot release production')
 require(snap['mode']==binding['mode']=='BPF_REQUIRED','PRIMARY/IR require proven BPF; no fallback mode')
 require(snap['overlay_record']['status']=='ACTIVE'and all(snap['overlay_record'].get(k)==v for k,v in record(cfg).items()),'Historical overlay record mismatch')
 require(snap['overlay_record']['configuration_sha256']==binding['config_sha256'],'Historical config record')
 for role in ROLES:
  source=snap['source_snapshots'][role];expected=cfg['qualified_sources'][role]
  require(source['path']==cfg['source_paths'][role]and source['sha256']==expected==utfsha(source['utf8']),'Source snapshot SHA')
  require(sha(source['path'])==expected,'Qualified source changed')
 require(cfg['qualified_sources']==binding['qualified_sources'],'Binding source set')
 require(cfg['source_paths']['extra_strict']==str(P(__file__).resolve())and cfg['qualified_sources']['extra_strict']==sha(__file__),'Wrong new strict source')
 for path,pin in cfg['expected_pins'].items():require(sha(path)==pin,'Required original source drift '+path)
 require(utfsha(snap['QA_utf8'])==cfg['QA_sha256']==binding['QA_sha256'],'QA SHA')
 require(utfsha(snap['readback_utf8'])==cfg['readback_sha256']==binding['readback_sha256'],'Readback SHA')
 qa=json.loads(snap['QA_utf8']);back=json.loads(snap['readback_utf8'])
 require(qa['status']=='PASS'and all(qa[x]is True for x in ['native_prefix_qualified','extra_strict_qualified','consumer_archive_qualified']),'Not complete CPU qualification')
 require(back['verified']is True and back['QA_sha256']==cfg['QA_sha256'],'Readback not verified')
 for v in [qa,back]:require(v['qualified_sources']==cfg['qualified_sources']and v['expected_pins']==cfg['expected_pins'],'QA/readback source mismatch')
 cp=root/'control/specs'/(c+'.json');spec=read(cp);dbp=root/'control/dispatch_bindings'/(c+'.json');db=read(dbp)
 producer=load_pinned(cfg['source_paths']['producer'],cfg['qualified_sources']['producer'],'v3_strict_producer')
 rule,metadata=producer.classify_scope(cfg,c,authority,spec=spec,stage='TERMINAL',historical_context=snap)
 require(rule==snap['scope_policy'],'Historical scope policy changed')
 verify_science_rule(spec,rule,contract)
 require(utfsha(snap['policy_source_utf8'])==cfg['policy_source_sha256']==sha(cfg['policy_source_path'])==FROZEN_POLICY_SHA,'Frozen policy source snapshot')
 require(utfsha(snap['canary4_prerequisite_utf8'])==cfg['canary4_prerequisite_sha256']==sha(cfg['canary4_prerequisite_path']),'Real canary gate snapshot')
 require(utfsha(snap['ir_plan_utf8'])==cfg['ir_plan_sha256']==sha(cfg['ir_plan_path']),'Frozen IR plan snapshot')
 trace=snap['trace_contract'];reference=json.loads(snap['trace_reference_spec_utf8'])
 require(trace['source_science_sha256']==science_sha(reference),'Trace reference scientific projection')
 require(trace['input_digest']==spec['input_digest']==reference['input_digest']and trace['input_binding_sha256']==spec['input_binding_sha256']==reference['input_binding_sha256'],'Trace reference identity')
 require(trace['expected']==spec['expected']==reference['expected'],'Complete frozen trace counts changed')
 for key in ['source_cohort','source_science_sha256','input_digest','input_binding_sha256','expected']:
  require(trace[key]==metadata['trace_contract'][key],'Current frozen trace reference changed '+key)
 require(reference['cohort']==trace['source_cohort'],'Wrong trace reference cohort')
 route=producer.read_route_claim(cfg,c,spec);rp=producer.route_claim_path(cfg,c)
 require(sha(rp)==snap['route_claim_sha256']==binding['route_claim_sha256']==utfsha(snap['route_claim_utf8']),'Persistent V3 route claim binding')
 require(json.loads(snap['route_claim_utf8'])==route and route['scientific_role']==rule['scientific_role']and route['primary_statistics_excluded']==rule['primary_statistics_excluded'],'Route claim role/science mismatch')
 memory=json.loads(snap['memory_configuration_utf8']);captured_memory=read(out/'CPU_SHARED_TIMESLICE_SNAPSHOT.json')['config']
 require(snap['memory_configuration_utf8']==snap['resource_configuration_utf8'],'Broad typed memory/resource scope differs')
 require(memory==captured_memory and c in memory['allowed_cohorts'],'Captured broad resource generation differs')
 require(utfsha(snap['resource_configuration_utf8'])==cfg['resource_configuration_sha256'],'Broad resource configuration binding')
 if rule['scientific_role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL':
  plan=json.loads(snap['ir_plan_utf8']);rows=[r for r in plan['rows']if r['new_cohort']==c];require(len(rows)==1,'IR one-to-one plan identity')
  row=rows[0];require(sha(row['draft_spec']['path'])==row['draft_spec']['sha256'],'Frozen IR draft spec changed')
  draft=read(row['draft_spec']['path']);require(spec['incident_recovery_trial_lineage']==draft['incident_recovery_trial_lineage'],'Full IR negative/source lineage changed')
  old=root/'analysis'/(row['original_cohort']+'.RESULT.json');require(sha(old)==row['original_negative_RESULT_sha256'],'Original negative changed')
  negative=read(old);require(negative.get('cycles')is None and negative.get('proof',{}).get('performance_accepted')is not True,'Original negative cannot become accepted')
  require(authority['consumed'][row['original_cohort']]['uuid']==row['original_uuid'],'Original failed UUID changed')
  require(sha(root/'control/qualification_ledger'/(row['original_cohort']+'.DONE.json'))==row['original_DONE_sha256'],'Original failure DONE changed')
 require(sha(cp)==binding['canonical_spec_sha256']==snap['canonical_spec_sha256']==utfsha(snap['canonical_spec_utf8']),'Current canonical source identity')
 require(json.loads(snap['canonical_spec_utf8'])==spec and db['canonical_spec_sha256']==sha(cp),'Canonical/dispatch join')
 require(sha(dbp)==binding['dispatch_binding_sha256']==snap['dispatch_binding_sha256']==utfsha(snap['dispatch_binding_utf8']),'Dispatch SHA')
 require(json.loads(snap['dispatch_binding_utf8'])==db and all(x['dispatch_binding_sha256']==sha(dbp)for x in docs),'Three dispatch bindings')
 require(snap['resolved_spec']==dict(spec,host_cpu=db['host_cpu'])and objsha(snap['resolved_spec'])==snap['resolved_spec_sha256']==binding['resolved_spec_sha256']==db['resolved_spec_sha256'],'Resolved spec identity')
 require(authority['admitted_specs'][c]==sha(cp)and authority['consumed'][c]['uuid']==intent['uuid']and authority['consumed'][c]['intent_sha256']==sha(ip),'Registered consumed identity')
 si={k:spec[k]for k in ['input_digest','core_commit','framework_commit','binary_sha256','cell','profile']}
 require(spec['input_binding_sha256']==sha(root/'control/input_bindings'/(spec['input_digest']+'.json')),'Frozen input-binding bytes changed')
 si.update(input_binding_sha256=spec['input_binding_sha256'],expected_options_sha256=objsha(spec['expected_options']),native_simulator_argv_sha256=objsha(spec['native_simulator_argv']))
 require(si==snap['scientific_identity']==binding['scientific_identity'],'Scientific identity drift')
 require(len(spec['expected_options'])==270,'Incomplete physics option contract')
 for key in ['schema','request','cohort','uuid','mode']:
  expected=ID if key=='schema'else REQ if key=='request'else c if key=='cohort'else intent['uuid']if key=='uuid'else binding['mode']
  require(snap[key]==expected,'Snapshot '+key)
 before,after=snap['expected_argv_before'],snap['expected_argv_after'];prefix=before[:before.index('--')]
 require(all(type(x)is str for x in before+after)and prefix.count('-f')==1,'Exact follow-fork argv required')
 require(prefix[prefix.index('-e')+1]=='trace=%file,process,network'and'--seccomp-bpf'not in before and'-p'not in prefix and'--attach'not in prefix,'Tracing contract changed')
 wanted=before[:before.index('-f')]+['--seccomp-bpf']+before[before.index('-f'):]if binding['mode']=='BPF_REQUIRED'else before
 require(after==wanted and objsha(before)==binding['expected_argv_before_sha256']and objsha(after)==binding['expected_argv_after_sha256'],'Unexpected argv change')
 require(docs[1]['argv']==after,'Recorded actual argv missing flag or wrong control mode')
 fork=read(out/FORK);act=read(out/ACT)
 require(sha(out/FORK)==docs[1]['strace_fork_plan_sha256']==act['fork_plan_sha256'],'Fork plan SHA')
 require(sha(out/ACT)==docs[2]['strace_observation_activation_sha256'],'Activation SHA')
 for doc in [fork,act]:
  require(doc['schema']==ID and doc['cohort']==c and doc['uuid']==intent['uuid']and doc['mode']==binding['mode']and doc['snapshot_sha256']==binding['snapshot_sha256'],'Runtime generation binding')
 require(fork['intent_sha256']==sha(ip)and fork['argv_before']==before and fork['argv_after']==after and fork['argv_list_mutated_in_place']is True and fork['scientific_identity']==si,'Own-INTENT pre-fork plan')
 verdict=verify_activation(act,snap,fork,docs[1],docs[2])
 return dict(intent=intent,out=out,docs=docs,binding=binding,snapshot=snap,verdict=verdict,scientific_identity=si,scope_policy=rule,spec=spec)
def terminal(c,base_proof,root,contract,authority,readonly=False):
 require(base_proof.get('performance_accepted')is True,'Original performance strict mandatory')
 require('additional_cpu_spare_memory_admission_strict'not in base_proof,'Broad Shared cannot claim CPU2 PASS')
 require(base_proof.get('additional_cpu_shared_timeslice_strict',{}).get('schema')=='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1'and base_proof['additional_cpu_shared_timeslice_strict'].get('status')=='PASS_CPU_SHARED_DYNAMIC_IO_AND_ORIGINAL_PERFORMANCE','Dynamic Shared strict mandatory')
 require('additional_shared_json_io_strict'in base_proof or'additional_future_memory_io_strict'in base_proof,'IO strict mandatory')
 v=verified_files(c,root,contract,authority);out=v['out']
 for k in ['cohort','uuid','input_digest','core_commit','framework_commit','binary_sha256']:
  expected=c if k=='cohort'else v['intent']['uuid']if k=='uuid'else v['scientific_identity'][k]
  require(base_proof[k]==expected,'Original strict/new observation identity mismatch '+k)
 done=read(P(root)/'control/qualification_ledger'/(c+'.DONE.json'))
 require(done==read(out/'NATIVE_EXIT.json')==authority['consumed'][c]['execution_receipt'],'Original natural execution closure')
 require(done['uuid']==v['intent']['uuid']and done['stop_reason']is None and done['launcher_wait_returncode']==0,'Not a natural successful canary')
 rule=v['scope_policy'];spec=v['spec']
 require(base_proof['cell']==spec['cell']and base_proof['profile']==spec['profile'],'Actual design/profile')
 require(base_proof['effective_options']==spec['expected_options']==rule['expected_options']and len(base_proof['effective_options'])==270,'Actual all270 options changed')
 for actual,frozen in [('CTA','CTA'),('instructions','instructions'),('kernel_count','kernels')]:
  require(base_proof[actual]==spec['expected'][frozen]==rule['expected'][frozen],'Complete frozen ROI count '+actual)
 require(type(base_proof['cycles'])is int and base_proof['cycles']>0,'Positive actual cycles required')
 if rule['scientific_role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL':
  require(v['intent']['uuid']!=spec['incident_recovery_trial_lineage']['original_uuid'],'Original failed UUID reused')
 result=dict(schema=ID,status='PASS_BROAD_SHARED_BPF_AND_ORIGINAL_IO',cohort=c,uuid=v['intent']['uuid'],mode=v['binding']['mode'],
  snapshot_sha256=sha(out/SNAP),activation_sha256=sha(out/ACT),fork_plan_sha256=sha(out/FORK),extra_strict_source_sha256=sha(__file__),
  scientific_identity=v['scientific_identity'],activation=v['verdict'],original_strict_required=True,CPU2_strict_required=False,old_CPU2_PASS_claimed=False,dynamic_shared_strict_required=True,IO_strict_required=True,
  scientific_role=rule['scientific_role'],science_projection_sha256=rule['science_projection_sha256'],
  primary_statistics_excluded=rule['primary_statistics_excluded'],validated_union_authorized=False,
  cross_profile_or_failed_cycles_equality_required=False,actual_cycles=base_proof['cycles'])
 side=out/SIDE;data=js(result)
 if readonly:require(side.exists()and side.read_bytes()==data,'Readonly observation sidecar missing/changed')
 elif side.exists():require(side.read_bytes()==data,'Immutable observation sidecar conflict')
 else:
  source=v['snapshot']['config']['source_paths']['producer']
  require(sha(source)==v['snapshot']['config']['qualified_sources']['producer'],'Atomic helper source drift')
  sp=importlib.util.spec_from_file_location('strict_pinned_observation_atomic',source);producer=importlib.util.module_from_spec(sp);sp.loader.exec_module(producer)
  producer.atomic_exclusive(side,result)
  require(side.read_bytes()==data,'Published strict sidecar bytes differ')
 return dict(base_proof,**{KEY:dict(result,sidecar_path=str(side),sidecar_sha256=hashlib.sha256(data).hexdigest())})
def verify_archive(c,archive,root,contract):
 root=P(root);intent=read(root/'control/qualification_ledger'/(c+'.INTENT.json'));out=P(intent['output']);receipt=archive['receipt']
 require(receipt['cohort']==c and receipt['status']=='ARCHIVE_VERIFIED_AND_RESTORE_VERIFIED_NATIVE_TARGET'and receipt['source_disposition']=='SOURCE_KEEP','Original archive verification mandatory')
 bundle=P(receipt['target_mount_path']);manifest=read(bundle/'SOURCE_MANIFEST.json')
 canonical=(json.dumps(manifest,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
 require(hashlib.sha256(canonical).hexdigest()==receipt['manifest_sha256']and manifest['cohort']==c and manifest['source_root']==str(out),'Archive manifest identity')
 restore=P(receipt['native_restore']);entries={x['path']:x for x in manifest['entries']}
 require(len(entries)==len(manifest['entries']),'Duplicate archive paths')
 require(restore.resolve().is_relative_to(root/'DTC/run/recovery'),'Wrong native restore namespace')
 if not contract.get('qualification_only',False):
  require(root==PRODUCTION_ROOT and restore.stat().st_dev==root.stat().st_dev==2128,'Restore is not actual native device2128')
  require(bundle.resolve().is_relative_to(P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/results')),'Wrong true164 archive namespace')
 keys=[SNAP,ACT,FORK,SIDE,'NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json','NATIVE_EXIT.json','L2_STRICT.json','CPU_SHARED_TIMESLICE_SNAPSHOT.json','CPU_SHARED_TIMESLICE_EXTRA_STRICT.json','SHARED_JSON_IO_SNAPSHOT.json','SHARED_JSON_IO_EXTRA_STRICT.json']
 proofs=[]
 for name in keys:
  entry=entries.get(name);require(entry is not None and entry['type']=='file','Missing archived key '+name)
  require(not(out/name).is_symlink()and not(restore/name).is_symlink(),'Unexpected key symlink')
  require(sha(out/name)==entry['sha256']==sha(restore/name)and(out/name).stat().st_size==entry['size']==(restore/name).stat().st_size,'Key archive/restore bytes changed '+name)
  proofs.append(dict(path=name,sha256=entry['sha256'],bytes=entry['size']))
 require(archive['independently_verified_entries']==len(manifest['entries']),'Original full archive/native verification incomplete')
 return dict(schema=ID,status='PASS_NEW_OBSERVATION_ARCHIVED_AND_NATIVE_RESTORED',cohort=c,uuid=intent['uuid'],manifest_sha256=receipt['manifest_sha256'],
  archive_sha256=receipt['archive_sha256'],native_restore=str(restore),required_files=proofs,original_full_archive_verifier_required=True)


# Included in the separate broad observation strict source.
ACTUAL_FOUR_GATE_SHA='2a5422d1097c2e6578ff3ba4b2769a64918378bd120c35a305c7ab90c8e990b9'
ACTUAL_FOUR_SOURCE_SHA='4d511441316523a833009d1e354e750d5cb60432fea4a39f8cec9771eeef1c1e'
def load_pinned(path,expected,name):
 require(sha(path)==expected,'Pinned helper/source drift '+str(path))
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def verify_release_prerequisite(cfg,authority,resource_configuration_utf8=None,resource_snapshot=None):
 """Use actual Main capture plus separate actual Main operational approval.

 This performs no raw archive replay and no authority call, and never grants.
 Historical replay may supply the INTENT-captured resource config.
 """
 resource_text=P(cfg['resource_configuration_path']).read_text()if resource_configuration_utf8 is None else resource_configuration_utf8
 require(utfsha(resource_text)==cfg['resource_configuration_sha256'],'Broad captured resource config SHA')
 rcfg=json.loads(resource_text)
 require(cfg['memory_configuration_path']==cfg['resource_configuration_path'],'Typed memory must refer to new broad resource')
 lib=load_pinned(rcfg['source_paths']['library'],rcfg['qualified_sources']['library'],'broad_release_actual_resource_library')
 require(lib.ID=='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1','Wrong broad resource generation')
 if resource_snapshot is None:evidence=lib.validate_broad_approval(rcfg,authority)
 else:
  require(resource_snapshot['config']==rcfg,'Historical resource snapshot generation differs')
  evidence=lib.validate_broad_approval(rcfg,authority,resource_snapshot['broad_approval_utf8'],resource_snapshot['broad_gate_utf8'],resource_snapshot['broad_source_artifacts_utf8'],resource_snapshot['scope_contract_utf8'])
 app=json.loads(evidence['certificate_utf8']);gate=json.loads(evidence['gate_utf8'])
 gr=app['actual_gate']
 require(gr['path']==cfg['canary4_prerequisite_path']and gr['sha256']==cfg['canary4_prerequisite_sha256']==ACTUAL_FOUR_GATE_SHA,'Actual Main mixed-four prerequisite identity')
 require(gr['source_sha256']==gate['gate_source_sha256']==ACTUAL_FOUR_SOURCE_SHA and sha(gr['source_path'])==ACTUAL_FOUR_SOURCE_SHA,'Actual mixed-four replay source bytes')
 require(utfsha(evidence['gate_utf8'])==ACTUAL_FOUR_GATE_SHA and gate['actual_owner_pid']==1498278 and gate['actual_owner_start_ticks']==977758783,'Actual same-owner gate generation')
 for row in gate['rows']:
  require(authority['consumed'][row['cohort']]['uuid']==row['uuid'],'Actual four consumed UUID changed')
  result=json.loads(evidence['source_artifacts_utf8'][row['cohort']+'.RESULT'])
  require(result['proof']['performance_accepted']is True and result['proof']['uuid']==row['uuid'],'Four original performance proof identity')
  require({k:result['proof'][k]for k in ['CTA','instructions','kernel_count']}==row['counts'],'Actual four counts changed')
  require(result['primary_statistics_excluded']is True and result['validated_union_authorized']is False,'Engineering four statistics isolation changed')
 return dict(status='PASS_ACTUAL_MAIN_MIXED_FOUR_AND_EXPLICIT_BROAD_SCOPE',production_release_eligible=not cfg['qualification_only']and not authority.get('qualification_only',False),prerequisite_sha256=ACTUAL_FOUR_GATE_SHA,broad_approval_sha256=rcfg['broad_approval_sha256'],scope_contract_sha256=rcfg['scope_contract_sha256'])
