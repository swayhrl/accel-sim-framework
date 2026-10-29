"""Observation-only strict AND the existing original/CPU2/IO proof. No install."""
import copy,hashlib,importlib.util,json,pathlib,re
P=pathlib.Path
ID='DTC_STRACE_FUTURE_ENTRY_V3'
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
 expected_pins=cfg['expected_pins'],QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],future_primary_policy=cfg['future_primary_policy'],future_ir_policy=cfg['future_ir_policy'],policy_source_sha256=cfg['policy_source_sha256'],canary4_prerequisite_sha256=cfg['canary4_prerequisite_sha256'])
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
 expected_status='PASS_BPF_REQUIRED_ACTIVE'if mode=='BPF_REQUIRED'else'PASS_DEFAULT_CONTROL_NO_BPF'
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
 verify_release_prerequisite(cfg,authority)
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
 memory=json.loads(snap['memory_configuration_utf8']);captured_memory=read(out/'CPU_SPARE_MEMORY_ADMISSION_SNAPSHOT.json')['config']
 require(c in memory['allowed_cohorts']and set(memory['allowed_cohorts'])<=set(captured_memory['allowed_cohorts']),'Official memory scope capture mismatch')
 require({k:v for k,v in memory.items()if k!='allowed_cohorts'}=={k:v for k,v in captured_memory.items()if k!='allowed_cohorts'},'Memory generation changed outside official allow append')
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
 require(base_proof.get('additional_cpu_spare_memory_admission_strict',{}).get('status')=='PASS_CPU_SPARE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE','CPU2 strict mandatory')
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
 result=dict(schema=ID,status='PASS_STRACE_V3_AND_ORIGINAL_CPU2_IO',cohort=c,uuid=v['intent']['uuid'],mode=v['binding']['mode'],
  snapshot_sha256=sha(out/SNAP),activation_sha256=sha(out/ACT),fork_plan_sha256=sha(out/FORK),extra_strict_source_sha256=sha(__file__),
  scientific_identity=v['scientific_identity'],activation=v['verdict'],original_strict_required=True,CPU2_strict_required=True,IO_strict_required=True,
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
 keys=[SNAP,ACT,FORK,SIDE,'NATIVE_LAUNCH.json','NATIVE_SIMULATOR_PID_AND_MAPS.json','NATIVE_EXIT.json','L2_STRICT.json']
 proofs=[]
 for name in keys:
  entry=entries.get(name);require(entry is not None and entry['type']=='file','Missing archived key '+name)
  require(not(out/name).is_symlink()and not(restore/name).is_symlink(),'Unexpected key symlink')
  require(sha(out/name)==entry['sha256']==sha(restore/name)and(out/name).stat().st_size==entry['size']==(restore/name).stat().st_size,'Key archive/restore bytes changed '+name)
  proofs.append(dict(path=name,sha256=entry['sha256'],bytes=entry['size']))
 require(archive['independently_verified_entries']==len(manifest['entries']),'Original full archive/native verification incomplete')
 return dict(schema=ID,status='PASS_NEW_OBSERVATION_ARCHIVED_AND_NATIVE_RESTORED',cohort=c,uuid=intent['uuid'],manifest_sha256=receipt['manifest_sha256'],
  archive_sha256=receipt['archive_sha256'],native_restore=str(restore),required_files=proofs,original_full_archive_verifier_required=True)

# Included verbatim into new bpf_extra_strict.py; never changes V2 sources.
GATE_SCHEMA='DTC_BPF_FUTURE_V3_REAL_CANARY4_GATE_V1'
V2_EXTRA=P('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/strace_bpf_future_entry_v2/bpf_extra_strict.py')
V2_EXTRA_SHA='cbbddba1fe954a1e7dd411c89f9feff2480d5314781204b75fc8364159586711'
V2_BRIDGE_SHA='5c4ded4df0dee860015208b0af46d967e91a0bb2a2fc98e6830ed7b54db6ae9f'
CPU_OWNER=P('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/cpu_spare_memory_v2/cpu_owner.py')
CPU_OWNER_SHA='4945156fe11db69f75a6f1dc39e08a0f5c7b28ef43244525f570bebbf33cf080'
OLD_STRICT_SHA='f889b248adca6f466f8ee19fb2dc17986e355196132c716b7b6fc50ced333b59'
OLD_OUTBOX_SHA='d4b58b362a39c9d198a40e5c252f6eb07ba780e4707ffd79f6724569e349c4a5'
def load_pinned(path,expected,name):
 require(sha(path)==expected,'Pinned helper/source drift '+str(path))
 sp=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module);return module
