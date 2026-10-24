"""Read-only independent archive/member/CPU-text review, then a native restore."""
from pathlib import Path
import hashlib,gzip,io,json,tarfile,os,time,re

D=Path('/root/data/cubin_collision_parent_closeout_20261024_v1')
ROOT='/data/c16/cubin_duplicate_extract_cpu_20261024_v1/'
archives=[
 ('COLLISION_EXTRACTOR_FROZEN_CLOSEOUT_V1.tar.gz','3048adf8536d93f86787321c66774d73c55bd785b34b369aaceb6648a74c380d',516,'native_restore','evidence/',28,'collision_closure_batch_v1/BATCH_RESULT.json'),
 ('FORMAL_SUPPLEMENT_CLOSEOUT_V1.tar.gz','bdd671e550a8baa19d4b95f99e10fb2cc906c572ad4b4ded766b4c00aa03309b',21,'supplement_native_restore','',1,'collision_closure_formal_supplement_v1/BATCH_RESULT.json')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proof=[];classifications=[]
for name,want,count,dirname,prefix,total,result_path in archives:
 p=D/name;assert sha(p)==want
 raw=gzip.decompress(p.read_bytes());assert len(raw)<64*1024**2
 dest=D/dirname;resume=dest.exists();assert not dest.is_symlink()
 if not resume:dest.mkdir(mode=0o700)
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:',ignore_zeros=True,errorlevel=2)as tf:
  members=tf.getmembers();assert len(members)==count and all(t.isfile()for t in members)
  names={t.name for t in members};assert len(names)==count
  m=json.loads(tf.extractfile('FREEZE.json').read());rows=m.get('members',m.get('files'));rows={r['member']:r for r in rows}
  assert names==set(rows)|{'FREEZE.json'}
  if resume:assert {str(f.relative_to(dest))for f in dest.rglob('*')if f.is_file()}==names
  for t in members:
   rel=Path(t.name);assert not rel.is_absolute()and '..'not in rel.parts
   b=tf.extractfile(t).read();h=hashlib.sha256(b).hexdigest()
   if t.name!='FREEZE.json':assert len(b)==rows[t.name]['bytes']and h==rows[t.name]['sha256']
   out=dest/rel
   if resume:assert out.stat().st_size==len(b)and sha(out)==h
   else:
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
   assert out.stat().st_dev==2128 and sha(out)==h
 q=json.loads((dest/(prefix+result_path)).read_text());assert q['success']==q['total']==total
 for row in q['results']:
  images=row['images'];seen=[]
  for x in images:
   assert x['cpu_readback']['sass']['path'].startswith(ROOT)
   outputs={}
   for kind,y in x['cpu_readback'].items():
    path=dest/(prefix+y['path'][len(ROOT):]);assert path.stat().st_size==y['bytes']and sha(path)==y['sha256']
    outputs[kind]=path.read_text()
   functions=re.findall(r'Function\s*:\s*(\S+)',outputs['sass']);assert functions==x['functions']
   empty=not functions
   assert empty==x['empty_code_image']
   if empty:assert 'FUNC'not in outputs['symbols']and '.text'not in outputs['sections']
   else:assert 'FUNC'in outputs['symbols']and '.text.'in outputs['sections']
   seen.append((x['basename'],empty))
  overwritten=[v for k,v in enumerate(seen)if v[0]in [y[0]for y in seen[k+1:]]]
  assert overwritten and all(empty for _,empty in overwritten)
  classifications.append({'binary_sha256':row['source_sha256'],'program':row['program'],'all_overwritten_preceding_images_empty_code':True,'listed_images':len(images),'overwritten_empty_images':len(overwritten)})
 proof.append({'archive':name,'sha256':want,'regular_members':count,'full_gzip_CRC_and_tar_header_scan':True,'every_native_member_full_SHA_reopen':True,'native_root':str(dest)})
assert len(classifications)==len({x['binary_sha256']for x in classifications})==29
out={'status':'PARENT_29_COLLISION_BINARIES_FULL_ARCHIVES_NATIVE_SHA_AND_EMPTY_CODE_ANALYSIS_PASS','archives':proof,'binary_classifications':classifications,'total_regular_members':537,'scope':'Exact29 binaries, all listed static images retained; does not grant actual-loaded/JIT/all-runtime/producer/consumer/timing qualification','source_keep':True,'old_failed_qualifier_retained':True,'GPU_or_simulator_execution':False,'verifier_sha256':sha(Path(__file__)),'unix':time.time()}
p=D/'PARENT_29_COLLISION_READBACK.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':out['status'],'regular_members':537,'unique_binary_rows':29,'receipt_sha256':sha(p)}))
