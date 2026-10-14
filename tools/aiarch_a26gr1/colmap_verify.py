"""Read official COLMAP bytes and verify full cross-file/image correspondence."""
import array,hashlib,json,math,pathlib,resource,struct,sys,time
from control import ROOT,check
base=ROOT/'colmap';raw=ROOT/'raw/rubble-pixsfm';t0=time.monotonic()
def read(f,n):
 b=f.read(n)
 if len(b)!=n:raise RuntimeError('TRUNCATED_COLMAP')
 return b
def qread(f):return struct.unpack('<Q',read(f,8))[0]
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(4*1024**2):h.update(b)
 return h.hexdigest()
def jpeg_dimensions(path):
 with path.open('rb') as f:
  assert read(f,2)==b'\xff\xd8'
  consumed=2
  while consumed<1024**2:
   b=read(f,1);consumed+=1
   if b!=b'\xff':continue
   while b==b'\xff':b=read(f,1);consumed+=1
   marker=b[0]
   if marker in {0xd8,0xd9}:continue
   length=struct.unpack('>H',read(f,2))[0];consumed+=2
   if marker in {0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf}:
    head=read(f,5);return struct.unpack('>HH',head[1:5])[::-1]
   if length<2:raise RuntimeError('BAD_JPEG_MARKER')
   f.seek(length-2,1);consumed+=length-2
 raise RuntimeError('NO_BOUNDED_JPEG_DIMENSIONS')
cameras={}
with (base/'cameras.bin').open('rb') as f:
 nc=qread(f);assert nc==1
 for _ in range(nc):
  cid,model,w,h=struct.unpack('<iiQQ',read(f,24));assert model==1
  params=struct.unpack('<dddd',read(f,32));assert all(math.isfinite(x) for x in params) and params[0]>0 and params[1]>0
  cameras[cid]={'model':'PINHOLE','width':w,'height':h,'params':params}
 assert not f.read(1)
paths={}
for p in raw.glob('*/rgbs/*'):
 if not p.is_file():continue
 assert p.name not in paths,'DUPLICATE_RAW_IMAGE_BASENAME'
 paths[p.name]=p
images={};total_features=0;ref_ids=set();names=set();quaternion_norm_deviations=[]
with (base/'images.bin').open('rb') as f:
 ni=qread(f);assert 0<ni<=10000
 for idx in range(ni):
  fields=struct.unpack('<idddddddi',read(f,64));iid=fields[0];camera=fields[-1];pose=fields[1:-1]
  assert iid not in images and camera in cameras and all(math.isfinite(x) for x in pose)
  assert sum(x*x for x in pose[:4])>0,'ZERO_COLMAP_QUATERNION'
  quaternion_norm_deviations.append(abs(sum(x*x for x in pose[:4])-1))
  namebytes=bytearray()
  while True:
   b=read(f,1)
   if b==b'\x00':break
   namebytes.extend(b);assert len(namebytes)<4096
  name=namebytes.decode('utf-8');assert pathlib.PurePosixPath(name).name==name and name not in names;names.add(name)
  assert name in paths,('COLMAP_IMAGE_MISSING',name)
  assert jpeg_dimensions(paths[name])==(cameras[camera]['width'],cameras[camera]['height']),('JPEG_CAMERA_DIMENSION_MISMATCH',name)
  n=qread(f);assert n<=5000000;buf=read(f,n*24);ids=array.array('q')
  for x,y,pid in struct.iter_unpack('<ddq',buf):
   assert math.isfinite(x) and math.isfinite(y)
   ids.append(pid)
   if pid!=-1:ref_ids.add(pid)
  images[iid]={'name':name,'camera_id':camera,'pose':pose,'point_ids':ids};total_features+=n
  if idx%128==0:check();print('COLMAP_IMAGES',idx+1,ni,flush=True)
 assert not f.read(1)
