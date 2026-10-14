"""Parallel byte-equivalent author BICUBIC preprocessing; no Torch import."""
import ast,concurrent.futures,hashlib,json,os,pathlib,shutil,sys,time,typing
import imageio.v2 as imageio,numpy as np
from PIL import Image
from control import ROOT,check
source=ROOT/'software_sources/gsscale/examples/datasets/colmap.py';text=source.read_text();tree=ast.parse(text)
fns=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'_get_rel_paths','_resize_image_folder'}]
ns={'os':os,'List':typing.List,'Image':Image,'imageio':imageio,'np':np,'tqdm':lambda x:x,'print':lambda *a,**k:None}
exec(compile(ast.Module(body=fns,type_ignores=[]),str(source),'exec'),ns)
SCENE=ROOT/'scene';IMAGES=SCENE/'images';RESIZED=SCENE/'images_4_png'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024**2):h.update(b)
 return h.hexdigest()
def one(row):
 name=row['name'];dst=IMAGES/name;raw=next((ROOT/'raw/rubble-pixsfm').glob('*/rgbs/'+name))
 if not dst.exists():shutil.copyfile(raw,dst)
 assert sha(dst)==row['raw_image_sha256']
 ns['_get_rel_paths']=lambda p:[name]
 ns['_resize_image_folder'](str(IMAGES),str(RESIZED),4)
 out=RESIZED/(pathlib.Path(name).stem+'.png')
 with Image.open(out) as im:assert im.size==(1152,864) and im.mode=='RGB'
 return {'image_name':name,'derived_name':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'dimensions':[1152,864]}
if __name__=='__main__':
 identity=json.loads((ROOT/'colmap_identity.json').read_text());assert identity['status']=='REAL_SCENE_BYTE_CORRESPONDENCE_PASS';rows=identity['image_manifest']
 check(extra=sum(x.stat().st_size for x in (ROOT/'raw/rubble-pixsfm').glob('*/rgbs/*'))+len(rows)*1152*864*3+8*1024**3)
 IMAGES.mkdir(parents=True,exist_ok=True);RESIZED.mkdir(exist_ok=True);(SCENE/'sparse/0').mkdir(parents=True,exist_ok=True)
 for p in (ROOT/'colmap').glob('*.bin'):shutil.copyfile(p,SCENE/'sparse/0'/p.name)
 t=time.monotonic();results=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
  for i,x in enumerate(pool.map(one,rows,chunksize=4)):
   results.append(x)
   if i%64==0:check();print('AUTHOR_RESIZE_PROGRESS',i+1,len(rows),flush=True)
 # Re-run exact original resize function on four singleton directories and compare emitted PNG bytes.
 checks=[]
 for i in [0,109,len(rows)//2,len(rows)-1]:
  row=rows[i];name=row['name'];tmp=ROOT/'resize_replay'/str(i);tmp.mkdir(parents=True,exist_ok=True);shutil.copyfile(IMAGES/name,tmp/name)
  ns['_get_rel_paths']=lambda p,n=name:[n];ns['_resize_image_folder'](str(tmp),str(tmp/'out'),4)
  replay=tmp/'out'/(pathlib.Path(name).stem+'.png');assert sha(replay)==results[i]['sha256'];checks.append({'index':i,'png_sha256':sha(replay),'exact_source_function_byte_match':True})
 manifest_sha=hashlib.sha256(json.dumps(results,sort_keys=True).encode()).hexdigest()
 (ROOT/'derived_image_manifest.json').write_text(json.dumps({'status':'PASS','author_function_ast_sha256':hashlib.sha256(ast.dump(ast.Module(body=fns,type_ignores=[])).encode()).hexdigest(),'image_count':len(results),'factor':4,'recipe':'exact frozen author function; four independent per-file CPU workers; pixels/encoder settings unchanged','versions':{'numpy':np.__version__,'imageio':__import__('imageio').__version__,'pillow':Image.__version__},'singleton_replay_checks':checks,'manifest_sha256':manifest_sha,'files':results,'wall_seconds':time.monotonic()-t,'budget':check()},indent=2)+'\n')
 print('AUTHOR_SCENE_PREPROCESS_PASS',len(results),manifest_sha,flush=True)
