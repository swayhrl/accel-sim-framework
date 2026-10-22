from pathlib import Path
import json,sys,hashlib,importlib.util,time
E=Path.cwd();P=E/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1';A=P/'approved_four_r1';C=Path('/tmp/e2_positive_ro_successor_candidate');sys.path.insert(0,str(E/'util/ep_l2/mechanism_e'));from coordinator import Coordinator,canonical
spec=importlib.util.spec_from_file_location('candidate_successor_manifest_builder',C/'detach_successor.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
read=lambda p:json.loads(Path(p).read_bytes());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ref=lambda p:{'path':str(p),'sha256':sha(p)}
i=Coordinator().snapshot();d=read('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json');assert d['mechanism_study_20261019_v1']==i and i['actual_starts']==51
approval=read(A/'USER_APPROVAL.json');ready=read(A/'QUALIFICATIONS_READY.json');proposal=P/'conditional_followup/PRIMARY_FOUR_EXISTING_POSITIVE_RO_r1/PROPOSAL.json';conditions={}
for row in ready['conditions']:
 s=read(row['spec_ref']['path']);q=read(row['qualification']['path']);content={}
 def add(p):
  p=Path(p)
  if p.is_file() and p.stat().st_size<4*2**20:content[str(p)]=ref(p)
 def collect(x):
  if isinstance(x,list):
   for z in x:collect(z)
  elif isinstance(x,dict):
   if 'path' in x and 'sha256' in x:add(x['path'])
   if 'evidence_path' in x:add(x['evidence_path'])
   for z in x.values():collect(z)
 for x in s['configs']+s['auxiliary_assets']:add(x['path'])
 collect(q);add(A/'FROZEN_RUNTIME_PHYSICAL_RECHECK.json')
 conditions[s['condition_id']]={'selection_id':s['selection_id'],'resources':{k:s[k] for k in ['cpu','memory_bytes','maximum_result_bytes']},'identity':s['identity'],'spec_ref':row['spec_ref'],'spec_sha256':mod.spec_sha(s),'qualification':row['qualification'],'parser':s['parser'],'content_refs':list(content.values())}
m={'schema':'E2_EXACT_POSITIVE_RO_FOUR_SUCCESSOR_V1','status':'E_SOURCE_BOUND_PRIMARY_FOUR_SEALED','synthetic_fixture':False,'campaign_id':approval['campaign_id'],'baseline_actual_starts':51,'maximum_new_actual_starts':4,'condition_order':approval['approved_conditions'],'batch_id':approval['batch_id'],'source_identity':approval['source_identity'],'approval_ref':ref(A/'USER_APPROVAL.json'),'proposal_ref':ref(proposal),'validation_scope':read(A/'common/VALIDATION_SCOPE.json'),'historical51_seal':mod.historical51_seal(i,d),'pairs':[],'endpoint_result_hardcap_bytes':384*2**20,'all_four_endpoint_results_hardcap_bytes':1536*2**20,'conditions':conditions}
p=A/'FINAL_MANIFEST.json';p.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n');scope=mod.Scope(ref(p));scope.manifest()
for row in ready['conditions']:scope.check_spec(read(row['spec_ref']['path']))
print(json.dumps({'final_manifest_ref':ref(p),'bound_conditions':len(conditions),'original51_actual':i['actual_starts'],'newQ_registered':False,'newstarts':0}))
