#!/usr/bin/env python3
"""Private finite evidence comparator. No IDs, registries, statuses or qualifications are changed."""
import json,hashlib,copy,argparse
CAPSULE_STATUS='OBSERVED_SUPPORTED_HTOD_SOURCE_BYTES_CLOSED_SHA_QUALIFIED'
OBSERVED_SCOPE='OBSERVED_SUPPORTED_HTOD_SOURCE_BYTES_ONLY'
FULL_FLAGS={'INSTR_BEGIN':'0','INSTR_END':'4294967295','C16_EXACT_ROOT_FUNCTION_ONLY':'0','C16_USE_NVBIT_STATIC_INDEX':'0','ENABLE_SPINLOCK_FAST_FORWARD':'0','TERMINATE_UPON_LIMIT':'0'}
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def digest(x):return hashlib.sha256(canon(x).encode()).hexdigest()
def declared_workload(t):
 if not isinstance(t,dict):return {'valid':False,'missing':['task']}
 sources=t.get('source_files',t.get('sources',[]))
 if not sources and t.get('source'):sources=[{'path':t['source'],'sha256':t.get('source_sha256')}]
 env=dict(t.get('env',{}));env.update(t.get('runtime_env',{}))
 d={'suite':t.get('suite'),'source_version':t.get('version',t.get('source_version')),'source_head':t.get('source_head'),'source_archive_sha256':t.get('source_archive_sha256'),'source_tree_sha256':t.get('source_tree_sha256'),'program':t.get('program'),'implementation_variant':t.get('variant'),'source_files':sources,'binary_sha256':t.get('binary_sha256'),'argv':t.get('argv'),'declared_working_directory':t.get('cwd',t.get('sample_path')),'working_directory_policy':t.get('cwd_policy','ABSENT private attempt'),'runtime_overlay':t.get('runtime_links',[]),'declared_inputs':t.get('input_files',t.get('input_identity')),'controlled_environment':env,'generated_input_rule':t.get('input_identity') if not isinstance(t.get('input_identity'),list) else None,'reference_output':t.get('golden_output'),'reference_checker':t.get('correctness',{}).get('postcheck_command')}
 missing=[k for k in ['suite','source_version','program','implementation_variant','binary_sha256','argv'] if not d.get(k)]
 if not sources or any(not isinstance(s,dict) or not s.get('sha256') for s in sources):missing.append('source_files_sha')
 return {'valid':not missing,'missing':missing,'projection':d}
def closure(s):
 errors=[];commit=s.get('commit');manifest=s.get('manifest')
 if not isinstance(commit,dict) or not isinstance(manifest,dict):return False,['missing_commit_or_manifest']
 # Raw manifest bytes are bound outside this pure comparator and supplied without reserialization.
 raw=s.get('manifest_raw_utf8')
 if not isinstance(raw,str):errors.append('missing_original_manifest_bytes')
 elif hashlib.sha256(raw.encode()).hexdigest()!=commit.get('manifest_sha256'):errors.append('commit_manifest_hash_mismatch')
 elif json.loads(raw)!=manifest:errors.append('manifest_parsed_bytes_mismatch')
 if commit.get('status')!='COMMITTED_VERIFIED':errors.append('not_committed')
 members={x['path']:x for x in manifest.get('files',[]) if isinstance(x,dict) and 'path' in x}
 for name,key in [('TASK.json','task'),('ASSET.json','asset'),('EXECUTION.json','execution')]:
  raw=s.get('metadata_raw_utf8',{}).get(name);member=members.get(name)
  if not isinstance(raw,str) or not member:errors.append('missing_bound_'+name);continue
  if hashlib.sha256(raw.encode()).hexdigest()!=member.get('sha256') or len(raw.encode())!=member.get('bytes'):errors.append('member_hash_'+name)
  elif json.loads(raw)!=s.get(key):errors.append('member_parse_'+name)
 return not errors,errors
def capture_profile(s):
 ok,errors=closure(s);a=s.get('asset') or {};e=s.get('execution') or {};m=s.get('manifest') or {};t=s.get('task') or {}
 members={x['path']:x for x in m.get('files',[]) if isinstance(x,dict) and 'path' in x}
 ps=[a.get('producer_sha256'),e.get('tool_sha256'),members.get('tools/producer.so',{}).get('sha256')]
 if any(not p for p in ps):errors.append('missing_actual_producer_triple')
 elif len(set(ps))!=1:errors.append('actual_producer_triple_mismatch')
 if a.get('binary_sha256')!=e.get('binary_sha256') or a.get('binary_sha256')!=t.get('binary_sha256'):errors.append('binary_bind_mismatch')
 flags=e.get('tracer_control_flags');env=e.get('explicit_capture_environment')
 if not isinstance(flags,dict) or not isinstance(env,dict):errors.append('missing_capture_flags_or_environment')
 if not a.get('full_application'):errors.append('missing_full_application_proof')
 for key in ['contract_sha256','validator_sha256','map_manifest_sha256','map_maker_sha256','postprocessor_sha256']:
  if not a.get(key):errors.append('missing_profile_proof_'+key)
 if e.get('exit_code')!=0:errors.append('capture_not_exit_zero')
 full=bool(isinstance(flags,dict) and isinstance(env,dict) and all(flags.get(k)==v for k,v in FULL_FLAGS.items()) and env.get('DYNAMIC_KERNEL_RANGE')=='' and a.get('full_application',{}).get('sampling')=='NONE' and a.get('full_application',{}).get('all_warps_terminate') is True)
 profile={'actual_producer_sha256':ps[0] if len(set(ps))==1 else None,'contract_sha256':a.get('contract_sha256'),'validator_sha256':a.get('validator_sha256'),'map_manifest_sha256':a.get('map_manifest_sha256'),'map_maker_sha256':a.get('map_maker_sha256'),'postprocessor_sha256':a.get('postprocessor_sha256'),'capture_flags':flags,'explicit_capture_environment':env,'full_application':a.get('full_application'),'binary_sha256':a.get('binary_sha256'),'capture_gpu_uuid':a.get('capture_gpu_uuid'),'capture_task_scope':t.get('capture_scope')}
 return {'valid':ok and not errors,'errors':errors,'full_capture_evidence':full,'profile':profile}
