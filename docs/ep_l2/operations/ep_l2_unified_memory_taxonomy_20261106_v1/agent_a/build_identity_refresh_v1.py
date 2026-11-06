#!/usr/bin/env python3
import json,hashlib,collections,copy,datetime
from pathlib import Path
J=Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
O=J/'research/unified_memory_taxonomy_20261106_v1/agent_a'
REG=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
F=J/'research/observation_guided_20261029_v1/agent_a/WORKLOAD_FEATURE_AND_OPPORTUNITY.json'
MAX=4*1024*1024
reads={}
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def ref(p):p=Path(p);b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':sha(b)}
def load(p,expected=None):
 p=Path(p)
 if not p.is_absolute() or p.suffix!='.json':raise ValueError('metadata JSON only')
 z=p.stat().st_size
 if z>MAX:raise ValueError('metadata size cap')
 b=p.read_bytes()
 if expected and sha(b)!=expected:raise ValueError('SHA mismatch '+str(p))
 reads[str(p)]={'bytes':len(b),'sha256':sha(b)}
 return json.loads(b)
def loadref(r):return load(r['path'],r.get('sha256'))
def source5(s):
 return {k:s.get(v) for k,v in [('core_commit','core_source_commit'),('framework_commit','framework_source_commit'),('vendor_commit','vendor_pybind11_commit'),('elf_sha256','binary_sha256'),('library_sha256','archive_sha256')]}
def scrub(x):
 if isinstance(x,dict):return {k:scrub(v) for k,v in x.items() if not any(t in k.lower() for t in ['token','nonce','secret'])}
 if isinstance(x,list):return [scrub(y) for y in x]
 return x
def write(n,d):p=O/n;p.write_text(json.dumps(scrub(d),sort_keys=True,indent=2,ensure_ascii=True)+'\n');return ref(p)
def reconstruct(req,co,c):
 e={'request_id':req,'cohort':co,'uuid':c.get('uuid'),'registry_state':c.get('state'),'accepted':c.get('state')=='CLOSED_ACCEPTED','registry_entry_canonical_sha256':sha(canon(c)),'source_refs':{},'identity_gaps':[]}
 for k in ['accepted_point_ref','archive_receipt_ref','done_ref','validation_ref']:
  if k in c:e['source_refs'][k]=c[k]
 point={}
 if c.get('accepted_point_ref'):point=loadref(c['accepted_point_ref'])
 sr=point.get('spec_ref')
 if not sr:
  p=Path(c['output']).parents[1]/'control/FROZEN_SPEC.json'
  if p.exists():sr=ref(p)
 if not sr:
  e['identity_gaps'].append('FROZEN_SPEC_UNLOCATED');return e
 s=loadref(sr);e['spec_ref']=sr
 if s.get('cohort')!=co:raise ValueError('cohort mismatch')
 e.update({k:s.get(k) for k in ['program','input_identity_sha256','mode','profile','geometry','command_count','expected_instructions','expected_CTA','expected_kernel_launches','observer_env']})
 e['observer_env_sha256']=sha(canon(s.get('observer_env',{})))
 e['source5']=source5(s['source_identity']);e['source_identity_original']=s['source_identity']
 e['cycles']=point.get('cycles');e['hardware_drained']=point.get('hardware_drained')
 e['estimated_wall_seconds']=s.get('estimated_wall_seconds');e['limits']=s.get('limits')
 opts=s.get('expected_effective_options',{});e['effective_option_count']=len(opts);e['effective_options_sha256']=sha(canon(opts));e['effective_options']=opts
 e['clock_domains']=opts.get('-gpgpu_clock_domains');e['ordered_configs']=s.get('ordered_configs')
 e['mode_feature_contract']=s.get('scientific_option_contract')
 if point:
  if point.get('source_identity')!=s.get('source_identity'):raise ValueError('point Source5 mismatch')
  if point.get('input_identity_sha256')!=s.get('input_identity_sha256'):raise ValueError('point input mismatch')
  if point.get('uuid')!=c.get('uuid'):raise ValueError('point UUID mismatch')
 br=s.get('input_binding_ref')
 if br:
  binding=loadref(br)
  if binding.get('input_identity_sha256')!=s.get('input_identity_sha256'):raise ValueError('binding input mismatch')
  cmds=binding.get('expectedcommands',binding.get('expected_commands'))
  kernels=binding.get('ordered_kernel_identity',binding.get('expected_kernel_scopes'))
  e['input_binding_ref']=br;e['literal_commandlist_sha256']=binding.get('literal_commandlist_sha256')
  e['ordered_commands']=cmds;e['ordered_commands_canonical_sha256']=sha(canon(cmds)) if isinstance(cmds,list) else None
  e['ordered_kernel_identity']=kernels
  if not isinstance(cmds,list):e['identity_gaps'].append('ORDERED_COMMANDS_NOT_EXPORTED')
 else:e['identity_gaps'].append('INPUT_BINDING_NOT_EXPORTED')
 if c.get('done_ref'):
  done=loadref(c['done_ref']);receipt=done.get('execution_receipt',done)
  e['host_elapsed_seconds']=receipt.get('elapsed_seconds')
 e['identity_status']='SOURCE5_INPUT_COMMAND_CONFIG_EXACT' if not e['identity_gaps'] else 'PARTIAL_EXACT_METADATA_WITH_GAPS'
 return e
