"""Observation-only strict AND the existing original/CPU2/IO proof. No install."""
import copy,hashlib,importlib.util,json,pathlib,re
P=pathlib.Path
ID='DTC_STRACE_SHARED_CPU_OBSERVATION_V1'
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
FIELD='additional_strace_bpf_observation_binding'
KEY='additional_strace_bpf_observation_strict'
ROLES=('entry','frontend','producer','extra_strict','consumer')
SNAP='STRACE_BPF_OBSERVATION_SNAPSHOT.json';ACT='STRACE_BPF_ACTIVATION.json';FORK='STRACE_BPF_FORK_PLAN.json';SIDE='STRACE_BPF_EXTRA_STRICT.json'
PRODUCTION_ROOT=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
SCIENCE_KEYS=('binary_sha256','cell','configs','core_commit','correctness_validation_only','downstream_profile','execution_mnt_namespace','expected','expected_options','framework_commit','input_binding_path','input_binding_sha256','input_digest','native_simulator_argv','original_environment','performance_scope','profile','project','request','runtime_files','schema','source_kind','source_worktrees','suite','workload','program')
DESIGN_PATH=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/coordinator/CPU_SHARED_TIMESLICE_V1/DESIGN_CONTRACT.json')
DESIGN_SHA='02e9050b76f695c21d72a73bff636a415f8fe45c6a7f543874108241ae22905d'
RESOURCE_KEY='additional_cpu_shared_timeslice_strict'
RESOURCE_STATUS='PASS_CPU_SHARED_TIMESLICE_IO_AND_ORIGINAL_PERFORMANCE'
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
def normalize_contract(document,root,source_sha256,qualification_only=False,cfg=None):
 require(source_sha256==MAIN_EXCLUSION_SHA,'Unreviewed exclusion contract generation')
 require(sha(MAIN_EXCLUSION_PATH)==MAIN_EXCLUSION_SHA and read(MAIN_EXCLUSION_PATH)==document,'Actual immutable Main contract mismatch')
 require(document['schema']=='DTC_ENGINEERING_OBSERVATION_EXCLUSION_CONTRACT_V1'and document['status']=='EXCLUSION_RULES_ONLY_NOT_ADMISSION_AUTHORITY','Wrong Main exclusion contract')
 require(tuple(document['science_keys'])==SCIENCE_KEYS and len(document['scope_cohorts'])==4,'Main frozen science scope')
 for c,r in document['scope_cohorts'].items():
  require(c==r['cohort']and r['scientific_role']=='ENGINEERING_OBSERVATION_CANARY'and r['primary_statistics_excluded']is True and r['validated_union_authorized']is False,'Main explicit engineer exclusion')
 require(sha(DESIGN_PATH)==DESIGN_SHA,'Main shared design changed')
 require(cfg is not None,'Stage2 captured config required')
 approval=validate_stage2_approval(cfg)
 allowed=approval['allowed_cohorts']
 require(set(allowed)==set(document['scope_cohorts'])and len(allowed)==4,'Only original four engineering identities')
 return dict(root=str(root),qualification_only=qualification_only,cohorts={c:copy.deepcopy(document['scope_cohorts'][c])for c in allowed},science_keys=document['science_keys'],
  primary_statistics_excluded=True,validated_union_authorized=False,original_primary_SCOPE_sha256=document['original_primary_SCOPE_sha256'],
  formal_exclusion_contract_sha256=source_sha256,exclusion_rules_are_not_admission_authority=True)
