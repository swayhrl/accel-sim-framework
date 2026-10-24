from pathlib import Path
import json,hashlib,collections,os,time
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
NAS=Path('/root/share/mnt164/huangrulin/traces')
T=NAS/'receipts/sm70_public_bootstrap_preparation_20261025_v1'
OUT=NAS/'receipts/sm70_public_suite_review_20261025_v1'
D=Path('/root/data/ep_l2_main_20261023_v1/worktree/docs/ep_l2/operations/sm70_public_runtime_r4_bootstrap_20261025_v1')
cache={}; rawmap={}; reads=[]
def sha(b): return hashlib.sha256(b).hexdigest()
def rd(ref):
 p=Path(ref['path']); assert str(p).startswith(str(NAS)+'/')
 if str(p) not in cache:
  with p.open('rb') as f: b=f.read(128*2**20+1)
  assert len(b)<=128*2**20 and sha(b)==ref['sha256'],str(p)
  rawmap[str(p)]=b; cache[str(p)]=json.loads(b)
  reads.append(dict(path=str(p),bytes=len(b),sha256=sha(b)))
 return cache[str(p)]
def put(p,b):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists(): assert p.read_bytes()==b,str(p)
 else:
  with p.open('xb') as f: f.write(b); f.flush(); os.fsync(f.fileno())
 assert p.read_bytes()==b
 return dict(path=str(p),bytes=len(b),sha256=sha(b))
cref=dict(path=str(T/'COMMIT_V3.json'),sha256='72f7004f48846a6bb27bea40718e46b23ae3b44eeeff6252f4d286a62e0ca3bb')
c=rd(cref); s=rd(c['prepared_template_ref']); report=rd(c['report_ref'])
previous=rd(c['prior_COMMIT_ref']); old=rd(previous['prepared_template_ref'])
assert set(s)==set(old) and {k for k in s if s[k]!=old[k]}=={'coverage_ref'}
assert c['metadata_only'] is True and c['activation'] is False and c['body_read_authorized'] is False
assert s['schema']=='SM70_BINDING_INTEGRATION_SPEC_V3_TEMPLATE_UNRESOLVED_NOT_EXECUTABLE'
assert s['body_reads_authorized'] is False and s['protected_after_ref'] is None
for k,v in s.items():
 if k.endswith('_ref') and v is not None: rd(v)
for ref in s['archive_audit_refs']: rd(ref)
for row in s['archives']: rd(row['source_manifest_ref'])
B=rd(s['base_all_bundles_ref']); O=rd(s['base_all_objects_ref'])
edges=sorted([b['bundle_id'],m['relative_path'],m['sha256'],m['size']] for b in B for m in b['members'])
assert (len(B),len(O),len(edges),sum(o['size'] for o in O.values()))==(125,22769,25149,972603859656)
assert {m[2] for m in edges}==set(O) and all(O[m[2]]['size']==m[3] for m in edges)
assert sha(('\n'.join(sorted(O))+'\n').encode())=='a007b5b9fd7e15bc06ca8a21421dcaa6d73e8aeaaa152611d9f291ed6a3ba11f'
assert sha((json.dumps(edges,separators=(',',':'))+'\n').encode())=='dfce715212f36408b272d21a9b6f5c6d22d97caa686ef12c8f00ce692f2c5e6f'
aliases={(a['host'],a['path'],b['extent']) for b in B for a in b['source_aliases']}
declared=rd(s['expected_aliases_ref'])
assert len(aliases)==len(declared)==442 and aliases=={(a['host'],a['path'],a['extent']) for a in declared}
coverage=rd(s['coverage_ref']); rows=coverage['rows']
actual=collections.Counter((b['suite'],b['program']) for b in B)
assert len(rows)==len(actual)==56 and {(r['suite'],r['program']):r['registered_assets'] for r in rows}==dict(actual)
assigned=[]
for row in rows:
 bs=[b for b in B if (b['suite'],b['program'])==(row['suite'],row['program'])]
 ids=sorted(b['bundle_id'] for b in bs); assert row['bundle_ids']==ids; assigned+=ids
 n=sum(b['extent']=='FRACTION_OR_TRIM_PATH' for b in bs)
 assert row['fraction_assets']==n and row['regular_assets']==len(bs)-n
 versions=row['source_version_distribution']
 assert len(versions)==len({b['version'] for b in bs}) and {v['source_version_evidence'] for v in versions}=={b['version'] for b in bs}
 for v in versions:
  vb=[b for b in bs if b['version']==v['source_version_evidence']]
  vn=sum(b['extent']=='FRACTION_OR_TRIM_PATH' for b in vb)
  assert v['bundle_ids']==sorted(b['bundle_id'] for b in vb)
  assert (v['registered_assets'],v['regular_assets'],v['fraction_assets'])==(len(vb),len(vb)-vn,vn)
