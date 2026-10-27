"""Assemble verified reports; no model/controller access. Archive and Git differ explicitly."""
import hashlib
import json
from pathlib import Path
import zipfile

R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=set()
def include(p):
 p=p.resolve()
 if R.resolve()not in p.parents:raise ValueError('OUTSIDE_ANALYSIS:'+str(p))
 if not p.is_file():raise FileNotFoundError(p)
 files.add(p)
def manifest(agent,name):
 base=R/'agents'/agent;p=base/name;d=read(p);include(p)
 entries=d.get('files',d)
 if isinstance(entries,dict):entries=[dict(v,name=k)for k,v in entries.items()]
 for e in entries:
  q=base/e.get('name',e.get('path'));assert sha(q)==e['sha256'],str(q);include(q)
for a,n in [('A','MANIFEST.json'),('B','DELIVERY_MANIFEST.json'),('C','DELIVERY_MANIFEST.json'),('D','DELIVERY_MANIFEST.json'),('E','DELIVERY_MANIFEST.json'),('F','MANIFEST.json')]:manifest(a,n)
manifest('E','LATEST_MANIFEST_SUPPLEMENT.json')
for a,n in [('D','ARCHIVE_READBACK.json'),('F','ARCHIVE_RECEIPT.json')]:
 p=R/'agents'/a/n
 if p.exists():include(p)
for n in ['build_latest_addendum.py','sync_reconciliation.py','MANIFEST_IDENTITY_RECONCILIATION.json','DELIVERY_MANIFEST_WINDOWS_ORIGINAL_BYTES.json','DELIVERY_MANIFEST_164_ORIGINAL_BYTES.json']:
 p=R/'agents/E'/n
 if p.exists():include(p)
include(R/'agents/B/METADATA.json')
for p in(R/'shared_address_index').glob('*.json'):include(p)
for p in(R/'coordinator').iterdir():
 if p.is_file()and p.suffix in ['.py','.json']:include(p)
for n in ['README.md','REQUEST.txt','AGENT_EXECUTION.json','FOLLOWUP_CONTRACTS.json']:include(R/n)
inputs=R/'inputs';inputs.mkdir(exist_ok=True)
for n in ['DTC_P42_PERFORMANCE.json','DTC_P42_LEDGER_AUDIT.json','DTC_P42_REPRESENTATIVE_FREEZE.json','DTC_P42_MODEL_COMPARABILITY.json']:
 p=inputs/n;p.write_bytes((Path('D:/repo/tmp')/n).read_bytes());include(p)

archive_only={'agents/B/METADATA.json','agents/B/METADATA_LIGHT.json','agents/B/INDEPENDENT_FEATURE_FREEZE_INITIAL_NO_ADDRESS.json',
 'agents/C/ORIGINAL_SOURCE_FILES.json','agents/D/DOWNSTREAM_SOURCE_FILES.json',
 'agents/E/ALLOWED_OBSERVATION_SNAPSHOT.json','agents/E/CLOSED_ACCEPTED_RECEIPTS_SNAPSHOT.json','inputs/DTC_P42_LEDGER_AUDIT.json'}
def rel(p):return p.relative_to(R).as_posix()
def in_git(p):return rel(p)not in archive_only and p.suffix!='.gz'
all_entries=[{'path':rel(p),'sha256':sha(p),'bytes':p.stat().st_size,'Git':in_git(p)}for p in sorted(files)]
policy={'schema':'DTC_PARALLEL_REVIEW_PUBLICATION_POLICY_V1','archive_root':'/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_p42_parallel_mechanism_review_v1/assembled_v1',
 'Git_prefix':'docs/dtc_l1/review_packs/DTC_P42_PARALLEL_MECHANISM_REVIEW_V1',
 'Git_excludes':'raw logs, traces, binaries, original large intermediate metadata, fixed periodic event snapshots and compressed raw-counter extracts. Their hashes and archive paths remain in this index.',
 'files':all_entries,'SOURCE_KEEP':True,'source_Agent_roots_unchanged':True}
(R/'PUBLICATION_POLICY.json').write_text(json.dumps(policy,indent=2)+'\n',encoding='utf-8');include(R/'PUBLICATION_POLICY.json')
A=read(R/'agents/A/SUITE_PERFORMANCE_ANALYSIS.json');E=read(R/'agents/E/ACCEPTED_CELL_EVIDENCE.json');add=read(R/'agents/E/LATEST_ACCEPTED_ADDENDUM.json')
original=[]
for row in A['programs']:
 for mode,c in row['cells'].items():original.append({'program':row['program'],'cell':mode,'input_digest':row['input_digest'],'cycles':c['accepted_cycles'],
  'cohort':c['cohort'],'uuid':c['uuid'],'Core':c['actual_core_commit'],'Framework':c['actual_framework_commit'],'binary_sha256':c['actual_binary_sha256'],
  'configs':c['original_configs'],'references':c['references'],'raw_gzip_sha256':c['raw_gzip_sha256'],'detail':'agents/A/SUITE_PERFORMANCE_ANALYSIS.json'})
idx={'schema':'DTC_P42_PARALLEL_MECHANISM_EVIDENCE_INDEX_V1','baseline_commit':'71584878be0c80375f9d25bcd80e171b7bf4478d','freeze_sha256':A['freeze_sha256'],
 'original_cells':original,'separate_new_scope_accepted':E+add['new_accepted_cells'],
 'accepted_cutoff_UTC':add['observed_UTC'],'pending_new_scope':add['pending_cells'],'no_repair_or_pending_substitution':True,
 'address_index':'shared_address_index/INDEX.json','cross_review':'coordinator/CROSS_REVIEW.json','research_boundary':'coordinator/FINAL_BOUNDARY_VERIFICATION.json',
 'source_files':all_entries,'all_key_quantities_have_full_input_and_build_receipts':True,
 'agent_reports':{'A':'agents/A/SUITE_PERFORMANCE_ANALYSIS.json','B':'agents/B/WORKLOAD_FEATURE_MATRIX.json','C':'agents/C/POSITIVE_CASE_MECHANISM_REPORT.json','D':'agents/D/STRIDED_WORKLOAD_ROOT_CAUSE_REPORT.json','E':'agents/E/PQ_PS_INDEPENDENT_REVIEW.json','E_addendum':'agents/E/LATEST_ACCEPTED_ADDENDUM.json','F':'agents/F/SEVEN_UNRESOLVED_ADJUDICATION_REPORT.json'}}
(R/'EVIDENCE_INDEX.json').write_text(json.dumps(idx,indent=2)+'\n',encoding='utf-8');include(R/'EVIDENCE_INDEX.json')
member_manifest={rel(p):{'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(files)}
(R/'ARCHIVE_MEMBER_MANIFEST.json').write_text(json.dumps(member_manifest,indent=2)+'\n',encoding='utf-8');include(R/'ARCHIVE_MEMBER_MANIFEST.json')
zpath=R/'full_review_v1.zip'
with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_DEFLATED)as z:
 for p in sorted(files):z.write(p,rel(p))
with zipfile.ZipFile(zpath)as z:assert z.testzip()is None
pub=[rel(p)for p in sorted(files)if in_git(p)]
out={'zip':str(zpath),'zip_sha256':sha(zpath),'zip_bytes':zpath.stat().st_size,'archive_files':len(files),'Git_files':len(pub),'Git_paths':pub,
 'source_zip_kept':True,'uncompressed_bytes':sum(p.stat().st_size for p in files)}
(R/'PACKAGE_BUILD.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items()if k!='Git_paths'}))
