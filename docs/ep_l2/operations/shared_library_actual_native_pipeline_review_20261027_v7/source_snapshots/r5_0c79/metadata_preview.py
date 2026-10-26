"""Root-frozen real-scope metadata preview: never target stat/body, never publication."""
from pathlib import Path
import json,hashlib,collections,gzip
def canonical(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def need(x,msg):
 if not x:raise RuntimeError('METADATA_PREVIEW_HOLD_'+msg)
def preview(r,spec,resources):
 stage=r.load_verified('stages')
 objects,_=stage.ref_read(spec['base_all_objects_ref'],resources)
 bundles,_=stage.ref_read(spec['base_all_bundles_ref'],resources)
 contract,_=stage.ref_read(spec['scope_contract_ref'],resources)
 need(spec['base_all_objects_ref']['sha256']==contract['all_objects_raw_sha256']=='85b0d7a4866d58852d8541f6d46bf95ed77c4c47983904ca687334527be7cb17','ACTUAL_BASE_OBJECTS')
 need(spec['base_all_bundles_ref']['sha256']==contract['all_bundles_raw_sha256']=='7ebb0949d9f81cd47d1d0cc4abab0596318babd6eafb2fb3295e8b0325182cc6','ACTUAL_BASE_BUNDLES')
 edges=[];used=set();bids=set()
 for b in bundles:
  need(b['bundle_id']not in bids,'DUP_BUNDLE');bids.add(b['bundle_id']);names=set()
  for m in b['members']:
   need(m['relative_path']not in names,'DUP_MEMBER');names.add(m['relative_path'])
   need(objects[m['sha256']]['size']==m['size'],'MEMBER_SIZE');used.add(m['sha256']);edges.append([b['bundle_id'],m['relative_path'],m['sha256'],m['size']])
 need(used==set(objects)and sorted(bids)==contract['expected_bundle_ids'],'EXACT_REFERENCE_CLOSURE')
 need(digest(('\n'.join(sorted(objects))+'\n').encode())==contract['expected_object_id_set_sha256'],'EXACT_OBJECT_SET')
 need(digest(canonical(sorted(edges)))==contract['expected_member_reference_graph_sha256'],'EXACT_MEMBER_GRAPH')
 need(len(objects)==22769 and len(bundles)==125 and len(edges)==25149 and sum(o['size']for o in objects.values())==972603859656,'EXACT_COUNTS_BYTES')
 source_map,_=stage.ref_read(spec['source_relocation_ref'],resources)
 proofs,_=stage.ref_read(spec['current_proof_index_ref'],resources)
 need(len(proofs)==1183,'FULL_REUSED_EVIDENCE_SET')
 resolver=r.Relocation(source_map['root'],source_map['mapping'],strict=True)
 legacy={x['root']:x for x in spec['legacy_routes']};chain_status={};proof_count=0;legacy_count=0;binding_encoded_bytes=0;history_encoded_bytes=0
 with r.Operation(resolver,resources)as op:
  for key,ref in proofs.items():
   doc=op.checked_ref(ref);o=objects[key]
   if doc.get('schema')=='ORIGINAL20_CURRENT_TRUE164_NAS_READBACK_V1':
    row=next(x for x in doc['members']if x['path']==o['storage']['path']and x['expected_sha256']==key)
    observed=dict(canonical_path=row['path'],mtime_ns=row['after']['mtime_ns'])
   else:observed=dict(canonical_path=doc['canonical_path'],mtime_ns=doc['current_after']['mtime_ns'])
   op.proof(ref,key,o['size'],observed);proof_count+=1
  for key,o in objects.items():
   path=Path(o['storage']['path']).absolute();root=next(x.parent for x in path.parents if x.name=='tree');rootstr=str(root)
   if rootstr in legacy:
    route=legacy[rootstr];pr=route['original_current_proofrefs'][key];doc=op.checked_ref(pr)
    row=next(x for x in doc['members']if x['path']==str(path)and x['expected_sha256']==key)
    h=r.legacy_declaration(op,key,o,route,dict(canonical_path=str(path),mtime_ns=row['after']['mtime_ns']))
    need(h['historical_Native_restore_claim_not_created']is True,'LEGACY_SCOPE');legacy_count+=1
   else:
    if rootstr not in chain_status:
     chain_status[rootstr]='PENDING_CLOSED_CHAIN_NOT_IN_FROZEN_METADATA_SNAPSHOT'if str(root/'COMMIT.json')not in source_map['mapping']else'CLOSED_STANDARD_METADATA_CHAIN'
    if chain_status[rootstr]=='CLOSED_STANDARD_METADATA_CHAIN':h=op.historical(key,o)
    else:
     # Size-only template is not a proof and is never saved as a binding.
     names=['COMMIT.json','SOURCE_MANIFEST.json','RECEIPT.json','TREE_VERIFICATION.json','RANGE_INDEX.json']
     h=dict(status='UNQUALIFIED_SIZE_ESTIMATE_PENDING_CHAIN',canonical_path=str(path),member=str(path.relative_to(root/'tree')),content_sha256=key,bytes=o['size'],references=[dict(path=str(root/n),sha256='0'*64)for n in names],commit_object_id='0'*20)
   history_encoded_bytes+=len(canonical(h))
   remote='/home/shared/'+str(path.relative_to('/root/share/mnt164'))
   # Upper digit widths are labels solely for serialized-size estimation.
   stable=dict(endpoint='admin-wcx@10.208.130.164:/home/shared',remote_path=remote,canonical_path=str(path),type='file',size=o['size'],mtime_ns=9223372036854775807,mode=4095)
   b=dict(schema='SM70_TARGET_BINDING_V2',base_all_objects_sha256=spec['base_all_objects_ref']['sha256'],sha256=key,size=o['size'],storage_kind=o['storage']['kind'],stable_metadata=stable,historical=h,current_full_SHA_reference=proofs.get(key),current_full_SHA_scope='PATH_EXACT_REUSED_REQUALIFICATION'if key in proofs else'ORIGINAL_NEW_CAS_CLOSED_COMMIT_CHAIN',science_context_unchanged=True,inode_diagnostics=dict(frozen_expected_identity=o['storage'].get('expected_identity'),admission_observed_inode=9223372036854775807,dev=9223372036854775807),binding_id='0'*64)
   binding_encoded_bytes+=len(canonical(key))+len(canonical(b))+1
  stats=op.stats
 assets=r.enrich_assets(bundles,{})
 provenance={k:o['sources']for k,o in objects.items()}
 size_estimate=dict(binding_member_upper_digit_encoding_bytes=binding_encoded_bytes,historical_embedded_bytes=history_encoded_bytes,assets_bytes=len(canonical(assets)),source_provenance_bytes=len(canonical(provenance)),relocation_bytes=len(canonical(source_map)),base_all_objects_bytes=spec['base_all_objects_ref'].get('bytes',32293623),base_all_bundles_bytes=5438127,not_an_overlay_or_binding=True,unknown_mode_inode_mtime_not_claimed=True,pending_chain_template_not_evidence=True)
 size_estimate['catalog_envelope_estimated_upper_digit_bytes']=binding_encoded_bytes+size_estimate['assets_bytes']+size_estimate['source_provenance_bytes']+size_estimate['relocation_bytes']+len(canonical(spec['legacy_routes']))+65536

 return dict(status='PASS_EXACT_REAL_SCOPE_METADATA_ONLY_NOT_BINDING_APPROVAL',assets=125,objects=22769,declared_members=25149,distinct_bytes=972603859656,suite_counts=dict(collections.Counter(b['suite']for b in bundles)),reused_original_receipt_schemas=proof_count,legacy_members=legacy_count,chain_status=chain_status,operation_stats=stats,metadata_size_estimate=size_estimate,target_trace_stat_calls=0,target_trace_body_bytes=0,new_Native_restore=False,actual_mode_or_uid_sampling_not_performed=True,publication_performed=False,production_binding_complete=False,scientific_qualification_granted=False)