assert len(assigned)==len(set(assigned))==125 and set(assigned)=={b['bundle_id'] for b in B}
assert (sum(r['regular_assets'] for r in rows),sum(r['fraction_assets'] for r in rows))==(100,25)
suites=dict(collections.Counter(b['suite'] for b in B))
assert suites=={'Rodinia':64,'CUDA Samples':18,'PolyBench/GPU':29,'Parboil':14}
rd(coverage['prior_family_coverage_and_gap_snapshot_ref'])
for ref in coverage['original_source_version_denominator_statistics_refs']: rd(ref)
assert coverage['issues_ref_unchanged']==s['issues_ref']==old['issues_ref']
assert set(s['architecture_by_sha'])==set(O)
kernel_ids={e[2] for e in edges if e[1]!='kernelslist.g'}
assert len(kernel_ids)==22681 and all(s['architecture_by_sha'][h]=='70' for h in kernel_ids)
assert all(s['architecture_by_sha'][h] is None for h in set(O)-kernel_ids)
prior20=rd(s['prior20_ref'])['assets']
old20=json.loads((NAS/'catalog/DTC_V100_ALL20_CURRENT_READBACK_20261025_V1.json').read_text())
assert len(prior20)==20 and {x['asset_id'] for x in prior20}=={x['asset_id'] for x in old20['assets']}
expectations=rd(s['archive_identity_expectations_ref'])
assert len(expectations)==4 and {x['receipt_sha256'] for x in expectations}=={x['sha256'] for x in s['archive_audit_refs']}
for x in expectations:
 audit=rd(next(ref for ref in s['archive_audit_refs'] if ref['sha256']==x['receipt_sha256']))
 for k in ['archive_identity','archive_path','archive_sha256','source_host']: assert audit[k]==x[k]
 assert audit['decoded_compression_EOF_integrity_checked'] is True and audit['source_before_after_unchanged'] is True and audit['source_writes']==0
assert len({(x['source_host'],x['archive_path'],json.dumps(x['archive_identity'],sort_keys=True)) for x in expectations})==4
payload=dict(schema='ROOT_REAL_BOOTSTRAP_V3_METADATA_ACCEPTANCE_V1',
 status='PASS_PREPARED_METADATA_EXACT125_COVERAGE_CORRECTION_ONLY_NOT_ACTIVATION',
 observed_unix=time.time(),bootstrap_commit_ref=cref,prepared_template_ref=c['prepared_template_ref'],
 coverage_ref=s['coverage_ref'],correction_report_ref=c['report_ref'],verified_public_metadata_refs=reads,
 metadata_bytes_read=sum(x['bytes'] for x in reads),
 scope=dict(assets=125,objects=22769,declared_members=25149,unique_bytes=972603859656,source_aliases=442,exact_suite_program_keys=56,ordinary=100,fraction=25,suites=suites,prior_assets=20,distinct_archive_identities=4,historical_sm70_kernel_object_evidence=22681,commandlist_objects_no_isa_claim=88),
 coverage_finding_ref=dict(path=str(R/'control/PARENT_REAL_BOOTSTRAP_COVERAGE_FINDING_V1.json'),sha256=sha((R/'control/PARENT_REAL_BOOTSTRAP_COVERAGE_FINDING_V1.json').read_bytes())),
 coverage_finding_resolved=True,all_version_distributions_and_bundle_assignments_independently_recomputed=True,
 template_only_coverage_ref_changed=True,original_coverage_and_issues_preserved=True,
 trace_payload_bytes_read=0,target_trace_stats=0,public_CURRENT_or_command_changed=False,
 source_or_science_changed=False,goal_complete=False,
 pending=['Actual Source2 closed complete SHA/COMMIT metadata and final relocation','Final immutable-tool after and mutable-authority external-change snapshots','Fresh exact install and activation preimages/grants','Actual 3cwd all-member validation and whole22769 Native restore and final audit'])
raw=(json.dumps(payload,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
refs=[put(R/'control/PARENT_REAL_BOOTSTRAP_V3_METADATA_ACCEPTANCE_V1.json',raw),
 put(OUT/'PARENT_REAL_BOOTSTRAP_V3_METADATA_ACCEPTANCE_V1.json',raw),
 put(D/'ROOT_REAL_BOOTSTRAP_V3_METADATA_ACCEPTANCE.json',raw)]
for name,ref in [('BOOTSTRAP_COMMIT_V3.json',cref),('UNRESOLVED_PRODUCTION_TEMPLATE_V3.json',c['prepared_template_ref']),('EXACT125_COVERAGE_V3.json',s['coverage_ref']),('COVERAGE_CORRECTION_REPORT_V3.json',c['report_ref'])]:
 put(D/name,rawmap[ref['path']])
print(json.dumps(dict(receipts=refs,scope=payload['scope'],metadata_bytes_read=payload['metadata_bytes_read'],ref_count=len(reads)),ensure_ascii=False))
