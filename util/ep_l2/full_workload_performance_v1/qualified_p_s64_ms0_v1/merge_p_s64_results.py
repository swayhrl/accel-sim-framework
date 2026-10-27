"""Strict read-only P_S64/MS0 comparisons and explicit accepted-F endpoint aliasing.
Never changes a case identity or grants acceptance. CLI reads the current Main
registry/epoch and referenced receipts through the byte-identical V1 collector.
"""
import argparse,hashlib,importlib.util,json,math
from pathlib import Path as P
ROOT=P(__file__).resolve().parent
PINS={'merge_performance_results_frozen_v1.py':'5169bf987ea4e69eb07d1d24d1d8ea2e8dc4c48a5020ddbed01a8060b11d972a','p_s64_terminal.py':'abbc0cf165a14589df20f50bdf1e96c7bb64ddc9ed30e5f54863c1425ca638fd'}
PSTUDY='P_S64_VS_UNIFIED1168_MSOFF';REFERENCE='REF_G_P1168_MSOFF';STATIC='-gpgpu_ep_l2_static_s64'
def need(x,msg):
 if not x:raise ValueError(msg)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(x):return hashlib.sha256(canonical(x)).hexdigest()
def load(rel,name):
 p=ROOT/rel;need(hashlib.sha256(p.read_bytes()).hexdigest()==PINS[rel],'frozen Pmerge dependency drift')
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def verified_pair(srec,frec,ss,fs):
 # This pure primitive requires records from frozen collect_case; merge() below
 # supplies those records using an epoch-pair stable current Main registry.
 m=load('merge_performance_results_frozen_v1.py','frozen_pmerge_base');p=load('p_s64_terminal.py','frozen_pmath');sb=p.qualify_history_spec(ss);fb=p.qualify_history_spec(fs)
 need(srec['accepted']is True and frec['accepted']is True,'both exact endpoints mustbe Mainaccepted')
 need(ss['mode']==srec['mode']=='S'and fs['mode']==frec['mode']=='F','formal S/F endpoints')
 need(ss['cohort']==srec['cohort']and fs['cohort']==frec['cohort'],'endpoint cohort identity')
 need(ss['profile']in(PSTUDY,REFERENCE)and fs['profile']in(PSTUDY,REFERENCE),'unsupported P comparison profiles')
 if ss['profile']==REFERENCE:need(fs['profile']==REFERENCE,'referencecomparison mustuse reference F')
 for key in('input_identity_sha256','source_identity','geometry','observer_env','observer_profile_id'):
  need(ss[key]==fs[key],'matched population mismatch '+key)
 for rec,spec in((srec,ss),(frec,fs)):
  need(rec['source_identity']==spec['source_identity']and rec['input_identity_sha256']==spec['input_identity_sha256']and rec['profile']==spec['profile'],'record/spec identity')
  need(rec['pair_population']['observer_env']==spec['observer_env'],'record observer identity')
  want={k:v for k,v in spec['expected_effective_options'].items()if k not in m.MODE_KEYS|m.CERT_KEYS|{'-trace'}}
  need(rec['pair_population']['background282']==want,'record background282 integrity')
 need(ss['trace_entry']==fs['trace_entry'],'matched actual trace pathname')
 a=srec['pair_population']['background282'];b=frec['pair_population']['background282'];delta={k:{'S':a.get(k),'F':b.get(k)}for k in sorted(set(a)|set(b))if a.get(k)!=b.get(k)}
 expected={STATIC:{'S':'1','F':'0'}}if ss['profile']==PSTUDY else{}
 need(delta==expected,'only explicitly qualified S64 mode-layout delta maydiffer')
 need(sb['modeled_physical_payload_data_bytes_GPU']==fb['modeled_physical_payload_data_bytes_GPU']==9568256 and sb['modeled_physical_payload_line_slots_per_slice']==fb['modeled_physical_payload_line_slots_per_slice']==1168,'same physicalbudget')
 need((srec['instructions'],srec['CTA'],srec['kernel_count'])==(frec['instructions'],frec['CTA'],frec['kernel_count']),'dynamic completepopulation differs')
 for rec in(srec,frec):need(rec['hardware_drained']is True and type(rec['cycles'])is int and rec['cycles']>0,'naturalaccepted cycles/drain required')
 actual_identity=dict(input=ss['input_identity_sha256'],source=ss['source_identity'],geometry=ss['geometry'],observer_profile_id=ss['observer_profile_id'],observer_env=ss['observer_env'],comparison_profile=ss['profile'],background_without_explicit_STATIC={k:v for k,v in a.items()if k!=STATIC})
 return dict(schema='EP_FULL_PERF_S64_EXPLICIT_ENDPOINT_COMPARISON_V1',status='OFFLINE_COMPARISON_ONLY_NOT_ACCEPTANCE',input_identity_sha256=ss['input_identity_sha256'],comparison_profile=ss['profile'],geometry=ss['geometry'],S_cohort=srec['cohort'],F_actual_cohort=frec['cohort'],S_actual_profile=ss['profile'],F_actual_profile=fs['profile'],S_point_ref=srec['point_ref'],F_point_ref=frec['point_ref'],S_spec_ref=srec['spec_ref'],F_spec_ref=frec['spec_ref'],F_endpoint_alias_into_comparison=ss['profile']==PSTUDY and fs['profile']==REFERENCE,alias_is_reference_not_new_case=True,S_cycles=srec['cycles'],F_cycles=frec['cycles'],speedup_S_over_F=srec['cycles']/frec['cycles'],explicit_mode_layout_delta=delta,physical_payload_slots_per_slice=1168,physical_payload_data_bytes_GPU=9568256,S_static_role_partition=sb['S_static_role_partition'],F_layout='UNIFIED1168_STATIC_S64_FALSE',source_identity=ss['source_identity'],observer_profile_id=ss['observer_profile_id'],observer_env=ss['observer_env'],comparison_population_digest=digest(actual_identity),S_role_reachability_upper_bound=sb['S_regular_RESIDENT_plus_WB_upper_bound'],upper_bound_is_not_measured_peak=True,hardware_area_power_cost='UNKNOWN; same modeled data capacity doesnotprove equal metadata/copy/area/power',science_granted=False)

