from pathlib import Path
import json,hashlib,collections,time,os
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');N=Path('/root/share/mnt164/huangrulin/traces')
names=['ALL_BUNDLES.json','ALL_OBJECTS.json','INPUT_ALIASES_FROM_AUDIT.json','ARCHIVE_FROZEN_BUDGET.json','EXPANDED_FROZEN_BUDGET.json']
raw={n:(R/'control'/n).read_bytes() for n in names};data={n:json.loads(b) for n,b in raw.items()}
bundles=data['ALL_BUNDLES.json'];objects=data['ALL_OBJECTS.json'];expected=data['INPUT_ALIASES_FROM_AUDIT.json']
assert len({b['bundle_id'] for b in bundles})==len(bundles)
seen=set();ids=set();member_count=0;by_suite=collections.defaultdict(collections.Counter);asset_rows=[]
for b in bundles:
 bid=b['bundle_id'];assert len(bid)==64 and all(c in '0123456789abcdef' for c in bid)
 rels=[m['relative_path'] for m in b['members']]
 assert len(rels)==len(set(rels)) and rels.count('kernelslist.g')==1
 for m in b['members']:
  p=Path(m['relative_path']);assert not p.is_absolute() and '..' not in p.parts and '\\' not in str(p)
  assert m['sha256'] in objects and m['size']==objects[m['sha256']]['size'];member_count+=1
 assert all(k in set(rels) for k in b['ordered_kernel_members'])
 for a in b['source_aliases']:seen.add((a.get('host'),a.get('path'),b['extent']))
 by_suite[b['suite']][b['extent']]+=1;ids.add(bid)
 asset_rows.append({'bundle_id':bid,'suite':b['suite'],'source_version_evidence':b['version'],'program':b['program'],'extent':b['extent'],'declared_members':len(rels),'kernel_launches':len(b['ordered_kernel_members']),'logical_bytes':sum(m['size'] for m in b['members']),'source_alias_count':len(b['source_aliases']),'publication_state':'PLAN_ONLY_NOT_PUBLIC_READY'})
missing=[(a['host'],a['path'],a['extent']) for a in expected if (a['host'],a['path'],a['extent']) not in seen];assert not missing,missing
prior=json.loads(Path('/root/data/ep_dtc_trace_migration_20261024_v1/controls/ASSET_CATALOG.json').read_text())['assets']
prior_missing=[p.get('id',str(i)) for i,p in enumerate(prior) if not any(set(p['aliases']).intersection(b.get('prior_asset_aliases',[])) for b in bundles)]
assert not prior_missing,prior_missing
batches=collections.Counter(o['storage'].get('batch_id') for o in objects.values() if o['storage'].get('batch_id'))
batch_states=[]
for bid,count in sorted(batches.items()):
 p=N/'bundles/_payload'/bid
 present=(p/'COMMIT.json').is_file()
 if present:
  commit=json.loads((p/'COMMIT.json').read_text());assert commit['schema']=='IMMUTABLE_MULTI_MEMBER_TRACE_INPUT_COMMIT_V1'
 batch_states.append({'batch_id':bid,'objects_in_plan':count,'commit_present':present})
q=json.loads((R/'control/PUBLIC_WRAPPER_QUALIFICATION.json').read_text())
source_sha=hashlib.sha256((R/'tools/trace_assets_public.py').read_bytes()).hexdigest()
assert source_sha==q['script_sha256'],'public script changed after synthetic qualification'
no_conflicts=True
for b in bundles:
 m=N/'bundles'/b['bundle_id']/'MANIFEST.json'
 if m.exists():
  old=json.loads(m.read_text());assert old['bundle_id']==b['bundle_id'] and old['members']==b['members']
result={'schema':'SHARED_SM70_PUBLICATION_PREFLIGHT_V1','status':'PASS_PLAN_CLOSURE_PUBLICATION_STILL_PENDING_TRANSFERS','observed_unix':time.time(),'frozen_inputs':{n:{'sha256':hashlib.sha256(v).hexdigest(),'bytes':len(v)} for n,v in raw.items()},'planned_assets':len(bundles),'unique_objects':len(objects),'unique_content_bytes':sum(o['size'] for o in objects.values()),'declared_member_references':member_count,'expected_complete_aliases':len(expected),'missing_expected_aliases':missing,'prior_assets_covered':len(prior),'missing_prior_aliases':prior_missing,'unsafe_or_duplicate_member_names':0,'unknown_or_size_mismatched_object_references':0,'publication_manifest_conflicts':0,'by_suite_extent':{k:dict(v) for k,v in by_suite.items()},'transfer_batches':batch_states,'public_source_matches_synthetic_qualification':True,'public_source_sha256':source_sha,'assets':asset_rows,'claim_limit':'Plan-closure preflight only. No full object SHA re-read, no data publication or Source writes, no scientific qualification or budget changes. Current incomplete archive batches remain incomplete.'}
out=R/'control/PUBLICATION_PLAN_CLOSURE_PREFLIGHT_V1.json';payload=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode()
assert not out.exists(),'preflight exists; preserve existing'
with out.open('xb') as f:f.write(payload);f.flush();os.fsync(f.fileno())
print(json.dumps({k:v for k,v in result.items() if k not in ['assets','frozen_inputs','transfer_batches']}))
print('pending_batches',[b for b in batch_states if not b['commit_present']]);print('receipt_sha256',hashlib.sha256(payload).hexdigest())
