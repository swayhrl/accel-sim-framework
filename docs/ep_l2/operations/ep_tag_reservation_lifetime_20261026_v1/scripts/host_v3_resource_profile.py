#!/usr/bin/env python3
"""Exact ON-only conditional admission estimate; no launch/authority operations.

4GiB is LIKELY working set, never a promised peak or a replacement hard cap.
The pinned R20 module supplies all foreign accounting and actual held-phase gates.
"""
import argparse,datetime,hashlib,importlib.util,json,os,stat
from pathlib import Path
J=Path('/root/data/ep_tag_reservation_lifetime_20261026_v1');G=1<<30;M=1<<20
PROFILE=J/'agent_a/v3/ON_WORKING_SET_PROFILE.json'
HOST_RUNTIME=J/'tools_v3/finite_native_runtime.py'
HOST_RUNTIME_SHA='17b0576e0babbffed8dc41fd996ff1a5ad69cf5f5783ae4d6a850e965e6309aa'
INPUT_PROOF=J/'agent_c/FRESH_INPUT_REOPEN_CONTINUATION_20261026T154215Z.json'
INPUT_PROOF_SHA='6c5fe0dba6e39eb89401957136a950a58a044fda152367fed80d177aabcba58b'
ORIGINAL_INPUT_SHA='de0e6db73adb59de9804b57d6f925537fcf9429a50249d82cd2a309df90862ce'
BASE=J/'agent_a/resource_snapshot_qualified_r20.py'
BASE_SHA='ab986c9ceb2310fcaaedfaefae313eb6de3bfbfe63a85c725afa80e8dfa40003'
OFF='EP_NATIVE_VECTOR_TAG_LIFETIME_OFF_20261026_V2';ON='EP_NATIVE_VECTOR_TAG_LIFETIME_ON_20261026_V2'
REG=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
EPOCH=Path('/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json')
LED=REG.parent.parent/'qualification_ledger'
SOURCEQ_SHA='8ed4d41852f6e26bc9c1ced140f4dc2ecc6f287f3c4df5d0e5cc6e883dfe2814'
HEADER_SHA='d88efa5012f1bd24c0b55be42504c1b8e3727bcabdf46a2c96385ee61082b8e1'
ORIGINAL_ON_SHA='4b702373dd8c1fc64a469a7397ff6aff5179024f912157d1423498bca9f84e76'
OFF_SPEC_SHA='bfd88b590fa82452e12df7daab9cbc56fdd1d89b7f97c94eb498ca01b301459c'
OFF_DONE_SHA='19869744eab2798ac798866e3a3a3c07a6b1c2697cbd2630690dcbdca47344ae'
OFF_POINT_SHA='d94469cd48f7064e2f2df07e40d79a4df596a8ae3c3296a7be67491b988da6c6'
OFF_SAMPLES_SHA='dd57f9b6f8834c4efd894484476cacb64889cf311b7b6da09cb8189c5d8011f4'
OFF_RAW_SHA='c8c41b772fc254bfb7a9410f0c56f6bba98974b6d48bd4f1ad8ab0e0a1ea02ce'
PEAK=578813952;HARD=9*G;ESTIMATE=4*G
SOURCE={'core_source_commit':'11c02df1034112013523429894f1f931323adbef',
 'framework_source_commit':'9dd1ee57a83d83b56b7874bc7c716185ab52c8f7',
 'vendor_pybind11_commit':'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b',
 'binary_sha256':'8d55f19bbe74c72e5da688f0ede6c2de1c3aa13040015475f23c9c6c521b9bef',
 'archive_sha256':'685b497b50328deff4b96741c9a770b4b37e5d4bb2c8a1b5db90558b90be73c4'}
_BASE=None
class InvalidProfile(ValueError):pass
def need(value,message):
 if not value:raise InvalidProfile(message)
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(M),b''):h.update(b)
 return h.hexdigest()
def load_base():
 global _BASE
 need(sha(BASE)==BASE_SHA,'exact R20 base resource bytes changed')
 if _BASE is None:
  spec=importlib.util.spec_from_file_location('ep_on_exact_readonly_r20_resource',BASE)
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);_BASE=module
 return _BASE

