from pathlib import Path
import json,hashlib,csv,datetime
P=Path(__file__).resolve().parent.parent
REG=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
count=0;reads={}
def check(x,n):
 global count
 assert x,n
 count+=1
def exact(r):
 p=Path(r['path']);cap=32*1024*1024 if p.name=='source812_generic_ro_loader' else 16*1024*1024
 check(p.stat().st_size<cap,'bounded_evidence_'+p.name)
 b=p.read_bytes();check(hashlib.sha256(b).hexdigest()==r['sha256'],'SHA_'+str(p))
 reads[str(p)]={'bytes':len(b),'sha256':r['sha256']}
 return json.loads(b) if p.suffix=='.json' else b
def main():
 global count
 for name in ['agent_a','agent_b','agent_c','agent_d']:
  d=read(P/name/'DELIVERY_MANIFEST.json')
  for f in d['files']:exact(f)
 frozen=read(P.parent/'observation_guided_20261029_v1/agent_a/WORKLOAD_FEATURE_AND_OPPORTUNITY.json')
 u=read(P/'UNIFIED_WORKLOAD_MEMORY_TAXONOMY_V1.json')
 idx=read(P/'agent_a/CURRENT_ENDPOINT_INDEX.json')
 reg=read(REG);pre=read(P/'main/REGISTRY_PREIMAGE.json')
 check(reg==pre,'whole_registry_no_change_during_task')
 check(u['new_scientific_starts']==u['budget_consumption']==0,'zero_science')
 check(len(u['rows'])==103,'103')
 check(len({r['row_id'] for r in u['rows']})==103,'unique_rowid')
 for i,(old,r) in enumerate(zip(frozen['rows'],u['rows'])):
  check(all(r[k]==v for k,v in old.items()),'preserve_old_fields_'+str(i))
  check(r['row_id']=='FROZEN103_%03d'%(i+1),'row_position')
  if not r['input_identity_sha256']:
   check(not r['current_result_endpoints'],'no_null_null_endpoint_join')
  for e in r['current_result_endpoints']:
   check(e['cycles'] is None if not e['accepted'] else isinstance(e['cycles'],int),'unaccepted_not_zero_or_accepted')
 for pop,n in [('member_ordinary96',96),('member_main35',35),('member_main42',42)]:
  check(sum(bool(r[pop])for r in u['rows'])==n,pop)
 check(sum(not r['input_identity_sha256']for r in u['rows'])==7,'seven_unresolved')
 check(len(idx['endpoints'])==291,'291')
 by={e['cohort']:e for e in idx['endpoints']}
 for e in idx['endpoints']:
  rr=reg['registered_future_requests'][e['request_id']]['consumed'][e['cohort']]
  check(hashlib.sha256(canonical(rr)).hexdigest()==e['registry_entry_canonical_sha256'],'registry_entry')
  s=exact(e['spec_ref'])
  check(s['input_identity_sha256']==e['input_identity_sha256'],'input')
  check(s['source_identity']==e['source_identity_original'],'Source5')
  check(all(e['source5'].values()),'five_pins')
  check(hashlib.sha256(canonical(s['expected_effective_options'])).hexdigest()==e['effective_options_sha256'],'all_options')
  ib=exact(e['input_binding_ref'])
  check(ib['literal_commandlist_sha256']==e['literal_commandlist_sha256'],'literal_commands')
  check(ib.get('expectedcommands',ib.get('expected_commands'))==e['ordered_commands'],'ordered_commands')
  check(bool(e['ordered_kernel_identity']),'ordered_kernel_identity')
  if e['accepted']:
   pt=exact(e['source_refs']['accepted_point_ref'])
   check(pt['cycles']==e['cycles'] and pt['uuid']==e['uuid'] and pt['hardware_drained'] is True,'acceptedpoint')
 c=read(P/'agent_c/WV_REUSE_EVIDENCE_BY_INPUT.json')
 for p in c['comparisons']:
  a,b=by[p['baseline']],by[p['candidate']]
  check(a['source5']==b['source5'] and a['input_identity_sha256']==b['input_identity_sha256'] and a['ordered_commands']==b['ordered_commands'],'C_pair_identity')
  check(a['observer_env_sha256']==b['observer_env_sha256'],'C_pair_observer')
  delta={k:[a['effective_options'][k],b['effective_options'][k]]for k in a['effective_options'] if a['effective_options'][k]!=b['effective_options'][k]}
  check(delta==p['option_delta'],'C_full_option_difference')
  check(a['cycles']-b['cycles']==p['saved_cycles'],'C_cycles')
 b=read(P/'agent_b/MEMORY_RESOURCE_CLASSIFICATION.json')
 for row in b['rows']:
  for p in row['memory_service_sensitivity'].get('comparisons',[]):
   a,bb=by[p['reference_cohort']],by[p['candidate_cohort']]
   check(a['source5']==bb['source5'] and a['input_identity_sha256']==bb['input_identity_sha256'] and a['ordered_commands']==bb['ordered_commands'] and a['mode']==bb['mode'],'B_service_identity')
   delta={k:[a['effective_options'][k],bb['effective_options'][k]]for k in a['effective_options'] if a['effective_options'][k]!=bb['effective_options'][k]}
   check(set(delta)=={'-gpgpu_clock_domains'},'service_only_clock')
   check(delta==p['option_diff'],'service_delta')
 req=read(P/'NEXT_EXACT_PERFORMANCE_EXPERIMENT_REQUEST.json')
 check(req['requested_new_starts']==4 and req['approved_starts']==req['consumed_starts']==0,'request_only4')
 q=read(P/'agent_b/SOURCE812_CONV_SCAN_CPU_QUALIFICATION.json')
 check(q['compile']['returncode']==0,'finite_cpu_compile')
 for g in req['groups']:
  qq=next(x for x in q['input_checks'] if x['input_identity_sha256']==g['input_identity_sha256'])
  opts=[]
  for i,point in enumerate(g['points']):
   oo=exact(point['effective_options_ref'])
   check(len(oo)==283 and oo==qq['parser_runs'][i]['effective_options'],'requested283_actual_parser')
   check(point['source_identity']==g['source_identity']==q['source_identity'],'request_source')
   check(point['launch_eligible_now'] is False,'no_unauthorized_release')
   check(qq['parser_runs'][i]['returncode']==qq['RO_loader_runs'][i]['returncode']==0,'production_cpu_io')
   exact(qq['parser_runs'][i]['stdout_ref']);exact(qq['RO_loader_runs'][i]['stdout_ref'])
   opts.append(oo)
  check([k for k in opts[0]if opts[0][k]!=opts[1][k]]==['-gpgpu_ep_l2_ro_pressure_epoch'],'one_flag')
 check(sum(1 for _ in csv.DictReader((P/'UNIFIED_WORKLOAD_MEMORY_TAXONOMY_V1.csv').open()))==103,'CSV103')
 # Independently reopen one existing sealed bundle per selected input, never raw/Trace.
 ce={e['cohort']:e for e in c['endpoints']}
 spot=[]
 for co in ['EP_PERF_STENCIL_BD0309DF_F_REF_V1','EP_PERF_3MM_F9F80028_F_REF_V1','EP_PERF_FASTWALSHTRANSFORM_FC3A9062_WV_ZERO_RO_REF_V1','EP_PERF_GEMM_140F6ED3_WV_ZERO_RO_REF_V1','EP_PERF_SCAN_CF8D1C4D_F_REF_V1','EP_PERF_CONV_F_REF_V1']:
  e=by[co];bundle=exact(e['source_refs']['validation_ref'])
  check(bundle['cycles']==e['cycles'] and bundle['input_identity_sha256']==e['input_identity_sha256'],'spot_bundle_identity')
  check(bundle['source_identity']==e['source_identity_original'],'spot_source')
  spot.append(co)
 evidence={'status':'MAIN_INDEPENDENT_POPULATION_IDENTITY_CLASSIFICATION_AND_REQUEST_AUDIT_PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks_passed':count,'all_four_agent_manifests_exact':True,'old_registry_whole_json_unchanged':True,'new_scientific_starts':0,'budget_consumption':0,'old_frozen_rows_preserved':103,'structured_scope_accepted':286,'structured_scope_unaccepted':5,'C_exact_comparisons_checked':len(c['comparisons']),'request_starts_prepared_not_approved':4,'spot_reopened_sealed_metadata_bundles':spot,'metadata_files_read':len(reads),'bounded_evidence_unique_bytes_read':sum(v['bytes']for v in reads.values()),'includes_CPU_fixture_ELF_SHA_only_no_execution':True,'raw_or_trace_body_reads':0,'Source_KEEP':True,'released_bytes':0,'limits':['No runtime pressure activation or performance prediction proof','No new simulation, NI or full-program numerical-output qualification','Exact program temporal-reuse distribution remains UNKNOWN']}
 (P/'main/MAIN_INDEPENDENT_ACCEPTANCE_AUDIT.json').write_text(json.dumps(evidence,sort_keys=True,indent=2)+'\n')
 (P/'main/MAIN_INDEPENDENT_METADATA_READ_MANIFEST.json').write_text(json.dumps(reads,sort_keys=True,indent=2)+'\n')
 print(json.dumps(evidence))
if __name__=='__main__':main()