def _require_existing_sidecars(result,out):
 proof=result['proof']
 for key in ['additional_cpu_spare_memory_admission_strict','additional_strace_bpf_observation_strict']:
  side=proof[key];path=P(side['sidecar_path']);require(path.parent==out and path.exists()and sha(path)==side['sidecar_sha256'],'Readonly prerequisite sidecar '+key)
 io=proof.get('additional_shared_json_io_strict')or proof.get('additional_future_memory_io_strict')
 require(io is not None and P(io['sidecar_path']).parent==out and sha(io['sidecar_path'])==io['sidecar_sha256'],'Readonly prerequisite IO sidecar')
def replay_v2_canary(cohort,authority):
 """Actual standalone readonly replay of the same old physics+CPU2+IO+V2 chain.

 Existing sidecars are mandatory before terminal helpers execute, so replay
 cannot mint missing strict evidence. No authority writer may call this.
 """
 require(sha(MAIN_EXCLUSION_PATH)==MAIN_EXCLUSION_SHA,'Main exact4 contract drift')
 exclusion=read(MAIN_EXCLUSION_PATH);require(cohort in exclusion['scope_cohorts'],'Not exact engineering4')
 rp=PRODUCTION_ROOT/'analysis'/(cohort+'.RESULT.json');value=read(rp)
 require(value['state']=='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'and value['scientific_role']=='ENGINEERING_OBSERVATION_CANARY'and value['primary_statistics_excluded']is True and value['validated_union_authorized']is False,'Not a real accepted engineering RESULT')
 require(read(PRODUCTION_ROOT/'analysis/engineering_results'/(cohort+'.RESULT.json'))==value,'Engineering mirror changed')
 intent=read(PRODUCTION_ROOT/'control/qualification_ledger'/(cohort+'.INTENT.json'));out=P(intent['output'])
 _require_existing_sidecars(value,out)
 original=load_pinned(PRODUCTION_ROOT/'tools/l2_strict.py',OLD_STRICT_SHA,'v3_gate_original_strict')
 base=original.terminal(cohort)
 owner=load_pinned(CPU_OWNER,CPU_OWNER_SHA,'v3_gate_historical_CPU2_owner')
 historical=owner.historical_extra(intent,out)
 proof=historical.terminal(cohort,base)
 v2=load_pinned(V2_EXTRA,V2_EXTRA_SHA,'v3_gate_V2_strict')
 contract=v2.normalize_contract(exclusion,PRODUCTION_ROOT,MAIN_EXCLUSION_SHA,False)
 observed=v2.terminal(cohort,proof,PRODUCTION_ROOT,contract,authority,readonly=True)
 require(observed==value['proof'],'Readonly original/CPU2/IO/V2 strict changed')
 outbox=load_pinned(PRODUCTION_ROOT/'tools/l2_outbox.py',OLD_OUTBOX_SHA,'v3_gate_original_outbox')
 archive=outbox.verify(cohort)
 require(archive=={k:v for k,v in value['archive'].items()if k!='additional_strace_bpf_archive_verification'},'Readonly original full archive changed')
 require(v2.verify_archive(cohort,archive,PRODUCTION_ROOT,contract)==value['archive']['additional_strace_bpf_archive_verification'],'Readonly observation/native restore changed')
 return value
def _gate_row(cohort,value):
 proof=value['proof'];extra=proof[KEY]
 return dict(cohort=cohort,RESULT_sha256=sha(PRODUCTION_ROOT/'analysis'/(cohort+'.RESULT.json')),
  uuid=proof['uuid'],cycles=proof['cycles'],mode=extra['mode'],
  counts={k:proof[k]for k in ['CTA','instructions','kernel_count']},
  archive_manifest_sha256=value['archive']['additional_strace_bpf_archive_verification']['manifest_sha256'],
  archive_sha256=value['archive']['additional_strace_bpf_archive_verification']['archive_sha256'])
