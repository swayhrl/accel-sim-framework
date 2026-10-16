from common import *
import base64,zipfile,subprocess
ref='fc36357f2c1d861870b4c13a58f73da2b93d1e73';expected={'ODC-By-1.0':'dab29a14b77b9cd9b523e4aeaaf6fdb2aaa3624b','LICENSE':'931d368d8f65923bb22d8d059da3d45ab3afac1c','igb/download.py':'478bf8d1f24ebefa4aed43cca44ced7dd4e39210','igb/dataloader.py':'b4b6e342df4511ef99a488336b57502fff754fe4'};out=[]
for path in ['ODC-By-1.0','LICENSE','README.md','igb/download.py','igb/dataloader.py']:
 r,b=request('https://api.github.com/repos/IllinoisGraphBenchmark/IGB-Datasets/contents/'+path+'?ref='+ref)
 assert r.get('status')==200,(path,r)
 d=json.loads(b);raw=base64.b64decode(d['content']);blob=hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest();assert blob==d['sha'];assert path not in expected or blob==expected[path]
 p=R/'source'/path.replace('/','_');p.write_bytes(raw);out.append({'path':path,'fixed_commit':ref,'blob':blob,'sha256':sha(p),'bytes':len(raw),'URL':r['url']})
print('AUTHOR_SOURCES_PASS',json.dumps(out),flush=True);save('author_source_identity.json',out)
old=pathlib.Path('/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014');site=old/'venv/lib/python3.10/site-packages';print('CACHED_SITE',site,site.exists())
names=['torch','torchgen','functorch','triton','nvidia'];print('REUSABLE',[(n,(site/n).exists()) for n in names]);print('CACHED_METADATA',[(p.name,p.stat().st_size) for p in site.glob('*.dist-info/METADATA') if p.parent.name.startswith(('torch-','nvidia_','triton-','numpy-','scipy-'))]);print('WHEEL_UNPACKED_LOWER',sum(x.file_size for x in zipfile.ZipFile(old/'wheels/torch-2.2.0+cu121-cp310-cp310-linux_x86_64.whl').infolist()))
print('SOURCE_LICENSE', (R/'source/LICENSE').read_text());print('SOURCE_DOWNLOADER',(R/'source/igb_download.py').read_text());print('SOURCE_DATALOADER',(R/'source/igb_dataloader.py').read_text())