def validate_spec_delta(original,current,profile,profile_sha,self_path,self_sha,meta):
 """All scientific and old pin fields remain exact; only resource binding adds."""
 mutable={'resource_module_path','resource_module_sha256','pinned_files',
          'host_working_set_profile_path','host_working_set_profile_sha256',
          'runtime_module_path','runtime_module_sha256','input_stat_continuation_path','input_stat_continuation_sha256'}
 need({k:v for k,v in original.items() if k not in mutable}=={k:v for k,v in current.items() if k not in mutable},'ON scientific/domain/limit fields changed')
 oldpins=original['pinned_files'];newpins=current['pinned_files']
 need(isinstance(newpins,dict) and all(newpins.get(p)==h for p,h in oldpins.items()),'ON original pinned dependency was removed/changed')
 for path,h in newpins.items():
  if path in oldpins:continue
  data=meta.raw(path);need(hashlib.sha256(data).hexdigest()==h,'new host-profile pin changed: '+path)
 unmodified=current==original
 if not unmodified:
  need(current['runtime_module_path']==str(HOST_RUNTIME) and current['runtime_module_sha256']==HOST_RUNTIME_SHA,'ON runtime is not the exact reviewed V3 host-only continuation')
  need(current.get('input_stat_continuation_path')==str(INPUT_PROOF) and current.get('input_stat_continuation_sha256')==INPUT_PROOF_SHA,'ON same-content input continuation binding missing/wrong')
  need(newpins.get(str(HOST_RUNTIME))==HOST_RUNTIME_SHA and newpins.get(str(INPUT_PROOF))==INPUT_PROOF_SHA,'ON actual host-runtime/input-proof pins missing')
  need(current['resource_module_path']==str(self_path) and current['resource_module_sha256']==self_sha,'ON resource path/SHA is not this exact wrapper')
  need(current.get('host_working_set_profile_path')==str(PROFILE) and current.get('host_working_set_profile_sha256')==profile_sha,'ON host-profile binding absent/wrong')
  need(newpins.get(str(PROFILE))==profile_sha and newpins.get(str(BASE))==BASE_SHA and newpins.get(str(self_path))==self_sha,'ON host-profile/base/wrapper pins missing')
 return not unmodified

def validate_input_continuation(proof,original):
 """Pure local proof validation only. Actual hostruntime freshly reads NAS twice."""
 need(proof['schema']=='FRESH_INPUT_REOPEN_CONTINUATION_V1' and
      proof['status']=='GENUINE164_SAME_CONTENT_INPUT_REOPEN_CONTINUATION_PASS' and
      proof['original_input_binding_sha256']==ORIGINAL_INPUT_SHA and proof['old_proof']['sha256']==ORIGINAL_INPUT_SHA and
      proof['old_proof']['preserved_byte_identical'] is True,'same-content input proof/original binding changed')
 need(proof['same_content_as_original_input_binding'] is True and proof['two_full_reads_each_closed_between'] is True and
      proof['metadata_stable_across_entire_validation'] is True and proof['alias_and_mount_stable'] is True and
      proof['source_changed'] is False and proof['old_stat_binding_modified'] is False and
      proof['new_complete_application_starts']==0 and proof['new_local_payload_bytes']==0 and proof['authority_or_budget_mutations']==0,'input continuation is not an independent same-content read')
 need(proof['input_trace_composite_sha256']==original['input_trace_composite_sha256'] and
      proof['source_root']==original['source_root'] and proof['native_mirror_mount_path']==original['native_mirror_mount_path'],'scientific input domain/alias changed')
 mount=proof['mount'];need(mount==proof['mount_before']==proof['mount_after'] and
      mount['fstype']=='fuse.sshfs' and mount['source']=='admin-wcx@10.208.130.164:/home/shared' and mount['target']=='/root/share/mnt164','same-content proof mount changed')
 old={x['path']:x for x in original['members']};rows={x['path']:x for x in proof['members']}
 need(len(old)==len(rows)==len(proof['members'])==2 and set(old)==set(rows),'input member set changed')
 for path,row in rows.items():
  prior=old[path];expected=prior['sha256']
  need(all(row[k]==expected for k in ['sha256','closed_reopen_full_sha256','first_full_sha256','second_full_sha256','old_expected_sha256']) and
       prior['closed_reopen_full_sha256']==expected and row['size']==prior['size'] and row['old_identity']==prior['identity'] and
       row['same_content_as_original_input_binding'] is True,'input member content/size/original identity changed')
  identity=row['identity'];need(len(identity)==4 and identity==row['current_identity'] and
       [identity[i] for i in [0,2,3]]==[prior['identity'][i] for i in [0,2,3]],'input continuation dev/size/mtime changed')
  rounds=row['full_read_rounds'];need(len(rounds)==2 and [x['open_number'] for x in rounds]==[1,2],'two closed/reopened full reads required')
  for sample in rounds:
   need(sample['sha256']==expected and sample['bytes']==prior['size'] and sample['closed_before_next_open'] is True and
        all(sample[k]==identity for k in ['stat_before','fstat_open','fstat_end','stat_after_close']),'full input read metadata/content was unstable')
 need(proof['total_NAS_bytes_read']==2*sum(x['size'] for x in old.values()),'full input byte coverage changed')
 # No os.stat/open/read on NAS paths here. Future inode changes alone are not a
 # scientific mismatch; frozen hostruntime17b independently does fresh full SHA.
 return True

