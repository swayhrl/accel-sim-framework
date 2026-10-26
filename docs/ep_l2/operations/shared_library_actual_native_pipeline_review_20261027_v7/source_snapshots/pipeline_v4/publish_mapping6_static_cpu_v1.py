"""Exact frozen CPU artifact emitter; never executes workload or foreign code."""
import json,hashlib,pathlib
PRODUCER='ROOT_MAPPING6_INDEPENDENT_STATIC_FACTS_V1'
PROFILE='EXACT6_RAW_ELF_OWNER_PC_PLR_CPU_V1'
GATES=['EXACT_STATIC_METADATA_REOPEN_OR_NEW_PROOF','COMPLETE_STATIC_MAP_METADATA_OR_ERROR_REPAIR','EXACT_MAPPING_REPAIR_WITH_NEGATIVE_REGRESSION']
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def emit(contract_ref,output):
 output=pathlib.Path(output);need_root=pathlib.Path(__file__).resolve().parent
 if not output.resolve().is_relative_to(need_root)or output.exists():raise ValueError('private absent output required')
 p=pathlib.Path(contract_ref['path']);raw=p.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=contract_ref['sha256']or len(raw)!=contract_ref['bytes']:raise ValueError('contract pin')
 c=json.loads(raw)
 if c['schema']!='ROOT_EXACT6_STATIC_REPAIR_ADDITIVE_DEPENDENCY_CONTRACT_V1'or len(c['rows'])!=6:raise ValueError('exact six')
 source=sha(__file__);evidence=[contract_ref,c['current_binary6_attestation_ref'],c['independent_static_report_ref']]
 for r in evidence:
  raw=pathlib.Path(r['path']).read_bytes()
  if hashlib.sha256(raw).hexdigest()!=r['sha256']or len(raw)!=r['bytes']:raise ValueError('fresh evidence pin')
 output.mkdir();refs=[]
 for r in c['rows']:
  q=r['queue_id'];doc={'schema':'AUTO161_ARTIFACT_V1','producer_id':PRODUCER,'profile':PROFILE,'producer_source_sha256':source,'status':'PASS','provided_gates':GATES,'next_stage':r['new_mapping_primary_next'],'target_queue_ids':[q],'row_bindings':{q:r['frozen_row_sha256']},'family_keys':[],'evidence':evidence,'requires':[],'qualification_granted':False,'gpu_executed':False,'historical_queue_mutated':False,'simulation_executed':False,'consumer_qualified':False,'science_qualified':False,'trace_qualified':False,'contract_additions_required':True}
  target=output/(hashlib.sha256(q.encode()).hexdigest()+'.json');raw=(json.dumps(doc,sort_keys=True,separators=(',',':'))+'\n').encode();target.write_bytes(raw);refs.append({'path':str(target),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
 return refs
