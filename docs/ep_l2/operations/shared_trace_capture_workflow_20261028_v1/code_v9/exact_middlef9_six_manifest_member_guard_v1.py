"""Private exact6 manifest geometry only. Original reviewed H is unchanged; sender/receiver routines remain original."""
from pathlib import Path,PurePosixPath
import json,hashlib
D=Path(__file__).resolve().parent
S=json.loads((D/'EXACT_MIDDLEF9_SIX_MANIFEST_SCOPE_V1.json').read_bytes())['scope']
def need(v,m):
 if not v:raise ValueError('MVT_ARCHIVE_REJECT:'+m)
def member_rows(m):
 aid=m.get('asset_id');need(aid in S,'exact6 asset ID');s=S[aid];need(m.get('kind')==s['kind'],'exact asset kind');rows=m['files'];need(type(rows)is list and len(rows)==s['count']and len(rows)<=1024,'exact member count')
 for r in rows:
  path=r['path'];p=PurePosixPath(path);need(not p.is_absolute()and '..'not in p.parts and str(p)==path and path not in['MANIFEST.json','COMMIT.json'],'canonical member path')
  need(type(r['bytes'])is int and 0<=r['bytes']<=128*2**20 and type(r['sha256'])is str and len(r['sha256'])==64 and all(c in'0123456789abcdef'for c in r['sha256']),'member size/hash')
 names=[r['path']for r in rows];need(len(names)==len(set(names)),'duplicate member');logical=sum(r['bytes']for r in rows);need(type(m['logical_bytes'])is int and m['logical_bytes']==logical,'logical sum')
 if s['kind']=='FULL_APPLICATION_TRACE':
  need(logical==s['logical_bytes'],'exact ordinary logical bytes');raw=(json.dumps(m,indent=2,sort_keys=True)+'\n').encode();need(hashlib.sha256(raw).hexdigest()==s['manifest_raw_sha256'],'actual Root ordinary manifest rawSHA')
 else:
  table={r['path']:r for r in rows};fixed={r['path']:r for r in s['fixed_members']};need(set(table)==set(fixed)|set(s['metadata_member_byte_maxima']),'exact derived payload plus4metadata')
  for name,r in fixed.items():need(table[name]==r,'actual frozen derived payload/tool row')
  for name,cap in s['metadata_member_byte_maxima'].items():need(0<table[name]['bytes']<=cap,'bounded generated parent metadata')
  need(s['logical_min_bytes']<=logical<=s['logical_max_bytes'],'derived actualdraft plus bounded4metadata logical bytes');need(m.get('parent_asset_id')==s['parent_asset_id']and m.get('parent_manifest_sha256')==s['parent_manifest_sha256'],'exact real parent manifest identity');p=m.get('parent_commit_sha256');need(type(p)is str and len(p)==64 and all(c in'0123456789abcdef'for c in p),'real parent COMMIT SHA shape; caller joins exact actual value')
 return rows
