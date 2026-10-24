"""Independent streaming join of every selected CTA against immutable full data."""
from pathlib import Path
import json,lzma,re,hashlib,time
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
B=Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/objects')
P=B/'SDK42_VECTOR_4000000_ADA7_A002';D=B/'SDK42_VECTOR_4000000_ADA7_A002_CTA_STRIDE_40_V1'
maps=[json.loads(x) for x in (D/'SELECTION_MAP.jsonl').read_text().splitlines()];assert len(maps)==391
assert hashlib.sha256((P/'MANIFEST.json').read_bytes()).hexdigest()=='b6df7945cf79251b2f816a9a6db59328f507339bdf35a0401fc742c71052d234'
assert hashlib.sha256((D/'MANIFEST.json').read_bytes()).hexdigest()=='d9a8c17342d56b41606682ae9f4311ba0c8c801e9f426b4ebb52aab3f377ad9c'
assert len({x['kernel']for x in maps})==1;name=maps[0]['kernel'];expected={tuple(x['origin']):x for x in maps};assert len(expected)==391
for i,x in enumerate(maps):assert x['origin']==[i*40,0,0] and x['origin_linear']==i*40 and x['derived']==[i,0,0]
record=re.compile(rb'^[0-9a-fA-F]+ [0-9a-fA-F]{1,8} [0-9]+ ')
def blocks(path,header):
 with lzma.open(path,'rb') as f:
  current=None;coords=None;records=0
  for line in f:
   if line.strip()==b'#BEGIN_TB':assert current is None;current=[line];coords=None;records=0
   elif current is None:header.append(line)
   else:
    if line.startswith(b'thread block = '):
     assert coords is None;coords=tuple(map(int,line.split(b'=',1)[1].strip().split(b',')))
    else:current.append(line)
    if record.match(line):records+=1
    if line.strip()==b'#END_TB':
     assert coords is not None;yield coords,hashlib.sha256(b''.join(current)).hexdigest(),records;current=None
  assert current is None
selected={};parent_header=[];total_parent=0
for coords,sha,count in blocks(P/'traces'/name,parent_header):
 total_parent+=1
 if coords in expected:selected[coords]=(sha,count)
assert total_parent==15625 and set(selected)==set(expected)
trim_header=[];joins=[]
for coords,sha,count in blocks(D/'traces'/name,trim_header):
 assert coords==tuple(maps[len(joins)]['derived']);origin=tuple(maps[len(joins)]['origin']);assert (sha,count)==selected[origin] and count==maps[len(joins)]['records']
 joins.append({'original_CTA':origin,'derived_CTA':coords,'coordinate_line_excluded_body_sha256':sha,'records':count,'all_other_body_bytes_equal':True})
assert len(joins)==391 and sum(x['records']for x in joins)==50048
ph=[x for x in parent_header if x.strip() and not x.startswith(b'-grid dim = ')]
dh=[x for x in trim_header if x.strip() and not x.startswith(b'-grid dim = ')]
assert ph==dh
proof={'status':'PASS_PARENT_INDEPENDENT_ALL_SELECTED_CTA_BODY_EQUALITY','parent_asset':P.name,'trim_asset':D.name,'full_parent_CTAs_streamed':total_parent,'selected_complete_CTAs':len(joins),'records':sum(x['records']for x in joins),'comparison':'Exact body bytes including every SASS/mask/address/dependency/warp line and BEGIN/END markers, excluding only the CTA coordinate line','all_other_nonblank_headers_equal_except_declared_grid_remap':True,'joins':joins,'whole_application_trace':False,'historical_crop_equivalence':False,'consumer_or_performance_qualification':'NOT_GRANTED','GPU_or_simulator_execution':False,'observed_unix':time.time()}
out=R/'control/PARENT_FIRST_TRIM_ALL_CTA_JOIN.json';assert not out.exists();out.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='joins'}))