def verify_science_rule(spec,rule,contract):
 require(spec['host_cpu']is None,'Canonical CPU must remain None; actual CPU belongs only to dispatch/resolved spec')
 require(tuple(contract['science_keys'])==SCIENCE_KEYS,'Scientific projection contract changed')
 require(science_sha(spec)==rule['science_projection_sha256'],'Frozen scientific fields changed')
 require(spec['cohort']in contract['cohorts']and spec.get('scientific_role')==rule['scientific_role']=='ENGINEERING_OBSERVATION_CANARY','Explicit engineer identity')
 require(rule['primary_statistics_excluded']is True and rule['validated_union_authorized']is False,'Missing engineer exclusion')
 lineage=spec['engineering_observation_canary_lineage']
 for k in ['mode','pair_id','science_projection_sha256','reference_cohort','reference_cycles','reference_result_sha256']:
  require(lineage[k]==rule[k],'Engineering lineage changed '+k)
 require(lineage['primary_statistics_excluded']is True and lineage['validated_union_authorized']is False,'Lineage exclusion missing')
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
 expected_pins=cfg['expected_pins'],QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],modes=cfg['modes'],future_primary_policy=cfg['future_primary_policy'],resource_configuration_sha256=cfg['resource_configuration_sha256'],design_contract_sha256=DESIGN_SHA,scope_extension_approval_sha256=cfg['scope_extension_approval_sha256'])
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
 expected_status='PASS_CPU_SHARED_BPF_REQUIRED_ACTIVE'if mode=='BPF_REQUIRED'else'PASS_CPU_SHARED_DEFAULT_CONTROL_NO_BPF'
 require(activation['verdict']['status']==expected_status,'Producer did not prove requested mode')
 return dict(status=expected_status,model_pid=model['pid'],model_start_ticks=model['start_ticks'],tracer_pid=tracer['pid'],tracer_start_ticks=tracer['start_ticks'],
  baseline_Seccomp=0,baseline_filters=0,model_Seccomp=expected[0],model_filters=expected[1],fallback_accepted=False)
