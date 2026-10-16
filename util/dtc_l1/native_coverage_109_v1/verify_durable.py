#!/usr/bin/env python3
"""Independent mounted164 SHA verification; never extracts/modifies archive."""
import json,os,pathlib,subprocess
root=pathlib.Path(os.environ.get('DTC_NATIVE_ROOT','/data/c16/dtc_native_coverage_109_v1'));repo=pathlib.Path(__file__).resolve().parents[3];pack=repo/'docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1'
code=r'''
import hashlib,json,pathlib,tarfile,datetime
root=pathlib.Path('/root/share/mnt164/huangrulin/dtc_native_behavior_workload_coverage_109_v1/20261016_v1')
a=root/'dtc_native_coverage_109_v1_20261016.tar.gz';index=root/'PAYLOAD_FILES.json';expected={r['relative_path']:r for r in json.loads(index.read_text())};h=hashlib.sha256()
with a.open('rb') as f:
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
seen=set()
with tarfile.open(a,'r|gz') as t:
 for m in t:
  if not m.isfile():continue
  f=t.extractfile(m);s=hashlib.sha256();size=0
  for b in iter(lambda:f.read(1024*1024),b''):s.update(b);size+=len(b)
  if m.name=='PAYLOAD_FILES.json':assert s.hexdigest()==hashlib.sha256(index.read_bytes()).hexdigest();continue
  assert m.name in expected,m.name
  r=expected[m.name];assert size==r['bytes'] and s.hexdigest()==r['sha256'],m.name;seen.add(m.name)
assert seen==set(expected),(len(seen),len(expected))
print(json.dumps(dict(status='PASS_DESTINATION_INDEPENDENT_ARCHIVE_AND_EVERY_MEMBER_SHA256',archive=str(a),archive_sha256=h.hexdigest(),archive_bytes=a.stat().st_size,index_sha256=hashlib.sha256(index.read_bytes()).hexdigest(),verified_files=len(seen),verified_payload_bytes=sum(r['bytes'] for r in expected.values()),verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),route='109 -> hrl174new -> mounted164',extraction='none; read-only streaming tar audit')))
'''
cp=subprocess.run(['ssh','hrl174new','python3','-'],input=code,text=True,capture_output=True)
if cp.returncode:raise RuntimeError(cp.stderr)
receipt=json.loads(cp.stdout);local=(root/'ARCHIVE_SHA256.txt').read_text().split()[0];assert receipt['archive_sha256']==local
(pack/'DURABLE_STORE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');(root/'DURABLE_STORE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