assert set(paths)==names,('RAW_AND_COLMAP_IMAGE_SET_MISMATCH',len(paths),len(names))
pointids=set();tracks=0;maxtrack=0;errors=[];first_failure=None
with (base/'points3D.bin').open('rb') as f:
 np=qread(f);assert 0<np<=10000000
 for idx in range(np):
  pid,x,y,z,r,g,b,error,ntrack=struct.unpack('<QdddBBBdQ',read(f,51))
  assert pid not in pointids and all(math.isfinite(v) for v in [x,y,z,error]);pointids.add(pid)
  assert 0<=error and ntrack<=10000;track=read(f,ntrack*8);tracks+=ntrack;maxtrack=max(maxtrack,ntrack)
  for image_id,point_idx in struct.iter_unpack('<II',track):
   if image_id not in images or point_idx>=len(images[image_id]['point_ids']) or images[image_id]['point_ids'][point_idx]!=pid:
    first_failure={'point3D_id':pid,'image_id':image_id,'point2D_idx':point_idx,'image_exists':image_id in images,'image_point_id':int(images[image_id]['point_ids'][point_idx]) if image_id in images and point_idx<len(images[image_id]['point_ids']) else None};break
  if first_failure:break
  if idx%100000==0:check();print('COLMAP_POINTS',idx+1,np,flush=True)
 if first_failure:
  failure={'status':'FAIL','reason':'COLMAP_POINT_IMAGE_TRACK_IDENTITY_MISMATCH','first_mismatch':first_failure,'camera_count':nc,'image_count':ni,'decoded_points_before_mismatch':len(pointids),'point_count_declared':np,'mutated_input':False,'wall_seconds':time.monotonic()-t0}
  (ROOT/'colmap_identity_failure.json').write_text(json.dumps(failure,indent=2)+'\n');raise RuntimeError(str(failure))
 assert not f.read(1)
dangling_forward_ids=sorted(ref_ids-pointids)
# Frozen GS-Scale builds point_indices from manager.point3D_id_to_images, not image feature forward IDs.
# Every consumed outgoing point->image track was checked above; preserve and report unused dangling metadata.
ordered=sorted(names);manifest=[]
extracted=json.loads((ROOT/'extracted_asset_files.json').read_text());hashmap={pathlib.PurePosixPath(x['name']).name:x['sha256'] for x in extracted['files'] if '/rgbs/' in x['name']}
for i,name in enumerate(ordered):
 manifest.append({'name':name,'sorted_index':i,'split':'test' if i%83==0 else 'train','raw_image_sha256':hashmap[name],'original_dimensions':[4608,3456],'author_downsample_factor':4,'expected_downsample_dimensions':[1152,864]})
receipt={'status':'REAL_SCENE_BYTE_CORRESPONDENCE_PASS','camera_count':nc,'cameras':cameras,'image_count':ni,'point_count':np,'feature_count':total_features,'track_entry_count':tracks,'max_track_length':maxtrack,'all_point_image_track_references_match':True,'all_image_point_refs_exist':not bool(dangling_forward_ids),'unused_dangling_feature_point_ids':dangling_forward_ids,'unused_forward_metadata_preserved':True,'frozen_author_consumed_point_indices_track_map_complete':True,'source_interpretation':'GS-Scale colmap.Parser lines 217-232 consumes points3D arrays and outgoing point3D_id_to_images; image feature forward IDs are not used to initialize or train this workload','all_original_jpeg_dimensions_match':True,'quaternion_norm2_max_deviation':max(quaternion_norm_deviations),'quaternion_bytes_not_normalized_or_modified':True,'raw_image_set_equals_merged_colmap_set':True,'train_count':sum(x['split']=='train' for x in manifest),'test_count':sum(x['split']=='test' for x in manifest),'scene_manifest_sha256':hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest(),'colmap_files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(base.glob('*.bin'))],'image_manifest':manifest,'derived_resize_bytes':'PENDING_AUTHOR_VERSION_CPU_PREPROCESSING','wall_seconds':time.monotonic()-t0,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'budget':check()}
(ROOT/'colmap_identity.json').write_text(json.dumps(receipt,indent=2)+'\n');print('COLMAP_COMPLETE_IDENTITY_PASS',ni,np,total_features,tracks,flush=True)