def observed_input(s):
 profile=capture_profile(s);errors=list(profile['errors']);cap=s.get('capsule') or {};pair=s.get('pair') or {};m=s.get('manifest') or {}
 members={x['path']:x for x in m.get('files',[]) if isinstance(x,dict) and 'path' in x}
 for name,key in [('INPUT_CAPSULE_QUALIFICATION_V4R2.json','capsule'),('INPUT_SNAPSHOT_PAIR_IDENTITY.json','pair')]:
  raw=s.get('metadata_raw_utf8',{}).get(name);member=members.get(name)
  if not isinstance(raw,str) or not member:errors.append('missing_bound_'+name);continue
  if hashlib.sha256(raw.encode()).hexdigest()!=member.get('sha256') or len(raw.encode())!=member.get('bytes'):errors.append('member_hash_'+name)
  elif json.loads(raw)!=s.get(key):errors.append('member_parse_'+name)
 if cap.get('status')!=CAPSULE_STATUS:errors.append('capsule_not_qualified')
 if pair.get('scope')!=OBSERVED_SCOPE:errors.append('unsupported_observed_input_scope')
 if pair.get('comparison')!='MATCH' or not pair.get('observer_ordered_sha256') or pair.get('observer_ordered_sha256')!=pair.get('trace_ordered_sha256'):errors.append('observer_trace_pair_not_equal')
 if cap.get('ordered_input_identity_sha256')!=pair.get('trace_ordered_sha256'):errors.append('capsule_pair_ordered_identity_mismatch')
 if not pair.get('source_initialization_oracle'):errors.append('missing_source_initialization_oracle')
 if cap.get('binary_sha256')!=s.get('task',{}).get('binary_sha256'):errors.append('capsule_binary_mismatch')
 if cap.get('tool_sha256')!=profile['profile'].get('actual_producer_sha256'):errors.append('capsule_actual_producer_mismatch')
 if not cap.get('lifecycle',{}).get('process_end_observed'):errors.append('capsule_lifecycle_not_closed')
 if cap.get('application_exit_code')!=0:errors.append('capsule_application_not_exit_zero')
 copies=[];total=0
 try:
  for seq,c in sorted(cap.get('copies',{}).items(),key=lambda kv:int(kv[0])):
   member=members.get(c.get('restorable_relative_path'),{})
   if not c.get('sha256') or member.get('sha256')!=c.get('sha256') or member.get('bytes')!=c.get('bytes'):errors.append('capsule_manifest_copy_mismatch_'+seq)
   if c.get('boundary')!='SYNC_API_SUCCESS_SOURCE_BYTES_FROZEN':errors.append('unsupported_copy_boundary_'+seq)
   copies.append({'sequence':seq,'api':c.get('api'),'bytes':c.get('bytes'),'sha256':c.get('sha256')});total+=c.get('bytes',0)
 except (ValueError,TypeError):errors.append('invalid_copy_sequence_or_size')
 if not copies or total!=cap.get('total_bytes'):errors.append('missing_or_partial_copy_set')
 return {'valid':not errors,'errors':errors,'scope':OBSERVED_SCOPE,'copies':copies,'total_bytes':total,'complete_CUDA_initialization':False,'device_readback':False,'fresh_payload_rehash_by_comparator':False}
def compare(left,right):
 dl,dr=declared_workload(left.get('task')),declared_workload(right.get('task'))
 workload_equal=bool(dl['valid'] and dr['valid'] and dl['projection']==dr['projection'])
 pl,pr=capture_profile(left),capture_profile(right);il,ir=observed_input(left),observed_input(right)
 profile_equal=bool(pl['valid'] and pr['valid'] and pl['profile']==pr['profile'])
 input_equal=bool(workload_equal and il['valid'] and ir['valid'] and il['scope']==ir['scope'] and il['copies']==ir['copies'])
 return {'schema':'FINITE_EVIDENCE_COMPARATOR_V1','declared_workload_identity':{'equal':workload_equal,'left':dl,'right':dr},'actual_capture_profile':{'equal':profile_equal,'left':pl,'right':pr},'observed_input_bytes':{'equal_observed_supported_scope_only':input_equal,'left':il,'right':ir},'availability_route':'WORKLOAD_AVAILABILITY_ROUTE_ONLY_NO_HISTORICAL_EQUIVALENCE' if workload_equal and pr['valid'] and pr['full_capture_evidence'] and ir['valid'] else 'MISSING_OR_DIFFERENT_EVIDENCE_NO_ROUTE','historical_equivalence':False,'old_hold_status_change':False,'consumer_acceptance':False,'science_acceptance':False,'device_source_equality':False,'complete_CUDA_initialization':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 with open(a.input) as f:d=json.load(f)
 result=compare(d['left'],d['right'])
 with open(a.output,'x') as f:json.dump(result,f,indent=2);f.write('\n')
if __name__=='__main__':main()