def validate_profile(meta,own_request,phase,own_write_bytes,own_memory_cap_bytes):
 need(own_request==ON,'conditional estimate is scoped to exact ON_V2 only')
 need(phase in {'admission','runtime','postrun'},'unknown phase')
 need(own_write_bytes==512*M and own_memory_cap_bytes==HARD,'own write/hard-cap identity changed')
 profile=meta.read(PROFILE);profile_sha=meta.before[str(PROFILE)]
 need(profile['schema']=='EP_LIFETIME_ON_CONDITIONAL_WORKING_SET_ESTIMATE_V3' and profile['cohort']==ON and
      profile['baseline_cohort']==OFF and profile['base_resource_module']=={'path':str(BASE),'sha256':BASE_SHA},'profile scope/base changed')
 self_path=Path(__file__).resolve();self_sha=sha(self_path)
 need(str(self_path) in profile['allowed_wrapper_paths'] and profile['wrapper_implementation_sha256']==self_sha,'conditional wrapper code/path changed')
 need(profile['source_identity']==SOURCE and profile['hard_RSS_AS_cap_bytes']==HARD and
      profile['admission_working_set_estimate_bytes']==ESTIMATE and profile['sampled_OFF_peak_bytes']==PEAK and
      profile['observer_fixed_state_bound_bytes']==16*M and profile['additional_margin_bytes']==G and
      profile['estimate_floor_bytes']==4*G and profile['evidence_grade']=='LIKELY' and
      profile['sampled_peak_is_OS_upper_bound'] is False and profile['scientific_noninterference_claimed'] is False,'profile formula/claim boundary changed')
 derived=max(profile['estimate_floor_bytes'],PEAK+16*M+G);need(derived==ESTIMATE,'conditional4GiB formula changed')
 refs=profile['evidence_refs'];required={'original_ON_spec','OFF_spec','OFF_done','OFF_point','OFF_samples','OFF_raw','source_qualification','observer_header','layout_proof','runtime','binary','static_library','actual_host_runtime','input_stat_continuation'}
 need(set(refs)==required,'conditional evidence scope changed')
 for label,ref in refs.items():
  data=meta.raw(ref['path']);need(hashlib.sha256(data).hexdigest()==ref['sha256'],'conditional evidence SHA drift: '+label)
 expected={'original_ON_spec':ORIGINAL_ON_SHA,'OFF_spec':OFF_SPEC_SHA,'OFF_done':OFF_DONE_SHA,
  'OFF_point':OFF_POINT_SHA,'OFF_samples':OFF_SAMPLES_SHA,'OFF_raw':OFF_RAW_SHA,
  'source_qualification':SOURCEQ_SHA,'observer_header':HEADER_SHA,
  'binary':SOURCE['binary_sha256'],'static_library':SOURCE['archive_sha256']}
 for label,h in expected.items():need(refs[label]['sha256']==h,'unreviewed conditional evidence identity: '+label)
 need(refs['actual_host_runtime']=={'path':str(HOST_RUNTIME),'sha256':HOST_RUNTIME_SHA} and refs['input_stat_continuation']=={'path':str(INPUT_PROOF),'sha256':INPUT_PROOF_SHA},'unreviewed V3 host runtime or input proof')
 original=meta.read(refs['original_ON_spec']['path']);offspec=meta.read(refs['OFF_spec']['path'])
 original_input=meta.read(original['input_binding_path']);need(meta.before[original['input_binding_path']]==original['input_binding_sha256']==ORIGINAL_INPUT_SHA,'original exact input binding changed')
 validate_input_continuation(meta.read(str(INPUT_PROOF)),original_input)
 current_path=J/'cases'/ON/'control/FROZEN_SPEC.json';current=meta.read(current_path)
 binding=validate_spec_delta(original,current,profile,profile_sha,self_path,self_sha,meta)
 need(original['cohort']==ON and offspec['cohort']==OFF and original['source_identity']==offspec['source_identity']==SOURCE and
      original['memory_cap_bytes']==offspec['memory_cap_bytes']==HARD,'baseline scientific/hard-cap identity changed')
 for field in ['input_trace_composite_sha256','expected_instructions','expected_CTA','expected_slices','host_cpu','nice','wall_timeout_seconds','runtime_module_path','runtime_module_sha256']:
  need(original[field]==offspec[field],'OFF/ON conditional domain differs: '+field)
 need(original['expected_instructions']==56000000 and original['expected_CTA']==15625 and original['expected_slices']==64,'conditional workload shape changed')
 need([x['sha256'] for x in original['ordered_configs']]==[x['sha256'] for x in offspec['ordered_configs']] and len(original['ordered_configs'])==4,'conditional four configs differ')
 need(original['observer_env']=={'EPL2_DETACH_DIAG':'1','EPL2_TAGPRESSURE_DIAG':'1','EPL2_TAG_LIFETIME':'1'} and offspec['observer_env']=={'EPL2_DETACH_DIAG':'1','EPL2_TAGPRESSURE_DIAG':'1','EPL2_TAG_LIFETIME':'0'},'only lifetime observer switch may differ')
 need(refs['runtime']['path']==original['runtime_module_path'] and refs['runtime']['sha256']==original['runtime_module_sha256'],'runtime88a profile binding changed')
 for spec in [offspec,current]:
  for path,h in spec['env_hashes'].items():need(hashlib.sha256(meta.raw(path)).hexdigest()==h,'OFF/ON actual config/env drift '+path)
 sourceq=meta.read(refs['source_qualification']['path'])
 need(sourceq['source_identity']==SOURCE and sourceq['header_sha256']==HEADER_SHA and sourceq['status']=='SOURCEQ_CPU_PASS_NOT_APPLICATION_ACCEPTED' and
      sourceq['scientific_acceptance_granted'] is False and sourceq['application_start_permission_issued_by_this_qualification'] is False and
      refs['layout_proof']==sourceq['evidence_refs']['layout_proof'],'SourceQ/static layout binding changed')
 reg=meta.read(REG);epoch=meta.read(EPOCH);need(meta.before[str(REG)]==epoch['native_registry_sha256'],'authority pair changed during profile validation')
 offrow=reg['registered_future_requests'][OFF]
 need(offrow['state']=='CLOSED' and offrow['consumed']==1 and offrow['remaining']==0 and offrow['reserved_write_bytes']==0 and
      offrow['uuid']==profile['OFF_uuid'] and offrow['spec_sha256']==OFF_SPEC_SHA and offrow['done_sha256']==OFF_DONE_SHA and
      offrow['accepted_point_sha256']==OFF_POINT_SHA,'OFF complete accepted/CLOSED identity lost')
 done=meta.read(refs['OFF_done']['path']);point=meta.read(refs['OFF_point']['path'])
 need(done==meta.read(Path(offrow['output'])/'NATIVE_EXIT.json') and done['uuid']==offrow['uuid'] and
      done['source_identity']==SOURCE and done['spec_sha256']==OFF_SPEC_SHA and done['raw_sha256']==OFF_RAW_SHA and
      done['peak_observed_rss_bytes']==PEAK and done['launcher_wait_returncode']==0 and done['stop_reason'] is None,'OFF natural result/memory measurement changed')
 need(point['status']=='EP_L2_TAG_RESERVATION_LIFETIME_APPLICATION_ACCEPTED' and point['source_identity']==SOURCE and
      point['uuid']==offrow['uuid'] and point['raw_sha256']==OFF_RAW_SHA and point['native_done_sha256']==OFF_DONE_SHA and
      point['native_spec_sha256']==OFF_SPEC_SHA and point['cycles']==75039 and point['instructions']==56000000 and
      point['CTA']==15625 and point['slices']==64 and point['hardware_drained'] is True and point['observer_enabled'] is False,'OFF accepted full-domain evidence changed')
 samples=[json.loads(x) for x in Path(refs['OFF_samples']['path']).read_text().splitlines() if x.strip()]
 need(samples and max(x['process_tree_RSS_bytes'] for x in samples)==PEAK,'OFF sampledRSS reproduction changed')
 own=reg['registered_future_requests'].get(ON);ip=LED/(ON+'.INTENT.json')
 if phase=='admission':
  need(meta.raw(ip,True) is None,'conditional admission cannot retry/reclassify consumed ON')
  if own is not None:need(own['state']=='AUTHORIZED_UNUSED' and own['consumed']==0 and own['remaining']==1 and own['budget']==1 and own['spec_sha256']==meta.before[str(current_path)],'ON registered identity/unused budget differs')
 else:
  need(own is not None and own['consumed']==1 and own['remaining']==0 and own['budget']==1,'held-phase lacks own exact consumed1')
  intent=meta.read(ip);need(own['spec_sha256']==meta.before[str(current_path)] and intent['spec_sha256']==own['spec_sha256'] and
      intent['uuid']==own['uuid'] and intent['output']==own['output'],'held ON current spec/INTENT generation differs')
 return {'profile_path':str(PROFILE),'profile_sha256':profile_sha,'wrapper_path':str(self_path),'wrapper_sha256':self_sha,
  'base_resource_module_sha256':BASE_SHA,'actual_hard_RSS_AS_cap_bytes':HARD,'admission_working_set_estimate_bytes':ESTIMATE,
  'sampled_OFF_peak_bytes':PEAK,'observer_fixed_state_bound_bytes':16*M,'additional_margin_bytes':G,
  'evidence_grade':'LIKELY','sampled_peak_is_OS_upper_bound':False,'scientific_noninterference_claimed':False,
  'hostprofile_binding_in_current_spec':binding,'engineering_reference_only_until_native_rebound':not binding,
  'application_start_permission_issued':False,'actual_host_runtime':refs['actual_host_runtime'],
  'input_stat_continuation':refs['input_stat_continuation'],'resource_wrapper_NAS_body_or_stat_reads':0,'SSHFS_inode_is_permanent_scientific_identity':False}