def main():
 frozen=load(F);registry=load(REG);registry_initial_sha=reads[str(REG)]['sha256'];endpoints=[];excluded=[];req_counts={}
 for req,v in registry['registered_future_requests'].items():
  if v.get('owner')!='EP-MAIN' or v.get('project')!='EP_L2':continue
  c=v.get('consumed')
  if not isinstance(c,dict):
   excluded.append({'request_id':req,'state':v.get('state'),'consumed':c,'reason':'SINGLETON_OR_COMPATIBILITY_SCHEMA_OUTSIDE_STRUCTURED_COMPLETE_APPLICATION_ENDPOINT_SCOPE'})
   continue
  counts=collections.Counter(x.get('state') for x in c.values())
  req_counts[req]=dict(counts)
  for co,x in c.items():endpoints.append(reconstruct(req,co,x))
 assert len({(e['cohort'],e['uuid']) for e in endpoints})==len(endpoints)
 byinput=collections.defaultdict(list)
 for e in endpoints:
  if e.get('input_identity_sha256'):byinput[e['input_identity_sha256']].append(e)
 rows=[]
 for i,r in enumerate(frozen['rows'],1):
  q=copy.deepcopy(r);q['row_id']='FROZEN103_%03d'%i;q['frozen_row_canonical_sha256']=sha(canon(r))
  ee=byinput.get(r.get('input_identity_sha256'),[])
  q['current_result_endpoints']=[{'cohort':e['cohort'],'uuid':e['uuid'],'request_id':e['request_id'],'accepted':e['accepted'],'registry_state':e['registry_state'],'source5':e.get('source5'),'mode':e.get('mode'),'geometry':e.get('geometry'),'clock_domains':e.get('clock_domains'),'cycles':e.get('cycles'),'spec_ref':e.get('spec_ref'),'effective_options_sha256':e.get('effective_options_sha256'),'observer_env_sha256':e.get('observer_env_sha256'),'ordered_commands_canonical_sha256':e.get('ordered_commands_canonical_sha256'),'literal_commandlist_sha256':e.get('literal_commandlist_sha256'),'identity_status':e.get('identity_status'),'identity_gaps':e['identity_gaps']} for e in ee]
  baseline=[]
  for old in r.get('reference_endpoints',[]):
   old_co=old.get('cohort')
   candidates=[e for e in ee if e['cohort']==old_co]
   baseline.extend(candidates)
  for short in q['current_result_endpoints']:
   if not baseline:
    short['relation_to_frozen_reference']='NO_ACCEPTED_REFERENCE_STRATUM_AT_FROZEN_DATE'
    continue
   exactcmd=[e for e in baseline if e.get('ordered_commands_canonical_sha256')==short['ordered_commands_canonical_sha256'] and short['ordered_commands_canonical_sha256']]
   samesource=[e for e in exactcmd if e.get('source5')==short['source5']]
   sameconfig=[e for e in samesource if e.get('effective_options_sha256')==short['effective_options_sha256']]
   short['relation_to_frozen_reference']=('SAME_SOURCE_COMMAND_CONFIG_EXACT_ENDPOINT' if sameconfig else ('SAME_SOURCE_COMMAND_DIFFERENT_MODE_OR_CONFIG' if samesource else ('SAME_INPUT_COMMAND_DIFFERENT_SOURCE5_KEEP_SEPARATE' if exactcmd else 'INPUT_SHA_MATCH_COMMAND_IDENTITY_CONFLICT_OR_UNAVAILABLE')))
   short['frozen_reference_same_command_cohorts']=[e['cohort'] for e in exactcmd]
  a=[e for e in ee if e['accepted']]
  q['current_accepted_endpoint_count']=len(a);q['current_unaccepted_endpoint_count']=len(ee)-len(a)
  q['current_measurement_state']='MEASURED_EXACT_INPUT_SEPARATE_SOURCE_CONFIG_STRATA' if a else ('ENGINEERING_OR_INPUT_IDENTITY_UNRESOLVED' if not r.get('input_identity_sha256') else ('MEASURED_UNACCEPTED_NO_PERFORMANCE_ACCEPTANCE' if ee else 'UNMEASURED_IN_DEFINED_CURRENT_ENDPOINT_SCOPE'))
  q['current_measurement_gaps']=['NEW_SOURCE_MECHANISM_FEATURES_NOT_AUTOMATICALLY_INHERITED_FROM_SOURCE78','NO_CROSS_SOURCE_PERFORMANCE_PAIRING'] if a else ['NO_CURRENT_ACCEPTED_ENDPOINT_IN_DEFINED_SCOPE']
  q['historical_features_preserved']=True;q['new_scientific_launch_grant']=False
  rows.append(q)
 groups=collections.defaultdict(list)
 for e in endpoints:
  if e['accepted']:
   key=sha(canon({k:e.get(k) for k in ['input_identity_sha256','source5','ordered_commands_canonical_sha256','mode','geometry','clock_domains','effective_options_sha256','observer_env_sha256']}))
   groups[key].append({'cohort':e['cohort'],'uuid':e['uuid'],'cycles':e.get('cycles')})
 v3v5={req:c for req,c in req_counts.items() if req in ['EP_L2_MID_TAG_850MHZ_V1_20261104','EP_L2_VECTOR1700_WV_DECOMPOSITION_V1_20261104','EP_L2_PFV4_A1_STENCIL_SOURCE78_850_L100_V1','EP_L2_PFV4_A3_TRANSPOSE_SOURCE78_850_L100_V1','EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104','EP_L2_PFV4_A2_3MM_SOURCE78_850_L100_V1','EP_L2_PFV5_A_FWT_G32W8_COLD_PROOF_MATCHED3_V1','EP_L2_PFV5_B1_VECTOR4M1700_PRESSURE_EPOCH_MATCHED_F_V1']}
 counts={'rows':len(rows),'content_group_rows':sum(bool(r['member_ordinary96']) for r in rows),'main35_rows':sum(bool(r['member_main35']) for r in rows),'main42_rows':sum(bool(r['member_main42']) for r in rows),'unresolved_slots':sum(not r.get('input_identity_sha256') for r in rows),'structured_native_endpoints':len(endpoints),'accepted_endpoints':sum(e['accepted'] for e in endpoints),'unaccepted_endpoints':sum(not e['accepted'] for e in endpoints),'distinct_exact_input_SHAs_with_accepted_results':len({e['input_identity_sha256'] for e in endpoints if e['accepted']}),'rows_with_accepted_results':sum(r['current_accepted_endpoint_count']>0 for r in rows),'input_sha_join_unmatched_endpoints':sum(e.get('input_identity_sha256') not in {r.get('input_identity_sha256') for r in rows} for e in endpoints),'accepted_identity_gap_endpoints':sum(bool(e['identity_gaps']) for e in endpoints if e['accepted'])}
 assert ref(REG)['sha256']==registry_initial_sha,'Registry changed during read-only snapshot; rerun metadata refresh'
 index={'schema':'UNIFIED_CURRENT_ENDPOINT_INDEX_V1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'All dict-consumed endpoints in current Native registry with owner EP-MAIN and project EP_L2; singleton earlier scopes and compatibility excluded explicitly. Not lifetime EP or all project global accepted count.','registry_ref':ref(REG),'counts':counts,'request_counts':req_counts,'V3_V4_V5_request_counts':v3v5,'endpoints':endpoints,'same_exact_full_identity_duplicates':[g for g in groups.values() if len(g)>1],'excluded_scopes':excluded,'source5_warning':'Legacy source_identity.archive_sha256 is static library body SHA, never a result archive SHA. Endpoint source5.library_sha256 is explicit.'}
 iref=write('CURRENT_ENDPOINT_INDEX.json',index)
 write('UPDATED_EVIDENCE_ROWS.json',{'schema':'UNIFIED_FROZEN103_EVIDENCE_REFRESH_V1','utc':index['utc'],'frozen_ref':ref(F),'frozen_counts_not_latest':frozen['counts'],'counts':counts,'endpoint_index_ref':iref,'join_policy':'Exact input SHA groups rows only. Every endpoint retains distinct Source5, full expected effective options SHA, mode, geometry, clock and ordered literal/canonical commandlist identity. No name join and no automatic performance pairing. Original features/reference endpoints preserved unchanged.','rows':rows,'new_scientific_starts':0,'budget_consumption':0,'registry_writes':0,'raw_or_trace_reads':0})
 write('IDENTITY_READ_MANIFEST.json',{'schema':'BOUNDED_METADATA_READ_MANIFEST_V1','max_file_bytes':MAX,'files':reads,'unique_files':len(reads),'unique_bytes':sum(x['bytes'] for x in reads.values()),'trace_or_raw_body_reads':0,'model_starts':0})
 print(json.dumps(counts))
if __name__=='__main__':main()