def capture_release_prerequisite(frame,main,path):
 """Explicit same-Main-owner receipt writer, not invoked on import/installation.

 It requires the actual current V2 bridge, never an injected fake callback.
 Actual model experiments and grant writes are not performed by this method.
 """
 import os,threading,datetime
 require(threading.current_thread()is threading.main_thread()and os.getpid()==1498278,'Actual Main owner required')
 require(int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783,'Main PID generation changed')
 marker=main.DTC_STRACE_BPF_PRIVATE_CONSUMER_V2
 require(marker['frame']is frame and marker['consumer']is frame.f_locals['consumer']and marker['consumer'].safe_finish is marker['wrapper'],'Actual V2 bridge route required')
 require(marker['source_sha256']==V2_BRIDGE_SHA and not marker['cfg']['qualification_only'],'Production V2 generation only')
 require(sha(marker['bridge']['readonly_replay'].__code__.co_filename)==V2_BRIDGE_SHA,'V2 replay source drift')
 engine=frame.f_locals['engine'];engine.assert_parent_lease()
 q=engine.registered()[2];rows=[]
 for cohort in sorted(read(MAIN_EXCLUSION_PATH)['scope_cohorts']):
  actual=marker['bridge']['readonly_replay'](cohort)
  require(actual==replay_v2_canary(cohort,q),'Actual bridge and standalone readonly replay differ')
  rows.append(_gate_row(cohort,actual))
 result=dict(schema=GATE_SCHEMA,kind='ACTUAL_SAME_OWNER_V2_FULL_READONLY_REPLAY',qualification_only=False,
  capture_source_sha256=sha(__file__),V2_bridge_sha256=V2_BRIDGE_SHA,V2_extra_sha256=V2_EXTRA_SHA,
  exclusion_contract_sha256=MAIN_EXCLUSION_SHA,canaries=rows,
  UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_owner_pid=os.getpid(),actual_owner_start_ticks=977758783)
 path=P(path);require(not path.exists(),'Prerequisite receipt immutable; do not overwrite')
 producer_path=marker['cfg']['source_paths']['producer'];producer=load_pinned(producer_path,marker['cfg']['qualified_sources']['producer'],'v3_gate_atomic_writer')
 producer.atomic_exclusive(path,result)
 return dict(path=str(path),sha256=sha(path),receipt=result)
def verify_release_prerequisite(cfg,authority):
 """Full replay before any V3 selected INTENT; never call under authority EX."""
 path=P(cfg['canary4_prerequisite_path']);require(sha(path)==cfg['canary4_prerequisite_sha256'],'Canary4 prerequisite SHA')
 gate=read(path);require(gate['schema']==GATE_SCHEMA,'Wrong prerequisite generation')
 qualification=cfg.get('qualification_only')is True and authority.get('qualification_only')is True and P(cfg['root']).resolve()!=PRODUCTION_ROOT.resolve()
 if qualification:
  require(gate['kind']=='CPU_ONLY_PREREQUISITE_STANDIN_NOT_ACTUAL_CANARY'and gate['qualification_only']is True,'Explicit CPU-only quorum fixture required')
  return dict(status='CPU_ONLY_GATE_QUALIFIED_NOT_PRODUCTION_RELEASE',production_release_eligible=False,prerequisite_sha256=sha(path))
 require(P(cfg['root'])==PRODUCTION_ROOT and cfg.get('qualification_only')is False and gate['qualification_only']is False,'CPU gate cannot release production')
 require(gate['kind']=='ACTUAL_SAME_OWNER_V2_FULL_READONLY_REPLAY'and gate['capture_source_sha256']==sha(__file__),'Real full-replay source-bound prerequisite required')
 require(gate['V2_bridge_sha256']==V2_BRIDGE_SHA and gate['V2_extra_sha256']==V2_EXTRA_SHA and gate['exclusion_contract_sha256']==MAIN_EXCLUSION_SHA,'Prerequisite old-source chain')
 require(gate['actual_owner_pid']==1498278 and gate['actual_owner_start_ticks']==977758783,'Prerequisite owner generation')
 rows={r['cohort']:r for r in gate['canaries']};required=set(read(MAIN_EXCLUSION_PATH)['scope_cohorts'])
 require(len(rows)==len(gate['canaries'])==4 and set(rows)==required,'Exact four actual accepted prerequisites')
 for cohort in sorted(required):require(rows[cohort]==_gate_row(cohort,replay_v2_canary(cohort,authority)),'Real prerequisite replay changed '+cohort)
 return dict(status='ACTUAL_CANARY4_GATE_VERIFIED',production_release_eligible=True,prerequisite_sha256=sha(path),actual_canary_cohorts=sorted(required))
