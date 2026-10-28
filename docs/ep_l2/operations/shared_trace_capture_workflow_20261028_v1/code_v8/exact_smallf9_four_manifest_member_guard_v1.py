"""Exact four frozen singleF9 archive manifests only; no general bound change or payload verification claim."""
import pathlib
EXACT_FOUR={'DWTHAAR1D_SM89_487DB4C26256_CAPTURE55_SINGLE_F9_ACTUAL_A001': {'count': 48, 'kind': 'FULL_APPLICATION_TRACE'}, 'DWTHAAR1D_SM89_487DB4C26256_CAPTURE55_SINGLE_F9_ACTUAL_A001_CTA_STRIDE_40_V1': {'count': 9, 'kind': 'DERIVED_COMPLETE_CTA_TRACE'}, 'STREAMCLUSTER_SM89_0E407037C56B_CAPTURE55_SINGLE_F9_ACTUAL_A001': {'count': 429, 'kind': 'FULL_APPLICATION_TRACE'}, 'STREAMCLUSTER_SM89_0E407037C56B_CAPTURE55_SINGLE_F9_ACTUAL_A001_CTA_STRIDE_40_V1': {'count': 137, 'kind': 'DERIVED_COMPLETE_CTA_TRACE'}}
def need(v,m):
 if not v:raise ValueError('MVT_ARCHIVE_REJECT:'+m)
def member_rows(m):
 aid=m.get('asset_id');need(type(aid)is str and aid in EXACT_FOUR,'only exact approved four assets');expected=EXACT_FOUR[aid];need(m.get('kind')==expected['kind'],'exact asset manifest kind')
 rows=m['files'];need(type(rows)is list and 1<=len(rows)<=512 and len(rows)==expected['count'],'exact scoped member count <=512')
 names=[]
 for r in rows:
  p=pathlib.PurePosixPath(r['path']);need(not p.is_absolute()and '..'not in p.parts and str(p)==r['path']and r['path']not in ['MANIFEST.json','COMMIT.json'],'canonical relative member')
  need(type(r['bytes'])is int and 0<=r['bytes']<=128*1024**2 and type(r['sha256'])is str and len(r['sha256'])==64 and all(c in '0123456789abcdef'for c in r['sha256']),'member size/digest')
  names.append(r['path'])
 need(len(names)==len(set(names))and m['logical_bytes']==sum(r['bytes']for r in rows)<=256*1024**2,'unique bounded complete package')
 return rows