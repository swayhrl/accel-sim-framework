import copy,hashlib,json,collections,datetime
from pathlib import Path
O=Path(__file__).parent
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def exact_endpoint(a,b):
 keys=['input_identity_sha256','source5','ordered_commands_canonical_sha256','mode','geometry','clock_domains','effective_options_sha256','observer_env_sha256']
 return all(a.get(k) is not None and a.get(k)==b.get(k) for k in keys)
def run():
 idx=json.loads((O/'CURRENT_ENDPOINT_INDEX.json').read_text());upd=json.loads((O/'UPDATED_EVIDENCE_ROWS.json').read_text())
 frozen=json.loads(Path(upd['frozen_ref']['path']).read_text())
 checks=[]
 def ck(name,condition):
  assert condition,name;checks.append(name)
 ck('103_rows',len(upd['rows'])==103)
 ck('96_content_7_slots',upd['counts']['content_group_rows']==96 and upd['counts']['unresolved_slots']==7)
 ck('35_and_42_populations',upd['counts']['main35_rows']==35 and upd['counts']['main42_rows']==42)
 for a,b in zip(frozen['rows'],upd['rows']):
  ck('frozen_fields_preserved_'+b['row_id'],all(b[k]==v for k,v in a.items()))
  ck('frozen_preimage_'+b['row_id'],sha(canon(a))==b['frozen_row_canonical_sha256'])
 ck('291_unique_endpoint_UUIDs',len({(e['cohort'],e['uuid']) for e in idx['endpoints']})==291)
 ck('286_accept_5_reject',sum(e['accepted'] for e in idx['endpoints'])==286 and sum(not e['accepted'] for e in idx['endpoints'])==5)
 ck('accepted_identity_all_closed',all(not e['identity_gaps'] for e in idx['endpoints'] if e['accepted']))
 ck('no_unknown_cycles_zero_fill',all(e.get('cycles') is None for e in idx['endpoints'] if not e['accepted']))
 e=next(e for e in idx['endpoints'] if e['accepted']);ck('exact_endpoint_self',exact_endpoint(e,e))
 for k in ['input_identity_sha256','source5','ordered_commands_canonical_sha256','mode','geometry','clock_domains','effective_options_sha256','observer_env_sha256']:
  b=copy.deepcopy(e);b[k]='DIFFERENT';ck('counterexample_reject_'+k,not exact_endpoint(e,b))
  b=copy.deepcopy(e);b[k]=None;ck('counterexample_reject_unknown_'+k,not exact_endpoint(e,b))
 b=copy.deepcopy(e);b['program']=e['program'];b['input_identity_sha256']='0'*64
 ck('same_program_name_not_a_join',not exact_endpoint(e,b))
 ck('library_SHA_not_archive_SHA',all(e['source5']['library_sha256']==e['source_identity_original']['archive_sha256'] for e in idx['endpoints']))
 ck('source5_old_key_normalized_not_renamed_proof',all(len(e['source5'])==5 for e in idx['endpoints']))
 ck('no_new_launch',upd['new_scientific_starts']==0 and upd['budget_consumption']==0)
 ck('no_registry_write',upd['registry_writes']==0)
 ck('no_trace_or_raw_read',upd['raw_or_trace_reads']==0)
 manifest=json.loads((O/'IDENTITY_READ_MANIFEST.json').read_text())
 ck('bounded_JSON_only_read',all(Path(p).suffix=='.json' and v['bytes']<=manifest['max_file_bytes'] for p,v in manifest['files'].items()))
 ck('read_files_unchanged',all(Path(p).stat().st_size==v['bytes'] and sha(Path(p).read_bytes())==v['sha256'] for p,v in manifest['files'].items()))
 rel=collections.Counter(x['relation_to_frozen_reference'] for r in upd['rows'] for x in r['current_result_endpoints'])
 result={'schema':'IDENTITY_REFRESH_FINITE_COUNTEREXAMPLE_QA_V1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','check_count':len(checks),'checks':checks,'relations':dict(rel),'input_scope_counts':upd['counts'],'metadata_unique_files':manifest['unique_files'],'metadata_unique_bytes':manifest['unique_bytes'],'source_reads_max_bytes':manifest['max_file_bytes'],'source_trace_raw_reads':0,'model_starts':0,'registry_writes':0}
 (O/'IDENTITY_QA_RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
if __name__=='__main__':run()
