"""The single approved official-sdist wheel build, without dependency resolution or CUDA."""
import pathlib,os,json,subprocess,hashlib,tarfile,zipfile,urllib.request,traceback,sys,time,importlib.metadata as md
root=pathlib.Path(os.environ['TASK_DATA']);old=pathlib.Path(os.environ['OLD_TASK_DATA']);raw=root/'raw';receipt={'build_attempts':0,'status':'RUNNING','version':'4.9.3','cuda_allowed':False};target=root/'inputs/antlr4-python3-runtime-4.9.3.tar.gz';expected='f224469b4168294902bb1efa80a8bf7855f24c99aef99cbefc1bcd3cce77881b'
def save():(raw/'PACKAGING_EXCEPTION_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try:
 assert sys.version_info[:3]==(3,11,17)
 for name,v in [('pip','26.2.1'),('setuptools','84.0.0'),('wheel','0.48.0')]:assert md.version(name)==v
 meta=json.loads((old/'raw/antlr4_4.9.3_pypi_metadata.json').read_text());entry=next(x for x in meta['urls'] if x['filename']==target.name);assert entry['digests']['sha256']==expected and entry['size']==117034
 url=entry['url'];assert urllib.request.urlparse(url).hostname=='files.pythonhosted.org' if hasattr(urllib.request,'urlparse') else url.startswith('https://files.pythonhosted.org/')
 subprocess.run(['curl','--fail','--location','--connect-timeout','15','--max-time','120','--max-filesize','117034','--output',str(target),url],check=True,stdout=subprocess.DEVNULL,stderr=(raw/'ANTLR_DOWNLOAD.log').open('w'))
 assert target.stat().st_size==117034 and sha(target)==expected
 receipt.update(sdist_url=url,sdist_bytes=117034,sdist_sha256=sha(target));save()
 extract=root/'antlr_build_source';extract.mkdir()
 with tarfile.open(target) as t:
  members=[{'name':m.name,'type':m.type.decode(),'bytes':m.size} for m in t.getmembers()]
  for m in t.getmembers():
   assert m.isfile() or m.isdir(),'archive links/special file forbidden';assert (extract/m.name).resolve().is_relative_to(extract.resolve()),'archive path escape'
  t.extractall(extract,filter='data')
 (raw/'ANTLR_SDIST_MEMBERS.json').write_text(json.dumps(members,indent=2)+'\n')
 setup=next(extract.glob('*/setup.py'));text=setup.read_text();(raw/'ANTLR_SETUP.py').write_text(text,encoding='utf-8')
 assert not any(x in text for x in ['subprocess','urlopen','os.system','requests.','download_url=']), 'unexpected automatic network/build script'
 receipt['setup_audit']='PASS_NO_NETWORK_SCRIPT';save()
 # No pip build isolation or package-index access; exactly one actual wheel build.
 cmd=[sys.executable,'-m','pip','wheel','--no-deps','--no-build-isolation','--no-index','--wheel-dir',str(root/'wheelhouse'),str(target)]
 receipt.update(build_attempts=1,build_command=cmd,build_dependencies={n:md.version(n) for n in ['pip','setuptools','wheel','packaging']});save()
 with (raw/'ANTLR_BUILD.log').open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
 receipt['build_returncode']=r.returncode;save();assert r.returncode==0,'SINGLE_BUILD_FAILED'
 wheels=list((root/'wheelhouse').glob('antlr4_python3_runtime-4.9.3-*.whl'));assert len(wheels)==1;w=wheels[0]
 from packaging.utils import parse_wheel_filename
 from packaging.tags import sys_tags
 name,version,build,tags=parse_wheel_filename(w.name);assert str(version)=='4.9.3' and tags.intersection(set(sys_tags()))
 with zipfile.ZipFile(w) as z:
  for n in z.namelist():assert not n.startswith('/') and '..' not in pathlib.PurePosixPath(n).parts
  assert not any('.data/scripts/' in n for n in z.namelist())
  metadata=z.read(next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'))).decode();wheelmeta=z.read(next(n for n in z.namelist() if n.endswith('.dist-info/WHEEL'))).decode();members=z.namelist()
 assert '\nVersion: 4.9.3\n' in metadata
 (raw/'ANTLR_WHEEL_METADATA.txt').write_text(metadata);(raw/'ANTLR_WHEEL_TAGS.txt').write_text(wheelmeta);(raw/'ANTLR_WHEEL_MEMBERS.json').write_text(json.dumps(members,indent=2)+'\n')
 receipt.update(wheel_filename=w.name,wheel_sha256=sha(w),wheel_bytes=w.stat().st_size,wheel_tags=sorted(map(str,tags)),wheel_metadata_version='4.9.3',unexpected_scripts=False)
 subprocess.run([sys.executable,'-m','pip','install','--no-deps','--no-index',str(w)],check=True,stdout=(raw/'ANTLR_INSTALL.log').open('w'),stderr=subprocess.STDOUT)
 import antlr4
 assert md.version('antlr4-python3-runtime')=='4.9.3';receipt['isolated_antlr_import']='PASS';receipt['import_path']=antlr4.__file__
 (root/'V1R1_DERIVED_WHEEL_LOCK').write_text(json.dumps({'distribution':'antlr4-python3-runtime','version':'4.9.3','official_sdist_sha256':expected,'local_wheel_sha256':sha(w),'wheel_filename':w.name,'original_lock_unchanged':True,'scope':'Only this artifact hash is derived; all82 resolved versions remain fixed'},indent=2)+'\n')
 receipt['status']='PACKAGING_SOURCE_WHEEL_PASS_ANTLR_ONLY';save()
except Exception as e:
 receipt.update(status='PACKAGING_SOURCE_WHEEL_FAIL',error=str(e),traceback=traceback.format_exc());save();print(receipt['traceback'],flush=True);sys.exit(1)
print(json.dumps(receipt),flush=True)