def equivalent_f_endpoint(actual_record,actual_spec,desired_comparison_spec):
 p=load('p_s64_terminal.py','p_alias_math');p.qualify_history_spec(actual_spec);p.qualify_history_spec(desired_comparison_spec)
 need(actual_record['accepted']is True and actual_spec['mode']==desired_comparison_spec['mode']=='F','only Mainaccepted F endpoint mayalias')
 need(actual_record['cohort']==actual_spec['cohort']and actual_record['profile']==actual_spec['profile'],'actual endpoint identity')
 for key in('input_identity_sha256','source_identity','geometry','observer_env','observer_profile_id','expected_effective_options','trace_entry','ro_qualification_ref'):
  need(actual_spec[key]==desired_comparison_spec[key],'F operationally identical endpoint mismatch '+key)
 need(actual_record['source_identity']==actual_spec['source_identity']and actual_record['input_identity_sha256']==actual_spec['input_identity_sha256'],'F record/spec identity')
 return dict(status='EXPLICIT_EXISTING_ACCEPTED_F_ENDPOINT_ALIAS_ELIGIBLE_NOT_NEW_ACCEPTANCE',actual_cohort=actual_record['cohort'],actual_point_ref=actual_record['point_ref'],actual_spec_ref=actual_record['spec_ref'],desired_comparison_profile=desired_comparison_spec['profile'],expected282_identical=True,source_input_env_geometry_identical=True,additional_model_start_needed=False,accepted_identity_copied=False,science_granted=False)

def merge(manifest):
 m=load('merge_performance_results_frozen_v1.py','p_merge_original_collector')
 need(manifest['schema']=='EP_FULL_PERF_S64_OFFLINE_MERGE_MANIFEST_V1'and manifest['goal']==m.GOAL,'Pmerge manifest identity')
 registry,snap=m.stable_authority(manifest['registry_path'],manifest['epoch_path']);request=registry['registered_future_requests'][m.GOAL]
 rows=[];blocked=[];seen=set()
 for item in manifest['comparisons']:
  key=(item['S_spec_ref']['path'],item['F_spec_ref']['path']);need(key not in seen,'duplicate explicitendpoint comparison');seen.add(key)
  ss=m.exact(item['S_spec_ref']);fs=m.exact(item['F_spec_ref']);sr=m.collect_case(item['S_spec_ref'],request);fr=m.collect_case(item['F_spec_ref'],request)
  try:rows.append(verified_pair(sr,fr,ss,fs))
  except(ValueError,KeyError,TypeError,OSError)as e:blocked.append(dict(S_cohort=ss['cohort'],F_cohort=fs['cohort'],reason=str(e),S_record=sr,F_record=fr))
 required=manifest['required_common_inputs'];need(len(required)==len(set(required))and all(type(x)is str and x for x in required),'explicit uniquecommoninputset')
 groups={}
 for r in rows:
  key=(r['comparison_profile'],digest(r['source_identity']),digest(r['observer_env']),digest(r['geometry']))
  groups.setdefault(key,[]).append(r)
 summaries=[]
 for key,rs in sorted(groups.items()):
  ids=[r['input_identity_sha256']for r in rs];need(len(ids)==len(set(ids)),'multipleacceptedreplicates requireexplicit selection; nobestrun')
  complete=bool(required)and set(ids)==set(required);gm=math.exp(sum(math.log(r['speedup_S_over_F'])for r in rs)/len(rs))
  summaries.append(dict(comparison_profile=key[0],source_digest=key[1],observer_env_digest=key[2],geometry_digest=key[3],common_set_complete=complete,required_common_count=len(required),observed_count=len(rs),missing_inputs=sorted(set(required)-set(ids)),unexpected_inputs=sorted(set(ids)-set(required)),observed_set_GM_not_global_claim=gm,full_common_set_GM=gm if complete else None,slowdown_count=sum(r['speedup_S_over_F']<1 for r in rs)))
 return dict(schema='EP_FULL_PERF_S64_OFFLINE_MERGE_RESULT_V1',status='OFFLINE_COMPARISON_ONLY_NOT_ACCEPTANCE',authority_snapshot=snap,comparisons=rows,summaries=summaries,blocked=blocked,model_launches=0,registry_writes=0,source_changes=0,science_granted=False)

def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--manifest',required=True);a.add_argument('--manifest-sha256',required=True);a.add_argument('--output',required=True);args=a.parse_args();m=load('merge_performance_results_frozen_v1.py','pmerge_cli');data=P(args.manifest).read_bytes();need(hashlib.sha256(data).hexdigest()==args.manifest_sha256,'manifest drift');result=merge(m.load_bytes(data));out=P(args.output);need(not out.exists()and not out.is_symlink()and not any(p.is_symlink()for p in out.parents),'fresh nonlinked output');out.mkdir(parents=True,exist_ok=False);(out/'SUMMARY.json').write_bytes(canonical(result)+b'\n');print(json.dumps(dict(status=result['status'],science_granted=False,output=str(out))))
if __name__=='__main__':main()