def verified_files(c,root,contract,authority):
 root=P(root);rule=contract['cohorts'][c];ip=root/'control/qualification_ledger'/(c+'.INTENT.json');intent=read(ip);out=P(intent['output'])
 require(contract['formal_exclusion_contract_sha256']==MAIN_EXCLUSION_SHA and sha(root/'control/SCOPE.json')==contract['original_primary_SCOPE_sha256'],'Frozen primary scope/contract drift')
 require(sha(MAIN_EXCLUSION_PATH)==MAIN_EXCLUSION_SHA and all(read(MAIN_EXCLUSION_PATH)['scope_cohorts'][key]==value for key,value in contract['cohorts'].items()),'Main scope rules changed')
 require(out==root/'DTC/run/results'/intent['uuid'],'Wrong output namespace')
 require(root==PRODUCTION_ROOT or(contract.get('qualification_only')is True and authority.get('qualification_only')is True),'Nonproduction root without private qualification')
 docs=[intent,read(out/'NATIVE_LAUNCH.json'),read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')];binding=intent[FIELD]
 require(all(x[FIELD]==binding for x in docs),'Missing or unequal three observation bindings')
 require(binding['schema']==binding['overlay_id']==ID and binding['request']==REQ and binding['cohort']==c and binding['uuid']==intent['uuid'],'Observation identity')
 require(sha(out/SNAP)==binding['snapshot_sha256'],'Snapshot SHA mismatch');snap=read(out/SNAP);cfg=snap['config']
 require(snap['schema']==cfg['schema']==cfg['overlay_id']==ID and cfg['status']=='ACTIVE_FUTURE_ONLY','Snapshot configuration schema/status')
 require(cfg['root']==str(root)and cfg['request']==REQ and objsha(cfg)==binding['config_sha256'],'Configuration identity')
 require(cfg['future_primary_policy']=='NONE','Shared exact1 does not authorize primary rollout')
 approval=validate_stage2_approval(cfg)
 require(cfg['modes']==approval['modes']and c in cfg['modes'],'Only Stage2 original four requested modes')
 require(utfsha(snap['scope_extension_approval_utf8'])==cfg['scope_extension_approval_sha256'],'Stage2 approval snapshot')
 require(not cfg['qualification_only']or authority.get('qualification_only')is True,'CPU fixture cannot release production')
 require(cfg['modes'].get(c)==snap['mode']==binding['mode']==rule['mode'],'Mode contract drift')
 require(snap['overlay_record']['status']=='ACTIVE'and all(snap['overlay_record'].get(k)==v for k,v in record(cfg).items()),'Historical overlay record mismatch')
 require('additional_cpu_shared_timeslice_binding'in intent and 'additional_cpu_spare_memory_admission_binding'not in intent,'Actual shared generation required')
 resource=read(out/'CPU_SHARED_TIMESLICE_SNAPSHOT.json');require(resource['schema']=='CPU_SHARED_TIMESLICE_FUTURE_MEMORY_095_V1','Shared resource snapshot schema')
 require(resource['config']==json.loads(snap['resource_configuration_utf8'])and utfsha(snap['resource_configuration_utf8'])==cfg['resource_configuration_sha256'],'Shared resource/observer configuration binding')
 require(utfsha(snap['design_contract_utf8'])==DESIGN_SHA,'Shared observer design snapshot')
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
 verify_science_rule(spec,rule,contract)
 for name in ['SCOPE.json','MATRIX_CURRENT.json']:
  require(not any(p['cohort']==c for p in read(root/'control'/name)['points']),'Canary leaked into primary '+name)
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
 return dict(intent=intent,out=out,docs=docs,binding=binding,snapshot=snap,verdict=verdict,scientific_identity=si)
def terminal(c,base_proof,root,contract,authority,readonly=False):
 require(base_proof.get('performance_accepted')is True,'Original performance strict mandatory')
 require('additional_cpu_spare_memory_admission_strict'not in base_proof,'Cannot claim old CPU2 PASS for shared CPU')
 require(base_proof.get(RESOURCE_KEY,{}).get('status')==RESOURCE_STATUS,'Actual SharedCPU resource strict mandatory')
 require('additional_shared_json_io_strict'in base_proof or'additional_future_memory_io_strict'in base_proof,'IO strict mandatory')
 v=verified_files(c,root,contract,authority);out=v['out']
 for k in ['cohort','uuid','input_digest','core_commit','framework_commit','binary_sha256']:
  expected=c if k=='cohort'else v['intent']['uuid']if k=='uuid'else v['scientific_identity'][k]
  require(base_proof[k]==expected,'Original strict/new observation identity mismatch '+k)
 shared=base_proof[RESOURCE_KEY];require(P(shared['sidecar_path'])==out/'CPU_SHARED_TIMESLICE_EXTRA_STRICT.json'and sha(shared['sidecar_path'])==shared['sidecar_sha256'],'Shared strict sidecar binding')
 done=read(P(root)/'control/qualification_ledger'/(c+'.DONE.json'))
 require(done==read(out/'NATIVE_EXIT.json')==authority['consumed'][c]['execution_receipt'],'Original natural execution closure')
 require(done['uuid']==v['intent']['uuid']and done['stop_reason']is None and done['launcher_wait_returncode']==0,'Not a natural successful canary')
 rule=contract['cohorts'][c];reference_path=P(root)/'analysis'/(rule['reference_cohort']+'.RESULT.json')
 require(sha(reference_path)==rule['reference_result_sha256'],'Accepted reference identity changed')
 reference=read(reference_path);rp=reference['proof']
 require(rp['performance_accepted']is True and bool(reference['archive'])and reference['cycles']==rp['cycles']==rule['reference_cycles'],'Reference is not accepted performance')
 for k in ['input_digest','core_commit','framework_commit','binary_sha256','cell','profile','effective_options','CTA','instructions','kernel_count','cycles']:
  require(base_proof[k]==rp[k],'Engineering same-physics comparison differs '+k)
 result=dict(schema=ID,status='PASS_CPU_SHARED_OBSERVATION_AND_ORIGINAL_IO',cohort=c,uuid=v['intent']['uuid'],mode=v['binding']['mode'],
  snapshot_sha256=sha(out/SNAP),activation_sha256=sha(out/ACT),fork_plan_sha256=sha(out/FORK),extra_strict_source_sha256=sha(__file__),
  scientific_identity=v['scientific_identity'],activation=v['verdict'],original_strict_required=True,CPU_shared_strict_required=True,old_CPU2_PASS_claimed=False,IO_strict_required=True,
  exclusion_contract_sha256=MAIN_EXCLUSION_SHA,
  engineering_reference=dict(cohort=rule['reference_cohort'],result_sha256=rule['reference_result_sha256'],cycles=rule['reference_cycles'],same_physics_counts_and_cycles=True),
  primary_statistics_excluded=True,validated_union_authorized=False)
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

STAGE2_RESOURCE_EXTRA_SHA='a6c79668e8520fefc92720476fb146af85c051a19b1792ec80aa919e8e3417ea'
# Included in the separate Stage2 observation source. No work on import.
APPROVAL_PATH=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/coordinator/CPU_SHARED_ENGINEERING4_SCOPE_EXTENSION_V1/SCOPE_EXTENSION_APPROVAL.json')
APPROVAL_SHA='30bd502f7fe6653907b3e835c2b7aee78c780c65ecde758df473942158d1b895'
OLD_SHARED_RESOURCE_SHA='b89910928efdd77f4686700362913fd241e12ab2256e517f1887fc8986b8fa47'
OLD_SHARED_OBSERVATION_SHA='1766aefbaf4710b876e0ed97a46bcfb91434a9f333e0a985b01864f592d1437b'
OLD_V2_OBSERVATION_SHA='cbbddba1fe954a1e7dd411c89f9feff2480d5314781204b75fc8364159586711'
CPU2_OWNER_SHA='4945156fe11db69f75a6f1dc39e08a0f5c7b28ef43244525f570bebbf33cf080'
ORIGINAL_STRICT_SHA='f889b248adca6f466f8ee19fb2dc17986e355196132c716b7b6fc50ced333b59'
ORIGINAL_OUTBOX_SHA='d4b58b362a39c9d198a40e5c252f6eb07ba780e4707ffd79f6724569e349c4a5'
def pinned_load(path,pin,name):
 require(sha(path)==pin,'Captured source bytes changed '+str(path))
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def validate_stage2_approval(cfg):
 require(cfg['scope_extension_approval_sha256']==APPROVAL_SHA and sha(cfg['scope_extension_approval_path'])==APPROVAL_SHA,'Actual Stage2 approval SHA')
 approval=read(cfg['scope_extension_approval_path'])
 require(approval['schema']=='CPU_SHARED_ACTUAL_CANARY_ENGINEERING4_SCOPE_APPROVAL_V1'and approval['status']=='PASS_CPU_SHARED_NATURAL_STRICT_ARCHIVE_NATIVE_RESTORE','Wrong actual approval')
 require(not approval.get('qualification_only',False)and approval['Main_scope_extension_approved']is True and approval['max_shared_running']==1,'Not an actual finite scope approval')
 require(approval['production_release_scope']=='FINITE_ORIGINAL_FOUR_ENGINEERING_QUALIFICATION_ONLY'and approval['production_primary_rollout_eligible']is False and approval['IR_rollout_eligible']is False and approval['validated_union_authorized']is False,'No broad or union approval')
 artifacts={}
 for key,reference in approval['source_artifacts'].items():
  require(sha(reference['path'])==reference['sha256'],'Actual first source artifact '+key);artifacts[key]=read(reference['path'])
 result,done,full=artifacts['RESULT'],artifacts['DONE'],artifacts['FULL_REPLAY']
 require(result['state']=='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'and result['proof']['performance_accepted']is True,'First actual RESULT not accepted')
 require(result['uuid']==done['uuid']==full['uuid']==approval['uuid']and result['cohort']==done['cohort']==full['cohort']==approval['cohort'],'Actual first UUID/cohort mismatch')
 require(done['stop_reason']is None and done['launcher_wait_returncode']==0,'Actual first not natural')
 require(result['cycles']==result['proof']['cycles']==full['cycles']==approval['cycles']==8551,'Actual first cycles changed')
 for key in ['CTA','instructions','kernel_count']:require(result['proof'][key]==full['counts'][key]==approval['counts'][key],'Actual first counts changed')
 require(full['status']==approval['status']and full['RESULT_sha256']==approval['source_artifacts']['RESULT']['sha256']==approval['first_RESULT_sha256'],'Full actual replay source mismatch')
 archive=result['archive']['receipt'];require(archive['archive_sha256']==approval['first_actual_archive_sha256']and archive['manifest_sha256']==approval['first_actual_archive_manifest_sha256'],'Actual first archive mismatch')
 require(sha(MAIN_EXCLUSION_PATH)==MAIN_EXCLUSION_SHA and set(approval['allowed_cohorts'])==set(read(MAIN_EXCLUSION_PATH)['scope_cohorts']),'Only original engineering four')
 require(approval['modes']=={c:r['mode']for c,r in read(MAIN_EXCLUSION_PATH)['scope_cohorts'].items()},'Original four modes changed')
 return approval
def _historical_contract(extra,cfg,root):
 document=read(MAIN_EXCLUSION_PATH)
 if sha(extra.__file__)==sha(__file__):return extra.normalize_contract(document,root,MAIN_EXCLUSION_SHA,cfg['qualification_only'],cfg=cfg)
 return extra.normalize_contract(document,root,MAIN_EXCLUSION_SHA,cfg['qualification_only'])
def replay_closed_generation(c,authority,root=PRODUCTION_ROOT):
 """Real readonly full-chain replay; choose by immutable INTENT generation.

 No simulator/model starts; CPU fixture roots are not accepted as a real gate.
 """
 root=P(root);require(root==PRODUCTION_ROOT and not authority.get('qualification_only',False),'Real gate needs actual production root/authority')
 require(c in read(MAIN_EXCLUSION_PATH)['scope_cohorts'],'Only four engineering identities')
 rp=root/'analysis'/(c+'.RESULT.json');value=read(rp);require(value['state']=='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'and value['proof']['performance_accepted']is True,'Missing actual accepted performance')
 require(value['primary_statistics_excluded']is True and value['validated_union_authorized']is False and read(root/'analysis/engineering_results'/(c+'.RESULT.json'))==value,'Actual engineering exclusion/mirror')
 ip=root/'control/qualification_ledger'/(c+'.INTENT.json');intent=read(ip);out=P(intent['output']);require(sha(ip)==authority['consumed'][c]['intent_sha256']and intent['uuid']==authority['consumed'][c]['uuid']==value['uuid'],'Actual consumed identity')
 for key in ['additional_cpu_shared_timeslice_strict','additional_cpu_spare_memory_admission_strict','additional_shared_json_io_strict',KEY]:
  if key in value['proof']:
   side=value['proof'][key];require(P(side['sidecar_path']).parent==out and sha(side['sidecar_path'])==side['sidecar_sha256'],'Existing readonly sidecar '+key)
 base=pinned_load(root/'tools/l2_strict.py',ORIGINAL_STRICT_SHA,'mixed_gate_original_physics').terminal(c)
 shared='additional_cpu_shared_timeslice_binding'in intent
 if shared:
  require('additional_cpu_spare_memory_admission_binding'not in intent,'Mixed resource bindings')
  b=intent['additional_cpu_shared_timeslice_binding'];rs=out/'CPU_SHARED_TIMESLICE_SNAPSHOT.json';require(sha(rs)==b['snapshot_sha256'],'Resource snapshot SHA');rcfg=read(rs)['config'];pin=rcfg['qualified_sources']['extra_strict']
  require(pin in [OLD_SHARED_RESOURCE_SHA,STAGE2_RESOURCE_EXTRA_SHA],'Unreviewed Shared source generation')
  resource=pinned_load(rcfg['source_paths']['extra_strict'],pin,'mixed_gate_captured_Shared_extra');proof=resource.terminal(c,base,root=root,authority=authority,readonly=True)
 else:
  require('additional_cpu_spare_memory_admission_binding'in intent,'Only captured Shared or old CPU2 accepted')
  owner=pinned_load(root/'control/operational_amendments/cpu_spare_memory_v2/cpu_owner.py',CPU2_OWNER_SHA,'mixed_gate_old_CPU2_owner');resource=owner.historical_extra(intent,out);proof=resource.terminal(c,base)
 obs_binding=intent[FIELD];obs_path=out/SNAP;require(sha(obs_path)==obs_binding['snapshot_sha256'],'Observation snapshot SHA');ocfg=read(obs_path)['config'];pin=ocfg['qualified_sources']['extra_strict']
 require(pin in [OLD_V2_OBSERVATION_SHA,OLD_SHARED_OBSERVATION_SHA,sha(__file__)],'Unreviewed observation source generation')
 require((pin==OLD_V2_OBSERVATION_SHA)==(not shared),'Observation/resource generation family mismatch')
 observer=pinned_load(ocfg['source_paths']['extra_strict'],pin,'mixed_gate_captured_observation');contract=_historical_contract(observer,ocfg,root)
 observed=observer.terminal(c,proof,root,contract,authority,readonly=True);require(observed==value['proof'],'Historical full strict replay changed')
 original=pinned_load(root/'tools/l2_outbox.py',ORIGINAL_OUTBOX_SHA,'mixed_gate_original_full_archive').verify(c)
 require(original=={k:v for k,v in value['archive'].items()if k!='additional_strace_bpf_archive_verification'},'Original full archive/native replay changed')
 archive=observer.verify_archive(c,original,root,contract);require(archive==value['archive']['additional_strace_bpf_archive_verification'],'Captured observation/native restore changed')
 return dict(cohort=c,uuid=value['uuid'],RESULT_sha256=sha(rp),cycles=value['cycles'],counts={k:value['proof'][k]for k in ['CTA','instructions','kernel_count']},resource_source_sha256=sha(resource.__file__),observation_source_sha256=pin,mode=observed[KEY]['mode'],archive_manifest_sha256=archive['manifest_sha256'],archive_sha256=archive['archive_sha256'],actual_full_chain_replayed=True)
def replay_mixed_four_gate(authority,root=PRODUCTION_ROOT):
 """Return HOLD until all four real chains pass; never accepts fake quorum."""
 rows=[];missing=[]
 for c in sorted(read(MAIN_EXCLUSION_PATH)['scope_cohorts']):
  try:rows.append(replay_closed_generation(c,authority,root))
  except Exception as error:missing.append(dict(cohort=c,error=repr(error)))
 if missing:return dict(status='HOLD_REAL_ENGINEERING_FOUR_INCOMPLETE',accepted_real_count=len(rows),rows=rows,missing=missing,four_point_qualified=False,primary_rollout_eligible=False,models_started=0)
 return dict(status='PASS_REAL_MIXED_GENERATION_ENGINEERING_FOUR_FULL_CHAIN',rows=rows,accepted_real_count=4,four_point_qualified=True,primary_rollout_eligible=False,IR_rollout_eligible=False,validated_union_authorized=False,gate_source_sha256=sha(__file__),models_started=0)
def capture_mixed_four_gate(frame,main,path):
 import os,threading,datetime
 require(threading.current_thread()is threading.main_thread()and os.getpid()==1498278,'Actual Main required')
 require(int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783,'Main generation')
 require(frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED is main.DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1['aging'],'Actual existing frame')
 engine=frame.f_locals['engine'];engine.assert_parent_lease();value=replay_mixed_four_gate(engine.registered()[2]);require(value['four_point_qualified'],'All four actual full chains required')
 value.update(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_owner_pid=os.getpid(),actual_owner_start_ticks=977758783)
 # Atomically publish a new independent derived gate, no overwrite/no grants.
 import uuid
 path=P(path);temporary=path.with_name('.'+path.name+'.'+uuid.uuid4().hex)
 try:
  with temporary.open('xb')as f:f.write(js(value));f.flush();os.fsync(f.fileno())
  os.link(temporary,path)
  fd=os.open(path.parent,os.O_RDONLY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if temporary.exists():temporary.unlink()
 return dict(path=str(path),sha256=sha(path),gate=value)