def snapshot(job_root,own_request,phase='admission',own_write_bytes=512*M,own_memory_cap_bytes=HARD):
 base=load_base();meta=base.Metadata()
 try:binding=validate_profile(meta,own_request,phase,own_write_bytes,own_memory_cap_bytes)
 except (OSError,ValueError,KeyError,TypeError) as error:
  stable=meta.stable();return {'schema':'EP_ON_CONDITIONAL_WORKING_SET_RESOURCE_REFERENCE_V1','phase':phase,'decision':'HOLD' if stable else 'RESAMPLE',
   'consistent_snapshot':False,'resample_required':not stable,'errors':[type(error).__name__+': '+str(error)],'disk_pass':False,'RAM_pass':False,'resource_pass':False,
   'actual_hard_RSS_AS_cap_bytes':HARD,'own_model_hard_cap_bytes':HARD,'own_admission_working_set_estimate_bytes':ESTIMATE,
   'abort_recommended':False,'metadata_SHA256_before':meta.before,'metadata_SHA256_after':meta.after,'authority_writes':0}
 internal=ESTIMATE if phase=='admission' else HARD
 result=base.snapshot(job_root,own_request,phase=phase,own_write_bytes=own_write_bytes,own_memory_cap_bytes=internal)
 stable=meta.stable();same_authority=(meta.before.get(str(REG))==result.get('metadata_SHA256_before',{}).get(str(REG)))
 result.update(schema='EP_ON_CONDITIONAL_WORKING_SET_RESOURCE_REFERENCE_V1',own_model_hard_cap_bytes=HARD,
  actual_hard_RSS_AS_cap_bytes=HARD,own_admission_working_set_estimate_bytes=ESTIMATE if phase=='admission' else None,
  base_internal_forecast_argument_bytes=internal,conditional_working_set_profile=binding,
  conditional_profile_metadata_SHA256_before=meta.before,conditional_profile_metadata_SHA256_after=meta.after,
  conditional_profile_snapshot_stable=stable and same_authority,application_start_permission_issued=False)
 if not stable or not same_authority:
  result.update(decision='RESAMPLE',consistent_snapshot=False,resample_required=True,resource_pass=False,disk_pass=False,RAM_pass=False,abort_recommended=False)
 return result

if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--job-root',default=str(J));a.add_argument('--own-request',default=ON);a.add_argument('--phase',choices=['admission','runtime','postrun'],default='admission');args=a.parse_args()
 print(json.dumps(snapshot(args.job_root,args.own_request,args.phase),indent=2))
